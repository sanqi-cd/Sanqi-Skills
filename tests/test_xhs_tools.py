import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "xhs-image-text-generator" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


render_carousel = load_module("render_carousel_html")
validate_delivery = load_module("validate_delivery")
normalize_input = load_module("normalize_input")


def sample_carousel():
    return {
        "topic": "高效学习",
        "audience": "职场新人",
        "angle": "四步建立复盘系统",
        "visual_system": {
            "style": "editorial utility",
            "background": "#F6F4EE",
            "foreground": "#1D2420",
            "accent": "#E5484D",
        },
        "pages": [
            {
                "number": index,
                "role": "cover" if index == 1 else "cta" if index == 6 else "content",
                "title": f"第 {index} 页",
                "subtitle": "一个清晰的信息点",
                "bullets": ["可执行步骤"],
                "visual_note": "文字层级清晰",
                "source_note": "",
            }
            for index in range(1, 7)
        ],
    }


class XhsToolsTest(unittest.TestCase):
    def test_carousel_renders_without_external_assets(self):
        data = sample_carousel()
        self.assertEqual(render_carousel.validate_carousel(data), [])
        output = render_carousel.render(data)
        self.assertEqual(output.count('<article class="card'), 6)
        self.assertNotIn("http://", output)
        self.assertIn("container-type:inline-size", output)
        self.assertIn("cqw", output)

    def test_delivery_allows_explicit_html_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for filename in validate_delivery.REQUIRED_FILES:
                if filename == "carousel.json":
                    content = json.dumps(sample_carousel(), ensure_ascii=False)
                else:
                    content = "complete"
                (root / filename).write_text(content, encoding="utf-8")
            (root / "cards.html").write_text(render_carousel.render(sample_carousel()), encoding="utf-8")
            self.assertEqual(validate_delivery.validate_package(root, allow_html=True), [])

    def test_normalizes_html_and_removes_scripts(self):
        title, body = normalize_input.normalize_html(
            "<html><title>Demo</title><script>bad()</script><p>Hello</p></html>"
        )
        self.assertEqual(title, "Demo")
        self.assertEqual(body, "Hello")


if __name__ == "__main__":
    unittest.main()
