import pandas as pd
from pathlib import Path
from validate_submission import validate_submission

folder = Path.home() / "Downloads"
data = Path(__file__).resolve().parents[1] / "data"
cutoff = 0.16
name = "AN_COMBINED_016_20261029"

# These are the two new SAS exports and the matching 0.14 exports.
files = [
    ("Historical", "table_AN_COMBINED_016_TRAIN_20261029.csv",
     "table_AN_COMBINED_014_TRAINING_20261016.csv"),
    ("Public", "table_AN_C016_PUBLIC_20261029_R2.csv",
     "table_AN_COMB014_LABEL_PUBLIC_20261016.csv"),
]
columns = ["LOAN_ID", "APPROVED", "EM_EVENTPROBABILITY", "P_DEFAULT1"]
labels = pd.read_csv(folder / "table_AN_LR_PD_LABELED.csv",
    usecols=["LOAN_ID", "DEFAULT", "_PARTITION111_"])

for dataset, new_file, old_file in files:
    current = pd.read_csv(folder / new_file, usecols=columns)
    previous = pd.read_csv(folder / old_file, usecols=columns)

    for table in [current, previous]:
        table["LOAN_ID"] = pd.to_numeric(
            table["LOAN_ID"].astype(str).str.strip().str.strip(chr(34)).str.strip())
        assert table["LOAN_ID"].mod(1).eq(0).all(), "Noninteger ID"
        table["LOAN_ID"] = table["LOAN_ID"].astype("int64")
        assert len(table) == 100_000 and table["LOAN_ID"].is_unique
        assert table["APPROVED"].isin([0, 1]).all()
        assert table["EM_EVENTPROBABILITY"].between(0, 1).all()
        assert (table["EM_EVENTPROBABILITY"] - table["P_DEFAULT1"]).abs().le(1e-12).all()

    check = current.merge(previous, on="LOAN_ID", validate="one_to_one",
                          suffixes=("_new", "_old"))
    assert len(check) == 100_000, "Missing IDs"
    difference = (check["P_DEFAULT1_new"] - check["P_DEFAULT1_old"]).abs().max()
    print(dataset, "largest probability difference:", difference)
    assert difference <= 1e-10  # The older SAS exports round probabilities to 10 decimals.

    # With the same model/value rule, raising the cutoff retains all old approvals.
    expected = check["APPROVED_old"].eq(1) | check["P_DEFAULT1_new"].lt(cutoff)
    assert check["APPROVED_new"].eq(expected.astype(int)).all(), "Rule mismatch"
    added = check["APPROVED_new"].eq(1) & check["APPROVED_old"].eq(0)
    print(dataset, "approvals:", int(current["APPROVED"].sum()),
          "added versus 0.14:", int(added.sum()), "rule mismatches: 0")

    if dataset == "Historical":
        validation = current.merge(labels, on="LOAN_ID", validate="one_to_one")
        validation = validation.loc[validation["_PARTITION111_"] == 0]
        assert len(validation) == 40_000
        approved = validation.loc[validation["APPROVED"] == 1]
        print("Validation approvals:", len(approved))
        print("Defaults among approvals:", int(approved["DEFAULT"].sum()))
        print("Approved default rate:", approved["DEFAULT"].mean())
    else:
        public = current

submission = public[["LOAN_ID", "APPROVED"]].astype("int64")
output = data / f"submission_{name}.csv"
submission.to_csv(output, index=False)
print(validate_submission(output, expected_ids=data / "official_ids.csv"))
print("Saved:", output)
