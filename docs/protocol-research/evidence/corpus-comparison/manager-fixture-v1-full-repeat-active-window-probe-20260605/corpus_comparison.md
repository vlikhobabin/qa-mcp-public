# Protocol Corpus Repeatability Report

- Generated at: `2026-06-05T11:17:02Z`
- Input count: `2`
- Case count: `11`
- Classification counts: `{"non_accepted": 11}`
- Stable case ids: `[]`
- Accepted case ids: `[]`
- Gap case ids: `[]`
- Normalizer investigation candidates: `[]`

## Inputs

| index | capture ids | cases | path |
| --- | --- | --- | --- |
| 0 | ["20260605-live-full-readonly-bootstrap-second-boundary-guard"] | 11 | docs/protocol-research/evidence/manager-fixture-v1-live-join/20260605-live-full-readonly-bootstrap-second-boundary-guard/corpus_cases.jsonl |
| 1 | ["20260605-live-full-readonly-repeat-second-boundary-guard"] | 11 | docs/protocol-research/evidence/manager-fixture-v1-live-join/20260605-live-full-readonly-repeat-second-boundary-guard/corpus_cases.jsonl |

## Cases

| case | classification | precise reasons | provider owners | safety | captures | row replay | effective replay | action status | probe evidence | request hash evidence | unresolved | before hashes | after hashes | request bytes | response bytes | action frames | background frames | action markers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-form | non_accepted | [] | [] | ["read_only"] | 20260605-live-full-readonly-bootstrap-second-boundary-guard, 20260605-live-full-readonly-repeat-second-boundary-guard | ["pending"] | ["pending"] | [] | [] | [] | [] | ["2a92e0e66ca73618bb352263d9d8ba83e28d42c3eac64c9e3b9131e138e31cbb", "df58d4117839a7a1d0e6727ec67d87c22535279240d46f58d4e2f8b3960e4e7c"] | ["484507fd5b4399e3cee38f0da8201ca4efc6e3b5721851199effac2f1d39e973"] | [16638, 16992] | [11280, 11520] | [null] | [[]] | [[]] |
| tm-v1-active-window | non_accepted | [] | [] | ["read_only"] | 20260605-live-full-readonly-bootstrap-second-boundary-guard, 20260605-live-full-readonly-repeat-second-boundary-guard | ["pending"] | ["pending"] | [] | ["docs/protocol-research/evidence/python-manager-probe/client-fixture-v1-active-window-20260604-172832/python_manager_probe_result.json"] | [] | ["expected_response_marker_not_observed"] | ["611b3bc7fc825303f4ad638db2393843f4171cdd157b7594130c57164bd05306", "fc0e7a0dcf65bc5b7159aeff903792b73052c364602aa7ffa9fa716175840bcf"] | ["840568665427219086966de565315bdc0a0adf25d6a7030da08a70a12ade50b5"] | [99] | [212] | [null] | [[]] | [[]] |
| tm-v1-button-inert | non_accepted | [] | [] | ["read_only"] | 20260605-live-full-readonly-bootstrap-second-boundary-guard, 20260605-live-full-readonly-repeat-second-boundary-guard | ["pending"] | ["pending"] | [] | [] | [] | [] | ["679d96078cbd2fcb7bb83b4f07f3a9f131ffc6b2e66dc1a8deab64cfaead4a12", "d05201ceb1d16e2b5813813745869503b0b9db13377c996034cf98297dfb4dcb"] | ["338c9594036d6108d6965d40e421f5d319463f6f5797f3ca96382af73ce8b8da"] | [17061, 17424] | [11703, 11952] | [null] | [[]] | [[]] |
| tm-v1-checkbox-true | non_accepted | [] | [] | ["read_only"] | 20260605-live-full-readonly-bootstrap-second-boundary-guard, 20260605-live-full-readonly-repeat-second-boundary-guard | ["pending"] | ["pending"] | [] | [] | [] | [] | ["3c9114dcd08f601ad0bb4496feca9a4225faaa08885cfff010f35e35c7028ecd", "9aa9d26837d0d1142439517d0532a1a604591c59a056a2f88236b2ee4581f16c"] | ["7a6b4ee6ce323d54fc81add277f7e2071513e9ddff9f5a5af6d666bd0fdc9581"] | [17202, 17690] | [11844, 12180] | [null] | [[]] | [[]] |
| tm-v1-commandbar-main | non_accepted | [] | [] | ["read_only"] | 20260605-live-full-readonly-bootstrap-second-boundary-guard, 20260605-live-full-readonly-repeat-second-boundary-guard | ["pending"] | ["pending"] | [] | [] | [] | [] | ["a80e22794f83b07e1e596cd2cbf7f1a43f50c036798ca2488ba2cd46b2b1d984", "ad30b0493b452e87cc6a373e383a4bd112022f4d4e083fc3795e1dbb2b2465e5"] | ["d53667875717aa2a84c7c7b878d931b7fa1c41f1ef8df5e4659cabdc53f34eeb"] | [17625, 18250] | [12267, 12702] | [null] | [[]] | [[]] |
| tm-v1-field-string | non_accepted | [] | [] | ["read_only"] | 20260605-live-full-readonly-bootstrap-second-boundary-guard, 20260605-live-full-readonly-repeat-second-boundary-guard | ["pending"] | ["pending"] | [] | [] | [] | [] | ["4fce5d04088a05951e6ee41f6ea539f84693549b4af737c1a13156941d69566e", "ab9b526c274c07653bc228f5257f5e4229f0e04fc1a56e1212b2c187085d78b0"] | ["125f5761a5508acc3a071c74f3c9dafa8d892624cf2251981316a0da87f8a148"] | [16920, 17280] | [11562, 11808] | [null] | [[]] | [[]] |
| tm-v1-field-version | non_accepted | [] | [] | ["read_only"] | 20260605-live-full-readonly-bootstrap-second-boundary-guard, 20260605-live-full-readonly-repeat-second-boundary-guard | ["pending"] | ["pending"] | [] | [] | [] | [] | ["477100ea4457580140d1ace91f6fe739efb3e244d64da5fa90ed4dd959109b1c", "b53276b13970da27343a0457e434a88228472678b2493d44b216ecd14dcf6e57"] | ["ced131ff5e070b8b1ff92591b0a9acf6ba53e0d74919534cf25cfd5863a5eb44"] | [15624, 17856] | [10836, 12384] | [null] | [[]] | [[]] |
| tm-v1-form-summary | non_accepted | [] | [] | ["read_only"] | 20260605-live-full-readonly-bootstrap-second-boundary-guard, 20260605-live-full-readonly-repeat-second-boundary-guard | ["pending"] | ["pending"] | [] | [] | [] | [] | ["9e612e5afa35c98ab46d02af49e1fc564ddbfb30f07f58e8d625e9297699ca96", "cde2720d1dfaeee06a9dcbcf3d2ea48b01e12f548c6df8c445e6972a46f69457"] | ["484507fd5b4399e3cee38f0da8201ca4efc6e3b5721851199effac2f1d39e973"] | [16638, 16992] | [11280, 11520] | [null] | [[]] | [[]] |
| tm-v1-group-main | non_accepted | [] | [] | ["read_only"] | 20260605-live-full-readonly-bootstrap-second-boundary-guard, 20260605-live-full-readonly-repeat-second-boundary-guard | ["pending"] | ["pending"] | [] | [] | [] | [] | ["2c1b2c8f304254671e9875d033e7408918127887344bcf66f1938f0357a08eaf", "aa9c5dec81ee646cab0c9611f14aefb23bf3c0144c701258e1fe391b4f8a52b2"] | ["20e49acc1255b6f49f94765120c406bd11f4c6e10ab1fbe809767275844bf5d7"] | [16898, 17493] | [11502, 11907] | [null] | [[]] | [[]] |
| tm-v1-pages-main | non_accepted | [] | [] | ["read_only"] | 20260605-live-full-readonly-bootstrap-second-boundary-guard, 20260605-live-full-readonly-repeat-second-boundary-guard | ["pending"] | ["pending"] | [] | [] | [] | [] | ["582e7088cf2f81cff8052634117c0ef3591887fbea0a94e22744a7e4cbdf6db1", "7c46b963ea756fc16f9782ab6625dedc0781cac2417f61ab019685b62ae8b8dd"] | ["f5ebb93e628a09a4a28051cd18e7453390d70a25354f77907cb2f8aed33bbf20"] | [16779, 17493] | [11421, 11907] | [null] | [[]] | [[]] |
| tm-v1-table-items | non_accepted | [] | [] | ["read_only"] | 20260605-live-full-readonly-bootstrap-second-boundary-guard, 20260605-live-full-readonly-repeat-second-boundary-guard | ["pending"] | ["pending"] | [] | [] | [] | [] | ["0806e391ac8594cc27cd9947e6988ce41bea555fad4a4428d794b21bfa970dfd", "57e7c5e57f43765587a9ff1d81282a927845fc258a814336bde47b503410be41"] | ["cde75cf79d2a25d4186e70bf7a1d799a459a789a576e83f92b7d75390b060cba"] | [16920, 17400] | [11562, 11890] | [null] | [[]] | [[]] |

## Notes

- The report compares reviewed corpus rows only; raw traffic remains under ignored runtime paths.
- `stable` requires the same non-null normalized hash in every input and accepted replay/probe status.
- `effective replay` includes compact direct-probe evidence supplied to the comparison.
- Safe action classifications use `accepted`, `pending`, `unsupported`, `partial`, `timeout`, `rejected` or `blocked`.
- `precise reasons` classify evidence blockers with stable reason values for follow-up planning.
- `incomplete_hash` marks repeated matrix rows whose reviewed evidence exists but one or more inputs lack captured request frames.
- `unsupported_gap` rows are fixture coverage gaps, not protocol mappings.
