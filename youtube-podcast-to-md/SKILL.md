---
name: youtube-podcast-to-md
description: 将 YouTube 播客视频字幕提取并整理为中文 Markdown 笔记，默认针对英文播客优化，支持「核心摘要」和「对话高保真还原」两种模式
---

# YouTube 播客 → 中文 Markdown

## 概述

将 YouTube 播客视频的字幕提取，整理为高质量中文 Markdown 文档，默认针对英文播客优化；其他语言也可尽力处理。两种输出模式：

- **精简版（summary）**：提取核心观点、关键数据、结构化摘要，过滤闲聊和重复表达
- **完整版（full）**：高保真还原整个对话，保留对话结构、论述逻辑和信息完整性，经轻度书面化处理后呈现为自然流畅的中文对话

## 工作流（必须按顺序执行）

**全局约定：**
- 中间文件默认放入 `${YTP2MD_TMP_DIR:-/tmp/youtube-podcast-to-md/}`
- 最终 Markdown 默认输出到 `${YTP2MD_OUTPUT_DIR:-$PWD}`；若用户想直接落到某个笔记库或知识库目录，请显式把 `YTP2MD_OUTPUT_DIR` 指向目标目录
- 任务结束后自动清理 `${YTP2MD_TMP_DIR:-/tmp/youtube-podcast-to-md/}` 中的中间文件
- 本技能**可任意目录下执行**，不依赖当前工作目录
- 所有命令使用 `python3`
- `yt-dlp` 可以直接在 PATH 中可用，或通过 `python3 -m yt_dlp` 可用；不要依赖某台机器上的固定 PATH
- 运行脚本时，把 `SKILL_DIR` 视为**当前 skill 根目录**（即包含本 `SKILL.md` 的目录）

### Step 1：确认输入参数

从用户消息中提取：
- **URL**：YouTube 视频链接
- **模式**：精简版 or 完整版（用户未指定时必须询问）

### Step 2：环境准备

```bash
SKILL_DIR="/absolute/path/to/youtube-podcast-to-md"
TMP_DIR="${YTP2MD_TMP_DIR:-/tmp/youtube-podcast-to-md}"
OUTPUT_DIR="${YTP2MD_OUTPUT_DIR:-$PWD}"

mkdir -p "$TMP_DIR" "$OUTPUT_DIR"
python3 -m pip install --quiet yt-dlp youtube-transcript-api
```

若需 Whisper 兜底，额外安装以下其一：

```bash
python3 -m pip install --quiet faster-whisper
# 或
python3 -m pip install --quiet openai-whisper
```

若遇到权限问题可改用 `python3 -m pip install --user ...`；在虚拟环境中则无需额外参数。

### Step 3：获取字幕

运行 `python3 "$SKILL_DIR/scripts/fetch_transcript.py" <URL> "$TMP_DIR"`，脚本按优先级自动选择：

1. YouTube 手动上传的英文字幕（质量最高）
2. YouTube 自动生成的英文字幕
3. YouTube 上其他可用字幕（自动适配）
4. 若以上均不可用 → 运行 `python3 "$SKILL_DIR/scripts/fetch_with_whisper.py" <URL> "$TMP_DIR"` 使用 Whisper 离线转录

补充说明：
- `fetch_transcript.py` 会优先拿英文字幕；如果只有其他语言字幕，会继续返回该语言字幕
- `fetch_with_whisper.py` 默认使用 `--language auto` 自动识别语言；若你明确只想按英文转录，可传 `--language en`

中间文件（位于 `"$TMP_DIR"`）：
- `transcript_raw.txt` — 原始字幕文本（含 `[TS:MM:SS]` 时间戳标记）
- `transcript_meta.json` — 视频元数据（标题、频道、时长、字幕来源等）

### Step 4：字幕清洗与分块

运行 `python3 "$SKILL_DIR/scripts/clean_transcript.py" "$TMP_DIR/transcript_raw.txt" "$TMP_DIR"`，执行：

- 去除 HTML 标签和噪音标记（`[Music]`、`[Applause]` 等）
- 合并被错误切断的句子
- 按约 5 分钟自动切分为处理块

中间文件（位于 `"$TMP_DIR"`）：
- `transcript_clean.txt` — 清洗后的完整字幕文本
- `chunks.json` — 分块数据（每块含 `chunk_index`、`start_time`、`end_time`、`text`、`word_count` 字段；`chunk_index` 从 1 开始）

### Step 5：模型内容重建（核心步骤）

读取 `references/prompt_templates.md` 获取对应模式的 prompt 模板。

**分块处理策略**：

1. 读取 `"$TMP_DIR/chunks.json"`，按 `chunk_index` 顺序处理
2. 将相邻 **3 块合并为一组**（约 15 分钟内容，~3000 词），最后一组可 2 块，减少处理轮数
3. 每组处理时传入**前一组已处理内容的主题/标题列表**作为上下文，保证跨组连贯
4. 在**当前对话中直接调用模型**，无需外部 API

**两种模式的行为差异**：

| 维度 | 精简版 | 完整版 |
|------|--------|--------|
| 目标 | 提取核心价值 | 还原完整对话 |
| 内容比例 | 原文 30-40% | 接近 100%，过滤掉口头禅 |
| 结构 | 按主题归类，用列表呈现 | 按对话时间线，保留说话人切换 |
| 语言 | 中文摘要 | 中文书面化对话 |
| 典型场景 | 快速了解观点 | 深入理解论述过程 |

所有分块处理完毕后，使用整合 prompt 做全局统合（合并重复话题、统一标题层级、生成头尾模块）。

### Step 6：组装最终 Markdown

按 `references/output_format.md` 中对应模式的格式规范组装文档。

**最终输出路径：** `"$OUTPUT_DIR/<文件名>.md"`

若用户想把结果直接落到某个笔记库目录，可先执行：

```bash
export YTP2MD_OUTPUT_DIR="/path/to/your/notes/youtube-podcast-notes"
mkdir -p "$YTP2MD_OUTPUT_DIR"
```

文件命名规则：`{频道名}_{视频标题前20字}_{YYYYMMDD}_{mode}.md`

（特殊字符 `/ \ : * ? " < > |` 替换为 `_`）

### Step 7：清理中间文件并呈现结果

删除中间文件目录：

```bash
rm -rf "$TMP_DIR"
```

告知用户：
- 输出文件的完整路径
- 文档结构概要（章节数、核心主题）
- 如果是完整版，提示总对话轮数和覆盖的时长范围

---

## 错误处理

| 情况 | 处理方式 |
|------|---------|
| 视频无任何字幕且 Whisper 不可用 | 告知用户无法处理，说明原因 |
| 视频为私密/会员内容 | 明确报错，提示无法访问非公开视频 |
| 字幕语言非英文 | 可继续处理；若走 Whisper 兜底，优先使用 `--language auto` 或显式传入语言代码 |
| 视频超过 3 小时 | 警告处理时间较长，建议只处理用户感兴趣的时间段 |

---

## 参考文件

| 文件 | 用途 | 使用步骤 |
|------|------|---------|
| `scripts/fetch_transcript.py` | 字幕获取（youtube-transcript-api + yt-dlp） | Step 3 时读取并执行 |
| `scripts/fetch_with_whisper.py` | Whisper 离线转录兜底 | Step 3 备选方案 |
| `scripts/clean_transcript.py` | 字幕清洗与自动分块 | Step 4 时读取并执行 |
| `references/prompt_templates.md` | 模型内容重建 prompt 模板 | Step 5 时读取 |
| `references/output_format.md` | Markdown 输出格式规范 | Step 6 时读取 |
