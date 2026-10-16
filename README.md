# Auto Loan Credit Risk

## Project overview

Default-risk modeling and auto-loan approval decisions using SAS Viya. The project uses synthetic loan data for the fictional iLink Capital Bank in the [SAS Hackathon 2026 Student Track](https://www.kaggle.com/competitions/sas-hackathon-2026).

The workflow covers model comparison, preprocessing, model registration, and scoring through SAS Intelligent Decisioning. Python compares approval policies and checks submission format and application ID coverage.

**Tools:** SAS Visual Analytics, Model Studio, Model Manager, Intelligent Decisioning, and Python.

## Data

- Training data: 100,000 historical loans with 83 variables.
- Scoring data: 100,000 applications.
- Target: `DEFAULT`, where 1 indicates default and 0 indicates repayment.
- `LOAN_ID` is retained for matching records and excluded from model inputs.

Competition data and submission files are not included in the repository.

## Workflow

```text
Data exploration → Model comparison → Model registration
→ Approval rules → Application scoring → Submission validation
```

Logistic regression, decision tree, forest, gradient boosting, neural network, and ensemble models were compared using a stratified 60% training / 40% validation split.

## Model results

Standardized Forward Logistic Regression was selected and registered in Model Manager. The scoring path applies imputation and standardization before prediction.

| Metric | Training | Validation |
| --- | ---: | ---: |
| AUC | 0.7975 | 0.7992 |
| KS | 0.4436 | 0.4490 |
| Average squared error | 0.0962 | 0.0961 |
| Log loss | 0.3210 | 0.3208 |

Standardization reduced information-matrix warnings from 13 to 0 while preserving similar validation performance.

## Approval policy

The initial policy approved loans with predicted default probability below 0.13. Two additional policies were evaluated on October 16: a value-only rule and a combined rule that approves when either the initial cutoff or the value rule is satisfied.

All three policies use the same registered model, version 1.1. The model was not retrained for this comparison.

| Submission date | Policy | Kaggle public score |
| --- | --- | ---: |
| October 8, 2026 | Initial cutoff | 48.168 |
| October 16, 2026 | Value-only | 47.082 |
| October 16, 2026 | Combined | **49.548** |

The combined policy is the current best submission, improving the public score by **1.380 points**. It produced 67,227 approvals and 32,773 declines across 100,000 public applications. Scoring checks confirmed complete ID coverage, unchanged model probabilities, and agreement with the intended rule on every row.

The [methodology](docs/methodology.md) records the policy comparison, financial assumptions, and evaluation limits. Public scores are interim competition results, not realized bank profit or final rankings.

## Project structure

- [docs/methodology.md](docs/methodology.md): modeling choices, policy comparisons, and scoring checks.
- [scripts/analyze_policy.py](scripts/analyze_policy.py): historical comparison of the initial and value-only policies, including loss sensitivity.
- [scripts/validate_submission.py](scripts/validate_submission.py): submission format, record count, and ID coverage checks.
- [tests/test_validate_submission.py](tests/test_validate_submission.py): validator tests using generated records.

## Output validation

Local Python checks verified column order, 100,000 records, unique integer identifiers, binary approval values, and exact application coverage before submission. These were file-integrity checks. SAS assessment and scoring audits separately evaluated model performance, probability consistency, and agreement with the saved approval rule.

The validator uses the Python standard library. Policy analysis uses pandas and NumPy. File paths are set in the scripts; the validator's main block checks `data/submission.csv` against `data/official_ids.csv`. Other submission files can be checked by calling `validate_submission` with their paths.

Scripts and generated-data tests are tracked in this private working repository. Competition data, scoring exports, and submission files remain local and are ignored by Git. The public portfolio repository contains documentation only.

Exact model reproduction requires SAS Viya, competition data, the unrecorded partition seed, and SAS configuration exports.
