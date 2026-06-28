# configured root + include/exclude patterns -> SourceArtifact objects

Target behavior

 Given:

 ```python
   adapter = LocalMarkdownSourceAdapter(
       root=Path("."),
       include_patterns=["README.md", "docs/**/*.md", ".lore/**/*.md"],
       exclude_patterns=[".venv/**", "cocoindex.db/**"],
   )
 ```

 Calling:

 ```python
   adapter.collect()
 ```

 should yield artifacts like:

 ```python
   SourceArtifact(
       source_kind="local_file",
       source_id="README.md",
       source_path="README.md",
       content="# Loreweaver\n...",
       metadata={...},
   )

 Hints

 Use:

 ```python
   Path.rglob("*")
 ```

 or start simpler with only include patterns:

 ```python
   for pattern in include_patterns:
       for path in root.glob(pattern):
           ...
 ```

 For each path:

 ```python
   if path.is_file():
       content = path.read_text(encoding="utf-8")
 ```

 For stable IDs:

 ```python
   relative_path = path.relative_to(root).as_posix()
 ```

 Then:

 ```python
   source_id = relative_path
   source_path = relative_path
 ```

 Best practice

 Keep the first version boring:

 - only text files
 - UTF-8 only
 - skip unreadable files
 - no binary detection yet
 - no GitHub yet
 - no CocoIndex yet

 Once this adapter works, make a second example:

 ```text
   examples/local_files_pipeline.py
 ```

 that uses:

 ```text
   LocalMarkdownSourceAdapter
   FakeClassifier
   FakeTransformer
   PrintingIndexer
 ```