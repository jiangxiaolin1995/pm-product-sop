import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_handbook.py"


class HandbookTests(unittest.TestCase):
    def build(self, folder, sop, template):
        folder = Path(folder)
        (folder / "sop.md").write_text(sop)
        (folder / "template.md").write_text(template)
        output = folder / "手册.html"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--sop", str(folder / "sop.md"),
             "--template", str(folder / "template.md"), "--output", str(output)],
            capture_output=True, text=True,
        )
        return result, output

    def test_embeds_content_and_template_without_executable_markdown_or_external_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            template = '# 模板\n\n原文：</script><script>alert("x")</script>\n'
            result, output = self.build(folder, '# SOP\n\n## 第一项\n\n执行说明。\n', template)
            self.assertEqual(result.returncode, 0, result.stderr)
            html = output.read_text()
            data = re.search(r'<script id="document-data" type="application/json">(.*?)</script>', html, re.S)
            self.assertIsNotNone(data)
            payload = json.loads(data.group(1))
            self.assertEqual(payload["template"], template)
            self.assertIn("执行说明。", html)
            self.assertNotIn('<script>alert("x")</script>', html)
            self.assertNotRegex(html, r'<(?:script|link|img)[^>]+(?:src|href)=["\']https?://')

    def test_rejects_personal_filesystem_paths_before_writing_shareable_file(self):
        with tempfile.TemporaryDirectory() as folder:
            result, output = self.build(folder, '# SOP\n[本机文件](/Users/private/work/example.md)\n', '# 模板\n')
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_equivalent_markdown_line_breaks_preserve_version_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "spaces").mkdir()
            (root / "explicit").mkdir()
            sop = "# SOP\n\n版本：1.1  \n更新日期：2026-11-01\n"
            first, a = self.build(root / "spaces", sop, "# 模板\n")
            second, b = self.build(root / "explicit", sop.replace("  \n", "\\\n"), "# 模板\n")
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(a.read_text(), b.read_text())


if __name__ == "__main__":
    unittest.main()
