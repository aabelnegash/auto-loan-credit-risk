# Methodology

## Model development

The training data was split into 60,000 training loans and 40,000 validation loans, stratified by `DEFAULT`. All model comparisons used the same partition. `LOAN_ID` was excluded from predictors.

The selected pipeline applies imputation, standardizes interval inputs, and fits Forward Logistic Regression with a Bernoulli target and logit link. Categorical inputs remain unchanged. Forward selection, stopping, and final model selection use SBC (Schwarz Bayesian criterion).

The original logistic fit produced information-matrix warnings and large coefficient standard errors. Standardizing interval inputs reduced those warnings from 13 to 0, and the new fit satisfied its convergence criterion. Close training and validation metrics supported selection of model version 1.1 for the first submission.

Autotuning was unavailable, so additional trials used manual settings. A gradient boosting trial with log-loss early stopping reached validation AUC 0.7960, compared with 0.7320 for its default run.

## Cutoff evaluation

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

## Decision scoring

Model version 1.1 is connected to decision version 1.0 in SAS Intelligent Decisioning. The branch expression is `EM_EVENTPROBABILITY < 0.13`; the two rule sets assign integer approval values of 1 or 0.

A labeled scoring test checked all 100,000 records. `EM_EVENTPROBABILITY` matched `P_DEFAULT1`, probabilities matched the earlier model-only output by `LOAN_ID`, and every approval assignment matched the saved cutoff.

The public scoring output contained 100,000 unique application IDs, matching an independently exported scoring input. All public decisions matched the cutoff. The Python validator checks CSV structure and ID coverage; the scoring audit separately checked the approval rule.

## Evaluation limits

The validation cohort informed both model and cutoff selection, so these results are not an independent final test. Probability calibration and borrower-group fairness have not been assessed. The illustrative loan values are separate from Kaggle's public score and do not represent realized bank profit.

This repository contains documentation only. Exact model reproduction requires access to SAS Viya and the competition data, along with the unrecorded partition seed and SAS configuration exports. Python scripts, generated-data tests, and local data files are excluded from this repository.
