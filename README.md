# Auto Loan Credit Risk

## Project overview

Default-risk modeling and auto-loan approval decisions using SAS Viya. The project uses synthetic loan data for the fictional iLink Capital Bank in the [SAS Hackathon 2026 Student Track](https://www.kaggle.com/competitions/sas-hackathon-2026).

The workflow covers model comparison, preprocessing, model registration, and scoring through SAS Intelligent Decisioning. Python checks the submission format and application ID coverage.

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

The decision flow assigns `APPROVED = 1` when predicted default probability is below 0.13 and `APPROVED = 0` otherwise. The cutoff was selected from seven candidates using validation results and an illustrative loan-value calculation.

Public scoring produced 65,145 approvals and 34,855 declines. The first submission was accepted on October 8, 2026, with a Kaggle public score of **48.168**.

The [methodology](docs/methodology.md) explains the policy assumptions and evaluation limits.

## Project structure

- [docs/methodology.md](docs/methodology.md): modeling choices, cutoff evaluation, and scoring checks.

## Output validation

Local Python checks verified column order, 100,000 records, unique integer identifiers, binary approval values, and exact application coverage before submission. These were file-integrity checks. SAS assessment and scoring audits separately evaluated model performance, probability consistency, and agreement with the saved approval rule.

Python scripts and generated-data tests are maintained locally and are excluded from this repository.

This repository contains documentation only. Exact model reproduction requires SAS Viya, competition data, the unrecorded partition seed, and SAS configuration exports.
