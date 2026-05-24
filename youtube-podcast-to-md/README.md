# youtube-podcast-to-md

将 YouTube 播客视频整理成中文 Markdown 笔记的通用 skill，支持两种模式：

- `summary`：提取核心观点、数据和结论
- `full`：高保真还原完整对话

这个仓库包含两部分能力：

1. 可执行脚本：抓取字幕、Whisper 兜底转录、清洗、分块
2. Skill 说明与 prompt 模板：指导支持 skill 的智能体在当前对话中完成中文整理和最终文档组装

## Scope

- 默认针对英文播客优化
- 其他语言可尽力处理
- 若走 Whisper 兜底，推荐使用 `--language auto` 自动识别，或显式传入语言代码

## Repository Layout

```text
youtube-podcast-to-md/
├── SKILL.md
├── scripts/
│   ├── fetch_transcript.py
│   ├── fetch_with_whisper.py
│   └── clean_transcript.py
└── references/
    ├── prompt_templates.md
    └── output_format.md
```

## Requirements

- Python 3
- `yt-dlp`
- `youtube-transcript-api`
- 可选：`faster-whisper` 或 `openai-whisper`

安装示例：

```bash
python3 -m pip install yt-dlp youtube-transcript-api
python3 -m pip install faster-whisper
```

## Using As a Skill

这个 skill 设计为**平台无关**：只要宿主智能体支持加载本地 skill、读取 `SKILL.md`、以及按需访问 `scripts/` 和 `references/`，就可以使用。

安装方式取决于宿主平台本身。一般做法是：

1. 把整个 `youtube-podcast-to-md/` 目录放到宿主智能体可发现的位置
2. 或按宿主智能体的 skill / plugin / resource 导入方式注册该目录
3. 触发时让智能体读取 [SKILL.md](./SKILL.md)，并按需访问 `scripts/` 和 `references/`

## Using The Scripts Manually

```bash
SKILL_DIR="$PWD"
TMP_DIR="${YTP2MD_TMP_DIR:-/tmp/youtube-podcast-to-md}"

mkdir -p "$TMP_DIR"
python3 "$SKILL_DIR/scripts/fetch_transcript.py" "<YOUTUBE_URL>" "$TMP_DIR"
python3 "$SKILL_DIR/scripts/clean_transcript.py" "$TMP_DIR/transcript_raw.txt" "$TMP_DIR"
```

如果没有可用字幕，再执行 Whisper 兜底：

```bash
python3 "$SKILL_DIR/scripts/fetch_with_whisper.py" "<YOUTUBE_URL>" "$TMP_DIR" --language auto
```

## Important Note

这个仓库**不是**一条命令全自动输出最终 Markdown 的 CLI 工具。

当前设计是：

1. 先用脚本生成 `transcript_raw.txt`、`transcript_clean.txt`、`chunks.json`
2. 再由当前智能体按 [references/prompt_templates.md](./references/prompt_templates.md) 和 [references/output_format.md](./references/output_format.md) 完成中文整理与成稿

## Configuration

- `YTP2MD_TMP_DIR`：中间文件目录，默认 `/tmp/youtube-podcast-to-md`
- `YTP2MD_OUTPUT_DIR`：最终 Markdown 输出目录，默认当前工作目录

## Validation

建议至少验证这两步：

```bash
python3 -m py_compile scripts/*.py
python3 scripts/fetch_with_whisper.py --help
```
