# Objective: GitHub Action / CI Mode

## Intent

Loreweaver runs once in CI with the project configuration and evaluates whether a GitHub issue or pull request is consistent with the current project knowledge.

## Desired behavior

- Load `.lore/lore.yaml`.
- Collect the relevant project sources.
- Read the issue or pull request context.
- Compare the new input against known claims, decisions, values, tech stack notes, and mission.
- Generate a report for the issue, pull request, or CI run.

## Example checks

- Does this PR contradict an ADR?
- Does this issue conflict with the project mission?
- Does this change introduce technology outside the accepted stack?
- What existing knowledge supports or challenges this proposal?

## Output

A consistency report that can be shown as:

- a GitHub Actions job summary
- a pull request comment
- an issue comment
- a generated artifact
