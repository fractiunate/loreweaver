# Code source and transform design

## Goal

Loreweaver should support code as structured project knowledge, not only as text chunks.

For local code files, the source step should read files and produce source artifacts. The transform step should parse code into symbols and relationships such as modules, classes, functions, methods, imports, and simple call expressions.

## Pipeline placement

```text
LocalFileSourceAdapter
  -> SourceArtifact(content=raw code)
  -> Classifier(role=code, format=python)
  -> PythonCodeTransformer
  -> CodeSymbol[] + CodeRelation[]
  -> Indexer
```

## Source responsibility

Code files are still local files, so they should use the same local file source adapter as Markdown and other project files.

The source adapter should only answer:

> Where did this content come from?

It should produce:

```text
source_kind: local_file
source_id: src/loreweaver/cli.py
source_path: src/loreweaver/cli.py
content: raw file text
metadata: file metadata
```

It should not decide whether the file is code, Python, documentation, or an objective.

## Classification responsibility

Classification should decide:

```text
content_role: code
content_format: python
```

Example config rule:

```yaml
files:
  include:
    - pattern: src/**/*.py
      role: code
```

The format can be inferred from the file extension:

```text
.py -> python
```

## Transform responsibility

A Python code transformer should parse code and produce structured outputs.

For Python, start with the standard library `ast` module:

```python
import ast

tree = ast.parse(source_code)
```

Then walk the tree with:

```python
ast.NodeVisitor
```

Useful AST nodes:

| Code concept | AST node |
|---|---|
| module | file / `ast.Module` |
| class | `ast.ClassDef` |
| function | `ast.FunctionDef` |
| async function | `ast.AsyncFunctionDef` |
| method | `FunctionDef` inside `ClassDef` |
| import | `ast.Import` |
| from import | `ast.ImportFrom` |
| call expression | `ast.Call` |

## Suggested models

```python
@dataclass(frozen=True)
class CodeSymbol:
    source_id: str
    symbol_id: str
    name: str
    kind: str  # module | class | function | method
    start_line: int
    end_line: int
    parent_symbol_id: str | None
    content: str
    metadata: dict[str, str]
```

```python
@dataclass(frozen=True)
class CodeRelation:
    source_symbol_id: str
    target_symbol_id: str | None
    relation_type: str  # defines | imports | calls | inherits
    target_name: str | None
    metadata: dict[str, str]
```

## Transform result

Markdown transforms may produce chunks. Code transforms may produce symbols and relations.

To support both, the transformer interface can evolve from:

```python
Transformer -> Iterable[Chunk]
```

to:

```python
Transformer -> TransformResult
```

Example:

```python
@dataclass(frozen=True)
class TransformResult:
    chunks: list[Chunk]
    symbols: list[CodeSymbol]
    relations: list[CodeRelation]
```

Markdown can return chunks only:

```text
chunks=[...]
symbols=[]
relations=[]
```

Code can return symbols and relations:

```text
chunks=[]
symbols=[...]
relations=[...]
```

Code may later return both, using function bodies as semantic chunks while also preserving symbol relationships.

## Simple call expressions

The first code transform should not try full name resolution.

It can extract unresolved call names such as:

```text
main calls init_project
main calls update_index
main calls asyncio.run
```

Later, a resolver can link unresolved names to known symbols across the project.

## Recommended phases

### Phase 1: syntax extraction

Extract:

```text
modules
classes
functions
methods
imports
simple calls
```

No cross-file name resolution.

### Phase 2: intra-file relationships

Resolve relationships inside one file:

```text
module defines class
module defines function
class defines method
function contains call
```

### Phase 3: project-level resolution

Resolve names across files:

```text
call "init_project" -> symbol "loreweaver.init.init_project"
```

Do not start here.

## Design principle

Keep source adapters boring:

```text
source adapters read content
classifiers assign role and format
transforms produce structured knowledge
indexers persist/search structured knowledge
```

For code, this means the local file adapter reads `.py` files, while the Python code transformer turns those files into symbols and relationships.
