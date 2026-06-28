# Chunking Strategies: When Each Makes Sense

Different chunking strategies fit different retrieval goals. There is no universal best option.

## 1. Fixed-size chunks

Split text into chunks of a fixed size, often with overlap.

Best when:

- Documents are unstructured
- Headings are unreliable
- You want a simple implementation
- You mostly care about semantic similarity

Pros:

- Easy to implement
- Predictable size
- Works on almost anything

Cons:

- Can split sections awkwardly
- Chunks can cross heading boundaries
- Metadata filters become fuzzy

## 2. Heading or section-based chunks

Use Markdown headings as chunk boundaries.

Best when:

- Docs have clean headings
- Users search by section/topic
- You want filters like `--heading`
- You want readable results

Pros:

- Clean `heading_path`
- Filters behave intuitively
- Output feels like real document sections

Cons:

- Section sizes vary a lot
- Huge sections can make weak embeddings
- Tiny sections may lack context

## 3. Section-first, size-split inside section

First split by headings, then split large sections into smaller chunks.

Best when:

- You want clean metadata
- Sections may be too long
- You still need good embedding quality

Pros:

- Chunks do not cross section boundaries
- Heading filters work well
- Avoids giant embeddings

Cons:

- More code
- Need to track section offsets

This is a strong default for Markdown documentation.

## 4. Paragraph chunks

Split by blank lines or paragraphs.

Best when:

- Documents are prose-heavy
- Paragraphs are self-contained
- You want precise answers

Pros:

- Natural text units
- Readable results

Cons:

- Paragraphs can be too small
- May lose context
- Less useful for code/config docs

## 5. Semantic chunks

Split by topic or meaning, often using embeddings or an LLM.

Best when:

- Docs are messy
- Headings are poor
- Paragraphs blend topics
- Quality matters more than simplicity/cost

Pros:

- Chunks match concepts
- Often improves retrieval quality

Cons:

- More expensive
- Harder to reproduce
- More moving parts

## 6. Code-aware chunks

Split code/config by syntax-aware units.

Examples:

- One Python function per chunk
- One Terraform resource per chunk
- One YAML job per chunk

Best when indexing:

- Python files
- Terraform
- YAML
- SQL
- Config files

Pros:

- Great for code search
- Results are meaningful units
- Metadata can include symbol/resource names

Cons:

- Needs language-specific parsing
- More complex implementation

## 7. Sliding window chunks

Fixed-size chunks with overlap.

Best when:

- You do not want to miss boundary context
- Text is continuous
- Queries may refer to ideas spanning paragraphs

Pros:

- Robust
- Avoids hard boundary loss

Cons:

- Duplicates content
- Search results can be redundant
- Filters are less exact

## 8. Parent-child chunks

Embed/search small chunks, but return a larger parent section.

Flow:

```text
embed small child chunks
retrieve best child chunk
display parent section
```

Best when:

- Small chunks retrieve better
- Users need full context in results

Pros:

- Good search quality
- Good output readability

Cons:

- Need parent IDs or section offsets
- More schema complexity

## 9. Summary plus detail chunks

Store both section summaries and detailed chunks.

Best when:

- Documents are long
- You want high-level discovery and detailed answers

Flow:

```text
query -> match summary -> search details inside matched section
```

Pros:

- Handles large docs well
- Helps broad conceptual queries

Cons:

- Needs summarization
- Summaries can be wrong or stale

## 10. Metadata prefilter plus vector chunks

Filter by metadata first, then run vector ranking.

Example:

```bash
--source migration --heading cloudfront
```

Best when:

- Users know source/section/date/type
- Docs are organized
- Search space is large

Pros:

- Fast
- Predictable
- Simple

Cons:

- Metadata must be accurate
- Filters can exclude useful chunks accidentally

## Rule of thumb

```text
Markdown docs: section-first, then size-split
General text: paragraph or fixed-size sliding window
Code: syntax-aware chunks
RAG app: parent-child chunks
Small docs: one section per chunk
Messy docs: semantic chunks
```

For the current CocoIndex Markdown project, a strong next direction is:

```text
section-first + size split + parent section display
```

That gives:

- Clean `heading_path`
- Accurate filters
- Good embedding chunk size
- Readable query output
