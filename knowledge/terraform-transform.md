# Terraform transform design

## Goal

Loreweaver should treat Terraform/OpenTofu configuration as structured infrastructure knowledge, not only as plain text.

Terraform files should become symbols and relationships that describe resources, data sources, modules, variables, outputs, providers, locals, and dependencies.

## Pipeline placement

Terraform files are still local files. The source adapter should only read them.

```text
LocalFileSourceAdapter
  -> SourceArtifact(content=raw HCL)
  -> Classifier(role=infrastructure_code, format=terraform)
  -> TerraformTransformer
  -> TerraformSymbol[] + TerraformRelation[]
  -> Indexer
```

## Source responsibility

The local file source adapter should produce artifacts like:

```text
source_kind: local_file
source_id: terraform/stacks/prod/main.tf
source_path: terraform/stacks/prod/main.tf
content: raw HCL text
metadata: file metadata
```

It should not parse Terraform and should not decide the file role or format.

## Classification responsibility

Classification should decide:

```text
content_role: infrastructure_code
content_format: terraform
```

Example config rule:

```yaml
files:
  include:
    - pattern: "**/*.tf"
      role: infrastructure_code
```

The format can be inferred from extension:

```text
.tf -> terraform
.tfvars -> terraform_variables
```

## Terraform concepts to extract

Phase 1 should focus on block-level extraction:

```text
root module / project
child modules
resources
data sources
providers
variables
outputs
locals
terraform blocks
```

Examples of symbols:

```text
module.root
module.vpc
resource.aws_instance.web
data.aws_ami.ubuntu
variable.region
local.tags
output.instance_id
provider.aws
```

## Relationships to extract

Examples:

```text
root module calls module.vpc
resource.aws_instance.web references data.aws_ami.ubuntu
resource.aws_instance.web references aws_security_group.web
output.instance_id exposes aws_instance.web.id
module.vpc receives variable cidr_block
resource.aws_instance.web depends_on aws_security_group.web
```

## Parser option

For Python, start with `python-hcl2` or `parse-hcl` for block extraction.

`python-hcl2` parses HCL2/Terraform config into Python dictionaries and is practical for extracting blocks such as:

```text
resource
data
module
variable
output
locals
provider
terraform
```

If `parse-hcl` is reliable, prefer it because it advertises dependency graphs and per-file metadata in addition to parsing.

Do not start with a custom parser.

## Suggested transform phases

### Phase 1: block extraction

Use `python-hcl2` or `parse-hcl` for block extraction.

If `parse-hcl` is reliable, prefer it because it advertises dependency graphs and metadata.

Extract the major Terraform blocks and create symbols.

No deep expression resolution yet.

Example:

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
}
```

Produces:

```text
symbol: resource.aws_instance.web
```

### Phase 2: normalized model and simple references

Add Loreweaver's own normalized model:

```text
KnowledgeSymbol
KnowledgeRelation
```

Do not let the parser's data shape leak into Loreweaver. Parser output should be adapted into Loreweaver domain models before indexing.

Then extract obvious references from expressions:

```text
var.region
local.tags
data.aws_ami.ubuntu.id
aws_security_group.web.id
module.vpc.vpc_id
```

Produces relationships such as:

```text
resource.aws_instance.web references data.aws_ami.ubuntu
resource.aws_instance.web references variable.instance_type
```

### Phase 3: dependency and module graph

Resolve:

```text
depends_on
module inputs
module outputs
provider usage
cross-module references
```

This can support impact questions such as:

```text
What breaks if this variable changes?
Which resources depend on this data source?
Which modules are affected by this output?
```

## Suggested generic models

Prefer generic symbols and relations over Terraform-only models at first.

```python
@dataclass(frozen=True)
class KnowledgeSymbol:
    source_id: str
    symbol_id: str
    name: str
    kind: str
    start_line: int | None
    end_line: int | None
    parent_symbol_id: str | None
    content: str
    metadata: dict[str, str]
```

```python
@dataclass(frozen=True)
class KnowledgeRelation:
    source_symbol_id: str
    target_symbol_id: str | None
    relation_type: str
    target_name: str | None
    metadata: dict[str, str]
```

Terraform can then use:

```text
kind = resource | data | module | variable | output | local | provider | terraform
relation_type = defines | references | depends_on | calls_module | exposes | receives
```

## Design principle

Keep Terraform support in the transform layer:

```text
source adapters read .tf files
classifiers assign infrastructure_code/terraform
transforms parse HCL into symbols and relations
indexers store/search symbols and relations
```

Do not make a separate Terraform source adapter unless Terraform is being fetched from a remote system rather than local files.
