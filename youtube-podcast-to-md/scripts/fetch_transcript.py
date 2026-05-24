#!/usr/bin/env python3
"""
fetch_transcript.py
获取 YouTube 视频字幕，按优先级：手动英文字幕 > 自动英文字幕 > 其他字幕
输出：
  - transcript_raw.txt   原始带时间戳文本
  - transcript_meta.json 视频元数据
若字幕不可用，meta 中标记 transcript_available=false，由上游调用 Whisper 兜底。
"""

import sys
import json
import re
import os
import shutil
import subprocess


def _get_ytdlp_cmd() -> list:
    """返回可用的 yt-dlp 命令，优先 PATH 中的 yt-dlp，否则用 python3 -m yt_dlp"""
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    # 尝试 python3 -m yt_dlp
    result = subprocess.run(
        ["python3", "-m", "yt_dlp", "--version"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return ["python3", "-m", "yt_dlp"]
    return []  # 不可用


def ensure_dependencies():
    """检查并提示缺失的依赖"""
    missing = []

    try:
        import youtube_transcript_api  # noqa: F401
    except ImportError:
        missing.append("youtube-transcript-api")

    if not _get_ytdlp_cmd():
        missing.append("yt-dlp")

    if missing:
        pkgs = " ".join(missing)
        print(f"错误：缺少依赖包: {missing}")
        print(f"请运行: python3 -m pip install {pkgs}")
        print("提示：请确保 yt-dlp 在 PATH 中，或可通过 `python3 -m yt_dlp` 调用")
        sys.exit(2)


def fetch_with_transcript_api(video_id: str) -> tuple:
    """
    尝试用 youtube-transcript-api 获取字幕
    返回 (字幕列表, 来源描述, language_code)
    字幕列表格式: [{"start": 0.0, "duration": 2.5, "text": "..."}]
    """
    from youtube_transcript_api import YouTubeTranscriptApi

    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        # 优先级 1：手动英文字幕
        try:
            t = transcript_list.find_manually_created_transcript(['en', 'en-US', 'en-GB'])
            if t is not None:
                return t.fetch(), "手动英文字幕", "en"
        except Exception:
            pass  # 无手动字幕时可能抛出异常

        # 优先级 2：自动生成英文字幕
        try:
            t = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB'])
            if t is not None:
                return t.fetch(), "自动生成英文字幕", "en"
        except Exception:
            pass

        # 优先级 3：遍历所有可用字幕，优先其余英文变体，再退回任意语言
        available_transcripts = list(transcript_list)

        for t in available_transcripts:
            lang = (getattr(t, 'language_code', '') or '').lower()
            if lang.startswith("en"):
                return t.fetch(), f"字幕（语言：{lang}）", lang

        for t in available_transcripts:
            lang = getattr(t, 'language_code', '') or ''
            return t.fetch(), f"字幕（语言：{lang}）", lang

    except Exception as e:
        error_msg = str(e)
        if "disabled" in error_msg.lower():
            return None, "字幕已禁用", None
        return None, f"获取失败: {error_msg}", None

    return None, "无可用字幕", None


def fetch_meta_with_ytdlp(url: str) -> dict:
    """用 yt-dlp 获取视频元数据"""
    ytdlp_cmd = _get_ytdlp_cmd()
    if not ytdlp_cmd:
        print("错误：未找到 yt-dlp，请确认已安装: python3 -m pip install yt-dlp")
        sys.exit(2)

    try:
        result = subprocess.run(
            ytdlp_cmd + ["--dump-json", "--no-download", url],
            capture_output=True, text=True, timeout=30
        )
    except FileNotFoundError:
        print("错误：未找到 yt-dlp，请确认已安装: python3 -m pip install yt-dlp")
        sys.exit(2)
    except subprocess.TimeoutExpired:
        print("错误：yt-dlp 执行超时，请检查网络连接")
        sys.exit(3)

    if result.returncode != 0:
        print(f"警告：yt-dlp 获取元数据失败: {result.stderr.strip()}")
        return {
            "title": "未知标题", "channel": "", "duration": 0,
            "url": url, "video_id": "", "upload_date": "", "description": ""
        }

    data = json.loads(result.stdout)
    return {
        "title": data.get("title", "未知标题"),
        "channel": data.get("channel", data.get("uploader", "未知频道")),
        "duration": data.get("duration", 0),
        "upload_date": data.get("upload_date", ""),
        "description": (data.get("description", "") or "")[:500],
        "url": url,
        "video_id": data.get("id", "")
    }


def format_time(seconds: float) -> str:
    """将秒数转为 MM:SS 或 HH:MM:SS 格式"""
    s = int(seconds)
    h, m, s = s // 3600, (s % 3600) // 60, s % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def segments_to_text(segments: list) -> str:
    """
    将字幕片段列表转为文本，每隔约 30 秒插入时间戳标记 [TS:MM:SS]
    时间戳标记供后续 clean_transcript.py 分块使用
    支持 dict 和 FetchedTranscriptSnippet 两种类型
    """
    lines = []
    last_ts_mark = -30

    for seg in segments:
        # 兼容 dict 和 dataclass 两种类型
        if hasattr(seg, 'start'):
            start, text = seg.start, seg.text
        else:
            start = seg.get("start", 0)
            text = seg.get("text", "")

        text = text.strip() if text else ""
        if not text:
            continue

        if (start - last_ts_mark) >= 30:
            lines.append(f"\n[TS:{format_time(start)}]")
            last_ts_mark = start

        lines.append(text)

    return "\n".join(lines).lstrip("\n")


def extract_video_id(url: str) -> str:
    """从 YouTube URL 中提取 video_id"""
    patterns = [
        r"(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$"
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return ""


def main():
    if len(sys.argv) < 2:
        print("用法: python fetch_transcript.py <YouTube URL> [输出目录]")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    # 检查依赖
    ensure_dependencies()

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    print(f"[1/3] 正在解析视频信息……")
    video_id = extract_video_id(url)
    if not video_id:
        print(f"错误：无法从 URL 中提取视频 ID: {url}")
        print("请提供有效的 YouTube 链接（如 https://www.youtube.com/watch?v=xxx）")
        sys.exit(1)

    # 获取元数据
    meta = fetch_meta_with_ytdlp(url)
    print(f"  标题: {meta['title']}")
    print(f"  频道: {meta['channel']}")
    duration_min = meta['duration'] // 60 if meta['duration'] else 0
    if duration_min > 180:
        print(f"  ⚠ 时长: {duration_min} 分钟（超过 3 小时，建议只处理需要的片段）")
    else:
        print(f"  时长: {duration_min} 分钟")

    print(f"\n[2/3] 正在获取字幕……")
    segments, source, language_code = fetch_with_transcript_api(video_id)

    if segments is None:
        print(f"  ✗ 无法获取字幕: {source}")
        print("  → 请尝试运行 Whisper 兜底脚本，例如：")
        print(f"    python3 fetch_with_whisper.py '{url}' . --language auto")
        meta["transcript_source"] = "none"
        meta["transcript_available"] = False
        meta["transcript_language"] = None
    else:
        print(f"  ✓ 来源: {source}，共 {len(segments)} 段")

        # 根据来源给字幕质量评分
        if "手动" in source:
            quality = "高"
        elif "自动" in source:
            quality = "中（含自动生成噪声，clean_transcript 会处理）"
        else:
            quality = "中（若非英文，后续整理时应避免套用英文口头禅规则）"
        print(f"  质量评估: {quality}")

        meta["transcript_source"] = source
        meta["transcript_available"] = True
        meta["segment_count"] = len(segments)
        meta["transcript_language"] = language_code

        # 生成原始文本（含时间戳标记）
        raw_text = segments_to_text(segments)
        raw_path = os.path.join(output_dir, "transcript_raw.txt")
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(raw_text)
        print(f"  ✓ 原始文本已保存: {raw_path} ({len(raw_text)} 字符)")

    print(f"\n[3/3] 保存元数据……")
    meta_path = os.path.join(output_dir, "transcript_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 元数据已保存: {meta_path}")

    if meta.get("transcript_available"):
        print("\n✅ 完成！下一步: python clean_transcript.py transcript_raw.txt")
    else:
        print("\n⚠ 未获取到字幕；如已安装 Whisper，可继续运行兜底脚本。")

if __name__ == "__main__":
    main()
