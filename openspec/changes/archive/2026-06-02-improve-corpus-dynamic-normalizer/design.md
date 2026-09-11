## Context

The current normalizer handles the first known binary offsets and GUID text
forms. Repeated captures for a wider case matrix will reveal additional
session-specific fields. New replacements must be narrow, documented and
backed by before/after evidence so protocol semantics are not erased.

## Goals / Non-Goals

**Goals:**

- Detect and report new dynamic ranges from repeated corpus comparisons.
- Add normalizer rules only when evidence shows a value is session-specific or
  otherwise dynamic.
- Record replacement names, offsets, lengths, source classes and before/after
  hash behavior.
- Add focused offline tests for new normalizer behavior.

**Non-Goals:**

- Do not normalize whole request bodies because lengths differ.
- Do not mark a mapping accepted solely because normalization made hashes
  equal.
- Do not require EDT/meta providers for byte-level dynamic-field proof.

## Decisions

### Evidence Before Rule

Every new replacement rule should be justified by repeated captures or replay
evidence showing that the field varies while response semantics remain the
same.

Alternative considered: automatically replace all differing byte ranges. That
would create stable hashes quickly but risks hiding the command bytes that
distinguish protocol operations.

### Keep Ambiguity In Reviewed Output

If a differing range might be semantic, the analyzer should report it as
ambiguous instead of normalizing it. Ambiguous ranges should keep mappings out
of stable accepted dictionary entries until replay/probe or more captures
explain them.

## Risks / Trade-offs

- Under-normalization leaves repeated cases divergent - mitigate by retaining
  candidate ranges for the next investigation pass.
- Over-normalization can merge unrelated operations - mitigate with operation
  token preservation, response marker comparison and tests.
- Some dynamic ranges may shift with payload length - mitigate by recording
  source class and surrounding marker context, not only absolute offsets.

## Migration Plan

Existing corpus rows remain valid. New normalizer evidence can update future
rows and comparison reports; old rows should not be rewritten unless a change
explicitly regenerates reviewed evidence.
