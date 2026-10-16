# Methodology

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

The value-only policy had the highest historical scenario value but scored below the initial policy on Kaggle. The combined policy produced the best public score, 49.548, compared with 48.168 initially and 47.082 for value-only. This difference shows why the illustrative calculation is not a substitute for the competition's undisclosed scoring formula.

The analysis script currently compares the initial and value-only policies. The combined rule is implemented in SAS; its exports were checked separately against the intended logic and source records.

## Decision scoring

Model version 1.1 is connected to three separate SAS Intelligent Decisioning flows: `iLinkAutoLoans_AN_R1`, `iLinkAutoLoans_AN_Value`, and `iLinkAutoLoans_AN_Combined`. Each branch routes to the existing approval or decline rule set, which assigns integer approval values of 1 or 0.

The combined flow's historical scoring test checked all 100,000 records. Probabilities and default labels matched the earlier scored data by `LOAN_ID`, and every approval assignment matched the combined rule. Validation membership was recovered by joining IDs to the original scored file.

The combined public output contained 100,000 unique application IDs, matching an independently exported scoring input. All public decisions matched the combined rule, and probabilities were unchanged from the initial model. It retained all 65,145 initial approvals and added 2,082, producing 67,227 approvals and 32,773 declines.

The submission retained only `LOAN_ID` and `APPROVED`, in that order, from the SAS scoring output. The Python validator checked structure, row count, unique IDs, binary decisions, and exact reference ID coverage before upload. It validates the submission file; it does not evaluate predictive accuracy or calculate approval decisions.

## Evaluation limits

The validation cohort informed both model and policy selection, so these results are not an independent final test. Public leaderboard comparisons also inform development and may not hold on the private evaluation set. Probability calibration and borrower-group fairness have not been assessed. The illustrative loan values are separate from Kaggle's public score and do not represent realized bank profit.

This private repository tracks Python analysis, submission validation, and generated-data tests. Local data files and SAS exports are excluded. Exact model reproduction requires access to SAS Viya and competition data, along with the unrecorded partition seed and SAS configuration exports.
