# Auto Loan Credit Risk

## Project overview

Default-risk modeling and auto-loan decisioning using SAS Viya. The project uses synthetic loan data for the fictional iLink Capital Bank in the [SAS Hackathon 2026 Student Track](https://www.kaggle.com/competitions/sas-hackathon-2026).

The project connects predictive modeling to a tested lending decision flow. Work completed through October 8, 2026 includes model comparison, fitting diagnostics, model registration, full application scoring, and an accepted Kaggle submission.

**Tools:** SAS Visual Analytics, Model Studio, Model Manager, Intelligent Decisioning, and Python for local output checks.

> **Competition code disclosure:** The full modeling, financial-analysis, and decision-policy implementation remains private during the competition to preserve the active strategy. [Kaggle Rule 6(b)](https://www.kaggle.com/competitions/sas-hackathon-2026/rules) requires publicly shared competition code to also be made available through the competition's discussion forum or notebooks. This limited release includes the submission validator and generated-data tests under the MIT license; those files are subject to the same sharing requirement.

## Workflow

| Stage | Tool | Completed work |
| --- | --- | --- |
| Exploration | Visual Analytics | Reviewed loan data and an initial decision-tree model |
| Modeling | Model Studio | Compared candidate models, reviewed fitting diagnostics, and tested preprocessing changes |
| Registration | Model Manager | Registered the selected Forward Logistic Regression model |
| Decisioning | Intelligent Decisioning | Connected model scoring to approval and decline rules; tested the complete flow |
| Verification | Python and Kaggle | Audited scoring outputs and submitted the verified approval file |

## Data

The modeling dataset contains 100,000 historical loans with a binary default outcome. Models were compared using a stratified 60% training / 40% validation split. Application identifiers were excluded from predictors and retained for matching scoring results.

## Modeling approach

Logistic regression, decision tree, forest, gradient boosting, neural network, and ensemble models were evaluated on the same validation partition. Model selection considered ranking performance, probability error, fitting diagnostics, and the difference between training and validation results.

### Selected development candidates

The leading completed trials produced the following results on the same 40,000-loan validation cohort. These runs used different pipelines and configurations; they are development comparisons rather than an exhaustive benchmark of each algorithm.

| Candidate | Training AUC | Validation AUC | Validation KS | Validation log loss |
| --- | ---: | ---: | ---: | ---: |
| Standardized Forward Logistic Regression | 0.7975 | 0.7992 | 0.4490 | 0.3208 |
| Ensemble, revised trial | 0.7969 | 0.7987 | 0.4484 | 0.3212 |
| Gradient Boosting, revised trial | 0.8257 | 0.7960 | 0.4471 | 0.3229 |

Forward Logistic Regression was selected for its validation results and close training/validation performance. Gradient Boosting had a larger AUC gap, while the ensemble performed similarly to the selected model. The small differences between the leading candidates have not been established as statistically significant.

### Fitting diagnostics

The original logistic fit produced **13 information-matrix warnings** and large coefficient standard errors. After numeric standardization was added to the existing preprocessing path, the selected fit satisfied its convergence criterion and produced **zero information-matrix warnings**. Validation performance changed only slightly.

This resolved the recorded matrix warnings without establishing their exact cause or the reliability of every coefficient. The [methodology](docs/methodology.md) includes the initial model comparison, metric definitions, and complete training/validation results for the selected fit.

## Decisioning and scoring

The registered model was connected to a SAS Intelligent Decisioning flow that converts default probabilities into approval decisions. The flow scores each application, evaluates the approval branch, assigns a binary outcome, and returns the result.

Policy evaluation considered approval volume, observed defaults, and illustrative loan-value scenarios. Predictive model quality and lending-policy performance were assessed separately because a stronger risk ranking does not automatically produce a better financial outcome.

### Scoring audit

The completed flow scored the historical dataset and all 100,000 public applications. Historical probabilities were unchanged between the model-only test and the complete decision flow. The public scoring audit verified:

| Check | Result |
| --- | --- |
| Applications scored | 100,000 |
| Unique, nonmissing application identifiers | 100,000 |
| Coverage against an independent input export | Exact match |
| Missing or invalid probabilities | 0 |
| Approval values | Binary on every row |
| Disagreements with the saved decision rule | 0 |

The submission retained the approval values generated by SAS. Local checks verified the required file structure and application coverage before upload.

## Submission validation code

[scripts/validate_submission.py](scripts/validate_submission.py) checks column order, record count, finite integer identifiers, duplicate IDs, binary approval values, and optional coverage against a reference ID file. It reports summary counts and a SHA-256 file hash without changing the submission or uploading it.

Requires **Python 3.10 or later**, with no external packages:

```sh
python scripts/validate_submission.py path/to/submission.csv
python scripts/validate_submission.py path/to/submission.csv --expected-ids path/to/reference_ids.csv
python -m unittest discover -s tests -v
```

[tests/test_validate_submission.py](tests/test_validate_submission.py) contains nine tests using generated records, including a 100,000-row example and rejection checks for malformed submissions. No competition records or submission files are included. The validator checks output integrity; it does not train the model or calculate approval decisions.

## Competition result

The first submission was accepted on October 8, 2026, with a Kaggle public score of **48.168**. This is an interim competition result, not a final ranking or realized bank profit.

Model comparison, registration, decision-flow testing, and the initial submission are complete. Further competition development remains in the private working repository.

## Publication scope

This repository contains a portfolio summary and the submission-validation utility. Modeling configurations, probability and loan-value analysis, decision thresholds, and detailed policy experiments remain private while the competition is active. This limited scope avoids publishing the active modeling and decision strategy.

An expanded technical repository will be published after the competition concludes, subject to the competition's data and sharing restrictions. Competition datasets, applicant-level outputs, and submission files are excluded from this repository.
