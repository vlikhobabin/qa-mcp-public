## 1. Establish plaintext package expectations

- [x] 1.1 Add wheel/source tests that require readable Python modules and plaintext curated JSON/JSONL assets.
- [x] 1.2 Add production-loader tests that start and load representative assets with every bundled-data key input absent.
- [x] 1.3 Inventory every protection-only dependency, script, test, environment variable, Docker stage, CI/release/bootstrap input, active spec and documentation reference.

## 2. Remove runtime encryption and compilation

- [x] 2.1 Remove `_bundled_crypto`, encrypted-file handling and bundled-data key settings/callers.
- [x] 2.2 Convert all curated asset reads and package-data declarations to the normal plaintext representation.
- [x] 2.3 Replace Nuitka/compile/strip/encrypt Docker stages with a normal readable package install.
- [x] 2.4 Remove compile, strip, encrypt and protected-image verifier helpers and their protection-only tests.
- [x] 2.5 Remove `cryptography` and lock-file entries if a post-removal dependency audit finds no remaining functional use.

## 3. Replace release and documentation gates

- [x] 3.1 Add source-visible wheel/image integrity, asset hash/parsing, import and tool-profile smokes.
- [x] 3.2 Remove active `BUNDLED_DATA_KEY*`, protected build and private-key inputs/instructions from CI, release, bootstrap and docs while preserving archived ChangeRail history.
- [x] 3.3 Document the single unprotected public package contract for standalone and downstream AI for 1C use, retain mandatory runtime security controls, and explicitly defer downstream pin/cutover evidence to OSS-09.
- [x] 3.4 Add a deterministic active-tree regression scan that rejects reintroduction of protection tooling while allowing only archived/canceled ChangeRail history and the current change's explicit migration artifacts before archive.
- [x] 3.5 Sync the replacement CI and standalone-release requirements, then remove fully retired protection capability files from the active main spec set without modifying archived specs/cards.
- [x] 3.6 Remove or rewrite the private protected-image release path; keep only source-visible artifact inputs and gates needed by the current repository, without implementing the OSS-08 public release train.

## 4. Verify unprotected delivery

- [x] 4.1 Build and inspect a clean wheel, sdist and source-visible image; prove expected readable modules/assets, manifest consistency and no data-key input.
- [x] 4.2 Run the full non-live Python suite, package/import/tool-surface tests, clean source build, container smoke, deterministic protection scan and strict OpenSpec validation.
- [x] 4.3 On the authorized Windows target, parse/install the current key-free standalone configuration and run a native TestClient read smoke with exact owned cleanup; if preflight blocks execution, retain the exact runtime-gap command and evidence. Do not claim the later OSS-05 bridge or OSS-08 release artifact as verified here.
- [x] 4.4 Record that no protocol mapping changed and therefore no new raw capture or evidence-index update is required.
- [x] 4.5 Verify the final diff contains no downstream AI for 1C pin/cutover change and records OSS-09 as that work's owner.
