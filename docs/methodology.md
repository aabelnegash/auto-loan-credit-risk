# Methodology

## Problem and target

The modeling task estimates borrower default probability. The decisioning task uses those predictions to assign an approval outcome. Ranking borrowers by risk and evaluating a lending policy are separate steps: stronger predictive metrics do not automatically imply a better financial outcome.

## Model comparison

Models were assessed on the same stratified training and validation partition. Application identifiers were excluded from predictors to keep record matching separate from prediction.

The comparison used AUC and KS to assess risk separation, alongside average squared error and log loss to assess probability predictions. Training and validation metrics were reviewed together to identify large performance gaps.

Forward Logistic Regression was selected for the initial submission. Its sequential predictor selection provides a way to build a smaller candidate model from the available inputs. Missing-value treatment and numeric standardization were incorporated into the scoring path.

Fitting diagnostics were reviewed alongside performance metrics. The original logistic fit raised information-matrix warnings and large coefficient standard errors. Following preprocessing changes, the selected fit satisfied its convergence criterion and no longer produced those matrix warnings. This improved the recorded diagnostics; it does not establish that every coefficient is reliable or explain the exact cause of the original warnings.

## Decision workflow

The selected model was registered in Model Manager and connected to Intelligent Decisioning. The flow applies model scoring before assigning an approval outcome through business rules.

Policy candidates were evaluated using approval volume, observed defaults among approved loans, and illustrative financial scenarios. Exact thresholds, financial formulas, and policy comparisons remain private during the competition.

## Output validation

The scoring review checked application coverage and matched records by identifier. Model probabilities were compared between model-only and completed-flow outputs, and final approval assignments were checked against the saved rule.

Public scoring covered all 100,000 applications. Local Python checks confirmed the submission format, unique identifiers, binary approval values, and agreement with an independently exported application list. The implementation of these checks remains in the private technical repository.

## Limitations

The validation cohort informed both model and policy selection, so its metrics are not an independent final test. Probability calibration and borrower-group fairness have not been assessed. Financial comparisons use hypothetical assumptions, and competition scores do not represent realized bank profit.

This repository describes the completed workflow and selected results. It is not a runnable model-training package. The expanded post-competition release will include permitted implementation details and identify any remaining reproduction requirements.
