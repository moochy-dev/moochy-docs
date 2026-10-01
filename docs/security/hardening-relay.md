# Hardening checklist — `relay/` (`moochy.dev/relay`, minus `internal/web`)

Owner: `mo-relay`. The relay is **untrusted for confidentiality** (adversary A3): it must still be robust, must not be a DoS amplifier, and must never be able to forge identity or money. Go 1.26, stdlib first. `go vet` + `-race` clean. Attack ids → [attack-catalog.md](attack-catalog.md).

## Transport and HTTP

| # | Control | Attack | Proof |
|---|---|---|---|
| R1 | `tls.Config{MinVersion: VersionTLS13}`; TLS terminated in-process (channel binding) | A10 | A10 |
| R2 | `http.Server` with `ReadHeaderTimeout` 10 s, `ReadTimeout`, `IdleTimeout` 60 s, `MaxHeaderBytes` 32 KiB; `http.MaxBytesReader` on every body (API JSON ≤ 64 KiB) | A15, A16 | A15, A16 |
| R3 | `/v1/node` upgrade: require subprotocol `moochy.v1`; **refuse any upgrade carrying an `Origin` header** (nodes never send one — CSWSH defense); never `InsecureSkipVerify`/`OriginPatterns:*` | A11, A12 | A11, A12 |
| R4 | WebSocket: `CompressionDisabled`; `SetReadLimit(64 KiB)` before the first read; control text ≤ 16 KiB pre-auth; binary before `welcome` → close 1008 | A13, A14 | A13, A14 |
| R5 | Auth deadline 10 s after `hello`; per-IP cap on pre-auth sockets and total connections | A19 | A19 |
| R6 | Go toolchain pinned to the latest patch (CVE-2025-22871 bare-LF smuggling, HTTP/2 rapid-reset/CONTINUATION); `govulncheck` in CI | A17, A87 | A17, M |
| R7 | `--dev` registers `/dev/*` and is refused unless `--addr` is a loopback literal | A18 | A18 |

## Parsing, identity, money

| # | Control | Attack | Proof |
|---|---|---|---|
| R8 | Route header and all security/money JSON parsed with a **duplicate-key-rejecting** decoder (not plain `encoding/json`); reject invalid UTF-8, lone surrogates, out-of-range numbers, depth > 64; the relay parses the decoded route bytes, matching the Worker | A20, A22 | U |
| R9 | Ed25519 verification via `ed25519consensus` (ZIP-215) on **every** signature; never `crypto/ed25519.Verify`; shared edge-case vectors | A06 | V, U |
| R10 | Never key dedupe/idempotency/storage on signature bytes; key on `(gateway_device, task_id, attempt)` | A07 | U |
| R11 | Auth: recompute the signed string with the relay's **own** exporter and dialed origin; nonce single-use (32 B); reject a replay on a second connection | A08 | U |
| R12 | Enforce owner-signed approvals from the key log for `pool.sync`; the relay can show a request but never forge `DONOR_APPROVED`/`MEMBER_ADDED`/`REPO_CLAIMED` | A72, A71, A70 | U |
| R13 | Repo claim requires a provider admin check + owner signature; account-age threshold (proposed 30 d) and per-account/-IP rate limits for claims and pledges | A70, A71 | U |
| R14 | Device revocation (`KEY_REVOKED`) drops the device immediately; events from non-current sessions ignored | A76 | U |

## Storage and resources

| # | Control | Attack | Proof |
|---|---|---|---|
| R15 | SQLite: parameterized statements only; CI grep fails on `fmt.Sprintf` into `Exec`/`Query`; `trusted_schema=OFF`; modernc ≥ SQLite 3.50.2 (CVE-2025-6965); never run SQL text from input | A29, A88 | U, M |
| R16 | No content (prompts/outputs/keys) in the DB, WAL or logs; schema holds only ids, sizes, codes | A28 | E13 |
| R17 | Logging via `log/slog` JSON only; never interpolate remote strings into a message; no ANSI/CRLF from input reaches a log line | A27 | U |
| R18 | Per-device and global byte budgets for buffered bodies; ≤ 8 wraps per submit; ≤ 3 attempts; drop and count frames arriving on a non-source connection; 1 MiB per-task response buffer; sheddable submit queue | A89, A75, A66 | E17, E20 |
| R19 | Per-member limits: 16 concurrent, 120 submits/min; the chaos dev hooks (`ignore_caps`, `tamper_route`, `replay_assign`, `inject_frame`) exist **only** under `--dev` | A66, A18 | E10, E11, E15–E17 |
