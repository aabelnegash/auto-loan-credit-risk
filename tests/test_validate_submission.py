"""Submission contract checks using generated examples only."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_submission.py"
SPEC = importlib.util.spec_from_file_location("validate_submission", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SubmissionValidationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "submission.csv"

    def write(self, content):
        self.path.write_text(content, encoding="utf-8")

    def test_valid_binary_decisions(self):
        self.write("LOAN_ID,APPROVED\n1,1\n2,0\n")
        result = MODULE.validate_submission(self.path, 2)
        self.assertEqual(result["records"], 2)
        self.assertEqual(result["approval_rate"], 0.5)
        self.assertEqual(len(result["sha256"]), 64)
        self.assertFalse(result["official_id_coverage_verified"])

    def test_full_size_generated_submission(self):
        self.write("LOAN_ID,APPROVED\n" + "".join(f"{i},{i % 2}\n" for i in range(100_000)))
        result = MODULE.validate_submission(self.path)
        self.assertEqual(result["approved"], 50_000)
        self.assertEqual(result["unique_loan_ids"], 100_000)

    def test_wrong_column_order_rejected(self):
        self.write("APPROVED,LOAN_ID\n1,1\n")
        with self.assertRaisesRegex(MODULE.SubmissionError, "Header"):
            MODULE.validate_submission(self.path, 1)

    def test_extra_columns_rejected(self):
        self.write("LOAN_ID,APPROVED\n1,1,extra\n")
        with self.assertRaisesRegex(MODULE.SubmissionError, "two columns"):
            MODULE.validate_submission(self.path, 1)

    def test_probabilities_rejected(self):
        self.write("LOAN_ID,APPROVED\n1,0.12\n")
        with self.assertRaisesRegex(MODULE.SubmissionError, "exactly 0 or 1"):
            MODULE.validate_submission(self.path, 1)

    def test_numerically_duplicate_ids_rejected(self):
        self.write("LOAN_ID,APPROVED\n1,0\n1.0,1\n")
        with self.assertRaisesRegex(MODULE.SubmissionError, "duplicate"):
            MODULE.validate_submission(self.path, 2)

    def test_missing_or_noninteger_ids_rejected(self):
        for identifier in ("", "NaN", "Infinity", "1.5", "abc", " 1"):
            with self.subTest(identifier=identifier):
                self.write(f"LOAN_ID,APPROVED\n{identifier},1\n")
                with self.assertRaises(MODULE.SubmissionError):
                    MODULE.validate_submission(self.path, 1)

    def test_wrong_row_count_rejected(self):
        self.write("LOAN_ID,APPROVED\n1,1\n")
        with self.assertRaisesRegex(MODULE.SubmissionError, "records"):
            MODULE.validate_submission(self.path)

    def test_official_id_coverage(self):
        reference = Path(self.directory.name) / "reference.csv"
        reference.write_text("LOAN_ID\n1\n2\n", encoding="utf-8")
        self.write("LOAN_ID,APPROVED\n2,1\n1,0\n")
        self.assertTrue(MODULE.validate_submission(self.path, 2, reference)["official_id_coverage_verified"])
        self.write("LOAN_ID,APPROVED\n1,0\n3,1\n")
        with self.assertRaisesRegex(MODULE.SubmissionError, "coverage mismatch"):
            MODULE.validate_submission(self.path, 2, reference)


if __name__ == "__main__":
    unittest.main()
