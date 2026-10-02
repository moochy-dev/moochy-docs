# Moochy implementation contract (Phase 1 walking skeleton → beta) — CLOSED SOURCE (internal)

Normative for every implementer. The design rationale lives in `docs/plan/` (03 = wire protocol, 05 = ledger, 06 = security, 07 = client). When this file and the plan disagree, **this file wins** for encodings and interfaces; raise the conflict in your final report.

## 0a. Source boundary (product owner decision, 2026-10-01)

| Side | Paths | License |
|---|---|---|
| **Open source** (published as `moochy-cli`) | `cli/**`, `spec/proto/**`, `spec/vectors/**`, `spec/protocol.md` (public protocol spec), `spec/KEYLOG.md`, `docs/guides/**`, client release tooling under `deploy/client/**` | **Apache-2.0**, contributions with DCO sign-off (`Signed-off-by:`) |
| **Closed source** (the `moochy-core` monorepo: backend + frontend) | `relay/**` (incl. `relay/internal/web/**`), `e2e/**`, `deploy/**` except `deploy/client/**`, `docs/plan/**`, `docs/ops/**`, `docs/security/**`, `docs/TRACEABILITY.md`, `spec/CONTRACT.md` | Proprietary, all rights reserved |

Rules: **open code never imports, links, or copies closed code** (the Rust client depends only on open crates and `spec/`); closed code may use open code. Everything that touches donor keys, maintainer code, or cryptography is in the open client, so users never need to trust the closed relay (it only sees ciphertext). Self-hosting the relay is **not** offered; the Node's relay URL stays configurable for development and tests. The product stays **100% free** (no fees, no commission, no paid tier). Public wording: **"Open-source client (Apache-2.0) · 100% free"** — never "100% open source".

## 0. Repository layout and ownership

| Path | Language | Owner (agent) | Notes |
|---|---|---|---|
| `spec/` | — | integrator | This contract; `spec/proto/moochy/v1/link.proto` (shared gRPC link, integrator-owned); `spec/vectors/*.json` written by `mo-proto` |
| `spec/proto/moochy/v1/local.proto` | protobuf | `mo-node` | Node local control plane (CLI / MCP shim ↔ Node over a 0600 Unix socket) |
| `relay/proto/moochy/admin/v1/admin.proto` | protobuf (closed) | `mo-relay` | Relay operator admin plane (over a 0600 Unix socket); closed source, so NOT under `spec/proto` |
| `cli/` | Rust workspace | — | `cli/Cargo.toml` = workspace root (members + profiles only; owned by integrator) |
| `cli/crates/proto` | Rust lib `moochy-proto` | `mo-proto` | Wire types, `lp`, labels, crypto, frames, receipts, vector generator |
| `cli/crates/worker` | Rust lib `moochy-worker` | `mo-worker` | Provider-facing logic, **no dependency on `moochy-proto`**: firewall tables + recursive validator, provider adapters (anthropic, openrouter, deepseek, openai, xai, local OpenAI-compatible hosts: Ollama, LM Studio, vLLM, llama.cpp), safe mutations, SSE/usage parsers for both dialects, tool-call inspection (structural checks + tripwire), outbox file, served-task set, local reservation counters |
| `cli/crates/sandbox` | Rust lib `moochy-sandbox` | `mo-sandbox` | Maintainer-side `moochy run` sandbox (Linux namespaces + Landlock + seccomp; macOS Seatbelt) and donor-side Worker privilege separation (CONTRACT §15); the only crate allowed a small audited `unsafe` module |
| `cli/crates/node` | Rust lib+bin `moochy` | `mo-node` | Node binary: CLI, config, keystore, relay link (TLS + channel binding), gateway API door + MCP door (stdio + Streamable HTTP), local security (tokens, Host check), wiring of `moochy-proto` (sealing) and `moochy-worker` (execution) |
| `cli/crates/node/src/{worker,link,node,keylog,keystore,approve,ctl,login,keycheck}.rs` + new files for lockdown/validator/monitor wiring | Rust (part of `moochy`) | `mo-donor` | Split from `mo-node` on 2026-10-01 to parallelize: donor side (Worker serving, relay link, drain, in-flight durability, validator child wiring, `lockdown_self`), keys (keystore, owner key §15.4, `keys rotate`), key-log monitor wiring, approvals. `mo-node` keeps the gateway side (gate, gateway, task, engine, mcp, files, scrub, connect, native, `moochy run`) and `cli.rs`/`config.rs`; both may add small, separate hunks to `cli.rs` and `lib.rs` |
| `relay/` | Go module `moochy.dev/relay` | `mo-relay` | Relay binary `relay`; everything except `relay/internal/web/**` |
| `relay/internal/web/**` | Go (stdlib only) | `mo-design` (was `mo-web`) | Pages, fragments, CSS, SSE hub; exposes the interface in §9 |
| `relay/internal/web/static/motion.{css,js}` + the signed-in app templates (`p-overview`, `p-activity*`, `p-donation*`, `p-donate*`, `p-devices`, `p-members`, `p-repos`, `p-settings`, `p-console`, `p-button`, `p-claim`, `p-receipt`) | CSS/JS/Go templates | `mo-motion` | Split from `mo-design` on 2026-10-02 (product owner: much richer effects, animations, transitions): the motion system of the signed-in app. `mo-design` keeps the tokens in `app.css`, `layout.html`, `frags.html`, the mascot and illustrations, and the public pages; `mo-motion` adds only a `<link>`/`<script>` line to `layout.html` and asks `mo-design` for anything else there |
| `e2e/` | Go module `moochy.dev/e2e` | `mo-e2e` | Harness, fake providers, scenarios; except `e2e/attacks/**` |
| `e2e/attacks/**`, `docs/security/**` | Go + Markdown | `mo-sec` | Attack catalog, attack scenarios, evil-peer tooling |
| `relay/internal/tlog/**`, `cli/crates/keylog/**` | Go + Rust lib `moochy-keylog` | `mo-keylog` | Key log: append, tlog hashing/proofs, C2SP tiles, signed checkpoints (only for replicated sizes), hourly public Git anchor; owner-signed `REPO_CLAIMED` / `DONOR_APPROVED` / `MEMBER_*` entries; Rust verifier + monitor library (mirror, consistency, own-key and owner alerts) |
| `relay/internal/oauth/**` | Go | `mo-oauth` | GitHub + GitLab OAuth, web sessions, handle choice at signup (§11), repo-claim admin check via provider APIs, device-approval web page logic |
| `relay/internal/metrics/**`, `deploy/**`, `docs/ops/**` | Go + config + Markdown | `mo-ops` | Prometheus metrics registry, SLOs, alert rules, runbooks, systemd units, Litestream config, internal deployment recipe, drain-and-restart procedure, backup/restore drill script |
| `docs/plan/**`, `docs/guides/**`, `SECURITY.md`, `cli/SECURITY.md` | Markdown | `mo-docs` | Keep the plan consistent with CONTRACT/ADRs; donor, maintainer, headless-node, and MCP/API integration guides; also the public `spec/protocol.md` |
| `relay/internal/docsite/**` | Go (closed) | `mo-docs` | Public docs site (2026-10-02): renders `docs/guides/**` (embedded) as `/docs`, `/docs/{slug}`, `/docs/{slug}.md`, `/llms.txt`, `/llms-full.txt`; exposes an `http.Handler` that mo-relay mounts in a few lines; pages use mo-design's layout/stylesheet through an exported web helper |
| `relay/internal/notify/**` | Go (closed) | `mo-notify` | Email notifications through Resend (CONTRACT §16): outbox, templates, preferences, unsubscribe, Resend webhooks, fake Resend for dev/E2E; exposes hooks mo-relay calls on events and handlers mo-relay mounts; the Settings UI is mo-design's, the sign-up email step mo-oauth's |
| `relay/internal/web/review/CRITIQUE.md`, `relay/internal/web/review/references/**` | Markdown + captures | `mo-critic` | Independent design critic (2026-10-02): reference research, scored critiques of every pass from the Playwright videos/captures; never edits product code |

Never edit a path you do not own. Need a change elsewhere? Write it under `## Requests to other owners` in your final report.

## 1. Encodings (both languages)

- **Machine-to-machine messages are protobuf over gRPC** (§12, `spec/proto/moochy/v1/link.proto`). **Signed artifacts stay JSON bytes** carried verbatim in `bytes` fields: route header, inner payload, receipts, projections, catalog. They are signed and stored as exact bytes and parsed with the strict rules below.
- **Parser-differential rule:** every JSON parse that feeds a security or money decision (route header, receipts, provider request bodies in the Worker firewall, provider responses for usage, MCP messages) MUST reject duplicate object keys, invalid UTF-8, lone surrogates, numbers outside i64/f64, and nesting deeper than 64. Go must not use plain `encoding/json` for these (use a decoder that detects duplicates); Rust must not rely on last-key-wins `serde_json::Value`. When the Worker mutates a body, it re-serializes from the validated tree; it never forwards bytes that a different parser could read differently.
- Bytes in JSON: **base64url without padding** (`RFC 4648 §5`). Ids: `task` = ULID canonical 26-char string; `device_id` = `d_` + ULID; `user_id` = `u_` + ULID (internal, never public); public user **pseudonym** = `ps_` + 16 random chars from lowercase Crockford base32 (`0-9a-hjkmnp-tv-z`, 80 bits, CSPRNG; never derived from `user_id`); `repo_id` = `r_` + ULID; `pledge_id` = `p_` + ULID. Money: JSON integer µ$ (`*_uusd`).
- `lp(a, b, …)` = concatenation of `u32_be(len(x)) || x` for each field. Integer fields are encoded with the width written at the call site (`u32(x)` = 4 bytes BE, `u64(x)` = 8 bytes BE); an integer written without a width is `u64`. Strings as UTF-8 bytes. Test vectors pin every width.
- Hash = SHA-256. HKDF = HKDF-SHA256 (RFC 5869); `Expand` length 32 unless stated.
- Signatures: Ed25519, **verification = ZIP-215** in both languages (Rust `ed25519-zebra` or equivalent; Go `github.com/hdevalence/ed25519consensus`). Signing is plain RFC 8032.
- AEAD: ChaCha20-Poly1305 (RFC 8439). Nonce (12 bytes) = `0x00 * 8 || u32_be(seq)`.
- HPKE: RFC 9180 base mode, KEM 0x0020 DHKEM(X25519, HKDF-SHA256), KDF 0x0001, AEAD 0x0003. `suite_id` string = `moochy.v1.hpke.x25519-sha256-chacha20poly1305`.

## 2. Labels (exact strings, all inside `lp`)

`moochy/v1/auth`, `moochy/v1/device-start`, `moochy/v1/req`, `moochy/v1/resp`, `moochy/v1/wrap`, `moochy/v1/task`, `moochy/v1/salt`, `moochy/v1/req-commit`, `moochy/v1/resp-commit`, `moochy/v1/provider-req`, `moochy/v1/receipt`, `moochy/v1/projection`, `moochy/v1/resp-progress`, `moochy/v1/dispute`, `moochy/v1/detail`, `moochy/v1/catalog` (signed catalog: Ed25519 by the key-log key over `lp(moochy/v1/catalog, json)`), `moochy/v1/key-rotate`, `moochy/v1/key-revoke`; key log: `moochy/v1/keylog`, `moochy/v1/keylog-sig`, `moochy/v1/key-pop`, `moochy/v1/receipt-log` (exact use in `spec/KEYLOG.md`).

## 3. Keys and derivations (from docs/plan/03 §6, made exact)

- `CK`: 32 random bytes, fresh per sealed body.
- `K_req = HKDF(salt = "", ikm = CK, info = lp("moochy/v1/req", task_id))`.
- Request chunk `i`: `AEAD(K_req, nonce(i), aad = lp("moochy/v1/req", kind_byte, task_id_16B, u32(i), last_byte))` with `kind_byte` the constant `0x01` (kept for domain separation; frame kinds no longer exist), `task_id_16B` the 16 raw ULID bytes, `last_byte` `0x01`/`0x00`; plaintext ≤ 65,497 bytes.
- Wrap: `HPKE.SealBase(pkR = enc_pub, info = lp("moochy/v1/wrap", suite_id, task_id), aad = route_header_bytes, pt = CK)` → `enc (32) || ct (48)` = 80 bytes.
- `R`: 32 random bytes per attempt (Worker). `RK = HKDF(salt = R, ikm = CK, info = lp("moochy/v1/resp", task_id, worker_device, u64(attempt)))`.
- Response chunk: `AEAD(RK, nonce(seq), aad = lp("moochy/v1/resp", task_id_16B, u64(attempt), R, u32(seq), last_byte))`.
- Sealed refusal detail (Nack/Failed `sealed_detail`): `K_det = HKDF(salt = R, ikm = CK, info = lp("moochy/v1/detail", task_id, worker_device, u64(attempt)))`; `sealed_detail = AEAD(K_det, nonce = 12 zero bytes, aad = lp("moochy/v1/detail", task_id_16B, u64(attempt), code), pt = UTF-8 detail ≤ 1 KiB)`. One detail per attempt, so the zero nonce is never reused under a key.
- Salts: `S` 32 random bytes in the inner payload; `S_x = HKDF(salt="", ikm=S, info=lp("moochy/v1/salt", name))` for name ∈ {`req`,`resp`,`pid`}.
- Gateway task signature: `Ed25519(gw_key, lp("moochy/v1/task", task_id, repo_id, route_header_bytes, body_sha256, headers_sha256))`.
- Auth signature: `Ed25519(dev_key, lp("moochy/v1/auth", nonce, dialed_origin, tls_exporter, device_id))`; `tls_exporter` = RFC 9266 (`EXPORTER-Channel-Binding`, empty context, 32 bytes). `dialed_origin` = the exact origin the Node dialed for the gRPC link, scheme included: `https://host:port`.
- Route header bytes = the exact UTF-8 JSON bytes the Gateway puts in `SubmitOpen.route`; the Relay forwards the same bytes in `Assign.route` (raw protobuf `bytes`, no base64).

## 4. Inner payload (sealed request plaintext, before zstd)

JSON: `{"v":1,"body_b64":..., "body_sha256":..., "headers": {"anthropic-version": "...", "anthropic-beta": "..."}, "S":..., "gateway_device":..., "task_sig":...}`; the whole JSON is zstd-compressed (level 3) then chunked and sealed.

## 5. Messages

**Superseded by `spec/proto/moochy/v1/link.proto`** (gRPC, §12). The plan's message catalog (03 §5) maps 1:1 onto it; the 23-byte binary frame header of plan 03 §4.2 is gone (the gRPC stream identifies the task; `Chunk{attempt, seq, last, ct}` carries the rest; the AEAD AAD in §3 is unchanged). Historical field list, kept for reference: `t`, `task`, `attempt`, `route_b64`, `wraps` (`[{"worker_device","wrap"}]`), `body_len`, `body_chunks`, `worker_device`, `R`, `code`, `retryable`, `retry_after_ms`, `sealed_detail`, `receipt_b64`, `donor_sig`, `projection_b64`, `projection_sig`, `seq`, `running_hash`, `sig`, `slots_free`, `models` (`[{"dialect","model","rl_headroom"}]`), `pledges`, `window_open`, `local_cap_left`, `tasks` (known_tasks), `since`.
Route header JSON fields (03 §7.1): `repo_id, dialect, model, effort, max_tokens, est_input_tokens, cache_ttl, stream, affinity, flags`. There is no binary frame header any more (ADR-33).

## 6. Process interface (what the e2e harness runs)

### Relay
`relay serve --addr 127.0.0.1:0 --grpc-addr 127.0.0.1:0 --db <path> --tls-cert <pem> --tls-key <pem> [--admin-socket <path>] [--dev] [--catalog <json>]`
- `--addr` serves HTTP (web, dev API); `--grpc-addr` serves the gRPC `NodeLink` service (TLS 1.3, h2). Separate listeners so the gRPC server keeps its native HTTP/2 hardening.
- Prints exactly one JSON line to stdout when ready: `{"event":"ready","addr":"127.0.0.1:P1","grpc_addr":"127.0.0.1:P2"}`. Logs go to stderr (JSON, `log/slog`).
- `--dev` is refused unless `--addr` is a loopback address. It enables the dev API below.
- Endpoints: gRPC `moochy.v1.NodeLink` on `--grpc-addr` (Session, Submit, Serve, DeviceStart, DevicePoll); on `--addr` the web routes, and with `--dev`:
  - `POST /dev/user {"username"}` → `{"user_id","pseudonym","session"}` (session = cookie value)
  - `POST /dev/repo {"owner","name","owner_username"}` → `{"repo_id"}`
  - `POST /dev/member {"repo_id","username","cap_uusd_month"?}`
  - `POST /dev/pledge {"donor_username","repo_id","budget_uusd","per_task_cap_uusd","policy":{"models":[],"max_effort","dialects":[],"flags":[]}}` → `{"pledge_id"}` (approved immediately; relay-asserted in Phase 1)
  - `POST /dev/device/approve {"user_code","username","roles":["gateway"|"worker"],"repo_scope"?}` → `{"device_id"}`
  - `GET /dev/state` → JSON: pledges (budget/spent/reserved), members, devices, attempts (status, cost), receipts count. For assertions only.
  - `POST /dev/chaos {"ignore_caps":bool,"tamper_route":bool,"replay_assign":bool,"inject_frame":bool}`: makes the relay misbehave like a malicious operator (skip cap checks; flip one byte of the route header sent to the Worker; deliver the same `Assign` twice; inject a forged `Chunk` into the victim Gateway's own live Submit stream). Used by E11, E15–E17 to prove the **clients** defend themselves.
- Catalog: `--catalog` JSON file with entries per 05 §2.2; default built-in test catalog when absent.

### Node
`moochy --home <dir> <command>`; all state under `<dir>`. Keystore backend for tests: encrypted file, passphrase from env `MOOCHY_PASSPHRASE`.
- `moochy login [--relay URL] [--ca-file <pem>] --roles gateway,worker --headless` — `--relay` defaults to the public relay `https://relay.moochy.dev:8443`; tests pass `--relay https://127.0.0.1:GRPCPORT --ca-file <pem>`; any non-default relay requires `MOOCHY_INSECURE_DEV=1` and prints a warning (attack A135) → prints `{"event":"device_code","user_code":"XXXX-XXXX"}` then blocks until approved, then `{"event":"logged_in","device_id":"d_…"}`.
- **Command surface on main** (2026-10-02; `moochy --help` is the reference, guides are diffed against it): `login`, `logout`, `up`/`down`, `status`, `doctor`, `keys add|list|rotate`, `owner init|rotate`, `donate`, `donations`, `pending`, `approve` (alias `accept`), `members add|remove`, `claim <owner/repo>`, `connect`, `run`, `verify`, `journal`, `config set`. **Amounts on the command line are dollars** (`--cap 20` = $20.00); µ$ only in `*_uusd` config keys and the wire.
- **Pinned key-log key** (integrator decision, 2026-10-02): the release build of `moochy` compiles in the verifier key of the default relay's key log (`relay.moochy.dev`), set by the release pipeline (`MOOCHY_DEFAULT_LOG_VKEY` at build time). A build without it (every dev build today) has no pinned key: nodes then require `--log-key` (or `MOOCHY_INSECURE_DEV=1`) and never fall back to trusting the relay's word.
- `moochy keys add <anthropic|openrouter|deepseek|openai|xai|local> --key-stdin [--base-url http://127.0.0.1:PORT]` — `--base-url` is accepted **only** for loopback hosts **and** only when env `MOOCHY_INSECURE_DEV=1`; otherwise refused.
- `moochy config set <key> <value>` for `monthly_limit` (dollars; `device_monthly_cap_uusd` stays as the µ$ alias), `slots_max`, `gateway_addr`, `firewall_level`, `schedule`. When `gateway_addr` is unset, the first `up` picks a free loopback port, persists it, and reuses it on every later start (clients keep a stable base URL); tests set `127.0.0.1:0` explicitly.
- `moochy up --foreground` → when ready writes `<dir>/state/node.json` `{"device_id","gateway_url":"http://127.0.0.1:P","mcp_url":"http://127.0.0.1:P/mcp","pid"}` and prints `{"event":"ready",...same}`.
- `moochy env --repo owner/name --json` → `{"anthropic_base_url","openai_base_url","token"}`.
- `moochy mcp --repo owner/name` → stdio MCP server (JSON-RPC 2.0, newline-delimited); the shim talks to the running Node through the gRPC `LocalControl` service on the 0600 Unix socket `<dir>/state/node.sock`.
- All other CLI commands that act on a running Node (`status`, `pause`, `resume`, `approve`, `members`, `journal`) use the same `LocalControl` service.
- Exit codes: 0 ok, 2 usage, 3 auth/approval refused, 4 network, 10 internal.

## 7. Fake providers (e2e) — behaviour switches

Fakes are Go `httptest` servers. Behaviour is chosen by **tags in the last user message text**: `#tokens:N` (output tokens), `#fail:429|529|500` (before stream), `#cut:K` (drop connection after K SSE events), `#slow:MS` (delay before headers), `#tool:<json>` (emit one tool call with that input), `#model:<id>` (report a different model). Anthropic fake: `POST /v1/messages` (SSE identical in shape to the real API, with `message_start` usage and `message_delta` final usage, cache fields), `GET /v1/models`. OpenAI-style fakes (`openai`, `deepseek`, `openrouter`): `POST /v1/chat/completions` (SSE `data:` chunks, final usage chunk only when `stream_options.include_usage`; DeepSeek adds cache hit/miss fields; OpenRouter adds `usage.cost`), `GET /v1/models`. OpenRouter and DeepSeek fakes also serve the Anthropic shape on their Anthropic-compatible prefix. Every fake records received requests (headers + body) for assertions.

## 8. E2E scenarios (the definition of "working")

IDs are stable; each is one Go test `TestE<NN>_<name>`. A scenario may `t.Skip("pending: <component>")` until its components exist, but never be deleted.

| ID | Scenario |
|---|---|
| E01 | Anthropic streaming through the API door: client receives the same SSE events as the provider sent (semantically identical; framing and JSON are the Gateway's canonical re-emission, §15.4 — integrator decision N4); one receipt; `spent` = catalog cost; reservation released |
| E02 | OpenAI dialect via OpenRouter donor; usage forced on; cost = OpenRouter-reported cost |
| E03 | Anthropic dialect via DeepSeek donor and via OpenRouter donor |
| E04 | MCP stdio: initialize, tools/list (two tools, model enum), `moochy_delegate` returns the fake's text wrapped as untrusted content |
| E05 | MCP Streamable HTTP: same as E04; missing/invalid bearer → 401 |
| E06 | Failover: worker A killed before `task.started` → worker B serves; exactly one charge |
| E07 | Provider 429 before start → rerouted; zero cost on the 429 attempt |
| E08 | Cancel: client disconnects mid-stream → provider request aborted (fake sees disconnect), receipt `cancelled` |
| E09 | Firewall: `mcp_servers`, server tool, file-id source, URL image, `n:2`, unknown top-level field → native 400, non-retryable, zero spend, fake never called |
| E10 | Budget: per-task cap → `over_task_cap`; exhausted pledge → `quota_exceeded`; both non-retryable |
| E11 | Device local cap enforced by the Worker even when the relay ignores caps (chaos `ignore_caps`) |
| E12 | Relay `kill -9` mid-stream → restart → outbox replay → exactly one settlement, no leaked reservations |
| E13 | Privacy canary: unique canary strings in prompts and outputs never appear in the relay DB file, WAL, or logs |
| E14 | Local gateway hardening: wrong token → 401; bad `Host` header → 403; no CORS headers; binds loopback only |
| E15 | Route tamper (chaos `tamper_route`) → worker refuses (`bad_envelope`), provider never called, zero spend |
| E16 | Task replay (chaos `replay_assign`) → second delivery refused (`unauthorized_task`), provider called once |
| E17 | Frame injection (chaos `inject_frame`: the malicious relay itself injects a forged `Chunk` into the live Submit stream toward the Gateway) → forged bytes never reach the client: the Gateway fails the task on the first AEAD failure with a native retryable error and logs `bad_envelope`; no forged byte appears in the client output |
| E18 | Tool-call gating: fake emits a tool call not in `tools[]` / failing schema / `curl … | sh` → replaced with an error tool result |
| E19 | Web: `/p/{owner}/{repo}` renders (palette tokens present), SSE `/p/{owner}/{repo}/events` delivers a fragment after a task |
| E20 | Throughput smoke: 200 concurrent streamed tasks across 3 workers complete; p50 relay-added latency reported |
| E21 | Unique usernames: a duplicate, a case variant (`Alice` vs `alice`), a reserved word (`admin`), an invalid/confusable handle (`аlice` with Cyrillic а), and a tombstoned handle are all refused; a rename redirects the old handle |

## 9. Web interface (between `mo-relay` and `mo-web`)

Package `moochy.dev/relay/internal/web` exports `func New(src Source) http.Handler` and the `Source` interface (read-only queries: repo by slug, pool summary, goal numbers, recent projections, donor station data) plus `func (h) Publish(topic string, ev Event)` for SSE. `mo-web` defines the interface and ships a fake `Source` for its own tests; `mo-relay` implements it.

**Visual direction (product owner, 2026-10-02 — supersedes the strict-monochrome rule of 2026-10-01):** keep the simple, uncluttered landing, the hamster mascot, real provider logos and the "Donate tokens" voice; drop the strict monochrome. The brand is **playful, warm and alive** — characterful, never corporate-bland, never generic "AI-made".
- **Palette (product owner, 2026-10-02 second review — "not a fan of the dark orange… same for the hamster color"):** no orange, apricot or brown anywhere. Ink (deep navy), Paper (white) and Sky (light blue) are the brand; one warm-but-light accent, **Butter** (soft sunny yellow) for donated tokens (little suns/coins), highlights and calls to action; signals **Mint** (healthy/success), **Butter-deep** (attention) and **Coral-soft** (stop/error); tints/shades for both themes; dark mode is deep navy (never brown). The mascot is a **"cloud hamster"**: soft white/cream fur shaded with Sky, light-blue ears, tiny blush cheeks, navy outline. Two alternates are kept as switchable themes for the product owner to compare (a Mint hamster, a Lilac-grey hamster, each with its palette); the product owner picks the default. WCAG AA for all text and controls.
- **Allowed now:** color-blocked sections and cards, illustrated scenes and spot illustrations around the mascot, playful shapes and patterns, subtle grain/texture, soft multi-color fields *inside an illustration* (never as a page wallpaper), color in data visualisation.
- **Still banned (the generic "AI look"):** purple/blue neon gradients and glows, glassmorphism, particle/constellation backgrounds, shimmer/gradient text, floating 3D blobs, stock AI imagery, scroll-jacking (the page always scrolls normally).
- **Motion system (signature of the product):** the mascot is a living character in SVG + CSS/Web Animations — idle breathing and blinking, eyes gently following the pointer, reactions to real events (cheers when a donation is accepted, a happy "nom" when a request is served, sleeps when your devices are offline, worried when a limit is near). Landing: scroll-driven storytelling with CSS scroll-driven animations (`animation-timeline: view()`/`scroll()`, progressive enhancement), an animated token flow from a donor's machine to a project (SVG path drawing + travelling tokens), live counters fed by the real SSE stream, staggered reveals, logo and button micro-interactions. App: page transitions with the View Transitions API (cross-document `@view-transition { navigation: auto; }`, shared elements such as a project card morphing into its page), list rows animating in/out as live data arrives, animated progress and limit bars, skeletons, toasts, an animated light/dark switch, the donate-button studio preview morphing between styles.
- **Craft and performance:** every motion has a purpose (orient, give feedback, or delight once); UI motion 120–400 ms, springy easing for the mascot; transform/opacity only (60 fps, no layout thrash); no animation delays content or input, and CONTRACT §13 budgets still hold; ship small (CSS, Web Animations, View Transitions; a motion library only if ≤ 15 KB gzip and justified). `prefers-reduced-motion` turns every non-essential animation off, and every page still works without JavaScript.
- **CLI:** friendly colored output (the mascot glyph, spinners, progress bars, clear success/warning colors) that respects `NO_COLOR`, `--json` and non-TTY output.

**Brand mascot:** Moochy has its own "pet" — a small, friendly, geometric creature drawn in the three base colors, legible as a 16 px favicon and as an illustration; a few expressions (idle, happy when a task completes, asleep when the pool is idle) used sparingly in empty states and loading, never as decoration on every surface.

**Motion:** subtle and functional only — state changes, list insertions, page transitions, the mascot's small expressions; first-view fades limited to one per section; `prefers-reduced-motion` turns it all off.

**Vocabulary and voice (product owner):** the key phrase is **"Donate tokens"**. Every user-facing word follows `docs/brand/VOICE.md` (normative): "pledge" is never shown (it is a **donation**; budget → monthly limit; reclaim → stop donating; station → Dashboard; console → Project settings; …), with its tone rules and banned words. Internal identifiers keep their names.

**UI/UX quality bar (product owner, 2026-10-02, verbatim: "much more dynamic UI/UX, motion design, effects, animations, be much much more creative … raise significantly the bar … more than 2 passes … not over engineered but by far extreme good quality on UI/UX, from both the landing page and the project itself").**
- *Ambition:* the product should feel alive and crafted, at the level of the best product sites and apps of 2026, while staying simple to read and to use. Directions (to be explored, refined or replaced by better ideas, not a checklist): the landing as one living sky scene — the cloud hamster on its cloud, donated tokens as little suns travelling from a donor's laptop to a project, layered parallax on the scroll timeline (never scroll-jacking), kinetic headline reveal, live token sparkles when real requests happen; an interactive "what my donation does" slider that animates the projected tokens per month; provider logos and project cards with tactile hover depth. In the app: a sky header that reflects real state (sunny when donating, clouds when paused, night when your devices sleep), shared-element transitions everywhere a thing becomes a page, staggered list entrances, spring-based micro-interactions, a ⌘K command palette, charts and sparklines that draw in and update live, celebratory but brief moments (first donation accepted, a project's goal reached), a short guided first-run with the mascot, the studio preview morphing as you edit.
- *Restraint:* every animation has a purpose, never blocks reading or input, never loops forever except the mascot's idle; budgets (§13, page weight) hold; WCAG AA, keyboard and screen-reader paths, `prefers-reduced-motion` and no-JS paths are part of the definition of done; no heavy frameworks (CSS, Web Animations, View Transitions, SVG; any library ≤ 15 KB gz and justified).
- *Process — at least four passes:* each pass = build → Playwright videos and captures (landing scroll, the main app flows, light/dark, 360/1280/1920) → an independent written critique by **mo-critic** (read-only design reviewer, scored rubric: delight, clarity, consistency, craft/polish, performance, accessibility, restraint; with concrete, prioritised changes and best-in-class references) → the integrator's review → the next pass. Pass 1 = the new palette and cloud hamster; pass 2 = the motion system at full ambition; pass 3 = polish and consistency across every page and state (empty, loading, error, success); pass 4 = final critique, fixes only. Scores and critiques are kept in `relay/internal/web/review/CRITIQUE.md`.

**Polish: buttons, alignment, states (product owner, 2026-10-02: "a lot of issues with buttons, alignments and so on … we need something much much more polish").** One button system (primary / secondary / ghost / danger / icon; sizes sm/md/lg; every state: hover, pressed, focus-visible ring, disabled, loading with a stable width, success), one spacing scale and grid, consistent radii, optical icon alignment, baseline-aligned labels, min target 24×24 px (44×44 on touch), no text overflow, no orphaned single items in rows, forms aligned label/field/help/error. Every page and state (empty, loading, error, success, long names, 360–1920 px, light/dark) is audited: a Playwright layout check fails on overlapping elements, clipped text, controls below the target size, focus rings invisible, and buttons not built from the system; mo-critic adds a pixel-level alignment and button audit to each pass.

**Leaderboard (product owner, 2026-10-02: "a real nice leaderboard … attractive to look at, clean, maybe animated, real dynamic effects, also live ranking or utilisation").** `/leaderboard` is a showcase page: a podium for the top three (mascots, the cloud scene), then a clean ranked list; tabs for donors, projects and models; periods this month / last 30 days / all time; live ranking over SSE — rows re-order with FLIP animation when ranks change, numbers morph, a rank-change indicator (▲/▼) fades in; per-row utilisation sparklines (requests or tokens per hour), a live "serving now" strip (anonymous, aggregate); share links. Privacy: only donors who chose to be listed appear by handle, others as pseudonyms or aggregated; no amounts per private donor; no device data. Fast (budgets), accessible (a table under the visuals for screen readers), reduced-motion and no-JS versions. The relay serves the ranking and utilisation data and an SSE stream of ranking deltas (bounded, rate-limited).

**Analytics and charts (product owner, 2026-10-02: "analytics, graphs, histograms and charts … as much as possible on places that matter").** Charts where they inform a decision, never decoration:
- *Donor (Overview, Donations, Devices):* tokens and $ donated over time (daily area, stacked by project), spend vs monthly limit per donation (bullet bars), when your devices serve (hour × weekday heatmap), cost and tokens by model (bars), cache savings over time, device uptime timeline, latency added (histogram).
- *Maintainer (Repositories, project settings, Activity):* project usage over time stacked by model, contribution by donor (bars, privacy rules apply), the month's pool burn-down vs goal, success / refusal / error rates over time, request latency and duration histograms, usage per member against their caps.
- *Public (project page, landing, leaderboard):* donated vs goal over the last months, donors over time, live utilisation sparklines; the landing's counters can grow into a small live chart.
- *Operators:* Grafana dashboards for the relay metrics (mo-ops).
- *How:* one small chart system — server-rendered inline SVG from Go templates (visible without JS, crisp, tiny), progressively enhanced by a few KB of JS for tooltips, crosshair, legend toggles, draw-in animation and live SSE updates; colours from the theme tokens (light/dark, colour-blind-safe pairs); every chart has an accessible data table and a text summary; reduced motion respected; budgets hold. Data from the relay's rollups (daily + hourly + histogram buckets), aggregates only — each user sees their own data, maintainers their projects, the public only public aggregates.

**Navigation without flashing, lazy loading, loading states (product owner, 2026-10-02: "flashing visuals when switching between menu bar items is not the best … handle lazy loads as much as possible … transitions and loading when possible").**
- *Persistent shell:* in the signed-in app, in-app links swap only the content area (fetch the page's content fragment, History API, same-document View Transition); the sidebar, top bar and the mascot never re-render or flash; Back/Forward, deep links, focus management (focus moves to the new page's heading, announced to screen readers) and scroll restoration work; without JS, plain full-page loads. The server returns the content fragment for these requests (same handler, a request header selects the fragment).
- *Instant feel:* Speculation Rules (`<script type="speculationrules">`) prefetch, and prerender on hover/intent, same-origin pages (public pages and the app; never for POST or sign-out URLs); hover/touchstart prefetch fallback for in-app links.
- *Loading states:* a thin top progress bar for any navigation over ~120 ms, skeletons shaped like the final content that morph into it, button loading states with stable widths, optimistic updates for reversible actions (with rollback on error).
- *Lazy loading:* charts and heavy sections render when they approach the viewport (IntersectionObserver + server fragments), images/illustrations `loading="lazy"` + `decoding="async"` below the fold, `content-visibility: auto` for long lists, the page shell flushed first (early flush) so first paint never waits for slow data.

**Public documentation for people and AI agents (product owner, 2026-10-02):** the docs are public on the site so that any AI agent knows exactly how to add a Moochy donate button to a project (and how to use Moochy otherwise).
- **Routes (no sign-in, cacheable, rate-limited per IP):** `/docs` (index) and `/docs/{slug}` (HTML, in the site design, readable without JavaScript); `/docs/{slug}.md` (the same page as raw Markdown, `text/markdown; charset=utf-8`); `/llms.txt` (the llms.txt convention: one-paragraph summary + links to every `.md` page, the donate-button recipe first) and `/llms-full.txt` (all pages concatenated). Content source = `docs/guides/**` (open source, Apache-2.0), embedded at build time — one source for the site, the repo and agents.
- **The donate-button recipe for agents** (`/docs/donate-button.md`) is exact and copy-pasteable: the URL scheme (`/p/{owner}/{repo}/button.svg` with every allowed query parameter and its values, `/p/{owner}/{repo}/donate`), the Markdown, HTML (`<picture>` light/dark) and reStructuredText snippets, where to put it in a README, how to derive `{owner}/{repo}` from `git remote get-url origin` (GitHub and GitLab, SSH and HTTPS forms), how to check that the project is on Moochy, and what to tell the maintainer when it is not yet claimed (the claim link). No secrets, no tokens, never asks for keys.
- **Machine checks:** `GET /api/v1/projects/{provider}/{owner}/{repo}` → `{"claimed":bool,"donate_url":…,"button_url":…,"docs":"/docs/donate-button.md"}` (public, no auth, rate-limited, never reveals donors or amounts); and `moochy button [--repo owner/repo] [--style …] [--format markdown|html|rst]` prints the snippet (works offline from the git remote).

**Project URLs (integrator decision, 2026-10-02):** canonical project pages are `/p/github/{owner}/{repo}` and `/p/gitlab/{group}[/{subgroup}…]/{repo}` (GitLab nested groups supported). The legacy two-segment form `/p/{owner}/{repo}` stays valid forever as a GitHub project (README buttons in the wild) and is told apart by its segment count (`/p/github/docs` = owner `github`, repo `docs`). Button and donate URLs follow the same rule (`…/button.svg`, `…/donate`); the projects API is `/api/v1/projects/{provider}/{path…}`.

**Donate button studio:** the app includes a small studio where a maintainer (or donor) builds a "Donate tokens" button for a GitHub README: pick the repo, label, style (mascot + text, text only, compact), theme (light, dark, or auto via `<picture>` / `prefers-color-scheme`), size; live preview; one-click copy of the Markdown snippet (`[![Donate tokens](https://moochy.dev/p/{owner}/{repo}/button.svg?...)](https://moochy.dev/p/{owner}/{repo}/donate)`) and the HTML `<picture>` snippet. `button.svg` is a static-safe SVG (no script, no external refs, escaped text, strict query-parameter allowlist, `Content-Type: image/svg+xml`, `Cache-Control` suited to GitHub's image proxy) so it renders in GitHub READMEs.

**Supported donor providers (product owner):** Anthropic, OpenAI, OpenRouter, DeepSeek, and **xAI (Grok)**. Every provider has its adapter (worker), key command (`moochy keys add <provider>`), catalog entries, fake provider + E2E scenarios, and docs.

**Provider logos:** real company logos, from each company's official brand/press assets (fallback: Simple Icons), vendored locally (never hot-linked; CSP stays `self`), shown in their official single-color variant so they fit the monochrome system, shapes unaltered, used only in a "works with" context; sources and usage notes recorded in `relay/internal/web/third_party/LOGOS.md`.

**Public privacy (E68):** public pages, their SSE and `/log` show no device ids, task ids or sub-day times; key-log checkpoint times are shown as dates only (integrator decision, 2026-10-01).

**Information architecture:** public marketing pages are minimal (landing, explore, public repo page, leaderboard, receipts, open-source client, connect). **When signed in, `/` is the app**: an app shell with a menu bar/sidebar (Overview, Donations, Repositories, Devices, Activity, Members for owners, Settings), each with listings (filters, sort, empty states), detail views, and configure forms; everything also works without JavaScript.

**Budgets (replace the earlier 12 KB / no-font rule):** CSS ≤ 48 KB raw (≤ 12 KB gzip); motion JS ≤ 12 KB gzip, no framework, no CDN, external files only (strict CSP, no inline script or style attributes); htmx + sse extension vendored; at most one self-hosted variable font (OFL, Latin subset, woff2 ≤ 45 KB, `font-display: swap`, preloaded); landing page ≤ 150 KB transferred, dashboards ≤ 100 KB; LCP ≤ 1.0 s on 4G, CLS = 0, INP ≤ 100 ms; TTFB budgets of §13 unchanged.

## 10. Build and test entry points

- Rust: `cd cli && cargo build --release` (binary `cli/target/release/moochy`); `cargo clippy --all-targets -- -D warnings`.
- Go: `cd relay && go build -trimpath -o bin/relay ./cmd/relay`; `go vet ./...`.
- E2E: `cd e2e && go test -race -count=1 ./...` (env `MOOCHY_BIN`, `RELAY_BIN` point to the built binaries; defaults to the paths above).

## 11. Identity and uniqueness rules

**Moochy username (handle)** — every user has exactly one, unique on the instance:
- Format: ASCII only, lowercase, `^[a-z0-9](?:[a-z0-9-]{1,30}[a-z0-9])$` (3–32 chars), no `--`. ASCII-only removes homoglyph/confusable impersonation (Cyrillic `а` vs Latin `a`, zero-width chars, RTL marks).
- Uniqueness is **case-insensitive** (stored lowercase; SQLite `UNIQUE` + `COLLATE NOCASE` as a second guard).
- Chosen at first sign-in: default = the provider login lowercased **if valid and free**; otherwise the user must pick one (no silent auto-suffixing, so nobody becomes `alice-2` by accident and looks like `alice`).
- **ASCII look-alikes** (integrator decision, 2026-10-01): uniqueness, reserved words and tombstones are compared on a **skeleton**: lowercase, then `rn`→`m`, `vv`→`w`, `0`→`o`, `1`→`l`, then `-` removed. `rnoochy`, `m00chy`, `ange-s` vs `anges`, `ali1ce` vs `alilce` collide with the existing handle and are refused ("too close to an existing name"). Stored as `users.username_skeleton` with a `UNIQUE` constraint (tombstones keep their skeleton). The handle itself is shown exactly as chosen.
- **Reserved** (refused at signup and rename): every first path segment of the web routes and API (`api`, `dev`, `p`, `r`, `u`, `log`, `logout`, `events`, `open`, `connect`, `explore`, `station`, `console`, `device`, `devices`, `claim`, `leaderboard`, `auth`, `admin`, `static`, `mcp`, `v1`, and since the redesign `activity`, `button`, `donate`, `donations`, `members`, `repos`, `settings`, `signin`, `theme`; reserved for the email, passkey and box pages: `owner-key`, `email`, `hooks`, `decide`, `box`, `boxes`, `outbox`; reserved ahead for planned pages: `studio`, `overview`, `repositories`, `sessions`, `account`, `export`, `help`, `docs`, `about`, `privacy`, `terms`, `status`, `login`, `signup`, `search`, `favicon`, `new`), staff and system words (`moochy`, `admin`, `root`, `support`, `security`, `staff`, `official`, `system`, `null`, `undefined`, `anonymous`, `relay`, `node`, `bot`), and every handle ever used before (see recycling).
- **Rename**: at most once per 30 days. The old handle becomes a **permanent tombstone**: it is never assigned to anyone else (blocks username-recycling takeovers of links, badges and reputation) and redirects to the new one for 90 days.
- Validation is implemented identically in Go (relay) and Rust (node prints handles) with shared test vectors (`spec/vectors/usernames.json`: valid, invalid, reserved, confusables, case variants).
- Rust CLI and logs never print a handle, repo name, or any server-provided string raw: strip/escape control characters (terminal-escape injection).

**Other uniqueness constraints (enforced by the database, not only by code):**

| Thing | Unique key |
|---|---|
| User handle | `users.username` (case-insensitive) + `username_tombstones.username`, and their skeletons |
| User pseudonym (public log) | `users.pseudonym` |
| Provider identity | (`provider`, `provider_user_id`); at most one identity per provider per user |
| Device signing key | `devices.sign_pub` |
| Device name | (`user_id`, lower(`name`)) |
| Repository | (`provider`, `provider_repo_id`) and (`provider`, lower(`owner`), lower(`name`)) |
| Live pledge | (`donor_id`, `repo_id`) where status ∈ {pending, active, paused} |
| Membership | (`repo_id`, `user_id`) |
| Local token | the random token itself (≥ 256-bit), stored hashed |
| Task | (`gateway_device`, `task_id`) |
| Receipt | (`task_id`, `attempt`); `receipt_ref` unique |
| Web session | `id_hash` |

The dev API (§6) uses `username` = this handle.

## 12. gRPC: where and how

**Where gRPC is used (machine-to-machine):**
1. **Node ↔ Relay** — `moochy.v1.NodeLink` (`link.proto`): Session (control), Submit (one stream per task, gateway), Serve (one stream per attempt, worker), device login. Per-task streams give HTTP/2 flow control, clean cancellation (stream cancel = provider call aborted), and deadlines for free.
2. **CLI / MCP stdio shim ↔ running Node** — `moochy.v1.LocalControl` (`local.proto`, owner `mo-node`) over the Unix socket `<home>/state/node.sock` (mode 0600, peer uid checked).
3. **Operator ↔ Relay** — `moochy.admin.v1.RelayAdmin` (`relay/proto/moochy/admin/v1/admin.proto`, closed, owner `mo-relay`) over a 0600 Unix socket (`--admin-socket`), used by `relay admin …` (suspend, catalog publish, drain, state). Never exposed on the network.
4. Later: regional Edge ↔ central Scheduler (plan 10 §9) reuses `NodeLink` messages.

**Where it is NOT used (external compatibility decides):** the provider-compatible API door (Anthropic/OpenAI HTTP+SSE), the MCP door (MCP stdio / Streamable HTTP per the MCP spec), the browser (HTML/HTMX/SSE), OAuth callbacks, badges, the dev API used by tests.

**Libraries:** Go `google.golang.org/grpc` + `google.golang.org/protobuf`; Rust `tonic` (no default TLS features; our own rustls connector) + `prost`. Generated code is **committed** (Go: `relay/internal/pb`; Rust: `cli/crates/proto/src/pb/`) so builds never need `protoc`; regenerate with `spec/proto/gen.sh` (pinned `protoc` + plugins).

**Connection, auth, channel binding:** one HTTP/2 connection = one authenticated session (header of `link.proto`). Go: a custom `credentials.TransportCredentials` wrapping TLS tags each connection with an id and the RFC 9266 exporter (`tls.ConnectionState.ExportKeyingMaterial("EXPORTER-Channel-Binding", nil, 32)`); handlers read it via `peer.FromContext`. Rust: a custom tonic connector (`Endpoint::connect_with_connector`) built on `tokio-rustls` that captures `export_keying_material` from the client connection; one `Channel` per TLS connection, rebuilt (and re-authenticated) on any transport error.

**Hardening (all mandatory, all tested):**
- TLS 1.3 only, ALPN `h2`; no plaintext h2c anywhere except the local Unix sockets.
- Server: `MaxConcurrentStreams` 128 per connection (Worker `slots_max` ≤ 64 + Gateway ≤ 16 concurrent tasks + Session fit with margin); `MaxRecvMsgSize`/`MaxSendMsgSize` 128 KiB (a chunk is ≤ 64 KiB); `MaxHeaderListSize` 16 KiB; keepalive enforcement (`MinTime` 10 s, `PermitWithoutStream` true) + server pings every 15 s, 2 missed = dead; per-connection limit on stream-open rate (HTTP/2 Rapid Reset, CVE-2023-44487) and on resets; current grpc-go / x/net with the CONTINUATION-flood fixes (2024) and HPACK limits; per-IP connection cap; `DeviceStart`/`DevicePoll` rate-limited per IP; unauthenticated calls other than Session/Device* rejected before any allocation of task state.
- Client (Rust): same message-size caps, `http2_max_header_list_size`, connect/request timeouts, bounded per-stream buffers, no gRPC compression.
- gRPC reflection and channelz disabled in production; `grpc.health.v1` allowed.
- Status mapping: Relay policy errors travel as `Failed{code, retryable}` messages inside the stream (not as gRPC status), so the Gateway can map them to provider-native errors (plan 03 §10.3). gRPC status codes are reserved for transport/auth failures (`UNAUTHENTICATED`, `RESOURCE_EXHAUSTED`, `UNAVAILABLE`, `DEADLINE_EXCEEDED`).
- Protobuf parsing is NOT trusted for security decisions that need strictness (proto3 merges repeated singular fields, last wins): every security/money decision reads the signed JSON bytes with the strict parser of §1.

## 13. Responsiveness budgets ("drastic responsiveness" — product owner requirement)

Responsiveness is a feature with numbers. Every budget below is measured by E22 on the dev box (fake provider answering instantly, loopback network) and is a release blocker.

| Path | Budget (p50 / p99) | How |
|---|---|---|
| Gateway: client request accepted → first sealed byte on the gRPC stream (100 KB body) | ≤ 1 ms / ≤ 3 ms | zstd level 1–3 chosen by size, sealing streamed chunk-by-chunk while compressing, no full-body copies |
| Relay: Submit received → Assign sent (scheduler + durable reservation) | ≤ 2 ms / ≤ 8 ms | **adaptive group commit**: commit immediately when the writer is idle, batch only while a commit is in flight (never wait for a timer when idle) |
| Worker: Assign last body chunk → Ack | ≤ 1 ms / ≤ 3 ms | open/verify/firewall without re-copying; local reservation in memory, persisted asynchronously-but-before-receipt |
| Per response chunk, provider byte → client byte (Worker seal + Relay forward + Gateway open + write) | ≤ 300 µs / ≤ 1 ms added | no batching of tokens anywhere: every chunk flushed immediately, `TCP_NODELAY` on every socket, HTTP/2 / gRPC message flushed per chunk, SSE flushed per event |
| End-to-end added time-to-first-token (all hops on loopback, instant fake) | ≤ 5 ms / ≤ 15 ms | sum of the above |
| `moochy status` / MCP shim start / `moochy env` | ≤ 20 ms | Unix-socket gRPC to the warm Node |
| Node `up` → ready (relay reachable) | ≤ 300 ms | keys cached in memory after one unlock, connection pre-warm |
| Web: TTFB for `/` and `/p/{owner}/{repo}` | ≤ 30 ms / ≤ 80 ms | precompiled templates, in-memory aggregates, no N+1 queries |
| Web: live update visible after a task settles | ≤ 500 ms | SSE coalescing window 250 ms |

Mandatory techniques: warm connections everywhere (provider HTTP/2 pools, the relay link, the local socket); HTTP/2 windows sized so a 1 MiB body never stalls (initial stream window ≥ 1 MiB, connection window ≥ 4 MiB); no lock or allocation in the per-chunk path that can be avoided; no synchronous fsync in the per-chunk path; timeouts tight and explicit. Any change that regresses a budget must show the measurement in its commit message.

| ID | Scenario |
|---|---|
| E22 | Responsiveness budgets: run 1,000 tasks with an instant fake provider and measure every row of §13 from timestamps (client, Gateway, Relay, Worker, fake); fail if any p50/p99 budget is exceeded; print the table |
| E92 | xAI (Grok): a donor with an `xai` key serves an OpenAI-dialect request routed to a `x-ai/*` model through the fake xAI provider; usage, cost and receipt are correct; the key never leaves the donor |
| E93 | Sandbox filesystem (`moochy run`, §15.1): inside, the command edits the worktree; reading `~/.ssh`, `~/.aws`, the Moochy keystore or any dir outside the allowed view fails; nothing outside the worktree changes |
| E94 | Sandbox network: inside, only the gateway is reachable (the request succeeds end to end); any other TCP/UDP/DNS destination fails; no provider key is visible in the environment |
| E95 | Sandbox containment: a fork bomb and a memory hog hit the limits without affecting the host; terminal injection (TIOCSTI) and ptrace of the parent are denied; every descendant dies with `moochy run` |
| E96 | Donor lockdown (§15.0/15.2): a hostile request (fake exploit payload asking to run `sh`, decompression bomb, deep JSON) never leads to any process being spawned on the donor (exec is denied after start-up: verified by attempting it from inside the locked process); the donor process cannot read files outside its state dir nor connect anywhere but the provider and the relay; the validator child cannot open files or sockets; a crash in it fails the attempt with a native retryable error and the donor keeps serving |
| E97 | Malicious donor vs maintainer (§15.4): an evil worker returns a `curl … | sh` tool call, a tool call reading `~/.ssh/id_ed25519`, SSE injection (extra `event:` lines, duplicate keys, ANSI escapes, oversized fields), a decompression bomb and a forged progress checkpoint → no tool call reaches a client outside `moochy run`; inside, executing them changes nothing outside the worktree and reads nothing secret; the client receives only canonical events; the bomb and the forgery fail the attempt with native errors. A worker the relay injects into the pool without a key-log approval never receives a wrap. `.env` in the worktree is invisible inside `moochy run` |
| E98 | Local GPU donor: a donor serving through a local OpenAI-compatible host (Ollama / llama.cpp fixtures behind the fake) answers a request; usage comes from the server (or a flagged estimate), the cost is 0, the receipt is marked self-reported (trust tier), the same firewall and limits apply, and a model the host routes to a cloud service is refused |

## 14. Integrator decisions (from docs/TRACEABILITY.md review, 2026-10-01)

| # | Decision |
|---|---|
| D14 | Until the key log ships, a Worker accepts **relay-asserted** membership/approval only when started with `MOOCHY_INSECURE_DEV=1` (tests, design partners). With the key log, it requires the owner-signed log entries (plan 03 §7.2). The key log is in scope **now** (full plan), not deferred. |
| D18 | Served-task set: in memory (±10 min window) plus a **boot-time floor**: the Worker refuses any task whose ULID timestamp is earlier than its own process start. No fsync in the hot path; replay across restarts is impossible. |
| D19 | **Per-request limit default = $5** (`per_task_cap_uusd` 5,000,000; plan 05 §4.1, Q9) in `moochy donate`, the web donation form and the relay's dev API; mo-trace N9. |
| D20 | **Run token under the standard variable names** (mo-trace N7): inside `moochy run`, `ANTHROPIC_API_KEY`/`OPENAI_API_KEY`/`ANTHROPIC_AUTH_TOKEN` carry the per-run gateway token so agents work unchanged; no provider key VALUE may ever be visible inside (A153 checks values). |
| C1 | Adaptive group commit (ADR-34) supersedes the "10 ms window" wording in plans 02/04/05/09. |
| C2 | gRPC (ADR-33) supersedes every WebSocket/frame mention in plans 01/02/03/04/07/10. |
| C3 | A closing schedule window is an **eligibility** condition (`window_open`), never a pledge status change. |
| C4 | `over_task_cap` → HTTP 400 `invalid_request_error`; `quota_exceeded` → HTTP 403 `permission_error` (never 429, which agents retry). |
| C6 | The relay binary is `relay`. |
| C11 | UI shows public slugs; native ids as secondary text. |
| C12 | §13's 250 ms coalescing applies to audit feed, pool, and station; goal bars may update at most every 30 s and donor rankings every 60 s. |
| D15 | Additional relay flags (all optional): `--config <toml>`, `--metrics-addr` (Prometheus, loopback by default), `--autocert-domain`, `--read-only` (restore drills). |
| D16 | Key log uses `x/mod/sumdb/tlog` hashing/proofs + `x/mod/sumdb/note` with our own C2SP tile path layer (no Tessera). |

### 14b. Integrator decisions (round 2)

| # | Decision |
|---|---|
| R1 | Public routes: profiles at `/u/{handle}` (never a bare `/{handle}`); `POST /auth/logout`; handle choice at `/auth/handle`. `u` is reserved (§11). |
| R2 | Default relay for the client: `https://relay.moochy.dev:8443` (gRPC listener); web at `https://moochy.dev`. |
| R3 | PDFs: firewall level `strict` (default) allows `document` blocks only with the pledge flag `documents` and ≤ 100 pages (pages × `catalog.max_page_tokens` in the estimate); level `paranoid` allows no images and no documents. |
| R4 | `admin.proto` is closed-source and lives under `relay/proto/`; `spec/proto/` contains only the open `link.proto` and `local.proto`. |
| R6 | Crypto throughput target: ≥ 800 MB/s applies to AEAD alone (measured 976–1,375 MB/s); AEAD + running SHA-256 together must stay ≥ 750 MB/s per core (measured ~777 MB/s, the single-core ceiling). Both are orders of magnitude above token streaming rates. |
| R7 | The reserved-username list is defined once in `spec/vectors/usernames.json` (`reserved` array); Rust and Go embed their copy and a test fails if either differs from the vector file. |
| R5 | Vectors must also pin: task-id text form (canonical ULID, uppercase Crockford), `headers_sha256` input (canonical `lp` of sorted lowercase header name/value pairs), `resp_commit`, progress-signature field widths, and `sealed_detail` (above). |
| R8 | **`spec/KEYLOG.md` is normative** for key-log entry formats, signatures and checkpoints (adopted from mo-keylog). `DeviceStartRequest.pop_sig` (field 7) carries the `moochy/v1/key-pop` proof-of-possession that goes into `KEY_ADDED`. The key log is open-spec (clients verify it) — `spec/KEYLOG.md` and `spec/vectors/keylog/` are on the open side of §0a. |

## 15. Sandboxing (product owner: "extremely important", 2026-10-01)

Work that donated tokens drive must run in a sandbox, built into the Rust client — no Docker, no daemon. Two layers:

**15.1 Maintainer side — `moochy run -- <command>` (primary).** Runs the coding agent (Claude Code, OpenCode, Aider, any CLI) and everything it spawns inside a lightweight sandbox, pre-wired to the Moochy gateway. It contains the output-injection threat (plan 06 T8): even if a donor returns a poisoned tool call and the agent executes it, the damage stays inside.
- **Filesystem:** read-write only on the project worktree (and a private `$TMPDIR`/`$HOME` in tmpfs or a per-run scratch dir); read-only system paths needed to run tools; NO access to `~/.ssh`, `~/.aws`, `~/.config` secrets, keychains, browser profiles, other repos, the Moochy keystore and state, or the real home directory.
- **Network:** no network at all, except the Moochy gateway exposed inside the sandbox (base URL env vars point to it; on Linux via a Unix-socket bridge into an empty network namespace). Optional `--allow-host <domain>` allowlist through a client-side CONNECT proxy (e.g. package registries), off by default.
- **Process:** clean environment (only an allowlist of variables + the gateway env), no new privileges, resource limits (CPU time, memory, open files, process count, wall time), the sandbox and all descendants die with `moochy run`.
- **Linux:** unprivileged user + mount + PID + network + IPC + UTS namespaces, `pivot_root` into a minimal view, Landlock filesystem (and network on kernels that support it) rules as a second layer, a seccomp-bpf filter (deny `ptrace`, `mount` after setup, `bpf`, `keyctl`, `perf_event_open`, `userfaultfd`, `kexec*`, module loading, namespace re-entry, etc.), `no_new_privs`, rlimits (cgroup v2 limits when a delegated cgroup is available). Detect and explain hosts where unprivileged user namespaces are restricted (e.g. Ubuntu's AppArmor restriction) in `moochy doctor`, with the exact fix.
- **macOS:** Seatbelt (`sandbox-exec` with a generated profile, as other coding-agent CLIs do): deny by default, allow reads of system paths and the worktree, writes only to the worktree and the scratch dir, network only to the gateway's loopback port/socket.
- **Windows:** AppContainer + Job objects (later phase; `moochy run` refuses to run unsandboxed and says so).
- **Never silently unsandboxed:** if the sandbox cannot be established, `moochy run` fails closed with the reason; `--unsafe-no-sandbox` exists only for debugging and prints a loud warning.

**15.0 Principle (product owner, 2026-10-01): the donor computes, the maintainer executes.** A donor's machine only ever does: open the sealed request → validate it → one HTTPS inference call to the provider with the donor's key → seal the output back. It never runs a command, a tool, a script or a provider-side execution feature (server tools, code execution, MCP connector, containers, file search, stored state — already refused by the firewall tables). Tool calls in the output are returned to the maintainer, gated on the maintainer's Gateway (`node/src/gate.rs`) and executed only inside `moochy run` (15.1). Because a malicious donor can fabricate any output, every execution safeguard lives on the maintainer side; donor-side output checks are hints, never a security control.

**15.2 Donor side — "zero commands", enforced by the kernel.**
- **Nothing to execute, in either role.** The Moochy background process never needs `exec`: file sharing for `moochy_delegate` (which needs repo access and `git`) is done by the client-side shim (`moochy mcp` over stdio, which runs inside the agent's own sandbox), never by the background process. So one process serves both roles and locks itself as below.
- **Self-lockdown at startup.** After it has loaded its keys, read its config and opened its connections, the Moochy background process (donor and gateway roles alike) locks itself irreversibly: no `execve`/`execveat` and no `ptrace`, `mount`, `bpf`, `keyctl`, `perf_event_open`, `userfaultfd`, namespace or module syscalls (seccomp-bpf, `no_new_privs`); filesystem limited to its state dir (outbox, served-task set) and the read-only files it still needs (CA roots), via Landlock; outbound TCP only to port 443 and the relay port, and bind only the loopback gateway port, where the Landlock network ABI exists (ABI ≥ 4). macOS: Seatbelt with `process-exec` and `process-fork` denied and file access limited the same way. If the lockdown cannot be applied, the donor refuses to serve and `moochy doctor` says why (`--unsafe-no-lockdown` exists for debugging only, loud).
- **One short-lived validator per request.** The only place a stranger's bytes are parsed — decompression + strict JSON + firewall of the opened request — runs in a single-use child (pre-spawned, so no added latency) with no files, no network, no keys and a seccomp allowlist of read/write/memory/exit; it returns the canonical re-serialized body, which is all the parent sends to the provider. The parent decrypts (AEAD, fixed-size parsing) and keeps the provider key, the outbox and the caps. Responses are parsed in the parent: their structure comes from the provider over TLS, and the hot path stays in-process (no per-chunk IPC; CONTRACT §13).
- **No C code on hostile input.** Every decompression of bytes from another party (Worker: requests; Gateway: responses) uses a pure-Rust decoder (`ruzstd`), with the 32 MiB cap. The C `zstd` may remain only for compressing one's own data.
- **Bounded worst case.** `moochy keys add` recommends a dedicated provider key with a provider-side spend limit; the service units (`deploy/client/**`) add the platform hardening (systemd `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `SystemCallFilter`, `RestrictAddressFamilies`; launchd equivalents).
- **Never on donors:** running agents, tools or commands; browser-tab donating; handing provider keys (or provider OAuth sub-keys) to the relay.

**15.4 Maintainer side — everything a donor returns is hostile.** A donor controls its output completely: it can skip the provider and fabricate any stream. Every safeguard below runs on the maintainer's machine and none of them trusts the donor or the relay.
- **Only approved donors see the content.** The Gateway seals only to worker keys that are logged, unrevoked and owner-approved for the repo (`node.rs` `worker_approved`). The Phase 1 fallback (D14: "the relay's pool is accepted as-is until the mirror has a verified checkpoint") ends as soon as the key log is served over the link: from then on, no verified checkpoint means no sealing, outside `--dev`. A donor injected by the relay never receives a wrap.
- **Hostile bytes.** Pure-Rust decompression with the 32 MiB cap (15.2), strict bounded parsing, fuzzed. The Gateway re-emits every event to the client from its parsed, typed form (allowlisted fields, canonical JSON, normalized SSE framing): no donor byte reaches the agent's parser verbatim. Terminal control sequences are stripped wherever text is displayed (E91); donor output is never rendered as HTML.
- **Tool calls.** The gate (`node/src/gate.rs`: declared name, schema, tripwire, released only after a verified donor-signed progress checkpoint) stays. In addition, by default tool calls from pooled compute are released only to sandboxed sessions: `moochy run` gets a run token marked sandboxed; a client outside `moochy run` receives the text and a visible `[moochy]` notice in place of each tool call, unless the maintainer opts in per project (`allow_unsandboxed_tools`, with a warning at every start).
- **Text is an attack too** (prompt injection telling the agent, or the human, to run something): contained by the sandbox; the tripwire flags dangerous commands found in text.
- **Secrets never leave.** The outbound scrubber runs on every door (API, MCP, file sharing). Inside `moochy run`, secret-shaped and git-ignored files (`.env*`, `*.pem`, `*.key`, `id_*`, `.npmrc`, `.netrc`, `.pypirc`, `credentials*`, cloud CLI config) are hidden from the agent's view, so they cannot be read into a prompt; the environment inside carries no token except the run's gateway token.
- **Approvals need the human.** Owner approvals (`DONOR_APPROVED`, `MEMBER_*`, `REPO_CLAIMED`) are signed with a separate owner key — the CLI owner key or the owner's passkey (§16.6), registered in the key log, kept encrypted at rest and loaded only by the foreground CLI after an explicit confirmation, never by the background process. Even a fully compromised background process cannot approve a donor.
- **Provider choice.** A project may exclude providers (e.g. for data retention); the Gateway never seals to a donor serving through an excluded provider.
- **Known limit:** a donor can still return low-quality or fabricated answers. That is a quality problem, not a safety one: receipts, disputes and per-project donor approval handle it.

**15.3 Verification.** E2E scenarios (E93+): a sandboxed agent can edit its worktree but cannot read `~/.ssh` or the keystore, cannot reach any host except the gateway, cannot escape its PID namespace or exceed its limits; a poisoned `curl … | sh` tool call executed inside the sandbox has no effect outside; the donor process cannot `exec` anything, open files outside its state dir or connect anywhere but the provider and the relay (E96); the request validator child cannot open files or sockets. Attack tests (mo-sec) for known escape techniques. Owner: new crate `cli/crates/sandbox` (`moochy-sandbox`, owner `mo-sandbox`); `unsafe` is permitted ONLY in its small, documented syscall module, reviewed and fuzzed.

## 16. Email notifications (product owner, 2026-10-02)

Moochy sends email through the **Resend API** (`POST https://api.resend.com/emails`, bearer key) for account confirmation and every notification kind. Closed source (relay side); owner `mo-notify` (`relay/internal/notify/**`).

**16.1 Account email.** At first sign-in (and on any change) the user gives an email address — prefilled from the provider's verified email, never a private/no-reply address — and must confirm it through a single-use link (random 256-bit token, stored hashed, 24 h expiry, bound to the user and the address, consumed once; a fresh-auth web session is required to change the address). Until confirmed, only the confirmation email can be sent. The address is used only for Moochy notifications, appears in the data export and is deleted with the account.

**16.2 Kinds** (each a template in VOICE.md wording, plain text + HTML, the brand's light palette, no tracking pixels, no remote images):
- *Account and security (always on, cannot be disabled):* confirm your email; sign-in from a new device; a device was added or revoked; an owner key was added or revoked (A224: the first owner key also needs this email's confirmation link before it signs anything); your account is being deleted.
- *Donor:* donation accepted / declined / stopped by the maintainer; 80 % and 100 % of a monthly limit; a device offline for more than a day while a donation is active; a receipt was disputed; the provider key is failing (auth/billing errors); monthly summary.
- *Maintainer:* a new donor is waiting for your approval (`moochy pending`); a member request; a donation stopped or lowered; the project's pool is running low; repository claim confirmed; monthly summary.
- Preferences per category in Settings (security ones locked on); every non-security email carries a one-click unsubscribe (`List-Unsubscribe` + `List-Unsubscribe-Post`, RFC 8058) for its category; digests group bursts (at most one email per kind per hour per user, summaries daily/monthly).

**16.3 Delivery.** A durable outbox in the relay DB (send after the triggering transaction commits; never inside it); Resend `Idempotency-Key` = the outbox id; retries with backoff on 429/5xx; give up after 24 h and record it. Resend webhooks (`/hooks/resend`) verified with the Svix signature (`svix-id`, `svix-timestamp`, `svix-signature`, HMAC-SHA256, 5-minute tolerance, constant-time compare) mark bounces and complaints: a hard bounce or a complaint stops non-security email to that address until the user confirms it again. Per-user and global send rate limits. **Never** in an email: prompts, outputs, keys, tokens, receipts' internal ids beyond the public `r_` reference, other people's private data.

**16.4 Configuration and secrets.** `--email-from "Moochy <…>"` and the Resend API key as a systemd credential (`resend-key`, never plaintext on disk or in logs); the webhook signing secret likewise (`resend-webhook-secret`). Without a configured key and sender the relay sends nothing and says so at start-up (fail closed). The sender domain is verified at Resend by the product owner — agents never configure DNS, the Resend account or any real address, and never send real email (`security@moochy.dev` stays unused, AGENTS.md). `--dev` and E2E use a fake Resend server (records requests, can return errors) and a dev outbox page `/dev/outbox` listing the rendered emails.

**16.5 Verification.** E99: sign-up asks for an email, the confirmation link verifies it once (replay, expired, wrong-user and tampered tokens refused); E100: a donation accepted by the maintainer sends exactly one email to the donor through the fake Resend with the right template and idempotency key, retried on a 503, never duplicated; E101: unsubscribe and preferences stop that category but not security email; a signed bounce webhook stops sending; an unsigned or stale webhook is refused; no email body contains prompt text, keys or tokens.

**16.6 Accept or refuse a donation — from the app, the web or an email (product owner, 2026-10-02), and every decision traced.**
- *Decisions:* a maintainer (repo owner) accepts or refuses each donation request; a refusal can carry a short reason shown to the donor; a pending request that nobody answers expires after 30 days (the donor is told). Members' requests work the same way.
- *Email buttons:* the "a new donor is waiting" email shows the request (donor handle or pseudonym, models, monthly limit, limit per request) and two buttons, **Accept** and **Refuse**, plus "Review". A button never acts by itself (link scanners click links): it opens `/decide/{request}` with a single-use, 7-day token that only preselects the request; the page requires a signed-in session of the owner (fresh within 2 h) and acts on a POST with CSRF.
- *Refuse* is one click on that page (no owner-key signature needed: a refusal grants nothing); the relay records it and tells the donor.
- *Accept* keeps §15.4 "approvals need the human" with a **passkey**: the owner's WebAuthn credential (platform authenticator: Touch ID, Windows Hello, a security key) is registered as an **owner key** in the key log (`OWNER_KEY_ADDED` with algorithm `webauthn-es256`, credential id + COSE public key; spec/KEYLOG.md). Accepting = a WebAuthn assertion (user verification required) whose challenge is the hash of the exact `DONOR_APPROVED` entry; the relay appends the entry with the assertion (authenticatorData, clientDataJSON, signature) and every node verifies it like any owner signature (P-256 ECDSA over authenticatorData ‖ SHA-256(clientDataJSON), challenge, origin, rpId, UV flag, sign counter non-decreasing). The relay can neither forge nor replay it. Registering the FIRST passkey on an account with no owner key needs the confirmed email's link (A224) — and not within 72 h after the email address was changed (integrator decision); later passkeys need an existing owner key or passkey. `moochy approve` on the command line stays.
- *Traced:* every request and decision is an append-only event (`requested`, `accepted`, `refused`, `expired`, `stopped`, `lowered`, `resumed`, `revoked`) with who, when, how (cli / web / email link / passkey) and the key-log index when signed; the maintainer sees the full history per project (Activity → Decisions), the donor sees it per donation, both appear in the data export, and approvals are verifiable in the public key log.
- *Emails:* the donor is told of every decision (accepted, refused with the reason, expired); the maintainer gets a confirmation of their own decision only for passkey/web actions (security: an unexpected one means trouble).
- *Verification:* E102 email → /decide → refuse: one event, donor emailed, no key-log entry; E103 email → /decide → accept with a passkey (virtual authenticator in E2E): a verifiable `DONOR_APPROVED` in the key log, the donor's node starts serving, a forged/replayed/wrong-challenge assertion is refused by nodes; E104 the decisions history matches the events; link prefetch (GET without session) changes nothing.

**Link port (integrator decision, 2026-10-02):** the relay also serves the gRPC link on **443**, multiplexed with the web on the same TLS listener (ALPN h2, `content-type: application/grpc`), because several box platforms (Daytona lower tiers, Modal/E2B allow-lists) block 8443; nodes default to `https://relay.moochy.dev` (443); 8443 stays available.

## 17. Cloud boxes and agent sandboxes (product owner, 2026-10-02: "boat.dev and some platforms that provide also boxes for ai compute, make sure moochy.dev [is] able to support and handle those")

Platforms such as boat.dev (persistent Ubuntu VMs for agents, SSH, Docker inside, disk-level fork), E2B, Daytona, Modal sandboxes, Morph, Fly Machines, GitHub Codespaces/devcontainers (agent boxes), and RunPod, Vast.ai, Lambda (GPU boxes).

**17.1 Maintainers' agents in a box.** A box never receives a copy of the maintainer's device key. The owner (or a member, within their caps) creates an **enrollment token** — `moochy box token create --repo owner/repo [--ttl 24h] [--cap $20] [--max-boxes N]` or from the web (Repositories → Boxes) — single-purpose, hashed at rest, revocable, shown once. Inside the box: `MOOCHY_ENROLL=<token> moochy up --headless` (or the platform template) creates an **ephemeral gateway device**: its own keys generated in the box, `KEY_ADDED` with a `box` flag and an expiry, scoped to that repo, its own monthly cap, no owner powers, no donor role. The relay enforces one live session per device; a second concurrent session with the same device key (a cloned/forked VM) is refused, alerts the owner and the clone must enroll again (clone detection, integrator decision after mo-docs' platform research: machine-id is copied by forks, templates and memory snapshots, so it is only a hint; each `up` registers a fresh random instance value at session start, and the relay treats two different instance values for one device key inside the session lease as a clone — the newer is refused, the owner alerted). Boxes are listed, capped and revoked like devices (`moochy box list|revoke`, web, email on enrollment).

**17.2 Sandboxing inside a box.** In a full VM (boat.dev) `moochy run` works as on any Linux host (AppArmor note on Ubuntu). Where user namespaces or Landlock are unavailable (some containers), `moochy doctor` says exactly what is missing; `moochy run --box-is-sandbox` lets the maintainer declare that this single-purpose VM/container is the sandbox: the run still gets the clean environment, the gateway token and the secret masks, prints a loud warning, and the gateway marks the session "platform-sandboxed" (tool calls from pooled compute are released to it only if the project allows platform sandboxes, a repo setting, default on for ephemeral box devices only).

**17.3 Donors on boxes.** A headless donor node runs on a cloud VM like on any server (keys from the platform's secret store or an env file, lockdown applies; in containers, doctor reports what the container runtime blocks). A donor's own GPU server on RunPod/Vast/Lambda can serve as a `local`-kind provider over **TLS** when explicitly vetted: exact host allowlist, an auth header from the keystore, certificate verification, and the same firewall, limits and self-reported trust tier as other local hosts (T-06-061).

**17.4 Templates and docs.** Ready-to-use setup for boat.dev, E2B, Daytona, Modal, Codespaces/devcontainers (a devcontainer feature + cloud-init/setup scripts), and RunPod/Vast/Lambda GPU donors; guides in docs/guides and in /llms.txt so agents can set themselves up.

**17.5 Verification.** E105: a box enrolls with a token, serves requests within its cap, expires; E106: a cloned box (same device key, second session; changed machine-id) is refused and the owner alerted; E107: `--box-is-sandbox` in a container without user namespaces runs with the clean environment and the warning, and tool calls are released only when the repo allows platform sandboxes; E108: a vetted TLS GPU host serves a donation; an unvetted or plain-HTTP remote host is refused.

