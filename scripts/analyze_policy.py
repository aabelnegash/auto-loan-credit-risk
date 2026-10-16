import pandas as pd
import numpy as np

scores = pd.read_csv(
    r"C:\Users\14044\Downloads\table_AN_LR_PD_LABELED.csv",
    usecols=[
        "LOAN_ID",
        "DEFAULT",
        "EM_EVENTPROBABILITY",
        "_PARTITION111_",
    ],
    encoding="utf-8-sig", 
)

print(scores.shape)
print(scores.head())
print(scores.dtypes)




print(scores["_PARTITION111_"].value_counts())

validation = scores.loc[scores["_PARTITION111_"] == 0].copy()

print("Validation loans:", len(validation))
print("Actual defaults:", validation["DEFAULT"].sum())



validation["approved_current"] = validation["EM_EVENTPROBABILITY"] < 0.13

current_approved = validation.loc[validation["approved_current"]]

print("Current approvals:", len(current_approved))
print("Approval rate:", validation["approved_current"].mean())
print("Defaults among approvals:", current_approved["DEFAULT"].sum())
print("Default rate among approvals:", current_approved["DEFAULT"].mean())

loans = pd.read_csv(
    r"C:\Users\14044\Downloads\table_ILINK_CREDITRISK_TRAINING.csv",
    usecols=[
        "LOAN_ID",
        "LOAN_AMOUNT",
        "INTEREST_RATE",
        "LOAN_TERM",
    ],
    dtype={"LOAN_ID": "string"},
    encoding="utf-8-sig",
)

print(loans.shape)
print(loans.dtypes)
print(loans.head())

loans["LOAN_ID"] = loans["LOAN_ID"].str.replace("\ufeff", "", regex=False)
loans["LOAN_ID"] = loans["LOAN_ID"].str.replace('"', "", regex=False)
loans["LOAN_ID"] = loans["LOAN_ID"].str.strip()

loan_columns = ["LOAN_ID", "LOAN_AMOUNT", "INTEREST_RATE", "LOAN_TERM"]

for column in loan_columns:
    loans[column] = pd.to_numeric(loans[column], errors="raise")

if not np.isfinite(loans[loan_columns].to_numpy(dtype=float)).all():
    raise ValueError("Loan IDs and loan terms must contain finite numbers.")

if (loans["LOAN_ID"] % 1 != 0).any():
    raise ValueError("Loan IDs must be whole numbers.")

loans["LOAN_ID"] = loans["LOAN_ID"].astype("int64")

if scores["LOAN_ID"].duplicated().any() or loans["LOAN_ID"].duplicated().any():
    raise ValueError("Each source must have one row per loan ID.")

if set(scores["LOAN_ID"]) != set(loans["LOAN_ID"]):
    raise ValueError("The scored and original files contain different loan IDs.")

if (loans["LOAN_AMOUNT"] <= 0).any():
    raise ValueError("Loan amounts must be positive.")

if not loans["INTEREST_RATE"].between(0, 1, inclusive="left").all():
    raise ValueError("Interest rates must be annual decimals from 0 up to 1.")

if (loans["LOAN_TERM"] <= 0).any() or (loans["LOAN_TERM"] % 1 != 0).any():
    raise ValueError("Loan terms must be positive whole months.")

validation = validation.merge(
    loans,
    on="LOAN_ID",
    how="left",
    validate="one_to_one",
    indicator=True,
)

if not (validation["_merge"] == "both").all():
    raise ValueError("Some validation loans have no matching loan terms.")

if not validation["EM_EVENTPROBABILITY"].between(0, 1).all():
    raise ValueError("Default probabilities must be between 0 and 1.")

if not validation["DEFAULT"].isin([0, 1]).all():
    raise ValueError("Historical default outcomes must be 0 or 1.")

principal = validation["LOAN_AMOUNT"]
months = validation["LOAN_TERM"]
monthly_rate = validation["INTEREST_RATE"] / 12

validation["scheduled_payment"] = principal / months

has_interest = monthly_rate > 0

validation.loc[has_interest, "scheduled_payment"] = (
    principal[has_interest] * monthly_rate[has_interest]
    / (1 - (1 + monthly_rate[has_interest]) ** (-months[has_interest]))
)

validation["scheduled_interest"] = (
    validation["scheduled_payment"] * months - principal
)

validation.loc[~has_interest, "scheduled_interest"] = 0.0

default_probability = validation["EM_EVENTPROBABILITY"]

validation["expected_value"] = (
    (1 - default_probability) * validation["scheduled_interest"]
    - default_probability * principal
)

calculated_columns = [
    "scheduled_payment",
    "scheduled_interest",
    "expected_value",
]

if not np.isfinite(
    validation[calculated_columns].to_numpy(dtype=float)
).all():
    raise ValueError("The financial calculation produced invalid values.")

validation["approved_candidate"] = validation["expected_value"] > 0

validation["historical_scenario_value"] = validation["scheduled_interest"].where(
    validation["DEFAULT"] == 0,
    -principal,
)

comparison = []

for column in ["approved_current", "approved_candidate"]:
    approved = validation.loc[validation[column]]

    comparison.append({
        "policy": column,
        "approved": len(approved),
        "approval_rate": validation[column].mean(),
        "defaults": approved["DEFAULT"].sum(),
        "approved_default_rate": approved["DEFAULT"].mean(),
        "scenario_value": approved["historical_scenario_value"].sum(),
    })

print("\nPolicy comparison:")
print(
    pd.DataFrame(comparison).to_string(
        index=False,
        float_format="{:,.4f}".format,
    )
)

groups = validation.groupby(
    ["approved_current", "approved_candidate"]
).agg(
    loans=("LOAN_ID", "size"),
    defaults=("DEFAULT", "sum"),
    principal_exposure=("LOAN_AMOUNT", "sum"),
    scenario_value=("historical_scenario_value", "sum"),
)

print("\nDecision groups:")
print(groups.round(2).to_string())

print("\nSensitivity: candidate minus current historical scenario value")

for loss_fraction in [0.25, 0.50, 0.75, 1.00]:
    scenario_value = validation["scheduled_interest"].where(
        validation["DEFAULT"] == 0,
        -loss_fraction * principal,
    )

    current_value = scenario_value.loc[validation["approved_current"]].sum()
    candidate_value = scenario_value.loc[validation["approved_candidate"]].sum()
    difference = candidate_value - current_value

    print(f"Loss fraction {loss_fraction:.0%}: {difference:,.2f} USD")