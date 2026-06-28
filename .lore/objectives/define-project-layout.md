 A good extensible Loreweaver structure should separate domain concepts from infrastructure details.

 Core idea:

 ```text
   Loreweaver should not care whether knowledge came from files, GitHub, web docs, or an API.
   It should receive normalized artifacts and process them through the same pipeline.
 ```

 High-level architecture

 ```text
   sources -> classification -> transforms -> indexing -> query/check
 ```

 Or more domain-specific:

 ```text
   raw source
     -> SourceAdapter
     -> Document
     -> Classifier
     -> Transformer
     -> Chunk
     -> Claim
     -> Index
     -> Query / Consistency Check
 ```

 ────────────────────────────────────────────────────────────────────────────────

 Recommended project layout

 ```text
   src/loreweaver/
     cli.py
     config.py
     project.py

     core/
       __init__.py
       models.py
       interfaces.py
       pipeline.py

     sources/
       __init__.py
       local_files.py
       github_issues.py
       github_pull_requests.py
       web_docs.py

     classification/
       __init__.py
       classifier.py
       rules.py
       formats.py
       roles.py

     transforms/
       __init__.py
       markdown.py
       code.py
       github.py
       chunking.py
       metadata.py

     claims/
       __init__.py
       extractor.py
       evidence.py

     index/
       __init__.py
       postgres.py
       embeddings.py
       cocoindex_app.py

     query/
       __init__.py
       search.py
       sql.py
       formatters.py

     checks/
       __init__.py
       consistency.py
       contradictions.py
       impact.py
       reports.py
 ```

 ────────────────────────────────────────────────────────────────────────────────

 Key separation of concerns

 core/

 This is the most important package.

 It should contain stable domain types and interfaces.

 Example concepts:

 ```text
   SourceArtifact
   Document
   Chunk
   Claim
   Evidence
   Classification
 ```

 And interfaces like:

 ```text
   SourceAdapter
   Classifier
   Transformer
   Indexer
   QueryEngine
   ConsistencyChecker
 ```

 Teaching point:

 │ core/ should not import Postgres, GitHub, CocoIndex, or CLI code.

 That keeps your domain model clean.

 ────────────────────────────────────────────────────────────────────────────────

 sources/

 This package collects raw input.

 Examples:

 ```text
   local files
   GitHub issues
   GitHub PRs
   web docs
 ```

 Each source adapter should produce the same kind of object:

 ```text
   SourceArtifact
 ```

 So later the pipeline does not care where it came from.

 Good pattern:

 ```text
   Adapter Pattern
 ```

 Because every source has a different API, but Loreweaver wants one common interface.

 ────────────────────────────────────────────────────────────────────────────────

 classification/

 This decides:

 ```text
   source_kind
   content_role
   content_format
 ```

 Example:

 ```text
   source_kind: local_file
   content_role: objective
   content_format: markdown
 ```

 Useful patterns:

 ```text
   Strategy Pattern
   Chain of Responsibility
 ```

 Why?

 Classification can happen in ordered steps:

 ```text
   manual metadata
   config rules
   path rules
   extension rules
   content sniffing
   unknown
 ```

 That is a chain.

 ────────────────────────────────────────────────────────────────────────────────

 transforms/

 This turns classified documents into normalized text, metadata, and chunks.

 Examples:

 ```text
   Markdown -> heading-aware chunks
   Python -> code-aware chunks
   GitHub issue -> title/body/comments document
 ```

 Useful pattern:

 ```text
   Strategy Pattern
 ```

 Because each format can have its own transformer.

 ────────────────────────────────────────────────────────────────────────────────

 claims/

 This is Loreweaver’s future core.

 It turns chunks into knowledge claims:

 ```text
   "The project uses Postgres with pgvector."
 ```

 Each claim should link back to evidence:

 ```text
   claim -> chunk -> source document
 ```

 Useful patterns:

 ```text
   Factory Method
   Strategy
 ```

 Different claim extractors may exist:

 ```text
   rule-based extractor
   LLM extractor
   manual extractor
 ```

 ────────────────────────────────────────────────────────────────────────────────

 index/

 This stores and retrieves data.

 Examples:

 ```text
   Postgres
   pgvector
   CocoIndex
   embeddings
 ```

 Important rule:

 │ Postgres-specific code should stay here, not leak into domain models.

 Useful pattern:

 ```text
   Repository Pattern
 ```

 Your app asks:

 ```python
   claim_repository.save(claim)
 ```

 not:

 ```python
   asyncpg.execute(...)
 ```

 everywhere.

 ────────────────────────────────────────────────────────────────────────────────

 query/

 This is for user-facing retrieval.

 Examples:

 ```text
   semantic search
   SQL filters
   formatting results
 ```

 Keep query formatting separate from query execution.

 Why?

 Later you may output:

 ```text
   terminal text
   Markdown report
   JSON
   GitHub comment
 ```

 Useful pattern:

 ```text
   Presenter / Formatter
 ```

 ────────────────────────────────────────────────────────────────────────────────

 checks/

 This is where future consistency checking lives.

 Questions:

 ```text
   Does this proposal contradict an ADR?
   What breaks if this requirement changes?
   Does this fit the mission?
 ```

 Useful patterns:

 ```text
   Strategy Pattern
   Specification Pattern
 ```

 Each check can be its own object:

 ```text
   AdrContradictionCheck
   TechStackCheck
   MissionAlignmentCheck
   DuplicateFeatureCheck
 ```

 ────────────────────────────────────────────────────────────────────────────────

 GOF patterns that fit Loreweaver

 1. Adapter

 Use for sources.

 ```text
   GitHub API -> SourceArtifact
   Local file -> SourceArtifact
   Web page -> SourceArtifact
 ```

 2. Strategy

 Use for transform/classification behavior.

 ```text
   MarkdownTransformer
   PythonTransformer
   GithubIssueTransformer
 ```

 3. Chain of Responsibility

 Use for classification.

 ```text
   frontmatter -> config rule -> path rule -> extension rule -> sniffing -> unknown
 ```

 4. Factory Method

 Use to select the right transformer.

 ```text
   format=markdown -> MarkdownTransformer
   format=python -> CodeTransformer
 ```

 5. Repository

 Use for persistence.

 ```text
   ChunkRepository
   ClaimRepository
   SourceRepository
 ```

 6. Template Method

 Use for pipeline flow.

 The pipeline steps stay the same:

 ```text
   load -> classify -> transform -> index
 ```

 But individual steps can vary.

 ────────────────────────────────────────────────────────────────────────────────

 Best next design task

 Before coding folders, define the core interfaces on paper:

 ```python
   class SourceAdapter:
       def collect(self) -> Iterable[SourceArtifact]: ...

   class Classifier:
       def classify(self, artifact: SourceArtifact) -> Classification: ...

   class Transformer:
       def transform(self, document: Document) -> Iterable[Chunk]: ...

   class Indexer:
       def index(self, chunks: Iterable[Chunk]) -> None: ...
 ```

 Do not implement them yet. Just decide the shapes.

 That gives the project extensibility without overbuilding.