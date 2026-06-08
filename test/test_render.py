"""Unit + integration tests for bin/jarvis-render.

Run with:  python3 -m pytest test/test_render.py -v
Or stdlib: python3 -m unittest test.test_render
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

JARVIS_ROOT = Path(__file__).resolve().parents[1]
RENDER_BIN = JARVIS_ROOT / "bin" / "jarvis-render"

# Load the renderer as a module. SourceFileLoader is used directly because
# jarvis-render has no .py extension and importlib.util.spec_from_file_location
# refuses extensionless files in Python 3.14+.
_loader = SourceFileLoader("jarvis_render", str(RENDER_BIN))
_spec = importlib.util.spec_from_loader("jarvis_render", _loader)
jarvis_render = importlib.util.module_from_spec(_spec)
sys.modules["jarvis_render"] = jarvis_render
_loader.exec_module(jarvis_render)


class TestSlotSubstitution(unittest.TestCase):
    def test_basic_substitution(self):
        out = jarvis_render.render("hello {{NAME}}", {"NAME": "world"})
        self.assertEqual(out, "hello world")

    def test_multiple_slots(self):
        out = jarvis_render.render(
            "a={{A}} b={{B}} a-again={{A}}",
            {"A": "1", "B": "2"},
        )
        self.assertEqual(out, "a=1 b=2 a-again=1")

    def test_unknown_slot_renders_empty_in_non_strict(self):
        out = jarvis_render.render("hello {{MISSING}}!", {})
        self.assertEqual(out, "hello !")

    def test_unknown_slot_raises_in_strict(self):
        with self.assertRaises(ValueError):
            jarvis_render.render("hi {{X}}", {}, strict=True)

    def test_whitespace_in_slot_tolerated(self):
        out = jarvis_render.render("{{ NAME }}", {"NAME": "world"})
        self.assertEqual(out, "world")

    def test_no_substitution_when_no_braces(self):
        out = jarvis_render.render("plain text {NAME}", {"NAME": "ignored"})
        self.assertEqual(out, "plain text {NAME}")


class TestTemplateHash(unittest.TestCase):
    def test_hash_is_first_12_of_sha256(self):
        with tempfile.NamedTemporaryFile("w", suffix=".tmpl", delete=False) as f:
            f.write("hello world")
            path = Path(f.name)
        expected = hashlib.sha256(b"hello world").hexdigest()[:12]
        self.assertEqual(jarvis_render.template_hash(path), expected)
        path.unlink()

    def test_hash_changes_when_content_changes(self):
        with tempfile.NamedTemporaryFile("w", suffix=".tmpl", delete=False) as f:
            f.write("v1")
            path = Path(f.name)
        h1 = jarvis_render.template_hash(path)
        path.write_text("v2")
        h2 = jarvis_render.template_hash(path)
        self.assertNotEqual(h1, h2)
        path.unlink()


class TestManifestParser(unittest.TestCase):
    SAMPLE = """\
feature: testing
version: 1.0.0
description: sanity

files:
  always:
    - { src: a.tmpl, dst: out/a }
    - src: b.tmpl
      dst: out/b
  conditional:
    - if_feature: foo
      src: c.tmpl
      dst: out/c
    - { if_feature: bar, src: d.tmpl, dst: out/d }
"""

    def test_block_and_inline_entries_parse(self):
        m = jarvis_render._parse_manifest_fallback(self.SAMPLE)
        self.assertEqual(m["feature"], "testing")
        self.assertEqual(len(m["files"]["always"]), 2)
        self.assertEqual(len(m["files"]["conditional"]), 2)

    def test_always_entries(self):
        m = jarvis_render._parse_manifest_fallback(self.SAMPLE)
        a, b = m["files"]["always"]
        self.assertEqual(a["src"], "a.tmpl")
        self.assertEqual(a["dst"], "out/a")
        self.assertEqual(b["src"], "b.tmpl")
        self.assertEqual(b["dst"], "out/b")

    def test_conditional_entries(self):
        m = jarvis_render._parse_manifest_fallback(self.SAMPLE)
        c, d = m["files"]["conditional"]
        self.assertEqual(c["if_feature"], "foo")
        self.assertEqual(d["if_feature"], "bar")


class TestRenderFeatureEndToEnd(unittest.TestCase):
    def test_real_networking_feature(self):
        ctx_path = JARVIS_ROOT / "test" / "fixtures" / "sample-context.json"
        ctx = json.loads(ctx_path.read_text())
        feature_root = JARVIS_ROOT / "templates" / "features" / "networking"

        with tempfile.TemporaryDirectory() as tmp:
            written = jarvis_render.render_feature(
                feature_root=feature_root,
                context=ctx,
                target_dir=Path(tmp),
                feature_flags=set(ctx["features"]),
                dry_run=False,
            )
            # Should write at least the always files + ses/bedrock/aoss
            self.assertGreaterEqual(len(written), 9)

            # No unsubstituted slots anywhere
            for p in written:
                self.assertTrue(p.exists(), f"{p} should be written")
                content = p.read_text()
                self.assertNotIn("{{REGION}}", content)
                self.assertNotIn("{{APP_NAME}}", content)
                self.assertNotIn("{{ACCOUNT_ID}}", content)

            # APP_NAME should appear in at least one file (variables.tf default)
            all_content = "\n".join(p.read_text() for p in written)
            self.assertIn(ctx["APP_NAME"], all_content)
            self.assertIn(ctx["ACCOUNT_ID"], all_content)
            self.assertIn(ctx["REGION"], all_content)


if __name__ == "__main__":
    unittest.main()
