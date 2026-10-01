# Moochy attack catalog

Owner: `mo-sec`. The running list of attacks on Moochy with the countermeasure that stops each one and the test that proves it. Read with [06 — Security and Trust](../plan/06-security-and-trust.md) (threats T1–T22, adversaries A1–A9 = "Adv." below) and the per-component checklists `hardening-*.md` in this folder.

**Status:** `implemented` = code exists and the verification passes; `designed` = in the plan or contract, not yet built or verified; **`gap`** = not covered by the plan or contract: the row proposes the fix, and the owner must adopt it (or argue against it here).
**Verification:** `E<NN>` = CONTRACT §8 scenario; `A<NN>` = black-box test `TestA<NN>_*` in `e2e/attacks/`; `V` = golden vector in `spec/vectors/`; `U:<owner>` = unit/fuzz test the owner must write (attack needs a forged peer, which this suite deliberately does not build); `M` = manual/process check.
**Owners:** proto = `cli/crates/proto`, worker = `cli/crates/worker`, node = `cli/crates/node`, relay = `relay/` (minus web), web = `relay/internal/web`, e2e = `e2e/`, int = integrator (contract, CI, legal).

As of this commit no component binary exists, so nothing is `implemented` yet: every `A` test currently skips with `pending:`.

## 1. Cryptography and protocol (A01–A09)

| ID | Attack | Target | Adv. | Impact | Countermeasure (exact) | Owner | Verif. | Status |
|---|---|---|---|---|---|---|---|---|
| A01 | AEAD key/nonce reuse across attempts (relay assigns a task twice, or a failover) → XOR streams, forge chunks [S5.1] | proto, node | A3 | Plaintext recovery, forged output | `RK` = HKDF(salt=`R` fresh per attempt, ikm=CK, info binds task, worker, attempt); `R` in AAD; Gateway decrypts only the accepted attempt and aborts on a second started stream | proto, node | V (two attempts → distinct RK), E16, E17 | designed |
| A02 | Sequence-counter wrap/overflow on a chunk stream (nonce = `u32 seq`) [S5.2] | proto | A1, A2, A3 | Nonce reuse | Reject `seq` > ⌈32 MiB / 65,497⌉ = 513 for requests and > 2²⁰ for responses **before** decrypting; never wrap; a fresh CK per body | proto | U:proto | **gap** (bound not stated) |
| A03 | Reorder, splice, truncate chunks across tasks/attempts | proto, node | A3 | Corrupted or spliced output | AAD = `lp(label, kind, task_id, attempt, R, seq, last)`; Gateway requires contiguous `seq` from 0 and a `last` flag before success | proto, node | V, E17 | designed |
| A04 | Non-committing AEAD (invisible salamanders / partitioning oracle) [S5.3, S5.4]: a Gateway wraps different CKs for different Workers so one ciphertext decrypts to two bodies | proto, worker | A1 | Two donors see different requests for one signed task | `task_sig` covers `body_sha256` and the Worker checks the hash after decrypting, so only one plaintext can be valid. **Never** drop that check | worker | U:worker | designed |
| A05 | HPKE suite or version downgrade | proto | A3 | Weaker crypto | `suite_id` in the HPKE `info` and in `KEY_ADDED`; one suite only in v1; unknown suite → `bad_envelope` | proto | V | designed |
| A06 | Ed25519 verification differential (Relay accepts, Gateway rejects, or the reverse) [S6.1–S6.3] | proto, relay | A1–A3 | Disputed receipts, split views | ZIP-215 in both languages (`ed25519-zebra`, `ed25519consensus`); never Go `crypto/ed25519.Verify` on security paths; shared edge-case vectors | proto, relay | V | designed |
| A07 | Signature malleability (same message, second valid signature) [S6.4] | relay | A2, A3 | Double-counted receipts if signatures are used as ids | Never key dedupe, storage or idempotency on signature bytes; key on `(gateway_device, task_id, attempt)` and on `SHA-256(signed bytes)` | relay | U:relay | **gap** (rule not written) |
| A08 | Auth relay/replay: phishing relay forwards `auth`, or a captured `auth` is replayed on another connection | relay, node | A3, A4 | Device impersonation | Sig over `lp(auth, nonce, dialed_origin, tls_exporter, device_id)`; the Relay recomputes with **its own** exporter and origin; nonce single-use, 32 B random | relay, node | V, U:relay (replay on second conn → refused) | designed; **gap**: no E-test |
| A09 | Cross-protocol reuse of a signature (receipt sig as approval, …) | proto | A1–A3 | Forged artifacts | Distinct `lp` label per purpose (CONTRACT §2); verifiers prepend the label themselves, never accept it from input | proto | V | designed |

## 2. Relay transport (A10–A19)

| ID | Attack | Target | Adv. | Impact | Countermeasure (exact) | Owner | Verif. | Status |
|---|---|---|---|---|---|---|---|---|
| A10 | TLS downgrade to ≤ 1.2 | relay | A4 | Loses RFC 9266 exporter semantics | `tls.Config{MinVersion: tls.VersionTLS13}`; TLS terminated in-process | relay | A10 | designed |
| A11 | Upgrade without subprotocol (protocol confusion) | relay | any | Non-Moochy clients on `/v1/node` | Refuse the upgrade unless `Sec-WebSocket-Protocol` offers `moochy.v1` | relay | A11 | designed |
| A12 | Cross-site WebSocket hijacking (CSWSH) [S4.1, S4.2] | relay | A5 | Browser-driven sockets to the relay | Nodes never send `Origin`; **refuse any upgrade carrying an `Origin` header**. With `coder/websocket` that means checking `r.Header["Origin"]` before `Accept`. Never `InsecureSkipVerify` | relay | A12 | **gap** (not in plan) |
| A13 | Compression oracle / inflation bomb via `permessage-deflate` [S4.4] | relay | A4 | Secret recovery; memory DoS | `CompressionMode: CompressionDisabled`; never echo `Sec-WebSocket-Extensions` | relay | A13 | designed |
| A14 | Malformed or oversized frames before auth (huge declared length, binary before auth, bad UTF-8, reserved opcode) [S4.3] | relay | any | Memory DoS, crash | `conn.SetReadLimit(64 KiB)` **before** the first read; text frames are JSON ≤ 16 KiB pre-auth; binary before `welcome` → close 1008; the relay keeps serving | relay | A14 | designed (limit) |
| A15 | Slowloris (dripped headers) [S9.5] | relay | any | Connection exhaustion | `ReadHeaderTimeout` 10 s, `IdleTimeout` 60 s, per-IP connection cap | relay | A15 | designed |
| A16 | Header and body flooding on HTTP routes | relay | any | Memory DoS | `MaxHeaderBytes` 32 KiB; `http.MaxBytesReader` (≤ 64 KiB for API JSON) on **every** body | relay | A16 | designed |
| A17 | Request smuggling / desync shapes (duplicate CL, obfuscated TE, bare LF) [S9.1, S9.2] | relay, node | any | Desync behind a future CDN | Go ≥ 1.24.2 (CVE-2025-22871); HTTP/1.1 rules as is; the gateway (hyper) refuses the same shapes; govulncheck in CI | relay, node | A17, A35 | designed |
| A18 | Dev API exposed in production (`/dev/*` mints users and pledges) | relay | any | Total ledger compromise | Routes registered only with `--dev`; `--dev` refused unless `--addr` is a loopback literal | relay | A18 | designed |
| A19 | Unauthenticated sockets held open (upgrade, never send `auth`) | relay | any | Slot exhaustion | Auth deadline **10 s** after `hello`; per-IP cap on pre-auth sockets (proposed 32) | relay | A19 | **gap** (no deadline in plan) |

## 3. Parsing, content and the Worker firewall (A20–A29)

| ID | Attack | Target | Adv. | Impact | Countermeasure (exact) | Owner | Verif. | Status |
|---|---|---|---|---|---|---|---|---|
| A20 | Duplicate keys in the route header (`{"model":"cheap","model":"opus"}`): the Relay schedules and bills on one value, the Worker reads another [S7.1, S7.2] | relay, worker | A1 | Budget theft, cap bypass | CONTRACT §1 parser-differential rule: reject duplicates, invalid UTF-8, lone surrogates, out-of-range numbers, depth > 64, in both languages | relay, worker | U:relay, U:worker (A20 test skips: needs an authenticated peer) | designed |
| A21 | zstd decompression bomb in the sealed inner payload (tiny RLE blocks, huge `Frame_Content_Size`, window > 8 MiB) [S8.1–S8.4] | worker | A1 | Worker OOM | Streaming decode into a buffer capped at **32 MiB + 1** (fail at the cap); max window 8 MiB (2²³); ignore `Frame_Content_Size` for allocation; single frame only | worker | U:worker | designed (bound); **gap** (window and FCS rules) |
| A22 | Number and Unicode edge cases (`max_tokens: 1e400`, `-1`, `2^63`, `"\ud800"`, overlong UTF-8) [S7.4] | worker, relay | A1 | Cap bypass, crash | Integers parsed as `u64`/`i64` with range checks; floats rejected where ints are expected; lone surrogates rejected | worker, relay | U:worker, U:relay | designed |
| A23 | Route header ≠ body (declare a cheap model or small input, send something expensive) | worker | A1 | Overspend | Worker recomputes every route field; exact `est_input_tokens` match; `route_mismatch` non-retryable + strike | worker | U:worker, V | designed |
| A24 | Firewall bypass by encoding: escaped key names (`"mcp_servers"`), case variants, nesting inside `tool_result` / documents | worker | A1 | Server-side execution on the donor's account | Validate the **decoded** tree; allowlist compares decoded, case-sensitive keys; recursion over every content position; re-serialize from the validated tree | worker | E09, U:worker (fuzz) | designed |
| A25 | Server tools, `mcp_servers`, `container`, file ids, URL sources, `n:2`, unknown top-level fields | worker | A1 | Execution, exfiltration, cost | Allowlist tables (06 §7) | worker | E09 | designed |
| A26 | Beta-header smuggling (`anthropic-beta` value that enables long-context pricing or tools) | worker | A1 | Cost multiplier, features | Header values allowlisted per catalog version; unknown value → `firewall` | worker | U:worker; **propose** adding to E09 | designed; **gap** (no E-test) |
| A27 | Log injection (CR/LF, ANSI in usernames, repo names, error messages) [S14.1, S14.2] | relay, node | A1, A8 | Forged log lines, terminal attacks on operators | Relay: `log/slog` JSON handler only, never `fmt.Print` user data; Node: `tracing` JSON or sanitized fields; no string interpolation of remote values into log messages | relay, node | U:relay | designed (JSON logs) |
| A28 | Content written to the relay DB or logs | relay | A3 (disclosure) | Privacy breach | No content fields in the schema; log only ids, sizes and codes | relay | E13 | designed |
| A29 | SQL injection [S10.1] | relay | any | DB compromise | Parameterized statements only (`?` placeholders); CI grep that fails on `fmt.Sprintf` feeding `Exec`/`Query`; `PRAGMA trusted_schema=OFF` | relay | U:relay, M | **gap** (rule not written) |

## 4. Maintainer machine: local Gateway and MCP door (A30–A39)

| ID | Attack | Target | Adv. | Impact | Countermeasure (exact) | Owner | Verif. | Status |
|---|---|---|---|---|---|---|---|---|
| A30 | DNS rebinding against the loopback Gateway/MCP (`Host: evil.example`, `127.0.0.1.evil.example`, wrong port, absolute-form URI, userinfo, `0.0.0.0`) [S3.4, S3.5] | node | A5 | Pool use, file reads via MCP | Accept only `Host` ∈ {`127.0.0.1:P`, `[::1]:P`, `localhost:P`} with P = the bound port, exact string match; refuse absolute-form targets with another authority; 403 | node | A30, E14 | designed |
| A31 | CORS preflight grants a web page access | node | A5 | Same as A30 | Never emit `Access-Control-Allow-*`; OPTIONS → 403/405 | node | A31, E14 | designed |
| A32 | MCP Streamable HTTP without `Origin` validation (the MCP spec requires it; cf. MCP Inspector CVE-2025-49596, Claude Code IDE CVE-2025-52882) [S3.4, S3.5, S4.1] | node | A5 | RCE-class via local tools | `/mcp`: any present `Origin` that is not `http://127.0.0.1:P` / `http://localhost:P` → 403, in addition to the bearer token and the Host check | node | A32 | **gap** (plan has only Host) |
| A33 | MCP session hijack: reuse an `Mcp-Session-Id` with another token [S3.3] | node | A6 | Cross-repo delegation | Session ids are 128-bit random, bound to the token hash that created them; mismatch → 404; never treat a session id as authentication | node | A33 | **gap** |
| A34 | Slowloris on the Gateway | node | A6 | Local DoS of the agent workflow | Header read timeout 10 s, max 64 open connections, body read timeout | node | A34 | **gap** (no timeouts in plan) |
| A35 | Oversized or ambiguously framed bodies on the Gateway | node | A6 | OOM | Reject `Content-Length` > 32 MiB at headers; cap streamed bodies at 32 MiB; hyper's strict framing | node | A35 | designed (32 MiB) |
| A36 | Timing leak in the local token comparison [S16.1–S16.3] | node | A6 | Token recovery | Look up by `SHA-256(token)` in a map, then `subtle::ConstantTimeEq` on the full value; no early return on prefix | node | A36 (coarse) | designed |
| A37 | Port squatting: another local user binds the Gateway port while the Node restarts | node | A6 | Token capture, fake pool | Socket held by launchd/systemd; `moochy doctor` checks the listener uid; clients pinned to the port | node | M | designed |
| A38 | Local token committed to git or leaked through shared configs | node | A9 | Pool abuse | `connect --write` writes only user-scoped files and refuses git-tracked paths; tokens rotatable | node | U:node | designed |
| A39 | **Donor-controlled strings reach the delegating agent's context** (model ids in the `moochy_delegate` enum, donor pseudonym, `sealed_detail`) → line-jumping / tool-description prompt injection [S3.1, S3.2] | node, relay | A2, A8 | Agent steered before any call | Model ids only from the **signed catalog** (regex `^[a-z0-9][a-z0-9._:/-]{0,63}$`), never free text from offers; pseudonyms generated by the Relay from a fixed alphabet; `sealed_detail` shown only inside the untrusted-content envelope, length-capped (512 B), control characters stripped | node, relay | U:node, U:relay | **gap** |

## 5. Files, output and outbound requests (A40–A49)

| ID | Attack | Target | Adv. | Impact | Countermeasure (exact) | Owner | Verif. | Status |
|---|---|---|---|---|---|---|---|---|
| A40 | Path traversal in MCP `files` (`../`, absolute, `file://`, NUL) [S11.2] | node | A9 | Local file exfiltration to donors | Paths relative to the allowed root only; reject absolute, `..` components, NUL, URL schemes **before** resolution | node | A40 | designed |
| A41 | Symlink escape and realpath→open **TOCTOU** (swap a component between check and open) [S11.1–S11.4] | node | A6, A9 | Exfiltration of `~/.ssh`, etc. | Do not "realpath then open". Open from the root dirfd with `openat2(RESOLVE_BENEATH \| RESOLVE_NO_SYMLINKS \| RESOLVE_NO_MAGICLINKS)` on Linux, a component-wise `O_NOFOLLOW` walk elsewhere (or `cap-std`); `fstat` the opened fd | node | A40 (symlink cases) | **gap** (plan says realpath) |
| A42 | `.git/**`, secret-shaped and git-ignored files | node | A9 | Credential leak | Deny list (06 §13) + `git check-ignore` + scrubber | node | A40 | designed |
| A43 | Hard link inside the repo to an outside file | node | A6 | Exfiltration | Refuse regular files with `st_nlink > 1` | node | U:node | **gap** |
| A44 | Special files: FIFO, `/dev/zero`-style devices, sockets, huge sparse files | node | A9 | Hang, OOM | `fstat` → regular files only; read through a limit of the remaining 2 MiB budget; `O_NONBLOCK` on open | node | U:node | **gap** |
| A45 | SSRF / key exfiltration via provider base URL (metadata IP, private ranges, decimal/hex IPs, `user@host`, IPv4-mapped IPv6, non-http schemes) [S12.1–S12.3] | node, worker | A1, A9 | Provider key sent to the attacker | `--base-url` only with `MOOCHY_INSECURE_DEV=1` **and** a host that parses as a loopback IP literal or `localhost`; production hosts fixed per adapter; the HTTP client ignores proxies from env for provider calls and refuses redirects | node, worker | A45 | designed (loopback + flag); **gap** (redirects and proxy env) |
| A46 | Terminal escape / bidi injection through `moochy_delegate` results (OSC 52 clipboard, OSC 8 links, CSI screen clears, C1, U+202E) [S13.1–S13.3] | node | A2 | Hidden instructions, clipboard hijack, spoofed UI | Strip C0 except `\n\t`, DEL, C1 and bidi overrides/isolates (U+202A–202E, U+2066–2069) from delegate text and from everything the CLI prints; the API door stays byte-identical (the client renders it) | node | A46 | **gap** |
| A47 | Same as A46 but in moochy's own CLI output (relay `error.message`, donor pseudonyms, NACK details, `moochy status`) | node | A2, A3 | Operator terminal attacks | One `sanitize_for_terminal()` used by every print of a remote value | node | U:node | **gap** |
| A48 | Poisoned tool call from a malicious donor (`bash curl … \| sh`) [S2.1–S2.4] | node | A2 | **RCE on the maintainer's machine** | Structural checks + tripwire + progress signatures + owner approval of donors (06 §8) | node | E18 | designed (residual: highest) |
| A49 | Indirect prompt injection inside delegated results steering the calling agent | node | A2, A9 | Agent misuse | Untrusted-content envelope with the donor name; same tripwire scan; guidance to keep human approval on | node | E04 (envelope) | designed (residual) |

## 6. Web app (A50–A59)

| ID | Attack | Target | Adv. | Impact | Countermeasure (exact) | Owner | Verif. | Status |
|---|---|---|---|---|---|---|---|---|
| A50 | Stored XSS through repo/owner names, usernames, avatars | web, relay | A5, A8 | Session theft | Accept only `^[A-Za-z0-9._-]{1,100}$` names at claim time (relay); `html/template` everywhere; no `template.HTML` from data | web, relay | A50 | designed (auto-escape); **gap** (name validation) |
| A51 | SVG badge injection (markup in names or numbers; SVG opened directly runs script in the site's origin) [S17.3] | web | A5 | XSS on the relay origin | Badge from a `text/template` with only digits and fixed strings, plus XML escaping of every value; headers `Content-Type: image/svg+xml`, `Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'`, `X-Content-Type-Options: nosniff` | web | A50 | **gap** (badge headers) |
| A52 | CSRF on state-changing routes | web | A5 | Pledges or approvals made by the victim | `HX-Request: true` **and** exact `Origin` match; form fallback token; `SameSite=Lax` | web | A52 | designed |
| A53 | Missing browser hardening (framing, sniffing, inline script) | web | A5 | Clickjacking, XSS amplification | CSP `default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'`, no `unsafe-inline` scripts; `nosniff`; `Referrer-Policy: same-origin` | web | A53 | designed |
| A54 | OAuth login CSRF / code injection / mix-up (missing `state` or PKCE) [S17.1] | relay | A5 | Victim logged into the attacker's account | RFC 9700: PKCE S256 + one-time `state` bound to a pre-login cookie; exact `redirect_uri`; reject a reused `state` | relay | U:relay | **gap** |
| A55 | Session fixation [S17.2] | relay | A5 | Account takeover | New random 256-bit session id at login; store only its hash; `__Host-` prefixed cookie, `Secure; HttpOnly; SameSite=Lax; Path=/` | relay, web | U:relay | **gap** (rotation not stated) |
| A56 | Open redirect (`?next=//evil.example`) | web, relay | A5 | Phishing from the moochy.dev origin | `next` accepted only when it starts with a single `/` (not `//` or `/\`), else `/` | web, relay | U:web | **gap** |
| A57 | Avatar URL tracking, SSRF via an avatar proxy | web | A5 | Visitor tracking, internal fetches | CSP `img-src 'self' https://avatars.githubusercontent.com https://gitlab.com`; if proxied: fixed host allowlist, no redirects, size cap | web | A53 | designed |
| A58 | SSE connection exhaustion | web | any | DoS of public pages | Per-IP SSE cap (proposed 6), global cap, heartbeat with write deadline, drop slow subscribers | web | U:web | designed |
| A59 | Device-code phishing (attacker starts `moochy login` and sends the victim the code) [S21.1–S21.3] | relay, web | A5 | Attacker device on the victim's account (key log + alert mitigate later) | Approval page shows device name, requested roles, requesting IP country and age of the code, with "only approve a code shown in your own terminal"; codes expire in 10 min; `/api/device/poll` rate-limited (`slow_down`); `KEY_ADDED` alert on every Node of the account | relay, web | U:relay | **gap** |

## 7. Money: billing amplification and denial of wallet (A60–A69)

| ID | Attack | Target | Adv. | Impact | Countermeasure (exact) | Owner | Verif. | Status |
|---|---|---|---|---|---|---|---|---|
| A60 | `n > 1` / multiple choices [S18.1] | worker | A1 | Output × n | Firewall deny | worker | E09 | designed |
| A61 | Predicted outputs, `service_tier`, `speed: fast`, `inference_geo` [S18.2] | worker | A1 | Price multipliers | Firewall deny unless the pledge allows it | worker | U:worker | designed |
| A62 | OpenRouter `models[]` fallback, `route`, `plugins`, `:online` variants [S18.5, S18.6] | worker | A1 | Off-catalog models, per-request fees | Deny; set max-price to the catalog price | worker | U:worker | designed |
| A63 | Cache-write abuse: 1 h `cache_control` on every block (2× input price) [S18.3] | worker, relay | A1 | Donor pays 2× input | Reserve at the write price for `cache_ttl`; pledge policy flag `cache_1h` (default off) | worker, relay | U:worker | **gap** (policy flag) |
| A64 | Max thinking/effort [S18.4] | worker | A1 | Hidden output billed | `effort ≤ max_effort`; `max_tokens ≤ catalog max_output`; reserve at `max_tokens` | worker | U:worker | designed |
| A65 | Donor inflates or deflates usage | node | A2 | Leaderboard fraud | Gateway bands + signed disputes | node | U:node | designed |
| A66 | Denial of wallet by a member (concurrency, rate) [S18.7, S18.8] | relay | A1 | Pool drained | 16 concurrent / 120 per min per member; member monthly cap; per-task cap | relay | E10 | designed |
| A67 | Retry amplification on policy errors | node | A1 | Loops | Non-retryable native errors for policy codes | node | E09, E10 | designed |
| A68 | Estimate gaming with images or PDFs | worker | A1 | Under-reservation | Deterministic estimate with catalog maxima per image/page | worker | V | designed |
| A69 | Relay ignores caps | worker | A3 | Overspend | Worker local reservations | worker | E11 | designed |

## 8. Trust, identity and provider terms (A70–A79)

| ID | Attack | Target | Adv. | Impact | Countermeasure (exact) | Owner | Verif. | Status |
|---|---|---|---|---|---|---|---|---|
| A70 | Sybil donors or maintainers, star-farmed repos [S19.1–S19.3] | relay | A8 | Fake goals, approval spam | Owner approval of donors; GitHub identity; proposed minimum account age 30 days to claim or pledge on the public instance; per-account rate limits | relay | U:relay | designed; **gap** (age threshold) |
| A71 | Fake repo claim | relay | A8 | Pool hijack | Admin check via provider API + owner signature | relay | U:relay | designed |
| A72 | Relay invents an approved donor and receives plaintext | node | A3 | Confidentiality loss | Owner-signed `DONOR_APPROVED` in the key log; Gateways seal only to approved keys | node | **none yet** (key log after Phase 1) | designed; **gap** (no E-test) |
| A73 | Relay originates or replays tasks | worker | A3 | Spend on donor keys | Task signature, membership, ULID freshness ±10 min, served-task set | worker | E16 | designed |
| A74 | Relay tampers with the route header | worker | A3 | Budget theft | HPKE AAD = route bytes | worker | E15 | designed |
| A75 | Relay injects frames into a live task | node | A3 | Forged output | Source-connection check + AEAD | relay, node | E17 | designed |
| A76 | Stolen device | relay | any | Impersonation | `KEY_REVOKED`, immediate drop | relay | U:relay | designed |
| A77 | **Provider terms**: sharing keys or "making your account available" to others is restricted (OpenAI terms; Anthropic Commercial Terms D.4 on resale; OpenRouter on reselling) [S20.1–S20.4] | int | — | Donor bans; project viability | Phase 0 counsel review (06 §14); donor consent text; per-provider allow/deny in the catalog; ship only adapters whose terms permit it | int | M | **gap** (open legal risk) |
| A78 | Laundering stolen keys (LLMjacking) through donations [S1.1–S1.3] | worker | A8 | Abuse attributed to Moochy | Owner approval; account-age threshold; abuse reports → ban; `metadata.user_id` attribution | relay | M | designed (residual) |
| A79 | Donor account banned because of a maintainer's prompts | worker | A1 | Donor harm | Consent, `metadata.user_id`, local journal | worker | M | designed |

## 9. Supply chain and operations (A80–A89)

| ID | Attack | Target | Adv. | Impact | Countermeasure (exact) | Owner | Verif. | Status |
|---|---|---|---|---|---|---|---|---|
| A80 | Crate typosquat or a malicious `build.rs` / proc-macro (`faster_log`, `proc-macro1` via `arrayref`) [S15.1, S15.2] | cli | A7 | Code execution at build time | `Cargo.lock` committed; `cargo build --locked`; `cargo-deny` (advisories, bans, sources = crates.io only); `cargo-vet` for new crates; review every new `build.rs` | int | M (CI) | designed; **gap** (CI absent) |
| A81 | Go module typosquat or proxy-cached backdoor (`boltdb-go`) [S15.3] | relay, e2e | A7 | Backdoored relay | Allowlist of modules (AGENTS §4); `go.sum` committed; `-mod=readonly`; `govulncheck` in CI | int | M (CI) | **gap** (CI absent) |
| A82 | Release pipeline compromise (xz-style) [S15.4] | release | A7 | Backdoored binaries | Sigstore + SLSA provenance; reproducible musl builds; no build steps from release tarballs | int | M | designed |
| A83 | Update hijack | node | A7 | Backdoor | No silent auto-update; signature-verified `moochy update` | node | U:node | designed |
| A84 | Provider key or secrets in logs or crash reports | node | A1 | Key theft | `secrecy`/`zeroize` wrappers whose `Debug` redacts; redaction unit test | node, worker | U:node | designed |
| A85 | Secret-scrubber bypass (novel formats) | node | A9 | Secret to donor | Best-effort; deny secret-shaped files outright (A42) | node | U:node | designed (residual) |
| A86 | Offline brute force of the headless keystore | node | A6 | Device key theft | scrypt N=2¹⁷, r=8, p=1 minimum (or argon2id m=64 MiB); file mode 0600; refuse to start if group/world-readable | node | U:node | **gap** (params unset) |
| A87 | HTTP/2 Rapid Reset / CONTINUATION flood [S9.3, S9.4] | relay | any | DoS | Go toolchain at the latest patch; `govulncheck`; HTTP/2 stream limits left at Go defaults | relay | M | **gap** (CI) |
| A88 | SQLite engine CVEs (modernc tracks upstream; CVE-2025-6965) [S10.2] | relay | any | Memory corruption via crafted SQL | Never run SQL text from input; keep modernc ≥ the SQLite 3.50.2 build | relay | M | designed |
| A89 | Relay resource exhaustion by authenticated nodes (body budgets, wraps > 8, frames for unknown tasks) | relay | A1, A2 | DoS, memory | Per-device and global byte budgets; ≤ 8 wraps; drop and count frames from non-source connections; 1 MiB response buffer per task | relay | U:relay, E20 | designed |

## 10. Top gaps (ranked)

| Rank | ID | Gap | Owner | Severity |
|---|---|---|---|---|
| 1 | A41 | realpath→open TOCTOU and symlink escape in MCP `files` | node | High |
| 2 | A32 / A33 | MCP HTTP `Origin` validation and session↔token binding (the MCP Inspector RCE class) | node | High |
| 3 | A39 | Donor-controlled strings reach the agent's context (model enum, pseudonyms, NACK details) | node, relay | High |
| 4 | A46 / A47 | Terminal-escape and bidi sanitization of delegate results and CLI output | node | High |
| 5 | A77 | Provider terms on key sharing and resale: unresolved, possibly existential | int | High |
| 6 | A54 / A55 / A56 | OAuth `state` + PKCE, session rotation, open-redirect rule | relay, web | High |
| 7 | A59 | Device-code phishing UX and poll rate limits | relay, web | Medium |
| 8 | A12 / A19 | CSWSH Origin refusal and pre-auth deadline on `/v1/node` | relay | Medium |
| 9 | A21 | zstd window and `Frame_Content_Size` rules (bound exists, decoder config unstated) | worker | Medium |
| 10 | A80 / A81 / A87 | No CI yet: cargo-deny/vet, govulncheck, `--locked` | int | Medium |

## Sources

- **S1** LLMjacking. S1.1 Sysdig, https://www.sysdig.com/blog/llmjacking-stolen-cloud-credentials-used-in-new-ai-attack · S1.2 https://www.sysdig.com/blog/llmjacking-targets-deepseek · S1.3 Microsoft Storm-2139, https://blogs.microsoft.com/on-the-issues/2025/02/27/disrupting-cybercrime-abusing-gen-ai/
- **S2** Coding-agent prompt injection. S2.1 CVE-2025-53773, https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/ · S2.2 CVE-2025-54135/54136, https://www.tenable.com/blog/faq-cve-2025-54135-cve-2025-54136-vulnerabilities-in-cursor-curxecute-mcpoison · S2.3 https://github.com/advisories/GHSA-x56v-x2h6-7j34 · S2.4 CVE-2025-8217, https://github.com/aws/aws-toolkit-vscode/security/advisories/GHSA-7g7f-ff96-5gcw
- **S3** MCP. S3.1 https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks · S3.2 https://blog.trailofbits.com/2025/04/21/jumping-the-line-how-mcp-servers-can-attack-you-before-you-ever-use-them/ · S3.3 https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices · S3.4 https://modelcontextprotocol.io/specification/2025-11-25/basic/transports · S3.5 CVE-2025-49596, https://www.oligo.security/blog/critical-rce-vulnerability-in-anthropic-mcp-inspector-cve-2025-49596 · S3.6 CVE-2025-6514, https://jfrog.com/blog/2025-6514-critical-mcp-remote-rce-vulnerability/
- **S4** WebSocket. S4.1 CVE-2025-52882, https://securitylabs.datadoghq.com/articles/claude-mcp-cve-2025-52882/ · S4.2 https://pkg.go.dev/nhooyr.io/websocket · S4.3 CVE-2020-27813, https://nvd.nist.gov/vuln/detail/CVE-2020-27813 · S4.4 RFC 7692 §8, https://www.rfc-editor.org/rfc/rfc7692.html
- **S5** AEAD/HPKE. S5.1 https://eprint.iacr.org/2016/475 · S5.2 RFC 9180, https://www.rfc-editor.org/rfc/rfc9180.html · S5.3 https://www.usenix.org/system/files/sec21-len.pdf · S5.4 https://eprint.iacr.org/2019/016
- **S6** Ed25519. S6.1 https://eprint.iacr.org/2020/1244 · S6.2 https://hdevalence.ca/blog/2020-10-04-its-25519am/ · S6.3 https://github.com/hdevalence/ed25519consensus · S6.4 https://github.com/advisories/GHSA-q67f-28xg-22rw
- **S7** JSON. S7.1 https://bishopfox.com/blog/json-interoperability-vulnerabilities · S7.2 https://blog.trailofbits.com/2025/06/17/unexpected-security-footguns-in-gos-parsers/ · S7.3 https://go.dev/doc/go1.25 · S7.4 RFC 7493, https://www.rfc-editor.org/rfc/rfc7493
- **S8** zstd. S8.1 RFC 8878, https://www.rfc-editor.org/info/rfc8878/ · S8.2 RFC 9659, https://www.ietf.org/rfc/rfc9659.html · S8.3 https://github.com/advisories/GHSA-87m9-rv8p-rgmg · S8.4 https://pkg.go.dev/github.com/klauspost/compress/zstd
- **S9** HTTP. S9.1 CVE-2025-22871, https://app.opencve.io/cve/CVE-2025-22871 · S9.2 CVE-2023-39326, https://github.com/golang/go/issues/64433 · S9.3 https://pkg.go.dev/vuln/GO-2024-2687 · S9.4 https://www.cisa.gov/news-events/alerts/2023/10/10/http2-rapid-reset-vulnerability-cve-2023-44487 · S9.5 https://blog.cloudflare.com/exposing-go-on-the-internet/
- **S10** SQLite. S10.1 https://www.sqlite.org/security.html · S10.2 https://access.redhat.com/security/cve/cve-2025-6965
- **S11** Files. S11.1 CVE-2022-21658, https://blog.rust-lang.org/2022/01/20/cve-2022-21658/ · S11.2 CVE-2025-53109/53110, https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic/ · S11.3 https://man7.org/linux/man-pages/man2/openat2.2.html · S11.4 https://github.com/bytecodealliance/cap-std
- **S12** SSRF. S12.1 https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html · S12.2 https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-options.html · S12.3 https://github.com/directus/directus/security/advisories/GHSA-wv3h-5fx7-966h
- **S13** Terminal escapes. S13.1 https://blog.trailofbits.com/2025/04/29/deceiving-users-with-ansi-terminal-codes-in-mcp/ · S13.2 https://embracethered.com/blog/posts/2024/terminal-dillmas-prompt-injection-ansi-sequences/ · S13.3 CVE-2024-56803, https://www.netsecurity.no/en/technical-blog/code-execution-through-ghostty-window-title
- **S14** Logs. S14.1 CWE-117, https://cwe.mitre.org/data/definitions/117.html · S14.2 CVE-2021-44228, https://nvd.nist.gov/vuln/detail/CVE-2021-44228
- **S15** Supply chain. S15.1 https://blog.rust-lang.org/2025/09/24/crates.io-malicious-crates-fasterlog-and-asyncprintln/ · S15.2 https://blog.rust-lang.org/2026/08/20/supply-chain-attack-on-arrayref/ · S15.3 https://socket.dev/blog/malicious-package-exploits-go-module-proxy-caching-for-persistence · S15.4 CVE-2024-3094, https://openssf.org/blog/2024/03/30/xz-backdoor-cve-2024-3094/
- **S16** Timing. S16.1 Crosby et al., https://accurate-voting.rice.edu/pubs/index.html · S16.2 https://www.usenix.org/conference/usenixsecurity20/presentation/van-goethem · S16.3 https://docs.rs/subtle/latest/subtle/trait.ConstantTimeEq.html
- **S17** Web. S17.1 RFC 9700, https://www.rfc-editor.org/rfc/rfc9700.html · S17.2 https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html · S17.3 https://github.com/advisories/GHSA-63f2-6959-2pxj
- **S18** Billing. S18.1 https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create · S18.2 https://simonwillison.net/2024/Nov/4/predicted-outputs/ · S18.3 https://platform.claude.com/docs/en/build-with-claude/prompt-caching · S18.4 https://platform.claude.com/docs/en/build-with-claude/extended-thinking · S18.5 https://openrouter.ai/docs/guides/routing/model-fallbacks · S18.6 https://openrouter.ai/docs/guides/features/plugins/web-search · S18.7 https://arxiv.org/pdf/2104.08031 · S18.8 https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/
- **S19** Sybil. S19.1 https://www.microsoft.com/en-us/research/publication/the-sybil-attack/ · S19.2 https://arxiv.org/html/2412.13459v1 · S19.3 https://docs.github.com/en/site-policy/github-terms/github-terms-of-service
- **S20** Provider terms. S20.1 https://www.anthropic.com/legal/commercial-terms · S20.2 https://code.claude.com/docs/en/legal-and-compliance · S20.3 https://openai.com/policies/row-terms-of-use/ · S20.4 https://openrouter.ai/terms
- **S21** Device code. S21.1 RFC 8628 §5.4, https://www.rfc-editor.org/rfc/rfc8628#section-5.4 · S21.2 https://www.microsoft.com/en-us/security/blog/2025/02/13/storm-2372-conducts-device-code-phishing-campaign/ · S21.3 https://www.praetorian.com/blog/introducing-github-device-code-phishing/
- **S22** Channel binding and Host. S22.1 RFC 9266, https://www.rfc-editor.org/rfc/rfc9266.html · S22.2 https://portswigger.net/web-security/host-header

Source caveats: collected 2026-10-01. A few 2026 advisories (CVE-2026-*, the arrayref incident) and the OWASP LLM10 URL were taken from advisory databases and not re-checked against NVD.
