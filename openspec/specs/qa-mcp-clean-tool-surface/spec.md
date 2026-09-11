# qa-mcp-clean-tool-surface Specification

## Purpose
The runtime-exposed MCP tool surface (the `tools/list` descriptions FastMCP sends to every connecting agent) is
product-facing: it accurately describes what each tool does and how to use it, while carrying no internal
research-and-development references (card numbers, Vanessa/vanessa-mcp mentions, evidence paths). Cleaning this
surface is a documentation-only change that preserves every tool's behavior, arguments and return shape.

## Requirements
### Requirement: Shipped tool descriptions are free of internal R&D references

Every tool description exposed by the qa-mcp server through `tools/list` SHALL be product-facing and MUST NOT
contain internal research-and-development references. Specifically, no tool `description` shall contain, in a
case-insensitive match, a `card <number>` token, the substring `vanessa` (covering `Vanessa` and `vanessa-mcp`),
or an `evidence/` path token. Maintenance-useful card-trace context MUST be relocated to a `#` comment above the
tool function (dev-only) rather than left in the docstring.

#### Scenario: Tool descriptions contain zero R&D tokens
- **WHEN** the registered qa-mcp tool descriptions are scanned for `card \d`, `vanessa`, or `evidence` tokens
  (case-insensitive)
- **THEN** the total match count across all tool descriptions is exactly zero

#### Scenario: An MCP client sees clean descriptions
- **WHEN** an MCP client connects to the running qa-mcp server and reads `tools/list`
- **THEN** every returned tool `description` is product-facing and contains none of the internal R&D tokens

### Requirement: Tool functional accuracy is preserved

Rewriting tool descriptions to be product-facing SHALL NOT change any tool's behavior, argument names, parameter
documentation meaning, or return shape. The rewrite is documentation-only.

#### Scenario: Tool surface is unchanged after the rewrite
- **WHEN** the server is started after the description rewrite
- **THEN** the same set of tools is registered (63 tools), each with its original name, arguments and return
  shape, and the offline test suite stays green

#### Scenario: A description still tells the agent what the tool does
- **WHEN** an agent reads any rewritten tool description
- **THEN** the description accurately states what the tool does and how to use its arguments, with no loss of the
  functional guidance an agent needs to call it correctly
