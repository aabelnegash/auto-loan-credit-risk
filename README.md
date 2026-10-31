# Auto Loan Credit Risk

This is the auto-loan credit risk project I worked on for the [SAS Hackathon 2026 Student Track](https://www.kaggle.com/competitions/sas-hackathon-2026). I used SAS Viya to compare default-risk models, build loan approval rules, and score 100,000 applications.

The synthetic data represents the fictional iLink Capital Bank. It includes 100,000 historical loans for model development and 100,000 applications for scoring.

**Tools:** SAS Visual Analytics, Model Studio, Model Manager, Intelligent Decisioning, Python, pandas, and NumPy.

## What I worked on

- Compared logistic regression, decision tree, forest, gradient boosting, neural network, and ensemble models using the same 60% training / 40% validation split.
- Selected standardized Forward Logistic Regression and registered it in Model Manager.
- Built approval rules in Intelligent Decisioning using predicted default probability and a loan value calculation.
- Used Python to compare policies and check the exported CSVs for missing IDs, duplicate records, and invalid approval values.

## Model results

The scoring flow applies imputation and standardization before prediction. Standardization reduced information-matrix warnings from 13 to 0 while keeping similar validation performance.

| Metric | Training | Validation |
| --- | ---: | ---: |
| AUC | 0.7975 | 0.7992 |
| KS | 0.4436 | 0.4490 |
| Average squared error | 0.0962 | 0.0961 |
| Log loss | 0.3210 | 0.3208 |

## Policy results

I tested a default-probability cutoff, a value-only rule, and a combined rule that approves a loan when either condition is met. These comparisons used the same registered model, version 1.1.

| Policy | Kaggle public score |
| --- | ---: |
| Initial cutoff, PD < 0.13 | 48.168 |
| Value-only | 47.082 |
| Combined, PD < 0.13 | 49.548 |
| Combined, PD < 0.14 | **50.005** |

The combined 0.14 policy improved the initial public score by **1.837** and approved 68,811 of 100,000 scoring applications.

On October 29, I wrote a combined 0.16 version of the decision flow and a Python script to prepare and validate its output. The SAS flow approved 28,905 of 40,000 validation loans, with a 6.34% default rate among approvals. It approved 72,135 scoring applications, adding 3,324 approvals compared with 0.14. The exported CSV passed the rule and ID coverage checks.

## Code and notes

- [Policy analysis](scripts/analyze_policy.py): compares approval cutoffs and loan-loss assumptions.
- [CSV preparation](scripts/prepare_sas_submission.py): checks the SAS exports against the 0.14 baseline and prepares the two-column file.
- [CSV validation](scripts/validate_submission.py): checks columns, row count, unique IDs, binary decisions, and official ID coverage.
- [Methodology](docs/methodology.md): model choices, financial assumptions, detailed results, and evaluation limits.

Competition data, SAS scoring exports, and generated CSVs are kept locally. The Python scripts and validation tests are included here. Running the SAS workflow requires SAS Viya and the competition data.
