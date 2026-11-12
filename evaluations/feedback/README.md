# Feedback evaluation fixtures

**Synthetic only.** These public records never represent real engineering work, reviewers, or actual production success.

- `synthetic-labels.json`: fixed, 36 synthetic tasks, grouped to avoid group leakage between development and validation.
- `synthetic-baseline-predictions.json`: deliberately imperfect candidate for regression comparison.
- `synthetic-candidate-predictions.json`: expected policy-level actions for smoke testing.

Real task outcomes and independently sealed holdout labels **must not** be committed here. Store them in a private, access-controlled location and pass their local file paths to `python -m src.feedback_eval` in an authorized environment. An evaluation cannot invent labels from Agent predictions; it must be human-labeled using verifiable evidence.
