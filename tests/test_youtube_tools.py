import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "youtube-podcast-to-md" / "scripts"


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


fetch_transcript = load_module("fetch_transcript")
clean_transcript = load_module("clean_transcript")
validate_output = load_module("validate_output")


VALID_SUMMARY = """# 中文标题

> 原标题：English title
> 频道：Demo
> 时长：60 分钟
> 链接：https://www.youtube.com/watch?v=dQw4w9WgXcQ
> 整理模式：精简版
> 字幕来源：手动英文字幕
> 字幕语言：en

## 核心摘要
准确性说明：无不确定项。

## 内容目录
- 主题

## 关键要点
- 观点 [→04:32]

## 主题
### 小节
> 00:00 - 05:30
正文。

## 精彩金句
> 金句
"""


class YoutubeToolsTest(unittest.TestCase):
    def test_extracts_common_video_ids(self):
        expected = "dQw4w9WgXcQ"
        self.assertEqual(fetch_transcript.extract_video_id(f"https://youtu.be/{expected}"), expected)
        self.assertEqual(fetch_transcript.extract_video_id(f"https://www.youtube.com/watch?v={expected}"), expected)
        self.assertEqual(fetch_transcript.extract_video_id(expected), expected)

    def test_cleans_and_chunks_transcript(self):
        raw = "[TS:00:00]\nHello <i>world</i>.\n[Music]\n[TS:05:10]\nNext point."
        clean = clean_transcript.remove_noise(raw)
        chunks = clean_transcript.split_into_chunks(clean, 300)
        self.assertNotIn("Music", clean)
        self.assertEqual(len(chunks), 2)

    def test_validates_summary_provenance(self):
        self.assertEqual(validate_output.validate_output(VALID_SUMMARY, "summary"), [])
        errors = validate_output.validate_output(VALID_SUMMARY.replace("字幕来源：手动英文字幕\n", ""), "summary")
        self.assertIn("missing metadata: 字幕来源", errors)


if __name__ == "__main__":
    unittest.main()
