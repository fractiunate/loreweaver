# Objective: Git Hook Integration

## Intent

Loreweaver runs during Git events to help developers catch consistency problems before changes are committed or pushed.

## Desired behavior

Support optional Git hook entry points such as:

- `pre-commit`
- `post-commit`
- `pre-push`

## Example commands

```bash
loreweaver check --staged
loreweaver update --changed
loreweaver check --branch main
```

## Example checks

- Do staged changes contradict current ADRs?
- Do changed files affect known project claims?
- Does the commit introduce a dependency or pattern outside the project values?
- Should related docs, objectives, or decisions be updated?

## Principle

Git hooks should be fast, optional, and easy to bypass when needed. Slow or LLM-heavy checks should run in CI instead.
