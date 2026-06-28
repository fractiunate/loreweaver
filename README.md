# Loreweaver

Loreweaver builds a living knowledge base for software projects.

It collects files, docs, issues, pull requests, decisions, and project principles, then distills them into traceable knowledge claims. As the project changes, Loreweaver keeps that knowledge up to date and helps evaluate whether new ideas, features, and plans are consistent with the current codebase, tech stack, values, and mission.

> Loreweaver turns evolving project artifacts into living knowledge, then helps keep future changes consistent with it.

## Product framing

Loreweaver is not just document search.

It is:

```text
project memory + claim extraction + consistency checking
```

The core model is:

```text
sources -> claims -> knowledge graph/index -> consistency checks -> guidance
```

## Sources

Loreweaver is designed to collect knowledge from project artifacts such as:

- files
- docs
- ADRs
- issues
- PRs
- plans
- mission statements
- tech stack notes
- project values

## What Loreweaver should help answer

Future checks include questions like:

- Does this feature contradict an ADR?
- Does this plan fit the current tech stack?
- Does this issue conflict with project values?
- Does this change duplicate existing behavior?
- Does this proposal drift from the mission?
- What existing knowledge supports or challenges this idea?

## Local setup

See [local-setup.md](local-setup.md) for the current local CocoIndex and Postgres setup instructions.
