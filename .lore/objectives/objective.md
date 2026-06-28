Where current code is a bit blurry

 Right now, main.py manually constructs ChunkEmbedding directly inside process_chunk.

 That is okay for a prototype, but it mixes responsibilities:

 ```text
   chunk processing
   hashing
   heading extraction
   embedding
   database row construction
 ```

 Eventually better:

 ```text
   process_chunk
     -> create domain Chunk
     -> embed Chunk.content
     -> map to ChunkEmbeddingRow
     -> declare row
 ```

 ────────────────────────────────────────────────────────────────────────────────

 Important teaching distinction

 Domain object

 ```text
   Chunk
 ```

 Answers:

 │ What is the knowledge unit?

 Storage object

 ```text
   ChunkEmbeddingRow
 ```

 Answers:

 │ How is that knowledge unit stored and searched?

 Query result object

 Later you might also have:

 ```text
   SearchResult
 ```

 Answers:

 │ What do we return to the user?

 Example:

 ```python
   @dataclass(frozen=True)
   class SearchResult:
       source_id: str
       heading_path: str
       content: str
       score: float
       metadata: dict[str, str]
 ```

 So you can have:

 ```text
   Chunk              core/domain
   ChunkEmbeddingRow  index/storage
   SearchResult       query/output
 ```

 All related. Not duplicates. Different layers.

 ────────────────────────────────────────────────────────────────────────────────

 Best next design update

 I would not delete ChunkEmbedding.

 I would rename it mentally or later in code to:

 ```text
   ChunkEmbeddingRow
 ```

 Then make this rule:

 ```text
   core/models.py has pure Loreweaver concepts
   index/schema.py has Postgres/CocoIndex row schemas
   query/search.py has query result shapes
 ```

 That will keep the code clean as the project grows.