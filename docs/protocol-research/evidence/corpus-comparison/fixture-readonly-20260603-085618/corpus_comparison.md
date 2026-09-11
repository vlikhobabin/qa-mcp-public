# Protocol Corpus Repeatability Report

- Generated at: `2026-06-03T06:01:33Z`
- Input count: `1`
- Case count: `6`
- Classification counts: `{"incomplete_hash": 6}`
- Stable case ids: `[]`
- Accepted case ids: `[]`
- Gap case ids: `["fixture-button-readonly", "fixture-checkbox-readonly", "fixture-commandbar-readonly", "fixture-label-readonly", "fixture-page-readonly", "fixture-table-readonly"]`
- Normalizer investigation candidates: `[]`

## Inputs

| index | capture ids | cases | path |
| --- | --- | --- | --- |
| 0 | ["20260603-085618"] | 6 | docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/corpus_cases.jsonl |

## Cases

| case | classification | captures | row replay | effective replay | probe evidence | unresolved | before hashes | after hashes | request bytes | response bytes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixture-button-readonly | incomplete_hash | 20260603-085618 | ["pending"] | ["pending"] | [] | [] | [null] | [null] | [0] | [0] |
| fixture-checkbox-readonly | incomplete_hash | 20260603-085618 | ["pending"] | ["pending"] | [] | [] | [null] | [null] | [0] | [0] |
| fixture-commandbar-readonly | incomplete_hash | 20260603-085618 | ["pending"] | ["pending"] | [] | [] | [null] | [null] | [0] | [0] |
| fixture-label-readonly | incomplete_hash | 20260603-085618 | ["pending"] | ["pending"] | [] | [] | [null] | [null] | [0] | [0] |
| fixture-page-readonly | incomplete_hash | 20260603-085618 | ["pending"] | ["pending"] | [] | [] | [null] | [null] | [0] | [0] |
| fixture-table-readonly | incomplete_hash | 20260603-085618 | ["pending"] | ["pending"] | [] | [] | [null] | [null] | [0] | [0] |

## Notes

- The report compares reviewed corpus rows only; raw traffic remains under ignored runtime paths.
- `stable` requires the same non-null normalized hash in every input and accepted replay/probe status.
- `effective replay` includes compact direct-probe evidence supplied to the comparison.
- `incomplete_hash` marks repeated matrix rows whose reviewed evidence exists but one or more inputs lack captured request frames.
- `unsupported_gap` rows are fixture coverage gaps, not protocol mappings.
