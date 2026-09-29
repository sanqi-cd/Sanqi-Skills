import importlib.util
import json
import argparse
import tempfile
import types
import unittest
from unittest.mock import patch
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
fetch_with_whisper = load_module("fetch_with_whisper")


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

    def test_skips_failed_transcript_candidate(self):
        class TranscriptList:
            def find_manually_created_transcript(self, _):
                raise LookupError("none")

            def find_generated_transcript(self, _):
                raise LookupError("none")

            def __iter__(self):
                broken = types.SimpleNamespace(language_code="en-US", fetch=lambda: (_ for _ in ()).throw(OSError("failed")))
                working = types.SimpleNamespace(language_code="ja", fetch=lambda: [{"start": 0, "text": "Hello"}])
                return iter((broken, working))

        fake_api = types.SimpleNamespace(YouTubeTranscriptApi=lambda: types.SimpleNamespace(list=lambda _: TranscriptList()))
        with patch.dict("sys.modules", {"youtube_transcript_api": fake_api}):
            segments, source, language = fetch_transcript.fetch_with_transcript_api("dQw4w9WgXcQ")
        self.assertEqual(language, "ja")
        self.assertIn("ja", source)
        self.assertEqual(segments[0]["text"], "Hello")

    def test_ytdlp_uses_current_interpreter_in_both_fetchers(self):
        for module in (fetch_transcript, fetch_with_whisper):
            with self.subTest(module=module.__name__), patch.object(module.importlib.util, "find_spec", return_value=object()):
                self.assertEqual(module._get_ytdlp_cmd(), [module.sys.executable, "-m", "yt_dlp"])

    def test_cleans_and_chunks_transcript(self):
        raw = "[TS:00:00]\nHello <i>world</i>.\n[Music]\n[TS:05:10]\nNext point."
        clean = clean_transcript.remove_noise(raw)
        chunks = clean_transcript.split_into_chunks(clean, 300)
        self.assertNotIn("Music", clean)
        self.assertEqual(len(chunks), 2)

    def test_fetch_pipeline_writes_transcript_and_metadata(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        metadata = {"title": "Demo", "channel": "Channel", "duration": 120, "url": url}
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(fetch_transcript, "ensure_dependencies"), patch.object(
                fetch_transcript, "fetch_meta_with_ytdlp", return_value=metadata.copy()
            ), patch.object(fetch_transcript, "fetch_with_transcript_api", return_value=(
                [{"start": 0, "text": "Hello"}, {"start": 35, "text": "Next point"}],
                "手动英文字幕", "en"
            )), patch.object(fetch_transcript.sys, "argv", ["fetch_transcript.py", url, tmp]):
                fetch_transcript.main()
            raw = (Path(tmp) / "transcript_raw.txt").read_text(encoding="utf-8")
            saved = json.loads((Path(tmp) / "transcript_meta.json").read_text(encoding="utf-8"))
        self.assertIn("[TS:00:35]", raw)
        self.assertTrue(saved["transcript_available"])
        self.assertEqual(saved["segment_count"], 2)

    def test_fetch_pipeline_marks_empty_transcript_for_fallback(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        metadata = {"title": "Demo", "channel": "Channel", "duration": 120, "url": url}
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(fetch_transcript, "ensure_dependencies"), patch.object(
                fetch_transcript, "fetch_meta_with_ytdlp", return_value=metadata.copy()
            ), patch.object(fetch_transcript, "fetch_with_transcript_api", return_value=(
                [], "无可用字幕", None
            )), patch.object(fetch_transcript.sys, "argv", ["fetch_transcript.py", url, tmp]):
                fetch_transcript.main()
            saved = json.loads((Path(tmp) / "transcript_meta.json").read_text(encoding="utf-8"))
            self.assertFalse((Path(tmp) / "transcript_raw.txt").exists())
        self.assertFalse(saved["transcript_available"])

    def test_whisper_pipeline_uses_selected_model(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        metadata = {"title": "Demo", "channel": "Channel", "duration": 120, "url": url}
        with tempfile.TemporaryDirectory() as tmp:
            audio_path = Path(tmp) / "audio.wav"
            audio_path.write_bytes(b"audio fixture")
            args = argparse.Namespace(url=url, output_dir=tmp, language="en", model="tiny")
            with patch.object(fetch_with_whisper, "parse_args", return_value=args), patch.object(
                fetch_with_whisper, "ensure_ytdlp"
            ), patch.object(fetch_with_whisper, "init_whisper", return_value="faster-whisper"), patch.object(
                fetch_with_whisper, "fetch_meta_with_ytdlp", return_value=metadata.copy()
            ), patch.object(fetch_with_whisper, "download_audio", return_value=str(audio_path)), patch.object(
                fetch_with_whisper, "transcribe_with_faster_whisper", return_value=(
                    [{"start": 0, "text": "Hello", "duration": 1}], "en"
                )
            ) as transcribe:
                fetch_with_whisper.main()
            saved = json.loads((Path(tmp) / "transcript_meta.json").read_text(encoding="utf-8"))
            raw = (Path(tmp) / "transcript_raw.txt").read_text(encoding="utf-8")
            self.assertFalse(audio_path.exists())
        transcribe.assert_called_once_with(str(audio_path), "en", "tiny")
        self.assertEqual(saved["transcript_source"], "Whisper 离线转录（faster-whisper）")
        self.assertIn("Hello", raw)

    def test_validates_summary_provenance(self):
        self.assertEqual(validate_output.validate_output(VALID_SUMMARY, "summary"), [])
        errors = validate_output.validate_output(VALID_SUMMARY.replace("字幕来源：手动英文字幕\n", ""), "summary")
        self.assertIn("missing metadata: 字幕来源", errors)


if __name__ == "__main__":
    unittest.main()
