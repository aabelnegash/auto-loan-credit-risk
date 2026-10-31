# Methodology

The [SAS workflow walkthrough](sas-workflow.md) covers the Model Studio settings, model registration, Intelligent Decisioning branch expression, and scoring tests.

## Model development

The training data was split into 60,000 training loans and 40,000 validation loans, stratified by `DEFAULT`. All model comparisons used the same partition. `LOAN_ID` was excluded from predictors.

The selected pipeline applies imputation, standardizes interval inputs, and fits Forward Logistic Regression with a Bernoulli target and logit link. Categorical inputs remain unchanged. Forward selection, stopping, and final model selection use SBC (Schwarz Bayesian criterion).

The original logistic fit produced information-matrix warnings and large coefficient standard errors. Standardizing interval inputs reduced those warnings from 13 to 0, and the new fit satisfied its convergence criterion. Close training and validation metrics supported selection of model version 1.1 for the first submission.

Autotuning was unavailable, so additional trials used manual settings. A gradient boosting trial with log-loss early stopping reached validation AUC 0.7960, compared with 0.7320 for its default run.

## Initial cutoff evaluation

Seven default-probability cutoffs were compared on the 40,000 validation loans: 5%, 7.5%, 10%, 13%, 15%, 20%, and 30%. Each policy approves loans strictly below its cutoff.

The financial comparison calculates scheduled full-term interest from loan principal, annual rate, and term. For principal `L`, scheduled interest `I`, historical default outcome `d`, and predicted default probability `p`:

```text
Historical scenario value = (1 - d) * I - d * L
Predicted expected value  = (1 - p) * I - p * L
```

This scenario assumes repayers pay all scheduled interest and default causes loss of the full original principal. It excludes recovery, payments before default, funding and servicing costs, fees, discounting, and early repayment.

The 13% cutoff had the highest historical scenario value among the seven candidates under these assumptions:

| Validation measure | PD < 0.13 |
| --- | ---: |
| Approved loans | 26,042 |
| Approval rate | 65.11% |
| Defaults among approved loans | 1,416 |
| Default rate among approved loans | 5.44% |

The leading cutoff changes with loss assumptions. At zero discount, a 50% principal loss favors 20%, while a 75% loss favors 15%. The financial comparison supports the initial policy; it does not establish the optimal competition cutoff.

## Policy comparison

Three policies were compared using the same registered model on October 16, 2026:

- **Initial cutoff:** approve when predicted default probability is below 0.13.
- **Value-only:** approve when predicted expected value is positive under the full-principal-loss scenario above.
- **Combined:** approve when either the initial cutoff or the value-only condition is satisfied.

Results on the 40,000 validation loans:

| Policy | Approved | Defaults among approvals | Approved default rate | Historical scenario value (USD) |
| --- | ---: | ---: | ---: | ---: |
| Initial cutoff | 26,042 | 1,416 | 5.44% | 28,719,860.78 |
| Value-only | 24,786 | 1,328 | 5.36% | 29,437,520.53 |
| Combined | 26,895 | 1,542 | 5.73% | 28,850,726.04 |

The combined policy retained all initial approvals and added 853 validation loans, including 126 observed defaults. Its historical scenario value exceeded the initial policy by USD 130,865.26 under the stated assumptions. The larger approval volume also increased the default rate among approved loans.

The value-only policy had the highest historical scenario value but scored below the initial policy on Kaggle. Among these three policies, the combined policy produced the best public score, 49.548, compared with 48.168 initially and 47.082 for value-only. The later 0.14 combined policy scored 50.005. This difference shows why the illustrative calculation is not a substitute for the competition's undisclosed scoring formula.

The analysis script compares the initial, value-only, and combined policies, including cutoff and loss assumptions. The combined rule is implemented in SAS; its exports were checked separately against the intended logic and source records.

## Decision scoring

Model version 1.1 is connected to three separate SAS Intelligent Decisioning flows: `iLinkAutoLoans_AN_R1`, `iLinkAutoLoans_AN_Value`, and `iLinkAutoLoans_AN_Combined`. Each branch routes to the existing approval or decline rule set, which assigns integer approval values of 1 or 0.

The combined flow's historical scoring test checked all 100,000 records. Probabilities and default labels matched the earlier scored data by `LOAN_ID`, and every approval assignment matched the combined rule. Validation membership was recovered by joining IDs to the original scored file.

The combined public output contained 100,000 unique application IDs, matching an independently exported scoring input. All public decisions matched the combined rule, and probabilities were unchanged from the initial model. It retained all 65,145 initial approvals and added 2,082, producing 67,227 approvals and 32,773 declines.

The submission retained only `LOAN_ID` and `APPROVED`, in that order, from the SAS scoring output. The Python validator checked structure, row count, unique IDs, binary decisions, and exact reference ID coverage before upload. It validates the submission file; it does not evaluate predictive accuracy or calculate approval decisions.

## Evaluation limits

The validation cohort informed both model and policy selection, so these results are not an independent final test. Public leaderboard comparisons also inform development and may not hold on the private evaluation set. Probability calibration and borrower-group fairness have not been assessed. The illustrative loan values are separate from Kaggle's public score and do not represent realized bank profit.

This private repository tracks Python analysis, submission validation, and generated-data tests. Local data files and SAS exports are excluded. Exact model reproduction requires access to SAS Viya and competition data, along with the unrecorded partition seed and SAS configuration exports.


## October 29 cutoff test

The combined 0.14 submission scored 50.005 on Kaggle and approved 68,811 public applications. A separate SAS decision, `iLinkAutoLoans_AN_Combined_016`, retains registered logistic model v1.1 and the existing value condition, raising only the PD cutoff from 0.14 to 0.16.

Both SAS scoring tests completed successfully. The historical output is `AN_COMBINED_016_TRAIN_20261029`; the public output is `AN_C016_PUBLIC_20261029_R2`, both in the personal CASUSER library. The public test was rerun with a fresh table name after an output-table promotion name collision.

The original validation cohort approved 28,905 of 40,000 loans (72.26%), including 1,832 defaults (6.34% of approvals). Public scoring approved 72,135 of 100,000 applications, adding 3,324 approvals versus 0.14.

`scripts/prepare_sas_submission.py` compares the new SAS exports with the matching 0.14 exports by LOAN_ID. It checks unchanged probabilities within the older exports' ten-decimal precision (maximum difference below 5e-11), binary decisions, and agreement with the existing 0.14 approvals OR PD < 0.16 on every row. This is a baseline and threshold consistency check; the script does not recalculate the loan economics. Validation membership comes from the original partitioned scoring export. The two-column CSV passes the existing submission validator against all 100,000 official IDs.

The 0.16 decision flow and submission preparation script were written on October 29. The script was used to check the SAS exports and prepare the two-column CSV.

The policy analysis also compares 50%, 75%, and 100% loss assumptions. At a 0.16 cutoff, using 75% loss in the value rule approved 29,980 validation loans (74.95%), with a 6.82% default rate among approvals. Under the historical 75% loss scenario, this produced $36.836M versus $36.674M for the current 0.16 combined rule. The gain is small and uses the same validation cohort, so this is a candidate to test rather than a confirmed improvement.

The saved comparison covers the following validation results. Scenario values are in USD millions and use the same 40,000 validation loans.

| PD cutoff | Loss used in value rule | Approved | Approved default rate | Value at 50% loss | Value at 75% loss | Value at 100% loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.14 | 100% | 27,535 | 5.931% | 44.908 | 36.660 | 28.412 |
| 0.16 | 100% | 28,905 | 6.338% | 45.953 | 36.674 | 27.395 |
| 0.18 | 100% | 30,260 | 6.801% | 46.947 | 36.609 | 26.272 |
| 0.20 | 100% | 31,498 | 7.264% | 47.574 | 36.126 | 24.677 |
| 0.14 | 75% | 29,350 | 6.719% | 46.491 | 36.699 | 26.907 |
| 0.16 | 75% | 29,980 | 6.821% | 47.021 | 36.836 | 26.652 |
| 0.14 | 50% | 33,081 | 8.295% | 48.139 | 34.812 | 21.484 |

The local files saved from this work are:

- `data/policy_comparison_20261029.txt`: the policy comparison output.
- `data/sas_combined016_tests_20261029.jpg`: both completed SAS scoring tests.
- `data/submission_AN_COMBINED_016_20261029.csv`: the validated two-column CSV.
- `table_AN_COMBINED_016_TRAIN_20261029.csv` and `table_AN_C016_PUBLIC_20261029_R2.csv` in Downloads: the full historical and public SAS exports.

These files remain local. The scripts and aggregate results are tracked in Git.
