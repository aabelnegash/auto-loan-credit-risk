"""Check an Auto Loan Game submission locally without changing or uploading it.

Usage: python scripts/validate_submission.py path/to/submission.csv
Optional: --expected-ids path/to/official_scoring_ids.csv
Uses only the Python standard library. No competition data ships with this repo.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


class SubmissionError(ValueError):
    """The input does not meet the submission contract."""


def normalize_id(value: str, line_number: int) -> int:
    if not value or value != value.strip():
        raise SubmissionError(f"Line {line_number}: LOAN_ID is empty or has surrounding whitespace.")
    try:
        number = Decimal(value)
    except InvalidOperation:
        raise SubmissionError(f"Line {line_number}: LOAN_ID must be a numeric integer.") from None
    if not number.is_finite() or number != number.to_integral_value():
        raise SubmissionError(f"Line {line_number}: LOAN_ID must be a finite integer.")
    return int(number)


def read_expected_ids(path: Path) -> set[int]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if not reader.fieldnames or reader.fieldnames.count("LOAN_ID") != 1:
            raise SubmissionError("The expected-ID file needs one LOAN_ID column.")
        identifiers: set[int] = set()
        for line_number, row in enumerate(reader, start=2):
            if None in row or row.get("LOAN_ID") is None:
                raise SubmissionError(f"Expected-ID file line {line_number}: malformed row.")
            identifier = normalize_id(row["LOAN_ID"], line_number)
            if identifier in identifiers:
                raise SubmissionError(f"Expected-ID file line {line_number}: duplicate LOAN_ID.")
            identifiers.add(identifier)
        return identifiers


def validate_submission(
    path: Path, expected_rows: int = 100_000, expected_ids: Path | None = None
) -> dict[str, object]:
    if expected_rows < 1:
        raise SubmissionError("Expected row count must be positive.")
    identifiers: set[int] = set()
    approved = 0
    row_count = 0
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, strict=True)
        if next(reader, None) != ["LOAN_ID", "APPROVED"]:
            raise SubmissionError("Header must be exactly LOAN_ID,APPROVED in that order.")
        for line_number, row in enumerate(reader, start=2):
            if len(row) != 2:
                raise SubmissionError(f"Line {line_number}: expected exactly two columns.")
            identifier = normalize_id(row[0], line_number)
            if identifier in identifiers:
                raise SubmissionError(f"Line {line_number}: duplicate LOAN_ID.")
            if row[1] not in {"0", "1"}:
                raise SubmissionError(f"Line {line_number}: APPROVED must be exactly 0 or 1.")
            identifiers.add(identifier)
            approved += int(row[1])
            row_count += 1
    if row_count != expected_rows:
        raise SubmissionError(f"Expected {expected_rows:,} records; found {row_count:,}.")
    ids_verified = False
    if expected_ids is not None:
        reference_ids = read_expected_ids(expected_ids)
        if identifiers != reference_ids:
            missing = len(reference_ids - identifiers)
            unexpected = len(identifiers - reference_ids)
            raise SubmissionError(f"ID coverage mismatch: {missing:,} missing; {unexpected:,} unexpected.")
        ids_verified = True
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return {
        "status": "valid_format",
        "records": row_count,
        "unique_loan_ids": len(identifiers),
        "approved": approved,
        "declined": row_count - approved,
        "approval_rate": round(approved / row_count, 6),
        "sha256": digest.hexdigest(),
        "official_id_coverage_verified": ids_verified,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submission", type=Path)
    parser.add_argument("--expected-rows", type=int, default=100_000)
    parser.add_argument("--expected-ids", type=Path)
    args = parser.parse_args()
    try:
        result = validate_submission(args.submission, args.expected_rows, args.expected_ids)
    except (SubmissionError, OSError, UnicodeError, csv.Error) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    print("Checks file structure only. It does not measure model quality, fairness, or game profit.")
    if not result["official_id_coverage_verified"]:
        print("Use --expected-ids to check membership against the official scoring applicants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
