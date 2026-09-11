## Context

`src/qa_mcp/scenario/gherkin.py` is the single source for parsing `.feature` text into runner `Step` objects. The
defects in this change are pure parser defects: they happen before any TestClient launch, protocol replay, live form
access or capture evidence is involved.

The current `_q()` helper accepts either quote as a terminator, so a single-quoted value containing `"` is truncated.
The outline parser stores all examples rows in one list, so a second `Примеры:` header is interpreted as data. The table
splitter uses raw `str.split("|")`, so escaped pipes are treated as cell separators. Triple-quoted docstrings are not
part of the supported runner input; they need a deterministic parser outcome instead of accidental step parsing.

## Goals / Non-Goals

**Goals:**

- Preserve quoted step arguments that contain the other quote character.
- Expand every examples block from its own header row and data rows.
- Preserve escaped pipes in Gherkin table cells.
- Make triple-quoted docstrings explicit unsupported input with an unmapped diagnostic.
- Verify the behavior offline with parser/transpiler tests.

**Non-Goals:**

- No live TestClient execution.
- No new Gherkin execution semantics for docstring payloads.
- No protocol capture, replay, dynamic-field or runtime cleanup changes.

## Decisions

- Replace the generic quoted pattern with matching-delimiter alternatives. This keeps the regex registry local and
  avoids introducing a full parser dependency for a small, testable defect.
- Track examples as independent blocks. `_expand_outline` can then skip each block header and append only data rows,
  preserving existing single-block behavior while fixing repeated examples.
- Split table rows with a tiny escape-aware scanner. This is enough for `\|` without changing the DataTable payload
  contract used by existing tests.
- Treat docstrings as unsupported parser content and report the docstring block as unmapped. Adding executable
  pystring semantics would require runner/model design outside this correctness fix.

## Risks / Trade-offs

- Existing malformed feature text that relied on mismatched quotes may become unmapped. This is intentional fail-closed
  behavior; the tests cover valid single/double quoted values.
- Escaped table-cell handling remains deliberately narrow: only `\|` is decoded to a literal pipe. Other Gherkin escape
  forms are out of scope until a concrete feature needs them.
- Docstrings are still unsupported. The residual risk is visible because the transpile result records an unmapped line
  instead of silently treating the content as steps.
