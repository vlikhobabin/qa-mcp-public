# Подключить qa-mcp как полноценный ChangeRail consumer

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- ChangeRail consumer inventory 2026-07-13.
- `/opt/changerail/docs/consumer-adoption-runbook.md`
- `/opt/changerail/docs/wiring-discovery.md`

## Summary
`qa-mcp` должен запускать единый `$changerail-*`/`$chrl-*` workflow прямо из
репозитория. Сейчас Claude и Codex используют старый OPSX wiring, OpenSpec
skills указывают на отсутствующий `/opt/opsx`, helper wrappers отсутствуют, а
consumer verifier проходит только 9/43 проверки.

Полно-провайдерные `.mcp.json` и `.codex/config.toml` являются локальными
generated profiles и остаются ignored по политике qa-mcp. Change добавляет им
локальный filesystem scope для gate, но не публикует machine-specific provider
profile. Коммитируемая часть ограничена public-safe wiring и документацией.

## Acceptance
- `.codex/skills/changerail-*`, `.codex/skills/chrl-*` и
  `.codex/skills/openspec-*` resolve в `/opt/changerail/skills/*`.
- Старые default-ссылки на `/opt/opsx` и `opsx-*` удалены из ChangeRail-owned wiring.
- `.claude/skills`, `.claude/commands/changerail` и `.claude/commands/chrl`
  resolve в `/opt/changerail`.
- `bin/openspec`, `bin/changerail-review-verdict` и `bin/verify-project`
  resolve в `/opt/changerail/bin/*`.
- `AGENTS.md` и board README фиксируют ChangeRail flow и boundary между
  ChangeRail core, AI1C domain overlays и qa-mcp project skills.
- Runtime/auth ignore policy проходит fail-closed verifier и не раскрывает
  локальные full-provider profiles.
- `/opt/changerail/bin/verify-project /opt/ai-dev-suite-for-1c/qa-mcp`
  проходит 43/43.

## Change 1: `adopt-changerail-consumer-wiring`

Replace obsolete generic workflow links with canonical ChangeRail surfaces,
preserve project/domain skill ownership, align local profile and ignore policy,
and prove the complete consumer contract.

### OpenSpec
- `openspec/changes/archive/2026-07-13-adopt-changerail-consumer-wiring/`

### Verify
- `/opt/changerail/bin/verify-project /opt/ai-dev-suite-for-1c/qa-mcp`
- `python3 -m json.tool .mcp.json`
- `python3 -c 'import tomllib; tomllib.load(open(".codex/config.toml", "rb"))'`
- `./bin/openspec validate --all --strict --no-interactive`
- alternate-index whitespace gate over manifest paths
- `git status --short`

## OpenSpec Mapping
- Change 1 -> `adopt-changerail-consumer-wiring` (archived)

## Archive
- `openspec/changes/archive/2026-07-13-adopt-changerail-consumer-wiring/`

## Related
- `/opt/changerail/docs/consumer-adoption-runbook.md`
- `.codex/skills/`
- `.claude/`
- `bin/`
- `.gitignore`
- `AGENTS.md`
- `openspec/board/README.md`

## Result
Implemented and verified: ChangeRail consumer gate passes 43/43, strict
OpenSpec validation passes 14/14, both ignored local profiles parse with the
exact filesystem pin, and the alternate index covers only the manifest payload
without changing the real index. The separate host-agent card remains excluded.

Published reviewed payload as `cc6974d`; push status `pending` on `main`/`origin`.

## Next
- done

## Log
- 2026-07-13T00:00:00Z card created from ChangeRail consumer inventory.
- 2026-07-13T11:05:30Z fast-forward completed as one apply-ready change; separate host-agent version-forward-compat story excluded.
- 2026-07-13T11:07:00Z implementation completed with generic workflow links replaced, local full-provider profiles retained as ignored state, and project/domain ownership preserved.
- 2026-07-13T11:08:30Z verification passed: ChangeRail 43/43, OpenSpec 14/14, JSON/TOML parsing, manifest validation, and alternate-index whitespace/scope checks.
- 2026-07-13T11:09:30Z capability synced to `openspec/specs/changerail-consumer-wiring/spec.md`; Change 1 archived and card left in `3.inprogress` for independent review.
- 2026-07-13T11:10:30Z post-archive alternate-index gate covered every manifest path, removed the generated synced-spec EOF blank line, passed whitespace checks, and left the real index unchanged.
- 2026-07-13T11:16:40Z publish finalized card into `4.done` with commit `cc6974d` and push status `pending`.
