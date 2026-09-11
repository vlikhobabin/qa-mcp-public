# Protocol Corpus Repeatability Report

- Generated at: `2026-06-02T17:19:14Z`
- Input count: `2`
- Case count: `10`
- Classification counts: `{"incomplete_hash": 2, "non_accepted": 2, "unsupported_gap": 6}`
- Stable case ids: `[]`
- Gap case ids: `["button-family-readonly-gap", "checkbox-family-readonly-gap", "commandbar-family-readonly-gap", "form-element-details", "label-family-readonly-gap", "page-family-readonly-gap", "table-family-readonly-gap", "typed-input-field-readonly"]`
- Normalizer investigation candidates: `[]`

## Inputs

| index | capture ids | cases | path |
| --- | --- | --- | --- |
| 0 | ["20260602-193802"] | 10 | docs/protocol-research/evidence/corpus/20260602-193802-expanded-readonly/corpus_cases.jsonl |
| 1 | ["20260602-195407"] | 10 | docs/protocol-research/evidence/corpus/20260602-195407-expanded-readonly/corpus_cases.jsonl |

## Cases

| case | classification | captures | replay | before hashes | after hashes | request bytes | response bytes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| active-form-context | non_accepted | 20260602-193802, 20260602-195407 | ["pending"] | ["a80b3b8e82bb10b7a8045a34ba1119ffc91b7b291f2384daa7bf1aee92218c55", "c63209d269d87024ba6131644ac0239e170f547ae512fbf96511f586f823ec99"] | ["e43ce48cedae7b6df936a2e0db71e1afd93d32df8e0767d8750f4ff176231573"] | [801] | [2337] |
| active-window-context | non_accepted | 20260602-193802, 20260602-195407 | ["pending"] | ["5193c81c798e0de0327c0dd91e235ae8736391ba0299b825ff14a219d8090082", "af7098e700c1c522c4222c5524bfaa9a5a095a09b2053f4723f00f71e1d0ae53"] | ["62e03d159d511173297af9ab9a287d9ab21f788a82ab840d97c639e726ad80ad"] | [400] | [995] |
| button-family-readonly-gap | unsupported_gap | 20260602-193802, 20260602-195407 | ["unsupported"] | [null] | [null] | [0] | [0] |
| checkbox-family-readonly-gap | unsupported_gap | 20260602-193802, 20260602-195407 | ["unsupported"] | [null] | [null] | [0] | [0] |
| commandbar-family-readonly-gap | unsupported_gap | 20260602-193802, 20260602-195407 | ["unsupported"] | [null] | [null] | [0] | [0] |
| form-element-details | incomplete_hash | 20260602-193802, 20260602-195407 | ["pending"] | [null] | [null] | [0] | [0] |
| label-family-readonly-gap | unsupported_gap | 20260602-193802, 20260602-195407 | ["unsupported"] | [null] | [null] | [0] | [0] |
| page-family-readonly-gap | unsupported_gap | 20260602-193802, 20260602-195407 | ["unsupported"] | [null] | [null] | [0] | [0] |
| table-family-readonly-gap | unsupported_gap | 20260602-193802, 20260602-195407 | ["unsupported"] | [null] | [null] | [0] | [0] |
| typed-input-field-readonly | incomplete_hash | 20260602-193802, 20260602-195407 | ["pending"] | [null] | [null] | [0] | [0] |

## Notes

- The report compares reviewed corpus rows only; raw traffic remains under ignored runtime paths.
- `stable` requires the same non-null normalized hash in every input and accepted replay/probe status.
- `incomplete_hash` marks repeated matrix rows whose reviewed evidence exists but one or more inputs lack captured request frames.
- `unsupported_gap` rows are fixture coverage gaps, not protocol mappings.
