#!/bin/sh
set -eu

usage() {
    cat <<'EOF'
Usage: tools/release/publish_self_hosted.sh --version vX.Y.Z [options]

Options:
  --release-base-url URL    Authenticated product download versions base URL.
  --staging-root DIR        Local staging root (default: .artifacts/releases/qa-mcp).
  --skip-gates              Do not run local pytest/go gates.
  --skip-build              Reuse --image-archive and --host-agent-exe instead of building.
  --image-archive PATH      Existing docker archive to stage.
  --host-agent-exe PATH     Existing qa-mcp-host-agent.exe to stage.
  --image-tag TAG           Docker image tag (default: qa-mcp-thin:<version>).
  --manifest-signing-key PATH  Minisign secret key used to sign manifest.json.
  --manifest-minisig PATH   Prebuilt detached manifest.json.minisig to stage.
  --allow-dirty             Allow tracked release files to be dirty.

Environment:
  QA_MCP_RELEASE_PYTHON  Python executable for project release helper scripts.
  QA_MCP_PUBLIC_BASE_IMAGE  Optional immutable public uv/Python base override.
  AI1C_COMPONENT_MANIFEST_VALIDATOR
                         Optional external component manifest validator.
EOF
}

die() {
    printf 'publish_self_hosted: ERROR: %s\n' "$*" >&2
    exit 1
}

info() {
    printf '[publish_self_hosted] %s\n' "$*"
}

abs_path() {
    case "$1" in
        /*) printf '%s\n' "$1" ;;
        *) printf '%s/%s\n' "$(pwd)" "$1" ;;
    esac
}

release_python_label() {
    if [ -n "${QA_MCP_RELEASE_PYTHON:-}" ]; then
        printf '%s\n' "$QA_MCP_RELEASE_PYTHON"
    elif [ -x "$ROOT/.venv/bin/python" ]; then
        printf '%s\n' "$ROOT/.venv/bin/python"
    elif command -v uv >/dev/null 2>&1; then
        printf '%s\n' "uv run python"
    elif command -v python3 >/dev/null 2>&1; then
        printf '%s\n' "python3"
    else
        printf '%s\n' "<missing>"
    fi
}

run_python() {
    if [ -n "${QA_MCP_RELEASE_PYTHON:-}" ]; then
        [ -x "$QA_MCP_RELEASE_PYTHON" ] || die "QA_MCP_RELEASE_PYTHON is not executable: $QA_MCP_RELEASE_PYTHON"
        "$QA_MCP_RELEASE_PYTHON" "$@"
    elif [ -x "$ROOT/.venv/bin/python" ]; then
        "$ROOT/.venv/bin/python" "$@"
    elif command -v uv >/dev/null 2>&1; then
        uv run python "$@"
    elif command -v python3 >/dev/null 2>&1; then
        python3 "$@"
    else
        die "no Python runner found; create .venv, install uv, or set QA_MCP_RELEASE_PYTHON"
    fi
}

host_agent_artifact() {
    run_python tools/release/windows_host_agent_artifact.py "$@"
}

sha256_write() {
    file=$1
    dir=$(dirname "$file")
    base=$(basename "$file")
    if command -v sha256sum >/dev/null 2>&1; then
        (cd "$dir" && sha256sum "$base" > "$base.sha256")
    else
        (cd "$dir" && shasum -a 256 "$base" > "$base.sha256")
    fi
}

validate_component_manifest() {
    manifest=$1
    validator=${AI1C_COMPONENT_MANIFEST_VALIDATOR:-}
    if [ -z "$validator" ]; then
        validator="$ROOT/tools/release/validate_component_manifest.py"
        if [ ! -f "$validator" ]; then
            suite_root=$(CDPATH= cd -- "$ROOT/.." && pwd)
            validator="$suite_root/deploy/docker/bin/release-hardening-check.py"
        fi
    fi
    [ -f "$validator" ] || die "component manifest validator not found: $validator"
    info "validating component release manifest"
    run_python "$validator" validate-component-manifest "$manifest" >/dev/null
}

verify_open_archive() {
    archive=$1
    manifest=$2
    info "verifying saved source-visible image archive"
    run_python docker/verify_open_image.py --archive "$archive" --component-manifest "$manifest"
}

verify_image_archive_tag() {
    archive=$1
    expected_tag=$2
    scan_archive=$archive
    scan_tmp=
    case "$archive" in
        *.zst)
            command -v zstd >/dev/null 2>&1 || die "zstd is required to inspect compressed image archive: $archive"
            scan_tmp="$BUILD_ROOT/image-tag-scan-$$.tar"
            zstd -dc "$archive" > "$scan_tmp"
            scan_archive=$scan_tmp
            ;;
    esac
    info "verifying image archive contains tag $expected_tag"
    if run_python - "$scan_archive" "$expected_tag" <<'PY'
import json
import sys
import tarfile

archive_path, expected_tag = sys.argv[1], sys.argv[2]
try:
    with tarfile.open(archive_path) as archive:
        member = archive.extractfile("manifest.json")
        if member is None:
            raise RuntimeError("Docker archive does not contain manifest.json")
        manifest = json.load(member)
except Exception as exc:  # noqa: BLE001 - shell helper needs a concise diagnostic.
    print(f"image tag check failed: {exc}", file=sys.stderr)
    raise SystemExit(2)

repo_tags = []
for entry in manifest:
    repo_tags.extend(entry.get("RepoTags") or [])
if expected_tag not in repo_tags:
    print(
        f"image archive tag mismatch: expected {expected_tag}, found {', '.join(repo_tags) or '<none>'}",
        file=sys.stderr,
    )
    raise SystemExit(3)
PY
    then
        tag_status=0
    else
        tag_status=$?
    fi
    [ -z "$scan_tmp" ] || rm -f "$scan_tmp"
    return "$tag_status"
}

load_release_env_defaults() {
    if [ -f .ai1c/release.env ]; then
        info "loading ignored release defaults from .ai1c/release.env"
        # shellcheck disable=SC1091
        . ./.ai1c/release.env
    fi
    if [ -f .ai/release.env ]; then
        info "loading ignored release defaults from .ai/release.env"
        # shellcheck disable=SC1091
        . ./.ai/release.env
    fi
}

stage_manifest_signature() {
    manifest=$1
    output=$2
    if [ -n "$MANIFEST_SIGNING_KEY" ]; then
        [ -f "$MANIFEST_SIGNING_KEY" ] || die "manifest signing key does not exist: $MANIFEST_SIGNING_KEY"
        command -v minisign >/dev/null 2>&1 || die "minisign is required to sign manifest.json"
        minisign -S -s "$MANIFEST_SIGNING_KEY" -m "$manifest" -x "$output" >/dev/null
    elif [ -n "$MANIFEST_MINISIG" ]; then
        [ -f "$MANIFEST_MINISIG" ] || die "manifest minisig does not exist: $MANIFEST_MINISIG"
        cp "$MANIFEST_MINISIG" "$output"
    else
        die "manifest signing is required; pass --manifest-signing-key or --manifest-minisig"
    fi
}

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$ROOT"

VERSION=
RELEASE_BASE_URL=https://releases.aifor1c.ru/qa-mcp/download/versions
STAGING_ROOT=.artifacts/releases/qa-mcp
SKIP_GATES=0
SKIP_BUILD=0
IMAGE_ARCHIVE=
HOST_AGENT_EXE=
IMAGE_TAG=
MANIFEST_SIGNING_KEY=
MANIFEST_MINISIG=
ALLOW_DIRTY=0

load_release_env_defaults

while [ "$#" -gt 0 ]; do
    case "$1" in
        --version) VERSION=${2:-}; shift 2 ;;
        --release-link-id)
            [ -n "${2:-}" ] || die "--release-link-id requires a value"
            info "ignoring retired --release-link-id; using authenticated product version paths"
            shift 2
            ;;
        --release-base-url) RELEASE_BASE_URL=${2:-}; shift 2 ;;
        --staging-root) STAGING_ROOT=${2:-}; shift 2 ;;
        --server-root) die "--server-root is retired; root publishes the staged version to private S3" ;;
        --activate) die "--activate is retired; root owns immutable product publication" ;;
        --skip-gates) SKIP_GATES=1; shift ;;
        --skip-build) SKIP_BUILD=1; shift ;;
        --image-archive) IMAGE_ARCHIVE=${2:-}; shift 2 ;;
        --host-agent-exe) HOST_AGENT_EXE=${2:-}; shift 2 ;;
        --image-tag) IMAGE_TAG=${2:-}; shift 2 ;;
        --manifest-signing-key) MANIFEST_SIGNING_KEY=${2:-}; shift 2 ;;
        --manifest-minisig) MANIFEST_MINISIG=${2:-}; shift 2 ;;
        --allow-dirty) ALLOW_DIRTY=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) usage >&2; die "unknown option: $1" ;;
    esac
done

[ -n "$VERSION" ] || { usage >&2; die "--version is required"; }
case "$VERSION" in
    */*|*..*) die "unsafe version: $VERSION" ;;
esac
[ -n "$IMAGE_TAG" ] || IMAGE_TAG="qa-mcp-standalone:$VERSION"
RELEASE_BASE_URL=${RELEASE_BASE_URL%/}
case "$RELEASE_BASE_URL" in
    https://*/qa-mcp/download/versions) ;;
    *) die "--release-base-url must end with /qa-mcp/download/versions on an HTTPS origin" ;;
esac
PUBLIC_RELEASE_URL="$RELEASE_BASE_URL/$VERSION"
info "using release Python: $(release_python_label)"

if [ "$ALLOW_DIRTY" -eq 0 ]; then
    dirty=$(git status --short -- delivery docker docs/self-hosted-release-delivery-plan.md host-agent tools/release tests/test_component_manifest.py tests/test_self_hosted_release_scripts.py 2>/dev/null || true)
    if [ -n "$dirty" ]; then
        printf '%s\n' "$dirty" >&2
        die "tracked release files are dirty; commit first or use --allow-dirty for a local staging smoke"
    fi
fi

if [ "$SKIP_GATES" -eq 0 ]; then
    info "running Python offline gates"
    uv run pytest -q -ra -m "not live"
    info "running Windows host-agent Go gates"
    (cd host-agent/windows-display-agent && go test ./...)
fi

BUILD_ROOT="$STAGING_ROOT/.build-$VERSION"
VERSION_DIR="$STAGING_ROOT/versions/$VERSION"
STAGE_TMP="$VERSION_DIR.tmp.$$"
BUILD_ROOT_ABS=$(abs_path "$BUILD_ROOT")
rm -rf "$BUILD_ROOT" "$STAGE_TMP"
[ ! -e "$VERSION_DIR" ] || die "staged version already exists: $VERSION_DIR"
mkdir -p "$BUILD_ROOT" "$STAGE_TMP"
trap 'rm -rf "$STAGE_TMP"' EXIT HUP INT TERM
GIT_COMMIT=$(git rev-parse HEAD)
run_python docker/verify_open_image.py --package-root src/qa_mcp --source-commit "$GIT_COMMIT" \
    --write-inventory "$BUILD_ROOT/open-package-inventory.json"

if [ -n "$HOST_AGENT_EXE" ]; then
    [ -f "$HOST_AGENT_EXE" ] || die "host-agent exe does not exist: $HOST_AGENT_EXE"
    [ "$(basename "$HOST_AGENT_EXE")" = "qa-mcp-host-agent.exe" ] || \
        die "supplied host-agent executable must be named qa-mcp-host-agent.exe"
    HOST_AGENT_BUNDLE_DIR=$(dirname "$HOST_AGENT_EXE")
    info "verifying supplied source-bound Windows host-agent bundle"
    set -- verify --bundle-dir "$HOST_AGENT_BUNDLE_DIR"
    [ "$ALLOW_DIRTY" -eq 0 ] || set -- "$@" --allow-dirty
    host_agent_artifact "$@"
    cp "$HOST_AGENT_EXE" "$STAGE_TMP/qa-mcp-host-agent.exe"
elif [ "$SKIP_BUILD" -eq 0 ]; then
    info "building and verifying Windows host-agent executable"
    set -- build --output-dir "$BUILD_ROOT_ABS/windows-host-agent"
    [ "$ALLOW_DIRTY" -eq 0 ] || set -- "$@" --allow-dirty
    host_agent_artifact "$@"
    cp "$BUILD_ROOT/windows-host-agent/qa-mcp-host-agent.exe" "$STAGE_TMP/qa-mcp-host-agent.exe"
else
    die "--skip-build requires --host-agent-exe"
fi

if [ -n "$IMAGE_ARCHIVE" ]; then
    [ -f "$IMAGE_ARCHIVE" ] || die "image archive does not exist: $IMAGE_ARCHIVE"
    case "$IMAGE_ARCHIVE" in *.zst) die "source-visible verification requires an uncompressed docker-save tar" ;; esac
    verify_image_archive_tag "$IMAGE_ARCHIVE" "$IMAGE_TAG"
    IMAGE_ASSET=$(basename "$IMAGE_ARCHIVE")
    cp "$IMAGE_ARCHIVE" "$STAGE_TMP/$IMAGE_ASSET"
elif [ "$SKIP_BUILD" -eq 0 ]; then
    IMAGE_ASSET="qa-mcp-standalone-$VERSION.tar"
    info "building source-visible qa-mcp image $IMAGE_TAG"
    PUBLIC_BASE_IMAGE=${QA_MCP_PUBLIC_BASE_IMAGE:-ghcr.io/astral-sh/uv:0.11.14-python3.12-trixie-slim@sha256:13b5883729ec534af5863facf5c40ac0869f2c124ad5620c9ed36fe7c03fa87d}
    printf '%s' "$PUBLIC_BASE_IMAGE" | grep -Eq '^ghcr\.io/astral-sh/uv:[^@]+@sha256:[0-9a-f]{64}$' || \
        die "QA_MCP_PUBLIC_BASE_IMAGE must be an immutable public uv/Python reference"
    DOCKER_BUILDKIT=1 docker build -f docker/Dockerfile.thin \
        --build-arg PUBLIC_BASE_IMAGE="$PUBLIC_BASE_IMAGE" --build-arg SOURCE_COMMIT="$GIT_COMMIT" \
        -t "$IMAGE_TAG" .
    info "verifying source-visible image"
    docker run --rm -v "$BUILD_ROOT_ABS/open-package-inventory.json:/tmp/inventory.json:ro" \
        --entrypoint python "$IMAGE_TAG" /usr/local/bin/qa-mcp-verify-open-image --inventory /tmp/inventory.json
    info "smoking direct authenticated standalone runtime"
    run_python tools/release/smoke_standalone_image.py "$IMAGE_TAG" --expected-source-commit "$GIT_COMMIT"
    info "saving docker archive"
    docker save -o "$BUILD_ROOT/$IMAGE_ASSET" "$IMAGE_TAG"
    cp "$BUILD_ROOT/$IMAGE_ASSET" "$STAGE_TMP/$IMAGE_ASSET"
else
    die "--skip-build requires --image-archive"
fi

cp host-agent/install-windows-host-agent.ps1 "$STAGE_TMP/install-windows-host-agent.ps1"
run_python tools/release/render_standalone_bootstrap.py \
    --source delivery/bootstrap.ps1 \
    --output "$STAGE_TMP/bootstrap.ps1" \
    --release-base "$PUBLIC_RELEASE_URL"
cp delivery/standalone-product-runbook.md "$STAGE_TMP/README.md"
cp delivery/standalone-product-runbook.md "$STAGE_TMP/windows-agent-runbook.md"
cp delivery/standalone-product-runbook.md "$STAGE_TMP/agent-install-runbook.md"
cp "$BUILD_ROOT/open-package-inventory.json" "$STAGE_TMP/open-package-inventory.json"

# Every staged asset must be world-readable so the release web server (www-data) can serve it. `docker save`
# and a --image-archive source can land 0600, which nginx then rejects with 403 — make all assets a+r.
chmod a+r "$STAGE_TMP"/* 2>/dev/null || true

for asset in \
    "$STAGE_TMP/bootstrap.ps1" \
    "$STAGE_TMP/install-windows-host-agent.ps1" \
    "$STAGE_TMP/qa-mcp-host-agent.exe" \
    "$STAGE_TMP/$IMAGE_ASSET" \
    "$STAGE_TMP/README.md" \
    "$STAGE_TMP/windows-agent-runbook.md" \
    "$STAGE_TMP/agent-install-runbook.md" \
    "$STAGE_TMP/open-package-inventory.json"
do
    sha256_write "$asset"
done

set -- \
    --version "$VERSION" \
    --git-commit "$GIT_COMMIT" \
    --image-tag "$IMAGE_TAG" \
    --image-asset "$STAGE_TMP/$IMAGE_ASSET" \
    --package-inventory "$STAGE_TMP/open-package-inventory.json" \
    --output "$STAGE_TMP/manifest.json" \
    --asset "bootstrap.ps1=$STAGE_TMP/bootstrap.ps1" \
    --asset "install-windows-host-agent.ps1=$STAGE_TMP/install-windows-host-agent.ps1" \
    --asset "qa-mcp-host-agent.exe=$STAGE_TMP/qa-mcp-host-agent.exe" \
    --asset "README.md=$STAGE_TMP/README.md" \
    --asset "windows-agent-runbook.md=$STAGE_TMP/windows-agent-runbook.md" \
    --asset "agent-install-runbook.md=$STAGE_TMP/agent-install-runbook.md" \
    --asset "open-package-inventory.json=$STAGE_TMP/open-package-inventory.json"
run_python tools/release/component_manifest.py "$@" >/dev/null
verify_open_archive "$STAGE_TMP/$IMAGE_ASSET" "$STAGE_TMP/manifest.json"
validate_component_manifest "$STAGE_TMP/manifest.json"
stage_manifest_signature "$STAGE_TMP/manifest.json" "$STAGE_TMP/manifest.json.minisig"
sha256_write "$STAGE_TMP/manifest.json"
sha256_write "$STAGE_TMP/manifest.json.minisig"

mv "$STAGE_TMP" "$VERSION_DIR"
trap - EXIT HUP INT TERM
rm -rf "$BUILD_ROOT"

info "staged $VERSION at $VERSION_DIR"
info "source-visible bootstrap path: $PUBLIC_RELEASE_URL/bootstrap.ps1"
