# qa-mcp standalone source delivery

qa-mcp currently supports public source builds. A stable downloadable release
and GitHub/GHCR release train are not published by this repository-readiness
card; follow the [root README](../README.md) for the active source installation.

The standalone topology is:

```text
AI agent -> authenticated MCP HTTP -> qa-mcp container
                                      -> authenticated Windows bridge
                                         -> owned TestClient
```

The container contains readable Python source and reviewed plaintext protocol
assets. It contains no 1C platform binary, infobase, product activation,
entitlement service or private data key. The operator supplies a legal 1C
installation, a test infobase and ignored runtime credentials.

Build the thin source image:

```sh
docker build -f docker/Dockerfile.thin -t qa-mcp-standalone .
export QA_MCP_BEARER_TOKEN="$(openssl rand -hex 32)"
docker run --rm -p 127.0.0.1:8000:8080 \
  -e QA_MCP_BEARER_TOKEN="$QA_MCP_BEARER_TOKEN" \
  qa-mcp-standalone
```

The MCP URL is `http://127.0.0.1:8000/mcp` and requires
`Authorization: Bearer <QA_MCP_BEARER_TOKEN>`. Live TestClient operation also
requires the target and optional Windows bridge settings documented in
[docker/README.md](../docker/README.md) and
[host-agent/README.md](../host-agent/README.md).

```json
{"mcpServers": {"qa-mcp": {"type": "http", "url": "http://127.0.0.1:8000/mcp", "headers": {"Authorization": "Bearer <QA_MCP_BEARER_TOKEN>"}}}}
```

Для совместимости с существующей русскоязычной инструкцией: путь ровно `/mcp`;
до сборки проверьте `docker info`; если пароль пользователя 1C пустой,
параметр `-Password` надо **опустить**, а не передавать пустую строку.

Do not use retained pre-release bootstrap/staging scripts as proof of a public
release. OSS-08 owns future release automation and immutable published artifact
evidence.
