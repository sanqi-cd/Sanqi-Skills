import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


xhs_renderer = load_module(
    "example_xhs_renderer",
    ROOT / "xhs-image-text-generator" / "scripts" / "render_carousel_html.py",
)
learning_renderer = load_module(
    "example_learning_renderer",
    ROOT / "learning-path-designer" / "scripts" / "render_growth_map.py",
)


class PublicExamplesTest(unittest.TestCase):
    def test_xhs_examples_are_current_and_complete(self):
        sources = sorted((ROOT / "examples" / "xhs-image-text-generator").glob("*/carousel.json"))
        self.assertGreaterEqual(len(sources), 2)
        for source in sources:
            with self.subTest(example=source.parent.name):
                data = json.loads(source.read_text(encoding="utf-8"))
                self.assertEqual(xhs_renderer.validate_carousel(data), [])
                self.assertEqual(len(data["pages"]), 8)
                self.assertEqual(source.with_name("cards.html").read_text(encoding="utf-8"), xhs_renderer.render(data))

    def test_learning_examples_are_current_and_complete(self):
        sources = sorted((ROOT / "examples" / "learning-path-designer").glob("*/learning-plan.json"))
        self.assertGreaterEqual(len(sources), 2)
        for source in sources:
            with self.subTest(example=source.parent.name):
                data = json.loads(source.read_text(encoding="utf-8"))
                self.assertEqual(learning_renderer.validate_plan(data), [])
                self.assertEqual(source.with_name("growth-map.html").read_text(encoding="utf-8"), learning_renderer.render(data))


if __name__ == "__main__":
    unittest.main()
