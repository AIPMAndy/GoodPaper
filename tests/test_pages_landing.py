"""Static GitHub Pages contract tests: no accidental manuscript upload on Pages."""
from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs/index.html"

class LandingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.hrefs = []
        self.script_srcs = []
        self.file_inputs = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise AssertionError("Duplicate element ID " + attrs["id"])
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.hrefs.append(attrs["href"])
        if tag == "script" and attrs.get("src"):
            self.script_srcs.append(attrs["src"])
        if tag == "input" and attrs.get("type") == "file":
            self.file_inputs.append(attrs)

class PagesSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.parsed = LandingParser()
        cls.parsed.feed(cls.html)

    def test_no_uploads_or_external_tracking(self):
        self.assertFalse(self.parsed.file_inputs, "Pages must not accept manuscripts")
        self.assertFalse(self.parsed.script_srcs)
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("google-analytics", self.html.lower())
        self.assertNotIn("https://fonts.googleapis.com", self.html)

    def test_all_internal_anchors_resolve(self):
        for href in self.parsed.hrefs:
            if href.startswith("#"):
                with self.subTest(href=href):
                    self.assertIn(href[1:], self.parsed.ids)

    def test_brand_and_technical_truthfulness(self):
        for token in (
            "GoodPaper", "AI 酋长 Andy", "https://metaver.vip/",
            "https://github.com/AIPMAndy/GoodPaper",
            "AIPMAndy", "本机", "DOCX", "GB/T 7714", "三线表",
            "没有", "Apache-2.0", "data-platform", "copyWechat",
            "copyInstall", "role=\"img\"", "aria-live=\"polite\"",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.html)
        self.assertIn("不支持在线上传论文", self.html)
        self.assertIn("http://127.0.0.1:8787", self.html)
        self.assertIn("python app.py serve", self.html)

    def test_metadata_and_static_files(self):
        self.assertIn('<html lang="zh-CN">', self.html)
        self.assertIn('<link rel="canonical" href="https://aipmandy.github.io/GoodPaper/">', self.html)
        self.assertIn("prefers-reduced-motion", self.html)
        for name in ("favicon.svg", "robots.txt", "sitemap.xml", ".nojekyll"):
            self.assertTrue((ROOT / "docs" / name).exists())

    def test_workflow_has_pages_permissions_and_artifact(self):
        workflow=(ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        for token in (
            "pages: write", "id-token: write", "workflow_dispatch:",
            "actions/configure-pages@", "actions/upload-pages-artifact@",
            "actions/deploy-pages@", "path: ./docs", "branches: [main]"
        ):
            self.assertIn(token,workflow)
        self.assertNotIn("enablement: true", workflow)

if __name__ == "__main__":
    unittest.main()
