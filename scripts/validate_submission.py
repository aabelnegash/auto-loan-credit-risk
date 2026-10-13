import csv
from decimal import Decimal, InvalidOperation


def read_loan_id(text):
    if not text or text != text.strip():
        raise ValueError("LOAN_ID is blank or has surrounding spaces.")

    try:
        number = Decimal(text)
    except InvalidOperation:
        raise ValueError("LOAN_ID must be numeric.")

    if not number.is_finite():
        raise ValueError("LOAN_ID must be finite.")

    loan_id = int(number)

    if number != loan_id:
        raise ValueError("LOAN_ID must be a whole number.")

    return loan_id


def read_reference_ids(filename):
    ids = set()

    with open(filename, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, strict=True)

        if not reader.fieldnames or reader.fieldnames.count("LOAN_ID") != 1:
            raise ValueError("Reference file needs one LOAN_ID column.")

        for row in reader:
            if None in row or row.get("LOAN_ID") is None:
                raise ValueError("Reference file has a malformed row.")

            loan_id = read_loan_id(row["LOAN_ID"])

            if loan_id in ids:
                raise ValueError("Reference file has a duplicate LOAN_ID.")

            ids.add(loan_id)

    return ids


def validate_submission(filename, expected_rows=100_000, expected_ids=None):
    if expected_rows < 1:
        raise ValueError("Expected row count must be positive.")

    ids = set()
    approved = 0

    with open(filename, encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, strict=True)

        if next(reader, None) != ["LOAN_ID", "APPROVED"]:
            raise ValueError("Columns must be LOAN_ID,APPROVED in that order.")

        for row_number, row in enumerate(reader, start=2):
            if len(row) != 2:
                raise ValueError(f"Row {row_number} must have two columns.")

            loan_id = read_loan_id(row[0])

            if loan_id in ids:
                raise ValueError(f"Row {row_number} repeats a LOAN_ID.")

            if row[1] not in ("0", "1"):
                raise ValueError(f"Row {row_number}: APPROVED must be 0 or 1.")

            ids.add(loan_id)
            approved += int(row[1])

    records = len(ids)

    if records != expected_rows:
        raise ValueError(f"Expected {expected_rows} rows; found {records}.")

    if expected_ids is not None:
        reference_ids = read_reference_ids(expected_ids)

        if ids != reference_ids:
            raise ValueError("Submission IDs do not match the reference IDs.")

    return {
        "records": records,
        "approved": approved,
        "declined": records - approved,
        "approval_rate": approved / records,
        "official_id_coverage_verified": expected_ids is not None,
    }

if __name__ == "__main__":
    result = validate_submission(
        "data/submission.csv",
        expected_ids="data/official_ids.csv",
    )

    print(result)