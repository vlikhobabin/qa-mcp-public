# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T14:50:49Z`
- Run id: `tm-v1-ro-batchO2`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchO2`
- Join status counts: `{"joined": 14}`
- Accepted case ids: `["bo-deco-name", "bo-deco-title", "bo-deco-type", "bo-deco-visible", "bo-deco-enable", "bo-deco-readonly", "bo-deco-tooltip", "bo-deco-parent", "bo-deco-commandbar", "bo-deco-contextmenu", "bo-deco-children", "bo-deco-findobjects", "bo-deco-findobject", "bo-deco-fmthyperlinks"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bo-deco-name | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 16, "to": 24, "count": 9} | {"from": 17, "to": 25, "count": 9} |  | accepted_side_channel | True |
| bo-deco-title | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 27, "to": 35, "count": 9} | {"from": 28, "to": 36, "count": 9} |  | accepted_side_channel | True |
| bo-deco-type | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 38, "to": 46, "count": 9} | {"from": 39, "to": 47, "count": 9} |  | accepted_side_channel | True |
| bo-deco-visible | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 49, "to": 57, "count": 9} | {"from": 50, "to": 58, "count": 9} |  | accepted_side_channel | True |
| bo-deco-enable | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 60, "to": 68, "count": 9} | {"from": 61, "to": 69, "count": 9} |  | accepted_side_channel | True |
| bo-deco-readonly | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 71, "to": 79, "count": 9} | {"from": 72, "to": 80, "count": 9} |  | accepted_side_channel | True |
| bo-deco-tooltip | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 82, "to": 90, "count": 9} | {"from": 83, "to": 91, "count": 9} |  | accepted_side_channel | True |
| bo-deco-parent | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 93, "to": 101, "count": 9} | {"from": 94, "to": 102, "count": 9} |  | accepted_side_channel | True |
| bo-deco-commandbar | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 104, "to": 112, "count": 9} | {"from": 105, "to": 113, "count": 9} |  | accepted_side_channel | True |
| bo-deco-contextmenu | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 115, "to": 123, "count": 9} | {"from": 116, "to": 124, "count": 9} |  | accepted_side_channel | True |
| bo-deco-children | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 126, "to": 134, "count": 9} | {"from": 127, "to": 135, "count": 9} |  | accepted_side_channel | True |
| bo-deco-findobjects | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 137, "to": 145, "count": 9} | {"from": 138, "to": 146, "count": 9} |  | accepted_side_channel | True |
| bo-deco-findobject | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 148, "to": 156, "count": 9} | {"from": 149, "to": 157, "count": 9} |  | accepted_side_channel | True |
| bo-deco-fmthyperlinks | decoration_summary | decoration_summary | ok | True | joined |  | {"from": 159, "to": 167, "count": 9} | {"from": 160, "to": 168, "count": 9} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
