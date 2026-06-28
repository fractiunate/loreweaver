This is arguably the core research problem of the entire system.

Most AI systems stop at retrieval ("find the relevant document"). A reflection engine needs to perform knowledge abstraction: transforming artifacts into a common semantic representation that can be reasoned over.

Think of it as a compiler.

Engineering Artifact
        │
        ▼
Parsing
        │
        ▼
Semantic Extraction
        │
        ▼
Knowledge Objects
        │
        ▼
Knowledge Graph
        │
        ▼
Reasoning

The important step isn't embedding the document—it's extracting its meaning.

Step 1 — Decompose the artifact

Every artifact has several "layers."

Example issue

Customer synchronization fails during peak traffic.

Retries have been added three times.

Temporary fix merged.

Need better long-term solution.

Don't summarize it.

Decompose it.

Problem
Customer synchronization fails

Observed Symptom
Timeouts

Environment
Peak traffic

Existing Mitigation
Retries

History
Three previous fixes

Intent
Needs architectural solution

Now the AI has structure.

Step 2 — Identify semantic primitives

Regardless of whether the source is

source code
issue
ADR
meeting
documentation
incident

everything becomes one of a finite set of primitives.

Example taxonomy

Fact

Claim

Decision

Assumption

Constraint

Risk

Question

Goal

Capability

Dependency

Component

Actor

Process

Event

Metric

Evidence

Owner

Trade-off

Alternative

Unknown

Everything should map into these.

Example

Redis timeout

becomes

type: Problem

subject: Redis

property: latency

condition: exceeds SLA

evidence:
   Incident-124

confidence: High
Step 3 — Extract relationships

Relationships matter more than entities.

Instead of

Redis

Customer Service

Issue

extract

Customer Service

depends_on

Redis

Example

PR introduces retry logic

becomes

implements

Retry Strategy

for

Customer Synchronization

Documentation

Customer Service is stateless

becomes

claims

Customer Service

is

Stateless

Code

private Session session;

becomes

contradicts

Stateless Claim

Reflection starts here.

Step 4 — Classify certainty

Not everything has the same confidence.

Instead of

Redis causes failures.

store

statement:
Redis causes failures

confidence:
0.62

supporting evidence:
4 issues
2 incidents

contradicting evidence:
none

Knowledge should carry uncertainty.

Step 5 — Separate observation from interpretation

This is critical.

Observation

15 timeout issues.

Interpretation

Communication architecture may be brittle.

Never mix them.

Store separately.

Observation
↓

Hypothesis
↓

Evidence
↓

Confidence
Step 6 — Build canonical objects

Everything becomes one of these.

Component
Component

name:
Customer Service

owns:
Synchronization

depends_on:
Redis

Decision

Decision

title:
Introduce retries

status:
Implemented

motivation:
Reduce timeout failures

tradeoffs:
Higher latency

owner:
Platform Team

Constraint

Constraint

No downtime

reason:
Business SLA

Risk

Risk

Redis single point of failure

severity:
High

probability:
Medium

Assumption

Assumption

Traffic remains under
500 rps

Question

Question

Should retries remain
inside Customer Service?

Evidence

Evidence

Source:
Incident

Date:
2026-05-15

Supports:
Redis latency hypothesis
Step 7 — Normalize vocabulary

Humans write

customer

consumer

client

account holder

The system should understand

Canonical Entity

Customer

Likewise

authentication

login

identity

OIDC

becomes

Authentication Capability

Normalization is what makes cross-document reasoning possible.

Step 8 — Preserve provenance

Every extracted fact needs traceability.

Never store

Redis latency high.

Store

Fact

Redis latency high

derived from

Issue-312

Incident-5

Grafana Dashboard

observed

2026-06-27

Reflection requires provenance.

Step 9 — Detect contradictions

Now compare knowledge.

Documentation

Service is stateless

Code

Stores session

Result

Contradiction

Claim

Service is stateless

Evidence

Session object detected

Confidence

High
Step 10 — Generate higher-order knowledge

Only now should AI start reasoning.

Example

Knowledge Graph

Redis

↓

mentioned in

↓

23 issues

↓

linked to

↓

3 incidents

↓

fixed by

↓

17 retry PRs

↓

No ADR

The reflection engine creates

Insight

Recurring retries indicate an
implicit resilience strategy
without an explicit
architectural decision.

Notice

The insight did not exist in any document.

It emerged.

A layered extraction pipeline

Rather than a single extraction pass, I would model this as a hierarchy where each layer builds on the previous one:

                Raw Engineering Artifact
                         │
                         ▼
────────────────────────────────────────
Level 0 — Parsing
────────────────────────────────────────
Text
Code
Markdown
Diagrams
Issues
PRs

                         │
                         ▼
────────────────────────────────────────
Level 1 — Entity Extraction
────────────────────────────────────────
Components
Services
People
Repositories
APIs
Incidents
Technologies

                         │
                         ▼
────────────────────────────────────────
Level 2 — Semantic Extraction
────────────────────────────────────────
Facts
Claims
Assumptions
Constraints
Risks
Goals
Dependencies
Capabilities
Trade-offs
Questions

                         │
                         ▼
────────────────────────────────────────
Level 3 — Relationship Extraction
────────────────────────────────────────
depends_on
implements
owns
contradicts
caused_by
mitigated_by
documents
supersedes
questions
supports

                         │
                         ▼
────────────────────────────────────────
Level 4 — Reflection
────────────────────────────────────────
Contradictions
Knowledge gaps
Emerging patterns
Implicit decisions
Recurring risks
Architecture drift

                         │
                         ▼
────────────────────────────────────────
Level 5 — Intelligence
────────────────────────────────────────
Open Questions
ADR Candidates
Risk Forecasts
Scenario Models
Architectural Insights
An additional idea: use multiple specialized "lenses"

Instead of asking one model to extract everything in one pass, treat extraction as a panel of specialized analysts. Each lens produces a different semantic view of the same artifact:

Lens	Extracts
Domain	Business capabilities, bounded contexts, ubiquitous language
Architecture	Components, interfaces, dependencies, patterns, ADR implications
Operational	Incidents, SLOs, reliability risks, failure modes
Code	Classes, modules, APIs, dependencies, complexity
Security	Trust boundaries, threats, controls, compliance assumptions
Organizational	Ownership, teams, Conway's Law signals, decision makers
Knowledge	Assumptions, unknowns, contradictions, missing documentation

You then merge these into a unified knowledge object with provenance and confidence. This "multi-lens semantic extraction" is far more robust than a single generic extraction prompt and aligns well with the reflection engine you've been designing. It also creates a foundation for richer reasoning later, because each insight can be traced back to the specific evidence and analytical lens that produced it.


Use CocoIndex as the incremental extraction layer:

docs/issues/code snippets
        ↓
CocoIndex source
        ↓
LLM structured extraction
        ↓
semantic objects
        ↓
SQLite / Neo4j / Postgres
        ↓
questions, risks, ADR candidates

CocoIndex fits this because it is built for incremental AI context pipelines: source data changes, only the changed parts are reprocessed, and lineage is preserved.

Smallest useful example

Start with local Markdown files → extracted meaning → JSON/SQLite.

1. Project setup
mkdir meaning-index
cd meaning-index

python -m venv .venv
source .venv/bin/activate

pip install -U cocoindex
echo "COCOINDEX_DB=./cocoindex.db" > .env
export OPENAI_API_KEY="..."

CocoIndex currently supports Python 3.11–3.13 and installs with pip install -U cocoindex.

2. Create tiny source documents
mkdir knowledge

knowledge/issue-001.md

# Issue 001

Customer synchronization fails during peak traffic.

Retries were added three times, but incidents still occur.

Need a long-term solution.

knowledge/adr-001.md

# ADR 001

Customer Service communicates synchronously with Payment Service.

This was chosen because it was simple to implement.

Consequence: Customer requests depend on Payment Service availability.

knowledge/code-note.md

# Code note

Customer Service now has retry logic around PaymentClient.syncCustomer().

The retry count is 3.
3. Define the extracted meaning schema

For the MWE, keep the ontology small:

from dataclasses import dataclass

@dataclass
class Meaning:
    artifact_type: str
    summary: str
    components: list[str]
    facts: list[str]
    assumptions: list[str]
    decisions: list[str]
    risks: list[str]
    open_questions: list[str]
4. CocoIndex flow idea

Adapt CocoIndex’s knowledge-graph pattern: their example reads documents, splits them, uses ExtractByLlm, maps structured objects, and exports them to a graph store.

Conceptually your main.py should do this:

import cocoindex
from dataclasses import dataclass

@dataclass
class Meaning:
    artifact_type: str
    summary: str
    components: list[str]
    facts: list[str]
    assumptions: list[str]
    decisions: list[str]
    risks: list[str]
    open_questions: list[str]

@cocoindex.flow_def(name="ExtractMeaning")
def extract_meaning_flow(flow_builder, data_scope):
    # 1. Read Markdown files from ./knowledge
    # 2. For each document, run ExtractByLlm(output_type=Meaning)
    # 3. Collect extracted rows
    # 4. Export to SQLite/Postgres/Neo4j
    pass

The important part is not the storage yet. The important part is that the LLM output is typed. CocoIndex’s meeting-notes example uses dataclasses such as Person, Task, and Meeting, then calls ExtractByLlm(..., output_type=Meeting).

Expected first output

For issue-001.md, you want something like:

{
  "artifact_type": "issue",
  "summary": "Customer synchronization fails during peak traffic despite repeated retry fixes.",
  "components": ["Customer synchronization"],
  "facts": [
    "Failures occur during peak traffic",
    "Retries were added three times",
    "Incidents still occur"
  ],
  "assumptions": [
    "Retries are expected to mitigate the failure"
  ],
  "decisions": [
    "Retry-based mitigation was used"
  ],
  "risks": [
    "Recurring incidents may indicate brittle synchronous communication"
  ],
  "open_questions": [
    "Why do retries not solve the underlying failure?",
    "Is the customer synchronization flow too tightly coupled?",
    "Should this become an architecture decision?"
  ]
}
Minimal architecture
./knowledge/*.md
    ↓
CocoIndex local source
    ↓
split by document or heading
    ↓
ExtractByLlm → Meaning
    ↓
meaning_objects table
    ↓
later: graph edges + reflection engine
Next smallest upgrade

After the first version works, split Meaning into separate objects:

Fact
Assumption
Decision
Risk
Question
Component
Relationship

Then move from “document → JSON” to:

Document
  ├─ contains Fact
  ├─ contains Assumption
  ├─ contains Decision
  ├─ raises Question
  └─ mentions Component

That is where “Extract Meaning” becomes a real knowledge graph.