#!/usr/bin/env python3
"""
fetch_with_whisper.py — Whisper 离线转录兜底脚本
当 youtube-transcript-api 无法获取字幕时使用。

工作流程：
  1. 用 yt-dlp 下载视频的纯音频（m4a/mp3）
  2. 使用 faster-whisper 或 openai-whisper 进行离线语音转录
  3. 输出与 fetch_transcript.py 兼容的 transcript_raw.txt 格式

依赖（按优先级）：
  - faster-whisper（推荐，速度快）: python3 -m pip install faster-whisper
  - 或 openai-whisper（备选）: python3 -m pip install openai-whisper
  - yt-dlp: python3 -m pip install yt-dlp
"""

import argparse
import sys
import json
import os
import re
import subprocess
import shutil


def _get_ytdlp_cmd() -> list:
    """返回可用的 yt-dlp 命令，优先 PATH 中的 yt-dlp，否则用 python3 -m yt_dlp"""
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    result = subprocess.run(
        ["python3", "-m", "yt_dlp", "--version"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return ["python3", "-m", "yt_dlp"]
    return []


def ensure_ytdlp():
    """检查 yt-dlp 是否可用"""
    if not _get_ytdlp_cmd():
        print("错误：未找到 yt-dlp")
        print("请安装: python3 -m pip install yt-dlp")
        sys.exit(2)


def download_audio(url: str, output_dir: str) -> str:
    """
    用 yt-dlp 下载最佳音质的纯音频
    返回下载的音频文件路径
    """
    output_template = os.path.join(output_dir, "audio.%(ext)s")

    ytdlp_cmd = _get_ytdlp_cmd()
    if not ytdlp_cmd:
        print("错误：未找到 yt-dlp")
        sys.exit(2)

    print("  正在下载音频（仅音频流，不下载视频）……")
    result = subprocess.run(
        ytdlp_cmd + [
            "-f", "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
            "-o", output_template,
            "--extract-audio",
            "--audio-format", "wav",
            "--no-playlist",
            url
        ],
        capture_output=True, text=True, timeout=600  # 10 分钟超时
    )

    if result.returncode != 0:
        print(f"  下载失败: {result.stderr}")
        # 尝试查找任何已下载的音频文件
        for ext in ["wav", "m4a", "webm", "mp3", "opus"]:
            candidate = os.path.join(output_dir, f"audio.{ext}")
            if os.path.exists(candidate):
                return candidate
        sys.exit(3)

    # 查找输出文件
    audio_path = os.path.join(output_dir, "audio.wav")
    if os.path.exists(audio_path):
        return audio_path

    # 有时 yt-dlp 会生成带原始扩展名的文件
    for ext in ["m4a", "webm", "mp3", "opus"]:
        candidate = os.path.join(output_dir, f"audio.{ext}")
        if os.path.exists(candidate):
            return candidate

    print("  警告：找不到下载的音频文件")
    sys.exit(3)


def transcribe_with_faster_whisper(audio_path: str, language: str) -> tuple:
    """
    使用 faster-whisper 进行转录
    返回 (字幕列表, 检测到的语言代码)
    """
    from faster_whisper import WhisperModel

    print("  正在加载 Whisper 模型（首次运行会下载约 1.5GB）……")
    # 使用 large-v3 模型追求最佳质量，turbo 模型速度更快
    try:
        model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    except Exception:
        print("  large-v3-turbo 不可用，回退到 medium 模型")
        model = WhisperModel("medium", device="cpu", compute_type="int8")

    print("  正在转录（这可能需要几分钟，取决于视频长度）……")
    transcribe_kwargs = {"beam_size": 5}
    if language and language != "auto":
        transcribe_kwargs["language"] = language

    segments_result, info = model.transcribe(audio_path, **transcribe_kwargs)

    segments = []
    for seg in segments_result:
        segments.append({
            "start": seg.start,
            "duration": seg.end - seg.start,
            "text": seg.text.strip()
        })

    detected_language = getattr(info, "language", None)
    return segments, detected_language


def transcribe_with_openai_whisper(audio_path: str, language: str) -> tuple:
    """
    使用 openai-whisper 进行转录（fallback）
    返回 (字幕列表, 检测到的语言代码)
    """
    import whisper

    print("  正在加载 Whisper 模型……")
    model = whisper.load_model("medium")

    print("  正在转录……")
    transcribe_kwargs = {}
    if language and language != "auto":
        transcribe_kwargs["language"] = language
    result = model.transcribe(audio_path, **transcribe_kwargs)

    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": seg["start"],
            "duration": seg["end"] - seg["start"],
            "text": seg["text"].strip()
        })

    return segments, result.get("language")


def init_whisper():
    """尝试导入 Whisper，优先使用 faster-whisper"""
    try:
        import faster_whisper  # noqa: F401
        return "faster-whisper"
    except ImportError:
        pass

    try:
        import whisper  # noqa: F401
        return "openai-whisper"
    except ImportError:
        print("错误：未找到 Whisper 库")
        print("请安装其中之一:")
        print("  python3 -m pip install faster-whisper  （推荐，更快）")
        print("  python3 -m pip install openai-whisper  （备选）")
        sys.exit(2)


def format_time(seconds: float) -> str:
    """将秒数转为 MM:SS 或 HH:MM:SS 格式"""
    s = int(seconds)
    h, m, s = s // 3600, (s % 3600) // 60, s % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def segments_to_text(segments: list) -> str:
    """将字幕片段列表转为文本，与 fetch_transcript.py 格式一致"""
    lines = []
    last_ts_mark = -30

    for seg in segments:
        start = seg.get("start", 0)
        text = seg.get("text", "").strip()
        if not text:
            continue

        if (start - last_ts_mark) >= 30:
            lines.append(f"\n[TS:{format_time(start)}]")
            last_ts_mark = start

        lines.append(text)

    return "\n".join(lines).lstrip("\n")


def extract_video_id(url: str) -> str:
    """从 URL 中提取 YouTube video_id"""
    patterns = [
        r"(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$"
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return ""


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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Whisper 离线转录 YouTube 视频，输出 transcript_raw.txt 和 transcript_meta.json"
    )
    parser.add_argument("url", help="YouTube 视频 URL")
    parser.add_argument("output_dir", nargs="?", default=".", help="输出目录，默认当前目录")
    parser.add_argument(
        "--language",
        default="auto",
        help="Whisper 语言代码，如 en / zh / ja；默认 auto 自动识别",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    url = args.url
    output_dir = args.output_dir
    language = args.language

    ensure_ytdlp()
    whisper_backend = init_whisper()
    os.makedirs(output_dir, exist_ok=True)

    print(f"[1/4] 正在获取视频信息……")
    video_id = extract_video_id(url)
    if not video_id:
        print(f"错误：无法从 URL 中提取视频 ID: {url}")
        sys.exit(1)

    meta = fetch_meta_with_ytdlp(url)
    meta["transcript_source"] = f"Whisper 离线转录（{whisper_backend}）"
    meta["transcript_available"] = True
    meta["transcript_language_requested"] = language

    print(f"  标题: {meta['title']}")
    print(f"  频道: {meta['channel']}")
    duration_min = meta['duration'] // 60 if meta['duration'] else 0
    print(f"  时长: {duration_min} 分钟")

    if duration_min > 120:
        print(f"  ⚠ 视频较长（{duration_min} 分钟），Whisper 转录可能需要 10-30 分钟")

    print(f"\n[2/4] 正在下载音频……")
    audio_path = download_audio(url, output_dir)
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    print(f"  ✓ 音频已下载: {audio_path} ({file_size_mb:.1f} MB)")

    print(f"\n[3/4] 正在 Whisper 转录（{whisper_backend}）……")
    transcribe_start = __import__('time').time()

    if whisper_backend == "faster-whisper":
        segments, detected_language = transcribe_with_faster_whisper(audio_path, language)
    else:
        segments, detected_language = transcribe_with_openai_whisper(audio_path, language)

    elapsed = __import__('time').time() - transcribe_start
    print(f"  ✓ 转录完成，共 {len(segments)} 段，耗时 {elapsed:.0f} 秒")
    if segments:
        print(f"  平均每段 {elapsed/len(segments):.1f} 秒")
    if detected_language:
        print(f"  检测语言: {detected_language}")

    # 生成原始文本
    raw_text = segments_to_text(segments)
    raw_path = os.path.join(output_dir, "transcript_raw.txt")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(raw_text)
    print(f"  ✓ 原始文本已保存: {raw_path} ({len(raw_text)} 字符)")

    # 清理临时音频文件
    try:
        os.remove(audio_path)
        print(f"  ✓ 临时音频文件已清理")
    except OSError:
        pass

    print(f"\n[4/4] 保存元数据……")
    meta["segment_count"] = len(segments)
    meta["transcript_language"] = detected_language or language
    meta_path = os.path.join(output_dir, "transcript_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 元数据已保存: {meta_path}")

    print("\n✅ 完成！下一步: python clean_transcript.py transcript_raw.txt")


if __name__ == "__main__":
    main()
