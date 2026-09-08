import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from csv_dedupe import deduplicate
from jsonl_check import validate


ROOT = Path(__file__).resolve().parents[1]


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def file(self, name, text):
        path = self.root / name
        path.write_text(text, encoding="utf-8", newline="")
        return path

    def test_unicode_and_json_values(self):
        source = self.file("data.jsonl", '\ufeff{"city":"北京"}\n[1,2]\nnull\n42\n')
        self.assertEqual(validate(source), {"valid_records": 4, "errors": []})

    def test_blank_line_is_not_a_record(self):
        result = validate(self.file("data.jsonl", '{}\n\n{}\n'))
        self.assertEqual(result["valid_records"], 2)
        self.assertEqual(result["errors"], [{"line": 2, "error": "blank line"}])

    def test_invalid_json_and_nonstandard_numbers(self):
        result = validate(self.file("data.jsonl", '{}\n{"a":}\n{"value":NaN}\n'))
        self.assertEqual([e["line"] for e in result["errors"]], [2, 3])
        self.assertEqual(result["valid_records"], 1)

    def test_cli_status_and_output(self):
        for content, expected in [('{}\n', 0), ('not-json\n', 1)]:
            path = self.file("cli.jsonl", content)
            result = subprocess.run([sys.executable, str(ROOT / "jsonl_check.py"), str(path)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, expected)
            self.assertIn("valid_records", json.loads(result.stdout))

    def test_cli_missing_file(self):
        result = subprocess.run([sys.executable, str(ROOT / "jsonl_check.py"), str(self.root / "absent")],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("error", json.loads(result.stdout))

    def test_quoted_csv_preserves_first_record_and_blanks(self):
        original = 'id,note\r\n A ,"first, line\r\nsecond"\r\na,later\r\n,blank one\r\n,blank two\r\n'
        source = self.file("in.csv", original)
        output = self.root / "out.csv"
        stats = deduplicate(source, output, ["id"], ignore_case=True)
        with output.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.reader(stream))
        self.assertEqual(rows[1], [" A ", "first, line\r\nsecond"])
        self.assertEqual(len(rows), 4)
        self.assertEqual(stats["duplicates_removed"], 1)
        self.assertEqual(stats["rows_with_blank_keys_preserved"], 2)
        self.assertEqual(source.read_bytes(), original.encode())

    def test_case_sensitive_by_default(self):
        source = self.file("in.csv", 'id\nA\na\n')
        stats = deduplicate(source, self.root / "out.csv", ["id"])
        self.assertEqual(stats["output_rows"], 2)

    def test_composite_key(self):
        source = self.file("in.csv", 'a,b\n1,x\n1,y\n1,x\n')
        stats = deduplicate(source, self.root / "out.csv", ["a", "b"])
        self.assertEqual(stats["output_rows"], 2)

    def test_rejects_bad_schema_without_output(self):
        for content, key in [('a,a\n1,2\n', 'a'), ('a\n1,2\n', 'a'), ('a\n1\n', 'b')]:
            source = self.file("in.csv", content)
            output = self.root / "out.csv"
            with self.assertRaises(ValueError):
                deduplicate(source, output, [key])
            self.assertFalse(output.exists())
            self.assertEqual(list(self.root.glob("*.tmp")), [])

    def test_rejects_overwrite(self):
        source = self.file("in.csv", 'a\n1\n')
        output = self.file("out.csv", 'keep this')
        with self.assertRaises(FileExistsError):
            deduplicate(source, output, ["a"])
        self.assertEqual(output.read_text(), 'keep this')
        with self.assertRaises(ValueError):
            deduplicate(source, source, ["a"])

    def test_csv_cli(self):
        source = self.file("in.csv", 'a\n1\n1\n2\n')
        result = subprocess.run([sys.executable, str(ROOT / "csv_dedupe.py"), str(source),
                                 str(self.root / "out.csv"), '--key', 'a'],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["duplicates_removed"], 1)


if __name__ == "__main__":
    unittest.main()
