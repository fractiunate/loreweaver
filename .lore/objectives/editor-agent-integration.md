# Objective: Editor / Agent Integration

## Intent

Loreweaver becomes a context provider for coding agents and editors.

## Integration targets

- Native Pi tool integration
- Tool APIs for local coding agents
- MCP servers for agents that support MCP
- Editor integrations

## Desired behavior

- Provide relevant claims for the current file, task, issue, or plan.
- Surface related ADRs, project values, tech stack notes, and objectives.
- Help agents check whether proposed changes fit the existing project knowledge.
- Explain what parts of the project may need to change when requirements change.

## Example questions

- What project claims are relevant to this file?
- Does this proposed implementation contradict an ADR?
- Which objectives does this change support?
- What would break if this requirement changes?

## Principle

Loreweaver should provide traceable context, not opaque advice. Guidance should link back to claims and source evidence.
