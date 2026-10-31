import tempfile
import unittest
from pathlib import Path

from scripts.validate_submission import validate_submission


class SubmissionTests(unittest.TestCase):
    def check_text(self, text):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "submission.csv"
            path.write_text(text, encoding="utf-8")

            return validate_submission(path, expected_rows=2)

    def test_valid_submission(self):
        result = self.check_text("LOAN_ID,APPROVED\n1,1\n2,0\n")

        self.assertEqual(result["records"], 2)
        self.assertEqual(result["approved"], 1)
        self.assertEqual(result["approval_rate"], 0.5)

    def test_invalid_submissions(self):
        examples = [
            "APPROVED,LOAN_ID\n1,1\n2,0\n",
            "LOAN_ID,APPROVED\n1,1,extra\n2,0\n",
            "LOAN_ID,APPROVED\n1,1\n1.0,0\n",
            "LOAN_ID,APPROVED\n1,0.12\n2,0\n",
            "LOAN_ID,APPROVED\nNaN,1\n2,0\n",
            "LOAN_ID,APPROVED\n1.5,1\n2,0\n",
            "LOAN_ID,APPROVED\n1,1\n",
        ]

        for text in examples:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    self.check_text(text)

    def test_reference_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            submission = Path(folder) / "submission.csv"
            reference = Path(folder) / "reference.csv"

            submission.write_text(
                "LOAN_ID,APPROVED\n2,1\n1,0\n",
                encoding="utf-8",
            )
            reference.write_text(
                "LOAN_ID\n1\n2\n",
                encoding="utf-8",
            )

            result = validate_submission(submission, 2, reference)
            self.assertTrue(result["official_id_coverage_verified"])

            reference.write_text(
                "LOAN_ID\n1\n3\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                validate_submission(submission, 2, reference)