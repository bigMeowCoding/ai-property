# Review protocol

- Inspect diff and acceptance table, not the author's self-assessment.
- For Advanced changes, run a fresh-context reviewer if supported; otherwise state that review was non-independent.
- Search for missed requirements, uncovered exception paths, incorrect contracts, security or access-control changes, runtime platform differences, regressions, and unrelated edits.
- Findings should cite file locations and observable evidence. Severity: blocker, significant, suggestion.
- Fix blockers and rerun relevant checks; never lower tests or verification standards to gain a pass.
- A passing judge + no blocker + satisfied AC or explicitly accepted manual exception is required before requesting delivery confirmation.
