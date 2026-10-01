# Moochy implementation contract (Phase 1 walking skeleton → beta)

Normative for every implementer. The design rationale lives in `docs/plan/` (03 = wire protocol, 05 = ledger, 06 = security, 07 = client). When this file and the plan disagree, **this file wins** for encodings and interfaces; raise the conflict in your final report.

## 0. Repository layout and ownership

| Path | Language | Owner (agent) | Notes |
|---|---|---|---|
| `spec/` | — | integrator | This contract; `spec/vectors/*.json` are written by `mo-proto` |
| `cli/` | Rust workspace | — | `cli/Cargo.toml` = workspace root (members + profiles only; owned by integrator) |
| `cli/crates/proto` | Rust lib `moochy-proto` | `mo-proto` | Wire types, `lp`, labels, crypto, frames, receipts, vector generator |
| `cli/crates/node` | Rust lib+bin `moochy` | `mo-node` | Node: link, keystore, gateway (API + MCP doors), worker, adapters, firewall, outbox |
| `relay/` | Go module `moochy.dev/relay` | `mo-relay` | Relay binary `relay`; everything except `relay/internal/web/**` |
| `relay/internal/web/**` | Go (stdlib only) | `mo-web` | Pages, fragments, CSS, SSE hub; exposes the interface in §9 |
| `e2e/` | Go module `moochy.dev/e2e` | `mo-e2e` | Harness, fake providers, scenarios; except `e2e/attacks/**` |
| `e2e/attacks/**`, `docs/security/**` | Go + Markdown | `mo-sec` | Attack catalog, attack scenarios, evil-peer tooling |

Never edit a path you do not own. Need a change elsewhere? Write it under `## Requests to other owners` in your final report.

## 1. Encodings (both languages)

- Text frames: UTF-8 JSON objects. Unknown fields ignored. Required field `t` (message type).
- Bytes in JSON: **base64url without padding** (`RFC 4648 §5`). Ids: `task` = ULID canonical 26-char string; `device_id` = `d_` + ULID; `user_id` = `u_` + ULID; `repo_id` = `r_` + ULID; `pledge_id` = `p_` + ULID. Money: JSON integer µ$ (`*_uusd`).
- `lp(a, b, …)` = concatenation of `u32_be(len(x)) || x` for each field. Integers inside `lp` are encoded as `u64_be` (8 bytes). Strings as UTF-8 bytes.
- Hash = SHA-256. HKDF = HKDF-SHA256 (RFC 5869); `Expand` length 32 unless stated.
- Signatures: Ed25519, **verification = ZIP-215** in both languages (Rust `ed25519-zebra` or equivalent; Go `github.com/hdevalence/ed25519consensus`). Signing is plain RFC 8032.
- AEAD: ChaCha20-Poly1305 (RFC 8439). Nonce (12 bytes) = `0x00 * 8 || u32_be(seq)`.
- HPKE: RFC 9180 base mode, KEM 0x0020 DHKEM(X25519, HKDF-SHA256), KDF 0x0001, AEAD 0x0003. `suite_id` string = `moochy.v1.hpke.x25519-sha256-chacha20poly1305`.

## 2. Labels (exact strings, all inside `lp`)

`moochy/v1/auth`, `moochy/v1/device-start`, `moochy/v1/req`, `moochy/v1/resp`, `moochy/v1/wrap`, `moochy/v1/task`, `moochy/v1/salt`, `moochy/v1/req-commit`, `moochy/v1/resp-commit`, `moochy/v1/provider-req`, `moochy/v1/receipt`, `moochy/v1/projection`, `moochy/v1/resp-progress`, `moochy/v1/dispute`.

## 3. Keys and derivations (from docs/plan/03 §6, made exact)

- `CK`: 32 random bytes, fresh per sealed body.
- `K_req = HKDF(salt = "", ikm = CK, info = lp("moochy/v1/req", task_id))`.
- Request chunk `i`: `AEAD(K_req, nonce(i), aad = lp("moochy/v1/req", kind_byte, task_id_16B, u32(i), last_byte))`, plaintext ≤ 65,497 bytes.
- Wrap: `HPKE.SealBase(pkR = enc_pub, info = lp("moochy/v1/wrap", suite_id, task_id), aad = route_header_bytes, pt = CK)` → `enc (32) || ct (48)` = 80 bytes.
- `R`: 32 random bytes per attempt (Worker). `RK = HKDF(salt = R, ikm = CK, info = lp("moochy/v1/resp", task_id, worker_device, u64(attempt)))`.
- Response chunk: `AEAD(RK, nonce(seq), aad = lp("moochy/v1/resp", task_id_16B, u64(attempt), R, u32(seq), last_byte))`.
- Salts: `S` 32 random bytes in the inner payload; `S_x = HKDF(salt="", ikm=S, info=lp("moochy/v1/salt", name))` for name ∈ {`req`,`resp`,`pid`}.
- Gateway task signature: `Ed25519(gw_key, lp("moochy/v1/task", task_id, repo_id, route_header_bytes, body_sha256, headers_sha256))`.
- Auth signature: `Ed25519(dev_key, lp("moochy/v1/auth", nonce, dialed_origin, tls_exporter, device_id))`; `tls_exporter` = RFC 9266 (`EXPORTER-Channel-Binding`, empty context, 32 bytes). `dialed_origin` = `wss://host:port` exactly as dialed.
- Route header bytes = the exact UTF-8 JSON bytes the Gateway sends in `task.submit.route` (it is transmitted as base64url of those bytes, field `route_b64`, plus a decoded convenience copy is NOT sent; the Relay parses the decoded bytes).

## 4. Inner payload (sealed request plaintext, before zstd)

JSON: `{"v":1,"body_b64":..., "body_sha256":..., "headers": {"anthropic-version": "...", "anthropic-beta": "..."}, "S":..., "gateway_device":..., "task_sig":...}`; the whole JSON is zstd-compressed (level 3) then chunked and sealed.

## 5. Messages

Exactly the catalog of docs/plan/03 §5 with these field names: `t`, `task`, `attempt`, `route_b64`, `wraps` (`[{"worker_device","wrap"}]`), `body_len`, `body_chunks`, `worker_device`, `R`, `code`, `retryable`, `retry_after_ms`, `sealed_detail`, `receipt_b64`, `donor_sig`, `projection_b64`, `projection_sig`, `seq`, `running_hash`, `sig`, `slots_free`, `models` (`[{"dialect","model","rl_headroom"}]`), `pledges`, `window_open`, `local_cap_left`, `tasks` (known_tasks), `since`.
Route header JSON fields (03 §7.1): `repo_id, dialect, model, effort, max_tokens, est_input_tokens, cache_ttl, stream, affinity, flags`.
Binary frame header: 03 §4.2 (23 bytes).

## 6. Process interface (what the e2e harness runs)

### Relay
`relay serve --addr 127.0.0.1:0 --db <path> --tls-cert <pem> --tls-key <pem> [--dev] [--catalog <json>]`
- Prints exactly one JSON line to stdout when ready: `{"event":"ready","addr":"127.0.0.1:PORT"}`. Logs go to stderr (JSON, `log/slog`).
- `--dev` is refused unless `--addr` is a loopback address. It enables the dev API below.
- Endpoints: `wss://…/v1/node` (subprotocol `moochy.v1`), `POST /api/device/start`, `POST /api/device/poll`, the web routes, and with `--dev`:
  - `POST /dev/user {"username"}` → `{"user_id","pseudonym","session"}` (session = cookie value)
  - `POST /dev/repo {"owner","name","owner_username"}` → `{"repo_id"}`
  - `POST /dev/member {"repo_id","username","cap_uusd_month"?}`
  - `POST /dev/pledge {"donor_username","repo_id","budget_uusd","per_task_cap_uusd","policy":{"models":[],"max_effort","dialects":[],"flags":[]}}` → `{"pledge_id"}` (approved immediately; relay-asserted in Phase 1)
  - `POST /dev/device/approve {"user_code","username","roles":["gateway"|"worker"],"repo_scope"?}` → `{"device_id"}`
  - `GET /dev/state` → JSON: pledges (budget/spent/reserved), members, devices, attempts (status, cost), receipts count. For assertions only.
  - `POST /dev/chaos {"ignore_caps":bool,"tamper_route":bool,"replay_assign":bool,"inject_frame":bool}`: makes the relay misbehave like a malicious operator (skip cap checks; flip one byte of the route header sent to the Worker; deliver the same `task.assign` twice; send a forged binary frame for a live task on a different connection). Used by E11, E15–E17 to prove the **clients** defend themselves.
- Catalog: `--catalog` JSON file with entries per 05 §2.2; default built-in test catalog when absent.

### Node
`moochy --home <dir> <command>`; all state under `<dir>`. Keystore backend for tests: encrypted file, passphrase from env `MOOCHY_PASSPHRASE`.
- `moochy login --relay wss://127.0.0.1:PORT --ca-file <pem> --roles gateway,worker --headless` → prints `{"event":"device_code","user_code":"XXXX-XXXX"}` then blocks until approved, then `{"event":"logged_in","device_id":"d_…"}`.
- `moochy keys add <anthropic|openrouter|deepseek|openai> --key-stdin [--base-url http://127.0.0.1:PORT]` — `--base-url` is accepted **only** for loopback hosts **and** only when env `MOOCHY_INSECURE_DEV=1`; otherwise refused.
- `moochy config set <key> <value>` for `device_monthly_cap_uusd`, `slots_max`, `gateway_addr` (default `127.0.0.1:0`).
- `moochy up --foreground` → when ready writes `<dir>/state/node.json` `{"device_id","gateway_url":"http://127.0.0.1:P","mcp_url":"http://127.0.0.1:P/mcp","pid"}` and prints `{"event":"ready",...same}`.
- `moochy env --repo owner/name --json` → `{"anthropic_base_url","openai_base_url","token"}`.
- `moochy mcp --repo owner/name` → stdio MCP server (JSON-RPC 2.0, newline-delimited).
- Exit codes: 0 ok, 2 usage, 3 auth/approval refused, 4 network, 10 internal.

## 7. Fake providers (e2e) — behaviour switches

Fakes are Go `httptest` servers. Behaviour is chosen by **tags in the last user message text**: `#tokens:N` (output tokens), `#fail:429|529|500` (before stream), `#cut:K` (drop connection after K SSE events), `#slow:MS` (delay before headers), `#tool:<json>` (emit one tool call with that input), `#model:<id>` (report a different model). Anthropic fake: `POST /v1/messages` (SSE identical in shape to the real API, with `message_start` usage and `message_delta` final usage, cache fields), `GET /v1/models`. OpenAI-style fakes (`openai`, `deepseek`, `openrouter`): `POST /v1/chat/completions` (SSE `data:` chunks, final usage chunk only when `stream_options.include_usage`; DeepSeek adds cache hit/miss fields; OpenRouter adds `usage.cost`), `GET /v1/models`. OpenRouter and DeepSeek fakes also serve the Anthropic shape on their Anthropic-compatible prefix. Every fake records received requests (headers + body) for assertions.

## 8. E2E scenarios (the definition of "working")

IDs are stable; each is one Go test `TestE<NN>_<name>`. A scenario may `t.Skip("pending: <component>")` until its components exist, but never be deleted.

| ID | Scenario |
|---|---|
| E01 | Anthropic streaming through the API door: client receives byte-identical SSE; one receipt; `spent` = catalog cost; reservation released |
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
| E17 | Frame injection (chaos `inject_frame`) → forged bytes never reach the client: the Gateway fails the task on the first AEAD failure with a native retryable error and logs `bad_envelope`; no forged byte appears in the client output |
| E18 | Tool-call gating: fake emits a tool call not in `tools[]` / failing schema / `curl … | sh` → replaced with an error tool result |
| E19 | Web: `/p/{owner}/{repo}` renders (palette tokens present), SSE `/p/{owner}/{repo}/events` delivers a fragment after a task |
| E20 | Throughput smoke: 200 concurrent streamed tasks across 3 workers complete; p50 relay-added latency reported |

## 9. Web interface (between `mo-relay` and `mo-web`)

Package `moochy.dev/relay/internal/web` exports `func New(src Source) http.Handler` and the `Source` interface (read-only queries: repo by slug, pool summary, goal numbers, recent projections, donor station data) plus `func (h) Publish(topic string, ev Event)` for SSE. `mo-web` defines the interface and ships a fake `Source` for its own tests; `mo-relay` implements it.

**Palette (fixed):** white `#FFFFFF`, dark `#0B1220` (ink / dark background), light blue `#7DD3FC` (accent fills, highlights, focus rings) with `#0369A1` for small text links on white (contrast). Dark theme: background `#0B1220`, text `#F8FAFC`, accent `#7DD3FC`. Hand-written CSS with custom properties, no framework, no web fonts; total CSS ≤ 12 KB; htmx + sse extension vendored locally.

## 10. Build and test entry points

- Rust: `cd cli && cargo build --release` (binary `cli/target/release/moochy`); `cargo clippy --all-targets -- -D warnings`.
- Go: `cd relay && go build -trimpath -o bin/relay ./cmd/relay`; `go vet ./...`.
- E2E: `cd e2e && go test -race -count=1 ./...` (env `MOOCHY_BIN`, `RELAY_BIN` point to the built binaries; defaults to the paths above).
