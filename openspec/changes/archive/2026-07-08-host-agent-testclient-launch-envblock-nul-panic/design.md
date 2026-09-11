## Context

`startTestClientProcess` (Windows) passes the child environment to
`CreateProcessAsUserW` with the `CREATE_UNICODE_ENVIRONMENT` flag. That API
expects a UTF-16 environment block: `KEY=VALUE\0KEY=VALUE\0...\0\0`.

The previous helper built the block in one shot:

```go
return syscall.StringToUTF16(strings.Join(env, "\x00") + "\x00")
```

`syscall.StringToUTF16` documents that it panics if the argument contains a NUL
byte. The joined block is deliberately full of NUL bytes, so the call panicked
on every non-empty environment.

## Decision

Encode the block segment-by-segment with the cross-platform `unicode/utf16`
package, which has no NUL restriction and no OS dependency:

```go
for _, entry := range env {
    if entry == "" { continue }
    block = append(block, utf16.Encode([]rune(entry))...)
    block = append(block, 0) // segment terminator
}
block = append(block, 0)     // block terminator
```

Because the helper now uses only `unicode/utf16`, it moves out of the
`//go:build windows` file into a neutral file. The neutral placement is the
point: the offline suite (which runs on Linux) can now decode the rendered
block and assert its structure, so the panic class is caught before it ever
reaches a Windows launch again. The caller in the Windows file is unchanged.

## Alternatives Considered

- Keep the helper Windows-only and encode per-segment with
  `syscall.UTF16FromString`. Correct at runtime, but still uncovered by the
  offline suite — it would not have caught the original bug and would not catch
  a regression. Rejected in favor of the neutral, testable encoder.

## Risks

- Empty env yields a nil block; the launcher already guards
  `len(envBlock) > 0` before taking the pointer, so a nil block passes a null
  environment pointer to `CreateProcessAsUserW`, which inherits the caller
  environment — acceptable and matched by the empty-env test.
