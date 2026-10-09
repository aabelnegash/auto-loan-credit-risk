# Auto Loan Credit Risk

## Project overview

Default-risk modeling and auto-loan decisioning using SAS Viya. The project uses synthetic loan data for the fictional iLink Capital Bank in the [SAS Hackathon 2026 Student Track](https://www.kaggle.com/competitions/sas-hackathon-2026).

The work covers data exploration, model comparison, fitting diagnostics, model registration, and application scoring through SAS Intelligent Decisioning.

**Tools:** SAS Visual Analytics, Model Studio, Model Manager, Intelligent Decisioning, and Python for local output checks.

## Data

The modeling dataset contains 100,000 historical loans with a binary default outcome. Models were compared using a stratified 60% training / 40% validation split. Application identifiers were excluded from predictors and retained for matching scoring results.

## Modeling approach

Logistic regression, decision tree, forest, gradient boosting, neural network, and ensemble models were evaluated on the same validation partition. Model selection considered ranking performance, probability error, fitting diagnostics, and the difference between training and validation results.

### Forward Logistic Regression

Forward Logistic Regression was selected and registered in Model Manager. Logistic regression estimates the probability of a binary outcome, such as borrower default. Forward selection starts with an intercept and adds predictors based on improvements in model fit.

The development work included missing-value treatment, standardization of numeric inputs, and review of convergence and coefficient uncertainty. The selected fit satisfied its convergence criterion and had similar training and validation performance.

| Metric | Training | Validation |
| --- | ---: | ---: |
| AUC | 0.7975 | 0.7992 |
| KS | 0.4436 | 0.4490 |
| Average squared error | 0.0962 | 0.0961 |
| Log loss | 0.3210 | 0.3208 |

## Decisioning and scoring

The registered model was connected to a SAS Intelligent Decisioning flow that converts default probabilities into approval decisions. Policy evaluation considered approval volume, observed defaults, and illustrative loan-value scenarios.

The completed flow scored 100,000 public applications. Output checks verified unique identifiers, complete application coverage, binary decisions, and agreement with the saved decision logic.

The first submission was accepted on October 8, 2026, with a Kaggle public score of **48.168**. This is an interim competition result, not a final ranking or realized bank profit.

## Technical overview

[docs/methodology.md](docs/methodology.md) describes the evaluation approach, workflow checks, and limitations.

## Publication scope

This repository is a portfolio summary of an ongoing competition project. Implementation code, model configurations, decision thresholds, and detailed experiments remain private during the competition to avoid disclosing the active submission strategy.

An expanded technical repository will be published after the competition concludes, subject to the competition's data and sharing restrictions. Competition datasets, applicant-level outputs, and submission files are excluded from this repository.
