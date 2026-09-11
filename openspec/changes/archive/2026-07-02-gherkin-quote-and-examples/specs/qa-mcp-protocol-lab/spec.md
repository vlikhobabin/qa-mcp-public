## ADDED Requirements

### Requirement: Gherkin quoted arguments preserve embedded opposite quotes
The Gherkin transpiler SHALL parse single-quoted and double-quoted step arguments with matching delimiters and MUST
preserve the other quote character inside the captured value.

#### Scenario: Single-quoted input contains a double quote
- **WHEN** a feature step enters the value `'ООО "Ромашка"'`
- **THEN** the transpiled `input_text` step has `new_value == 'ООО "Ромашка"'`
- **AND** the step is not reported as unmapped.

#### Scenario: Double-quoted input contains a single quote
- **WHEN** a feature step enters the value `"owner's value"`
- **THEN** the transpiled step preserves the embedded single quote in the captured value.

### Requirement: Gherkin examples and tables preserve intended rows
The Gherkin parser SHALL expand each `Примеры:` or `Examples:` block from its own header and data rows, and SHALL treat
escaped `\|` sequences inside table cells as literal pipe characters rather than cell separators.

#### Scenario: Multiple examples blocks skip each header
- **WHEN** a scenario outline contains two examples blocks
- **THEN** expansion creates one scenario per data row only
- **AND** no scenario is generated from a repeated header row.

#### Scenario: Escaped pipe remains inside one table cell
- **WHEN** a DataTable row contains `a\|b` inside a cell
- **THEN** the parsed table cell value is `a|b`
- **AND** the value is not split into adjacent cells.

### Requirement: Unsupported Gherkin docstrings are explicit
The Gherkin parser SHALL not silently execute triple-quoted docstring content as ordinary steps. Unsupported docstring
blocks MUST produce an unmapped diagnostic that identifies the unsupported docstring input.

#### Scenario: Triple-quoted docstring is reported unsupported
- **WHEN** a scenario contains a `"""` docstring block
- **THEN** the transpile result includes an unmapped docstring diagnostic
- **AND** the docstring payload lines are not mapped as executable runner steps.
