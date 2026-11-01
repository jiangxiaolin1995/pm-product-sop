import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "init_requirement.py"


class RequirementRecordTests(unittest.TestCase):
    def run_init(self, output, **options):
        values = {
            "project": "示例项目",
            "requirement": "会员路径优化",
            "mode": "标准",
            "date": "2026-11-01",
            "output": str(output),
        }
        values.update(options)
        args = [sys.executable, str(SCRIPT)]
        for key, value in values.items():
            args.extend(["--" + key, value])
        return subprocess.run(args, capture_output=True, text=True)

    def test_creates_record_with_known_metadata_and_unconfirmed_business_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "docs" / "会员路径优化-推进记录.md"
            result = self.run_init(output)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = output.read_text()
            self.assertIn("# 示例项目｜会员路径优化推进记录", text)
            self.assertIn("2026-11-01", text)
            self.assertIn("标准", text)
            self.assertIn("当前问题及后果：【待填】", text)
            self.assertIn("效果状态 | 尚未观察", text)
            self.assertIn(str(ROOT / "references" / "sop.md"), text)

    def test_refuses_to_replace_existing_user_record(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "record.md"
            original = "# 用户记录\n\n已经确认的范围，请保留。\n"
            output.write_text(original)
            result = self.run_init(output)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(), original)

    def test_invalid_date_has_no_output_side_effect(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "record.md"
            result = self.run_init(output, date="2026-02-30")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_names_do_not_break_markdown_table_or_add_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "record.md"
            result = self.run_init(output, project="项目 | A", requirement="支付 <确认>")
            self.assertEqual(result.returncode, 0, result.stderr)
            text = output.read_text()
            self.assertIn("项目 \\| A", text)
            self.assertIn("支付 &lt;确认&gt;", text)
            refused = self.run_init(Path(folder) / "bad.md", requirement="名称\n新行")
            self.assertNotEqual(refused.returncode, 0)
            self.assertFalse((Path(folder) / "bad.md").exists())


if __name__ == "__main__":
    unittest.main()
