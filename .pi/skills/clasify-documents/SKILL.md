---
name: clasify-documents
description: Classify documents/files and choose an appropriate chunking strategy for indexing, retrieval, or RAG pipelines. Use when deciding whether to chunk by headings, sections, paragraphs, fixed size, code symbols, parent-child relationships, or semantic boundaries.
---

# Classify Documents for Chunking Strategy

Use this guide to inspect a document or file collection and choose the simplest chunking strategy that preserves meaning, supports metadata filters, and returns useful context.

## 1. First classify the file type

- **Markdown / docs / README / runbooks**
  - Prefer heading-aware strategies.
  - Look for `#`, `##`, `###` structure.
- **Plain prose / notes / articles**
  - Prefer paragraph or section-based chunks.
  - Use fixed-size fallback if structure is weak.
- **Code files**
  - Prefer syntax-aware chunks: functions, classes, modules, resources.
- **Config / IaC files**
  - Prefer resource/block-aware chunks.
  - Examples: Terraform resources, YAML jobs, Kubernetes objects.
- **Logs / transcripts / streams**
  - Prefer time/window/message-based chunks.
- **Tables / CSV / structured records**
  - Prefer row/group-based chunks, not arbitrary text windows.

## 2. Check document structure quality

- **Strong structure**
  - Clear headings, sections, symbols, records, or blocks.
  - Choose structure-aware chunking.
- **Weak structure**
  - Long text with few headings or inconsistent formatting.
  - Choose paragraph chunks or fixed-size sliding windows.
- **Mixed structure**
  - Use hierarchy: split by available structure first, then size-split inside large sections.
- **No structure**
  - Use fixed-size chunks with overlap, or semantic chunking if quality matters more than cost.

## 3. Match chunking strategy to retrieval goal

- **User wants exact section filtering**
  - Use heading/section-first chunking.
  - Store `heading_path`, `section_start`, and `section_end`.
- **User wants broad semantic search**
  - Use fixed-size or paragraph chunks with overlap.
- **User wants full context in answers**
  - Use parent-child chunking: search small chunks, display parent section.
- **User searches code or infrastructure**
  - Use syntax/block-aware chunking.
- **User searches by metadata**
  - Store source path, file type, headings, dates, owner, tags, and stable IDs.

## 4. Choose a default by content type

- **Markdown documentation**
  - Default: section-first, then size-split inside each section.
- **Small Markdown files**
  - One chunk per section may be enough.
- **Large Markdown sections**
  - Split within section using size limits and overlap.
- **General text**
  - Paragraph chunks, then size-split long paragraphs if needed.
- **Code**
  - Chunk by function/class/module.
- **Terraform / HCL**
  - Chunk by resource, module, variable, output, locals block.
- **YAML**
  - Chunk by top-level object, job, service, or manifest.
- **Logs**
  - Chunk by time window, request ID, trace ID, or event group.

## 5. Warning signs for the wrong strategy

- **Chunks cross unrelated headings**
  - Switch from fixed-size to section-first chunking.
- **Search results are too tiny to understand**
  - Add parent-child display or larger chunks.
- **Search results are huge and unfocused**
  - Split sections further or reduce chunk size.
- **Metadata filters return surprising content**
  - Ensure chunks do not cross metadata boundaries.
- **Many duplicate-looking results**
  - Reduce overlap or deduplicate by parent section.
- **Relevant exact terms are missed**
  - Add keyword/hybrid search in addition to embeddings.

## 6. Metadata to store during classification

- `source_path`
- `file_type`
- `heading_path` or symbol path
- `section_start` / `section_end`
- `chunk_start` / `chunk_end`
- `chunk_index`
- `content_hash`
- `file_modified_at`
- Optional: `parent_id`, `section_id`, `language`, `tags`, `owner`

## 7. Recommended decision flow

- Ask: does the file have reliable semantic boundaries?
  - If yes, split by those boundaries first.
  - If no, use paragraph or fixed-size chunks.
- Ask: can a boundary unit be too large?
  - If yes, split inside it by size.
- Ask: will users filter by source, heading, symbol, or date?
  - If yes, never let chunks cross those boundaries.
- Ask: do users need concise retrieval or full context?
  - Concise: return chunks.
  - Full context: return parent sections.

## 8. Practical defaults

- Start simple.
- Prefer deterministic chunking over LLM-based chunking unless needed.
- Use section-first plus size-split for Markdown docs.
- Use syntax-aware chunking for code and infrastructure files.
- Use parent-child retrieval when display quality matters.
- Revisit chunking after testing real queries, not before.
