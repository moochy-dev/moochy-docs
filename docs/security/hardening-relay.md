# Hardening checklist — `relay/` (`moochy.dev/relay`, minus `internal/web`)

Owner: `mo-relay`. The relay is **untrusted for confidentiality** (adversary A3): it must still be robust, must not be a DoS amplifier, and must never be able to forge identity or money. Go 1.26, stdlib first. `go vet` + `-race` clean. Attack ids → [attack-catalog.md](attack-catalog.md).

## Transport and HTTP

| # | Control | Attack | Proof |
|---|---|---|---|
| R1 | `tls.Config{MinVersion: VersionTLS13}`; TLS terminated in-process (channel binding) | A10 | A10 |
| R2 | `http.Server` with `ReadHeaderTimeout` 10 s, `ReadTimeout`, `IdleTimeout` 60 s, `MaxHeaderBytes` 32 KiB; `http.MaxBytesReader` on every body (API JSON ≤ 64 KiB) | A15, A16 | A15, A16 |
| R3 | (Superseded by the gRPC link, ADR-33.) The HTTP listener (`--addr`) serves only web, OAuth and dev routes: it never upgrades to WebSocket and never exposes `NodeLink` | A11, A12 | A12 |
| R4 | (Superseded.) No compression anywhere on the link: no gRPC compressor registered (never import `grpc/encoding/gzip`), per-message size caps in R21 | A13 | A13 |
| R5 | Per-IP caps on total and unauthenticated connections on both listeners; the auth deadline itself is R24 | A11, A15 | A11 |
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

## gRPC link (`NodeLink`, CONTRACT §12)

| # | Control | Attack | Proof |
|---|---|---|---|
| R20 | Separate listener on `--grpc-addr`: TLS 1.3 only, ALPN `h2`, no h2c on TCP; `--addr` keeps the HTTP hardening (R1–R7) | A10, A94 | A10 |
| R21 | `MaxConcurrentStreams` 64; `MaxRecvMsgSize`/`MaxSendMsgSize` 128 KiB; `MaxHeaderListSize` 16 KiB; current grpc-go/x-net (CONTINUATION-flood + HPACK fixes) | A13, A91 | A13 |
| R22 | Per-connection stream-open and RST_STREAM rate limits (HTTP/2 Rapid Reset); the relay keeps serving under a reset burst | A14 | A14 |
| R23 | `KeepaliveEnforcementPolicy{MinTime:10s, PermitWithoutStream:true}` + server pings 15 s / 2 missed = dead; GOAWAY on too-many-pings | A15 | A15b |
| R24 | Auth per connection: `Session` sends `Hello` first; first `NodeMsg` must be `Auth`; **10 s auth deadline**; the custom `TransportCredentials` tag each connection with an id and the RFC 9266 exporter | A11, A95 | A11 |
| R25 | `Submit`/`Serve` accepted only on the authenticated connection id **and** with a matching `x-moochy-session`; else `UNAUTHENTICATED` before any task-state allocation | A12 | A12 |
| R26 | Policy failures travel as `Failed{code,retryable}` inside the stream; gRPC status reserved for transport/auth; no gRPC compression | A93 | U |
| R27 | gRPC reflection and channelz disabled in production; only `grpc.health.v1` registered; `DeviceStart`/`DevicePoll` rate-limited per IP, unauthenticated | A19, A59 | U |
| R28 | Security/money decisions read the signed JSON `bytes`, never a protobuf scalar that proto3 could merge (repeated singular, unknown fields) | A90 | U, V |

## RelayAdmin Unix socket (CONTRACT §12)

| # | Control | Attack | Proof |
|---|---|---|---|
| R29 | `RelayAdmin` only on a path-based 0600 Unix socket in a 0700 dir (`--admin-socket`), never on the network, never abstract-namespace | A100, A103 | A100 |
| R30 | Check the peer uid (`SO_PEERCRED`) == the relay owner on every admin connection | A100 | A100, U |
| R31 | Create the socket safely: a 0700 owner-only dir is the real defense; bind to a temp name and atomic-`rename`, `fchmod`/umask (never chmod through a path); refuse if the final path is a symlink or non-socket | A102 | A100/A102 |

## Identity (CONTRACT §11)

| # | Control | Attack | Proof |
|---|---|---|---|
| R13b | Username validation shared with the Node via `spec/vectors/usernames.json`: ASCII `^[a-z0-9](?:[a-z0-9-]{1,30}[a-z0-9])$`, `UNIQUE COLLATE NOCASE`, reserved-word list, control chars rejected | A110, A112 | A110, E21 |
| R13c | `username_tombstones` makes every released handle permanent; rename ≤ once per 30 days; 90-day redirect | A111 | E21 |
