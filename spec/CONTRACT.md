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
| `e2e/` | Go module `moochy.dev/e2e` | `mo-e2e` | Harness, fake providers, scenarios; except `e2e/attacks/**` |
| `e2e/attacks/**`, `docs/security/**` | Go + Markdown | `mo-sec` | Attack catalog, attack scenarios, evil-peer tooling |
| `relay/internal/tlog/**`, `cli/crates/keylog/**` | Go + Rust lib `moochy-keylog` | `mo-keylog` | Key log: append, tlog hashing/proofs, C2SP tiles, signed checkpoints (only for replicated sizes), hourly public Git anchor; owner-signed `REPO_CLAIMED` / `DONOR_APPROVED` / `MEMBER_*` entries; Rust verifier + monitor library (mirror, consistency, own-key and owner alerts) |
| `relay/internal/oauth/**` | Go | `mo-oauth` | GitHub + GitLab OAuth, web sessions, handle choice at signup (§11), repo-claim admin check via provider APIs, device-approval web page logic |
| `relay/internal/metrics/**`, `deploy/**`, `docs/ops/**` | Go + config + Markdown | `mo-ops` | Prometheus metrics registry, SLOs, alert rules, runbooks, systemd units, Litestream config, internal deployment recipe, drain-and-restart procedure, backup/restore drill script |
| `docs/plan/**`, `docs/guides/**`, `SECURITY.md`, `cli/SECURITY.md` | Markdown | `mo-docs` | Keep the plan consistent with CONTRACT/ADRs; donor, maintainer, headless-node, and MCP/API integration guides; also the public `spec/protocol.md` |

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

**Visual direction (product owner review, 2026-10-01 — supersedes the earlier palette and motion paragraphs):** calm, editorial, product-grade; nothing that reads as "AI-made". **Strictly monochrome built from exactly three base colors** — Ink (dark), Paper (white) and Sky (light blue) — with every other color a derived variant of those three (tints, shades, or alpha of one base on another, defined as named tokens). **No gradients of any kind, no glows, no blur/glass, no sheen or shimmer text, no particle/constellation backgrounds, no cursor-follow effects, no magnetic buttons, no scroll-jacking or pinned scrollytelling, no marquees.** Flat surfaces, 1 px borders, generous whitespace, strong type hierarchy, real content. States (success/warning/error) are expressed with the same three bases plus icons, labels and weight; an extra hue is allowed only if a documented clarity/accessibility need proves it. WCAG AA everywhere.

**Brand mascot:** Moochy has its own "pet" — a small, friendly, geometric creature drawn in the three base colors, legible as a 16 px favicon and as an illustration; a few expressions (idle, happy when a task completes, asleep when the pool is idle) used sparingly in empty states and loading, never as decoration on every surface.

**Motion:** subtle and functional only — state changes, list insertions, page transitions, the mascot's small expressions; first-view fades limited to one per section; `prefers-reduced-motion` turns it all off.

**Vocabulary and voice (product owner):** the key phrase is **"Donate tokens"**. Every user-facing word follows `docs/brand/VOICE.md` (normative): "pledge" is never shown (it is a **donation**; budget → monthly limit; reclaim → stop donating; station → Dashboard; console → Project settings; …), with its tone rules and banned words. Internal identifiers keep their names.

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
- **Reserved** (refused at signup and rename): every first path segment of the web routes and API (`api`, `dev`, `p`, `r`, `u`, `log`, `logout`, `events`, `open`, `connect`, `explore`, `station`, `console`, `device`, `devices`, `claim`, `leaderboard`, `auth`, `admin`, `static`, `mcp`, `v1`, and since the redesign `activity`, `button`, `donate`, `donations`, `members`, `repos`, `settings`, `signin`, `theme`; reserved ahead for planned pages: `studio`, `overview`, `repositories`, `sessions`, `account`, `export`, `help`, `docs`, `about`, `privacy`, `terms`, `status`, `login`, `signup`, `search`, `favicon`, `new`), staff and system words (`moochy`, `admin`, `root`, `support`, `security`, `staff`, `official`, `system`, `null`, `undefined`, `anonymous`, `relay`, `node`, `bot`), and every handle ever used before (see recycling).
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
- **Approvals need the human.** Owner approvals (`DONOR_APPROVED`, `MEMBER_*`, `REPO_CLAIMED`) are signed with a separate owner key, registered in the key log, kept encrypted at rest and loaded only by the foreground CLI after an explicit confirmation, never by the background process. Even a fully compromised background process cannot approve a donor.
- **Provider choice.** A project may exclude providers (e.g. for data retention); the Gateway never seals to a donor serving through an excluded provider.
- **Known limit:** a donor can still return low-quality or fabricated answers. That is a quality problem, not a safety one: receipts, disputes and per-project donor approval handle it.

**15.3 Verification.** E2E scenarios (E93+): a sandboxed agent can edit its worktree but cannot read `~/.ssh` or the keystore, cannot reach any host except the gateway, cannot escape its PID namespace or exceed its limits; a poisoned `curl … | sh` tool call executed inside the sandbox has no effect outside; the donor process cannot `exec` anything, open files outside its state dir or connect anywhere but the provider and the relay (E96); the request validator child cannot open files or sockets. Attack tests (mo-sec) for known escape techniques. Owner: new crate `cli/crates/sandbox` (`moochy-sandbox`, owner `mo-sandbox`); `unsafe` is permitted ONLY in its small, documented syscall module, reviewed and fuzzed.
