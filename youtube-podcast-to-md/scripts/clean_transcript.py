#!/usr/bin/env python3
"""
clean_transcript.py
对原始字幕文本进行预处理：
  - 去除噪音字符和标记
  - 合并被错误切断的句子
  - 按时间戳自动分块（每块约 5 分钟）
输出：
  - transcript_clean.txt  清洗后的完整文本
  - chunks.json           分块数据（供 Step 5 模型整理用）
"""

import sys
import re
import json
import os


def remove_noise(text: str) -> str:
    """去除常见字幕噪音"""
    # 去除 HTML/XML 标签（如 <c>, <i>, <font>）
    text = re.sub(r"<[^>]+>", "", text)
    # 去除方括号内容标记（如 [Music], [Applause], [笑声], [Music Playing]）
    # 但保留时间戳标记 [TS:...]
    text = re.sub(r"\[(?!TS:)[^\]]*\]", "", text)
    # 去除多余空格和空行
    text = re.sub(r"  +", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def merge_broken_sentences(text: str) -> str:
    """
    合并被字幕系统错误切断的句子。
    规则：如果一行不以结束标点结尾，且下一行不以大写字母/中文字开头，
    则合并（说明是同一句被切断）。
    时间戳标记行保留不合并。
    """
    lines = text.split("\n")
    merged = []
    buffer = ""

    for line in lines:
        line = line.strip()
        if not line:
            if buffer:
                merged.append(buffer)
                buffer = ""
            continue

        # 时间戳标记行：先刷新缓冲区，再单独保留
        if re.match(r"\[TS:\d{2}:\d{2}", line):
            if buffer:
                merged.append(buffer)
                buffer = ""
            merged.append(line)
            continue

        if buffer:
            # buffer 末尾有结束标点 → 上一句已完整，开始新句
            ends_with_punct = bool(re.search(r"[.!?。！？…\"»)]$", buffer))
            # 当前行以大写字母或中文开头 → 新句开始
            starts_sentence = bool(re.match(r"[A-Z一-鿿\"«]", line))

            if ends_with_punct or starts_sentence:
                merged.append(buffer)
                buffer = line
            else:
                buffer = buffer + " " + line
        else:
            buffer = line

    if buffer:
        merged.append(buffer)

    return "\n".join(merged)


def parse_time(ts_str: str) -> int:
    """将 MM:SS 或 HH:MM:SS 转为秒数"""
    parts = ts_str.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def split_into_chunks(text: str, chunk_duration_seconds: int = 300) -> list:
    """
    按时间戳标记将文本分块，每块约 chunk_duration_seconds 秒（默认 5 分钟）。
    返回 chunks 列表，每个元素：
    {
        "chunk_index": 1,
        "start_time": "00:00",
        "end_time": "05:00",
        "text": "...",
        "word_count": 850
    }
    """
    lines = text.split("\n")
    chunks = []
    current_chunk_lines = []
    current_start = None
    current_start_seconds = 0
    last_ts = None
    for line in lines:
        ts_match = re.match(r"\[TS:(\d{2}:\d{2}(?::\d{2})?)\]", line)

        if ts_match:
            ts_str = ts_match.group(1)
            ts_seconds = parse_time(ts_str)

            if current_start is None:
                current_start = ts_str
                current_start_seconds = ts_seconds

            # 检查是否需要切分
            elif (ts_seconds - current_start_seconds) >= chunk_duration_seconds:
                chunk_text = "\n".join(current_chunk_lines).strip()
                if chunk_text:  # 跳过空块
                    chunks.append({
                        "chunk_index": len(chunks) + 1,
                        "start_time": current_start,
                        "end_time": last_ts or ts_str,
                        "text": chunk_text,
                        "word_count": len(chunk_text.split())
                    })
                current_chunk_lines = []
                current_start = ts_str
                current_start_seconds = ts_seconds

            last_ts = ts_str
            # 保留时间戳标记行，供模型翻译标注和回溯溯源使用
            current_chunk_lines.append(line)
        else:
            if line.strip():
                current_chunk_lines.append(line)

    # 最后一块
    if current_chunk_lines:
        chunk_text = "\n".join(current_chunk_lines).strip()
        if chunk_text:
            chunks.append({
                "chunk_index": len(chunks) + 1,
                "start_time": current_start or "00:00",
                "end_time": last_ts or "结束",
                "text": chunk_text,
                "word_count": len(chunk_text.split())
            })

    return chunks


def main():
    if len(sys.argv) < 2:
        print("用法: python clean_transcript.py <transcript_raw.txt> [输出目录]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(input_path) or "."

    if not os.path.exists(input_path):
        print(f"错误：文件不存在: {input_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    print(f"[1/3] 清理噪音字符……")
    text = remove_noise(raw_text)
    removed_chars = len(raw_text) - len(text)
    print(f"  去除了约 {removed_chars} 个噪音字符")

    print(f"[2/3] 合并断句……")
    text = merge_broken_sentences(text)
    line_count = len(text.split("\n"))
    print(f"  合并后共 {line_count} 行")

    # 保存清洗后文本
    clean_path = os.path.join(output_dir, "transcript_clean.txt")
    with open(clean_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  ✓ 清洗后文本: {clean_path}")

    print(f"[3/3] 分块处理……")
    chunks = split_into_chunks(text, chunk_duration_seconds=300)
    print(f"  共分为 {len(chunks)} 块（每块约 5 分钟）")

    # 保存分块数据
    chunks_path = os.path.join(output_dir, "chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 分块数据: {chunks_path}")

    # 打印分块摘要
    print("\n  分块概览：")
    total_words = 0
    for c in chunks:
        wc = c["word_count"]
        total_words += wc
        print(f"    块 {c['chunk_index']:02d}: {c['start_time']} ~ {c['end_time']}，约 {wc} 词")
    group_count = (len(chunks) + 2) // 3
    print(f"  总计约 {total_words} 词，预计需处理 {group_count} 组")

    if len(chunks) > 20:
        print(f"  ⚠ 分块数较多（{len(chunks)}），处理时间会较长。如果只想看部分内容，建议指定时间范围。")

    print("\n✅ 完成！下一步: 使用当前模型逐块处理（参见 SKILL.md Step 5）")


if __name__ == "__main__":
    main()
