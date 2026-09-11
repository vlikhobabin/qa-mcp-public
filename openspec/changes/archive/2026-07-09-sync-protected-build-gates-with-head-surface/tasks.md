## 1. Sync the protected-build gates with HEAD's surface

- [x] 1.1 Add `com_host.py` and `doctor.py` to `docker/compile_modules.sh` `MODULES`
- [x] 1.2 Add `com_host.py` and `doctor.py` to the `docker/Dockerfile.thin` drop loop
- [x] 1.3 Align the final-stage tool-count assertion `67` -> `68`
- [x] 1.4 Make the "no readable leaf source" gate fail loudly, naming offending modules

## 2. Verify

- [x] 2.1 `DOCKER_BUILDKIT=1 docker build -f docker/Dockerfile.thin` succeeds from HEAD
- [x] 2.2 In-image `docker/verify_protected_image.py` is green (68 tools, `.so`-only,
      bundled data encrypted+decryptable, license broker present)
- [x] 2.3 `openspec validate <change> --strict` passes
