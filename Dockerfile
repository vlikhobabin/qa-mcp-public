# qa-mcp delivery image — native 1C TestClient QA over MCP, served over HTTP.
#
# DESIGN (see docker/README.md):
#   * This image carries the Python MCP (TestManager) + the X11 toolchain it drives (Xvfb / xdotool /
#     ImageMagick / scrot) + the shared libraries the 1C thick client needs. The MCP's genuine protocol
#     captures and frame templates are bundled INSIDE the package, so the image is self-contained.
#   * It does NOT carry the 1C platform itself (proprietary — not redistributable) nor the infobase nor the
#     1C license. Those are MOUNTED at runtime as volumes and pointed at via env vars. The user's only
#     inputs are the infobase path and the platform version.
#
# BUILD:  docker build -t qa-mcp .
# RUN:    see docker/README.md (mount platform + infobase + license, publish the HTTP port).

FROM python:3.12-slim-bookworm@sha256:8a7e7cc04fd3e2bd787f7f24e22d5d119aa590d429b50c95dfe12b3abe52f48b

# --- Cyrillic locale (1C metadata/usernames are Russian) ---------------------------------------------------
ENV LANG=ru_RU.UTF-8 LC_ALL=ru_RU.UTF-8 PYTHONUNBUFFERED=1

# --- System deps: the X11 toolchain the engine shells out to + the 1C thick-client runtime libraries -------
# The X tools (xvfb/xdotool/imagemagick/scrot) are what qa-mcp itself calls. The lib* packages are the
# shared libraries the MOUNTED `1cv8` binary links against — a VERIFIED set for the 1C 8.3.2x thick client
# on Debian 12 (the 1C-on-Debian-12 community baseline). Two non-obvious points:
#   * 1C needs the OLD WebKit 4.0 API → `libwebkit2gtk-4.0-37`. Debian 12 (bookworm) is the LAST release
#     that ships it (Debian 13 / Ubuntu 24.04 dropped it) — that is why the base stays on bookworm.
#   * 1C looks for MS core fonts under /usr/share/fonts/truetype/msttcorefonts → `ttf-mscorefonts-installer`
#     (in `contrib`; EULA pre-accepted below; it downloads the fonts at build time).
# If a specific platform build still reports a missing .so, add it here (diagnose with
# `docker run --rm -v <platform>:/opt/1cv8 qa-mcp ldd /opt/1cv8/x86_64/<ver>/1cv8 | grep 'not found'`).
RUN sed -i 's/^Components: main$/Components: main contrib/' /etc/apt/sources.list.d/debian.sources \
 && echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections \
 && apt-get update && apt-get install -y --no-install-recommends \
      # qa-mcp's own X11 toolchain
      xvfb xauth xdotool imagemagick scrot x11-utils procps \
      # locale + fonts (managed-form text rendering; 1C wants the MS core fonts, liberation/dejavu as fallback)
      locales fontconfig libfreetype6 ttf-mscorefonts-installer fonts-dejavu fonts-liberation \
      # 1C thick-client GUI + runtime shared libraries
      libwebkit2gtk-4.0-37 libgtk-3-0 libgsf-1-114 libgsf-1-common libglib2.0-0 \
      libfontconfig1 libxml2 libkrb5-3 libgssapi-krb5-2 libodbc2 libcanberra-gtk3-module libgl1 libglu1-mesa \
      # 1C helper apps it shells out to (dialogs / print preview / privilege prompts) + iproute2:
      # 1C calls `ip` to read network parameters for LICENSE binding — without it the client fails to start.
      zenity evince policykit-1 iproute2 \
      ca-certificates \
 && sed -i 's/^# *\(ru_RU.UTF-8\)/\1/' /etc/locale.gen && locale-gen \
 && rm -rf /var/lib/apt/lists/*

# --- Install the qa-mcp package (self-contained: bundles captures + templates) -----------------------------
WORKDIR /opt/qa-mcp
COPY pyproject.toml ./
COPY delivery/README.md ./README.md

# Resolve metadata-declared build/runtime dependencies before mutable source so
# code-only edits reuse this stable layer. The project itself is installed later.
RUN python -c 'import pathlib, tomllib; metadata = tomllib.loads(pathlib.Path("pyproject.toml").read_text(encoding="utf-8")); pathlib.Path("/tmp/qa-mcp-build-requirements.txt").write_text("\n".join(metadata["build-system"]["requires"]) + "\n", encoding="utf-8"); pathlib.Path("/tmp/qa-mcp-runtime-requirements.txt").write_text("\n".join(metadata["project"]["dependencies"]) + "\n", encoding="utf-8")' \
 && pip install --no-cache-dir \
      -r /tmp/qa-mcp-build-requirements.txt \
      -r /tmp/qa-mcp-runtime-requirements.txt \
 && rm -f /tmp/qa-mcp-build-requirements.txt /tmp/qa-mcp-runtime-requirements.txt

COPY src ./src
RUN pip install --no-cache-dir --no-deps --no-build-isolation .

COPY docker/entrypoint.sh /usr/local/bin/qa-mcp-entrypoint
RUN chmod +x /usr/local/bin/qa-mcp-entrypoint \
 && groupadd --system qa-mcp \
 && useradd --system --gid qa-mcp --home-dir /home/qa-mcp --create-home --shell /usr/sbin/nologin qa-mcp \
 && mkdir -p /work \
 && chown -R qa-mcp:qa-mcp /work /home/qa-mcp

# --- Runtime contract --------------------------------------------------------------------------------------
# HTTP transport defaults to loopback; bridge-mode Docker runs that need port publishing must explicitly set
# For explicit non-loopback serving, set QA_MCP_HTTP_HOST together with a strong
# QA_MCP_BEARER_TOKEN; publish the host port on loopback unless broader access is intentional.
ENV QA_MCP_TRANSPORT=http \
    QA_MCP_HTTP_HOST=127.0.0.1 \
    QA_MCP_HTTP_PORT=8000 \
    QA_MCP_HOME=/work \
    PLATFORM_ROOT=/opt/1cv8/current \
    INFOBASE_PATH=/infobase \
    TEST_CLIENT_USER=Администратор \
    TEST_CLIENT_PASSWORD=""
VOLUME ["/opt/1cv8", "/infobase", "/work"]
EXPOSE 8000
USER qa-mcp
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import os,socket; host=os.environ.get('QA_MCP_HTTP_HOST','127.0.0.1').strip() or '127.0.0.1'; host='127.0.0.1' if host in {'0.0.0.0','::','[::]','*'} else host.strip('[]'); socket.create_connection((host,int(os.environ.get('QA_MCP_HTTP_PORT','8000'))),3).close()"

ENTRYPOINT ["qa-mcp-entrypoint"]
