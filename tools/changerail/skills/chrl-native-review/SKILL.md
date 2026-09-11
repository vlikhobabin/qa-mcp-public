---
name: chrl-native-review
description: Independently review a native OpenSpec change and continue that review after its exact archive move.
---

# Native OpenSpec review

Read `$CHRL_REVIEW_CONTEXT` and `$CHRL_NATIVE_CONTEXT`, then follow the review
and verdict protocol in `tools/changerail/skills/chrl-review/SKILL.md`.
Read the context's unchanged stock `workflows.verify` methodology. Check the
proposal, delta specs, design, tasks, acceptance conditions and retained semantic sync
report against the actual implementation and canonical specs. Checked tasks,
structural validation and a sync report alone are not acceptance evidence.

In the active phase a GO is preliminary. The outer runner alone archives the
change. In the final phase continue the same independent reviewer thread, use
the retained preliminary verdict and archive paths, and assess the exact move
plus refreshed evidence. Do not look up the removed active change or repeat
the broad audit. Return a new verdict bound to the actual current fingerprint.
The initial fresh context establishes independence; continuation never gives
this reviewer implementation authority or resets accumulated usage.

Never change tracked files, sync specs, archive, perform the product floor,
stage, commit or push. A substantive remaining defect is NO-GO with concrete
closure conditions. The outer runner owns repair and later fresh review cycles.
