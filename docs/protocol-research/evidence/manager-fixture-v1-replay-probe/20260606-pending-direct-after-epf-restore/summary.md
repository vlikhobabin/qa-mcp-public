# Manager Fixture V1 Pending Direct Probe After EPF Restore

- Source capture: `runtime/protocol-research/captures/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`
- Runtime probe output: `runtime/protocol-research/manager-fixture-marker-probe/20260606-pending-direct-after-epf-restore/`
- Candidate marker output: `runtime/protocol-research/manager-fixture-marker-probe/20260606-pending-direct-candidate-markers-after-epf-restore/`
- Transport status: `ok`
- Accepted with current contract: `1`
- Still blocked with current contract: `8`
- Candidate marker contracts supported: `5`

## Accepted Current Contract

| case | frames | expected marker | observed markers |
| --- | ---: | --- | --- |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.manager_frame_range.from)..130 | $(System.Collections.Specialized.OrderedDictionary.expected_marker) | $((@(System.Collections.Specialized.OrderedDictionary.observed_markers) -join ', ')) |

## Candidate Marker Evidence

| case | previous expected | candidate expected | status |
| --- | --- | --- | --- |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.previous_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.candidate_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.probe_status) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.previous_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.candidate_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.probe_status) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.previous_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.candidate_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.probe_status) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.previous_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.candidate_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.probe_status) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.previous_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.candidate_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.probe_status) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.previous_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.candidate_expected_marker) | $(System.Collections.Specialized.OrderedDictionary.probe_status) |

## Still Blocked With Current Contract

| case | frames | expected marker | observed markers |
| --- | ---: | --- | --- |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.manager_frame_range.from)..20 | $(System.Collections.Specialized.OrderedDictionary.expected_marker) | $((@(System.Collections.Specialized.OrderedDictionary.observed_markers) -join ', ')) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.manager_frame_range.from)..22 | $(System.Collections.Specialized.OrderedDictionary.expected_marker) | $((@(System.Collections.Specialized.OrderedDictionary.observed_markers) -join ', ')) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.manager_frame_range.from)..25 | $(System.Collections.Specialized.OrderedDictionary.expected_marker) | $((@(System.Collections.Specialized.OrderedDictionary.observed_markers) -join ', ')) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.manager_frame_range.from)..106 | $(System.Collections.Specialized.OrderedDictionary.expected_marker) | $((@(System.Collections.Specialized.OrderedDictionary.observed_markers) -join ', ')) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.manager_frame_range.from)..119 | $(System.Collections.Specialized.OrderedDictionary.expected_marker) | $((@(System.Collections.Specialized.OrderedDictionary.observed_markers) -join ', ')) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.manager_frame_range.from)..390 | $(System.Collections.Specialized.OrderedDictionary.expected_marker) | $((@(System.Collections.Specialized.OrderedDictionary.observed_markers) -join ', ')) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.manager_frame_range.from)..401 | $(System.Collections.Specialized.OrderedDictionary.expected_marker) | $((@(System.Collections.Specialized.OrderedDictionary.observed_markers) -join ', ')) |
| $(System.Collections.Specialized.OrderedDictionary.case_id) | $(System.Collections.Specialized.OrderedDictionary.manager_frame_range.from)..413 | $(System.Collections.Specialized.OrderedDictionary.expected_marker) | $((@(System.Collections.Specialized.OrderedDictionary.observed_markers) -join ', ')) |

Only `accepted_probe_cases` are suitable for reporter promotion. Candidate marker rows require a later evidence-gated manifest/contract correction before acceptance.
