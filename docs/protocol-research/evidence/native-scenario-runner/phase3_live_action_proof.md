# Card 74 Phase 3 step 2 — live action proof (2026-06-13)

Native scenario action registry drove a REAL warehouse mutation live, no Vanessa, then reverted.

- Capture replayed: `mut-warehouse-donotuse-20260610` (open-list/select-row/open-card + write).
- Renderers built by `qa_mcp.scenario.replay.build_action_renderers` from the action scenario
  (ordinals 8/15/19), driven via `run_replay_with_renderers` against a fresh TestClient (15381).
- COM snapshot/verify/restore of `Справочник.Склады["Средний"].НеИспользовать`:
  - before = False
  - after  = **True**  → the replay APPLIED the mutation (flag flipped) — the action executed
    end-to-end through the Python manager.
  - restored = False (independent COM read confirms data returned to baseline). SAFE.

Caveat: the full-capture replay is slow (hundreds of frames × per-frame idle timeouts) and was
interrupted before clean completion, so there is no zero-divergence report this run; the
meaningful write applied before interruption. Perf/robustness follow-up: thin poll frames
(keep_every), and/or replay through the proxy harness (port 15382) as the accepted-member probes
do, and/or skip past the write for a nav-only completion. Correctness of the action path is
demonstrated (a real mutation landed via the registry-driven native replay).
