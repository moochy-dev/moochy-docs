# Moochy — Requirements Traceability Matrix

Owner: `mo-trace`. Source of truth for "is everything in `docs/plan/*.md` implemented?". Every concrete requirement of the 14 plan documents (00 → 13), plus the requirements that exist only in `spec/CONTRACT.md` and `AGENTS.md`, has exactly one row here. Deferred and research items are included and flagged; they are still in scope for later waves.

Rules for keeping this file honest:

- IDs are stable. Never renumber; retire a row by setting status `dropped` with a reason.
- A row moves to `done` only when its verification is automated and green (11 §3 "definition of done").
- When a plan document changes, add or amend rows in the same commit.

## Legend

### Owner (CONTRACT §0)

| Owner | Path |
|---|---|
| `mo-proto` | `cli/crates/proto` (wire types, `lp`, labels, crypto, frames, receipts, vectors) |
| `mo-worker` | `cli/crates/worker` (firewall, adapters, SSE/usage parsers, tool-call inspection, outbox, served set, local counters) |
| `mo-node` | `cli/crates/node` (binary `moochy`: CLI, config, keystore, relay link, API door, MCP door, local security, wiring) |
| `mo-relay` | `relay/` except `relay/internal/web/**` |
| `mo-web` | `relay/internal/web/**` |
| `mo-e2e` | `e2e/` except `e2e/attacks/**` |
| `mo-sec` | `e2e/attacks/**`, `docs/security/**` |
| `integrator` | `spec/` (except `spec/vectors/*.json`, written by `mo-proto`), `cli/Cargo.toml` |
| `mo-ops*` | **Proposed.** `deploy/**`, `docs/ops/**` (runbooks, alert rules, dashboards, staging, probes, Litestream config) |
| `mo-release*` | **Proposed.** `.github/**`, release tooling (cargo-dist, Sigstore, SLSA, reproducible builds, cargo-deny/vet, npm wrapper, container image, Homebrew tap) |
| `mo-docs*` | **Proposed.** `docs/guides/**` (donor, maintainer, self-host guides), root `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `GOVERNANCE.md` |
| `human-po*` | **Proposed.** Product owner (decisions, recruiting, usability tests, sponsorship, status page) |
| `human-counsel*` | **Proposed.** Legal counsel (provider terms, ToS, privacy policy, consent text) |

`a + b` = primary owner `a`, contributing owner `b`. `*` = no owner in CONTRACT §0 today (see §A at the end).

### Phase (docs/plan/11)

`0`–`6` = plan phase. `1→3` = shipped relay-asserted in Phase 1, hardened by the Phase 3 trust layer. `D` = deferred (designed, built on a metric trigger). `R` = research track. `—` = permanent principle / negative requirement (applies in every phase).

### Verification

- `E01`–`E20`: CONTRACT §8 scenarios.
- `NEW:E21`…`NEW:E87`: proposed E2E scenarios, defined in §B.1.
- `NEW:CI-nn`: proposed automated non-E2E checks (vectors, fuzz, simulator, benchmarks, lint, build), §B.2.
- `NEW:MON-nn`: verified by an exported metric + tested alert/SLO rule, §B.3.
- `NEW:REV-nn`: human/document deliverable with a recorded sign-off, §B.4.
- `A-…`: attack-catalog ids. `docs/security/attack-catalog.md` does not exist on `main` yet; when it lands, `mo-sec` ids are added next to the E-ids of rows in 06 §3 and 03 §7.

Status: every row starts `todo`.

---

## 00 — PLAN (master index)

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-00-001 | Everything (relay, client, spec, docs) is open source, one public monorepo, dual-licensed Apache-2.0 OR MIT (root license files + per-crate/module license metadata) | 00 header; 01 §3.1 | integrator + mo-docs* | 0 | NEW:CI-18 | todo |
| T-00-002 | 100% free: no fees, no commission, no paid tier, no feature gating, Moochy never holds money; nothing in code or UI implies custody | 00 header; 01 §3.2; 05 §8 | human-po* | — | NEW:REV-02 | todo |
| T-00-003 | Works with any MCP client/agent and any tool with a base URL; donors on Anthropic, OpenRouter, DeepSeek, OpenAI, vetted OpenAI-compatible hosts | 00 header | mo-node + mo-worker | 1–5 | E01, E02, E03, E04, E05, NEW:E76, NEW:CI-20 | todo |
| T-00-004 | `draft-spec.md` stays unchanged; the plan supersedes it (its closed-source section is void) | 00 status | integrator | 0 | NEW:REV-02 | todo |
| T-00-005 | First artifacts written are the cross-language golden vectors in `spec/vectors/` | 00 §5 | mo-proto | 0 | NEW:CI-01 | todo |
| T-00-006 | Idea 1–17 table (µ$, sealed body + wraps, per-attempt keys, route header AAD + task sig, affinity, P2C, actor + commit-before-assign, outbox, owner-signed key log, signed checkpoints, disputes, projections, recursive firewall, MCP `files`, three-layer caps, native errors, README badge) is fully implemented — each idea is traced in its canonical doc section below | 00 §2 | integrator | 1–4 | rows of 03–08 | todo |
| T-00-007 | Glossary terms are used consistently in code identifiers and user-facing text (Node, Gateway, Worker, Relay, Door, Dialect, Pledge, Approval, Pool, Attempt, Route header, Envelope, Receipt, Projection, Dispute, Progress checkpoint, Reservation, Affinity, Firewall, Tripwire, Key log, µ$) | 00 §4 | integrator | — | NEW:REV-02 | todo |

## 01 — Vision, scope, and draft review

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-01-001 | Principle "works with anything": MCP door for any MCP client, API door for any base-URL tool, all major providers on the donor side | 01 §3.3 | mo-node | 1–5 | E01, E04, E05, NEW:CI-20 | todo |
| T-01-002 | Principle "trust no operator": confidentiality and integrity are enforced cryptographically in the client, never by trusting the relay | 01 §3.4 | mo-proto + mo-node + mo-worker | 1→3 | E13, E15, E16, E17 | todo |
| T-01-003 | Principle "donated money is sacred": cache affinity, cancellation propagation, no hedging, budget-proportional routing | 01 §3.5 | mo-relay | 2 | E08, NEW:E28, NEW:E31 | todo |
| T-01-004 | Principle "boring infrastructure": one Go binary + one SQLite file + one Rust binary; no queue, cache cluster, or microservice | 01 §3.6 | mo-relay + mo-node | — | NEW:REV-02, NEW:CI-07 | todo |
| T-01-005 | I1: a provider API key never leaves the donor's machine (keystore + Worker-only use, sent only to allowlisted provider hosts) | 01 §4 I1 | mo-node + mo-worker | 1 | E13, NEW:E59 | todo |
| T-01-006 | I2: the relay cannot read prompts or outputs | 01 §4 I2 | mo-proto + mo-node | 1 | E13, E17 | todo |
| T-01-007 | I3: a donor never spends more than their caps (bounded by open-attempt overages) | 01 §4 I3 | mo-relay + mo-worker | 1 | E10, E11 | todo |
| T-01-008 | I4: a donor's account never executes anything server-side or touches account data for a maintainer | 01 §4 I4 | mo-worker | 1 | E09, NEW:E55 | todo |
| T-01-009 | I5: every unit of spend has a donor-signed receipt checked by the Gateway (signed dispute on mismatch) and a donor-signed projection; every executed tool call carries a donor signature | 01 §4 I5 | mo-node + mo-worker + mo-relay | 1→3 | E01, NEW:E43, NEW:E44 | todo |
| T-01-010 | I6: maintainers' tools work unmodified (two doors) | 01 §4 I6 | mo-node | 1 | E01, E04, E05, NEW:CI-20 | todo |
| T-01-011 | I7: no personal data in the append-only log (pseudonyms + salted commitments) | 01 §4 I7 | mo-relay | 3 | NEW:E40 | todo |
| T-01-012 | I8: no silent spend — every cent is in the donor's local journal | 01 §4 I8 | mo-node + mo-worker | 1 | NEW:E60 | todo |
| T-01-013 | I9: the relay can neither invent a donor, member, or key, nor originate or replay a task, without published evidence | 01 §4 I9 | mo-node + mo-worker + mo-relay | 1→3 | E15, E16, NEW:E41 | todo |
| T-01-014 | Goal: donors pledge µ$ budgets to public repos using Anthropic, OpenRouter, DeepSeek, or OpenAI keys | 01 §5.1 | mo-relay + mo-web + mo-node | 1–4 | E01, E02, E03, NEW:E76 | todo |
| T-01-015 | Goal: maintainers and members consume through MCP or provider-compatible APIs from any client | 01 §5.1 | mo-node | 1 | E01, E04, E05 | todo |
| T-01-016 | Goal: real-time public pages, README badges, verifiable receipts | 01 §5.1 | mo-web + mo-node | 4 | E19, NEW:E61, NEW:E64 | todo |
| T-01-017 | Goal: self-hostable relay with a documented recipe | 01 §5.1 | mo-ops* + mo-docs* | 6 | NEW:REV-02, NEW:CI-21 | todo |
| T-01-018 | Non-goal: no payments, escrow, crypto tokens, or money flow | 01 §5.2 | human-po* | — | NEW:REV-02 | todo |
| T-01-019 | Non-goal: never host donor keys or run inference on Moochy servers | 01 §5.2 | mo-relay | — | NEW:REV-02, E13 | todo |
| T-01-020 | Non-goal: no arbitrary compute (shell, containers, binaries) | 01 §5.2 | mo-worker | — | E09, NEW:E55 | todo |
| T-01-021 | Non-goal: no content moderation by the relay | 01 §5.2 | mo-relay | — | E13 | todo |
| T-01-022 | Non-goal: no private repositories on the public instance (v1); repo claim of a private repo is refused when the instance is configured public-only | 01 §5.2; 06 §5 | mo-relay | 1 | NEW:E63 | todo |
| T-01-023 | Non-goal: no cross-dialect request translation (v1) | 01 §5.2 | mo-relay + mo-node | — | NEW:E27 | todo |
| T-01-024 | Metric: task success rate (excl. provider errors and cancels) ≥ 99.5% at beta | 01 §5.3 | mo-relay + mo-ops* | 2/6 | NEW:CI-22, NEW:MON-02 | todo |
| T-01-025 | Metric: relay-added latency p50 ≤ 60 ms same continent | 01 §5.3 | mo-relay | 2 | E20, NEW:MON-02 | todo |
| T-01-026 | Metric: ledger drift vs provider bills ≤ 0.5% | 01 §5.3 | mo-node + mo-worker | 1 | NEW:CI-20 | todo |
| T-01-027 | Metric: cache-read share of input tokens in agent sessions ≥ 80% | 01 §5.3 | mo-relay + mo-node | 2 | NEW:CI-20, NEW:MON-02 | todo |
| T-01-028 | Metric: donor onboarding → first served task < 5 min | 01 §5.3 | human-po* + mo-node | 4 | NEW:REV-04 | todo |
| T-01-029 | Metric: maintainer onboarding → agent on donated compute < 3 min | 01 §5.3 | human-po* + mo-node | 4 | NEW:REV-04 | todo |
| T-01-030 | Metric: ≥ 10 clients verified working through either door | 01 §5.3 | mo-e2e* + mo-node | 5 | NEW:CI-20 | todo |
| T-01-031 | Metric: public instance infra ≤ $200/month at 1M tasks/month | 01 §5.3 | mo-ops* | 6 | NEW:REV-06 | todo |
| T-01-032 | Draft "chi" dropped: stdlib `ServeMux` only | 01 §6 | mo-relay + mo-web | 1 | NEW:CI-02 | todo |
| T-01-033 | Draft `simd-json` dropped (no SIMD JSON dependency) | 01 §6 | mo-node | 1 | NEW:CI-07 | todo |
| T-01-034 | Draft per-repo `mcp_secret` dropped: no shared secret stored server-side; device-key handshake instead | 01 §6; 03 §3 | mo-relay | 1 | NEW:E21 | todo |
| T-01-035 | Ed25519 only; no GPG/OpenPGP anywhere | 01 §6 | mo-proto | 1 | NEW:CI-07 | todo |
| T-01-036 | Models never hard-coded: signed, versioned catalog fed from provider model lists | 01 §6; 05 §2 | mo-relay + mo-node | 1→3 | NEW:E39 | todo |
| T-01-037 | Draft verdict: public presence aggregated, per-node RTT/"verified" panel removed; honest verification via `moochy verify` | 01 §6 | mo-web + mo-node | 4 | NEW:E66, NEW:E61 | todo |

## 02 — Architecture overview

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-02-001 | Relay **Edge**: TLS termination in-process (autocert in prod; cert/key flags for tests), WS upgrade, device auth handshake, frame parsing, per-connection reader + writer goroutines, data-plane forwarding | 02 §3.1 | mo-relay | 1 | E01, NEW:E21 | todo |
| T-02-002 | Relay **Scheduler**: single goroutine owning all routing and budget state (workers, pledges, pools, affinity, in-flight) | 02 §3.1; 04 §1 | mo-relay | 1 | NEW:CI-04 | todo |
| T-02-003 | Relay **Ledger**: pure accounting rules (cost, reservation math, settlement) + persistence; no in-memory state of its own | 02 §3.1 | mo-relay | 1 | NEW:CI-10 | todo |
| T-02-004 | Relay **Key log** component: append entries, tree hashes, checkpoints only for replicated sizes, hourly Git anchor, tile serving | 02 §3.1; 06 §10 | mo-relay | 3 | NEW:E40, NEW:E42 | todo |
| T-02-005 | Relay **Identity**: GitHub/GitLab OAuth, device-approval flow, repo-claim verification; users, identities, devices, sessions | 02 §3.1 | mo-relay | 1/5 | NEW:E63 | todo |
| T-02-006 | Relay **Web**: HTMX pages, SSE hub (render once, fan out), badges, public verification pages | 02 §3.1 | mo-web | 4 | E19, NEW:E64, NEW:E65 | todo |
| T-02-007 | Relay **Store**: one writer goroutine with group commit, read-only connection pool, embedded forward-only migrations | 02 §3.1; 09 §2 | mo-relay | 1 | NEW:E67, E12 | todo |
| T-02-008 | Relay **Catalog**: versioned price/model catalog, signed, published to Nodes | 02 §3.1; 05 §2 | mo-relay | 1→3 | NEW:E39 | todo |
| T-02-009 | Node **Relay link**: single WSS connection, auth, reconnect with jittered backoff, frame mux | 02 §3.2 | mo-node | 1 | E01, E12, NEW:E33 | todo |
| T-02-010 | Node **Keystore**: Ed25519 signing key, X25519 encryption key, provider keys; OS keychain + encrypted-file fallback | 02 §3.2; 06 §4 | mo-node | 1/5 | NEW:E71, NEW:CI-16 | todo |
| T-02-011 | Node **Gateway**: loopback provider APIs, repo-scoped tokens, affinity key, task signing, compression + sealing to owner-approved donors, scrubber, tool-call checks, native errors, receipt checks + disputes, optional own-key fallback | 02 §3.2; 07 §4 | mo-node | 1→3 | E01, E14, E18, NEW:E43 | todo |
| T-02-012 | Node **MCP server**: stdio (`moochy mcp`, forwards to running Node over local socket) + Streamable HTTP on loopback; same tools | 02 §3.2; 07 §5 | mo-node | 1 | E04, E05 | todo |
| T-02-013 | Node **Worker**: slot grants, envelope opening, firewall, adapters with warm pools, usage extraction, cancellation, local caps, receipt signing, outbox | 02 §3.2; 07 §6 | mo-worker + mo-node | 1 | E01, E09, E11, E12 | todo |
| T-02-014 | Node **Monitor**: mirror key log, check checkpoint consistency and Git anchor, alert on unknown own-account keys and (owners) unsigned claims/approvals/memberships | 02 §3.2; 06 §10 | mo-node | 3 | NEW:E40, NEW:E41, NEW:E42 | todo |
| T-02-015 | Node **Local journal**: append-only record of every task served or consumed (metadata always, full text opt-in) | 02 §3.2; 07 §6.5 | mo-node | 1 | NEW:E60 | todo |
| T-02-016 | Trust boundary: relay sees routing metadata only; donor output is treated as UNTRUSTED by the Gateway | 02 §4 | mo-node | 1→3 | E13, E18 | todo |
| T-02-017 | Primary flow sequence (submit → schedule → reserve → commit → assign → ack → accepted → started → chunks → end → settle → receipt.ack → Gateway check → dispute on mismatch) implemented end to end | 02 §5 | mo-relay + mo-node + mo-worker | 1 | E01 | todo |
| T-02-018 | `moochy_delegate` builds the same request inside the Node and follows the identical pipeline from signing onward | 02 §5 | mo-node | 1 | E04 | todo |
| T-02-019 | Money settles on the donor-signed receipt; public feed shows the donor-signed projection (daily granularity, no device ids) | 02 §5 | mo-relay + mo-web | 1/4 | E01, E19, NEW:E66 | todo |
| T-02-020 | Secondary flow: device login (keys created, code + URL, browser approval, `KEY_ADDED`, device id returned) | 02 §6 | mo-node + mo-relay + mo-web | 1→3 | E01 (login step), NEW:E63, NEW:E40 | todo |
| T-02-021 | Secondary flow: repo claim (OAuth admin check at claim time, token not stored, owner's Node signs `REPO_CLAIMED`) | 02 §6; 06 §5 | mo-relay + mo-node | 1→3 | NEW:E63, NEW:E82 | todo |
| T-02-022 | Secondary flow: pledge (repo, budget µ$, per-task cap, models, max effort, schedule → owner signs `DONOR_APPROVED` → Scheduler indexes → Gateways may seal) | 02 §6 | mo-web + mo-relay + mo-node | 1→3 | NEW:E37, NEW:E82 | todo |
| T-02-023 | Secondary flow: reclaim / pause stops new reservations at once; in-flight settle; unspent released | 02 §6; 05 §8 | mo-relay | 2 | NEW:E37 | todo |
| T-02-024 | Secondary flow: settlement recovery (Workers abort + receipt on relay loss, `known_tasks`, outbox replay, idempotent by `(task_id, attempt)`, orphans released) | 02 §6; 05 §7 | mo-relay + mo-worker + mo-node | 1 | E12, NEW:E32 | todo |
| T-02-025 | Secondary flow: log monitoring by every Node | 02 §6 | mo-node | 3 | NEW:E40, NEW:E42 | todo |
| T-02-026 | Control plane = one goroutine (actor); data plane = `sync.Map` forwarding table `task_id → destination`, one lookup + one channel send per chunk | 02 §7 | mo-relay | 1 | NEW:CI-06 | todo |
| T-02-027 | Control-plane latency target p99 < 50 µs per event at 10k online workers | 02 §7 | mo-relay | 2 | NEW:CI-06 | todo |
| T-02-028 | Deployment: one process, one SQLite file, Litestream sidecar; no reverse proxy, Redis, or queue | 02 §8 | mo-ops* + mo-relay | 1 | NEW:REV-02, NEW:CI-21 | todo |
| T-02-029 | TLS via ACME autocert inside the Go process | 02 §8; 10 §2 | mo-relay | 6 | NEW:CI-21 | todo |
| T-02-030 | Litestream continuous WAL shipping (RPO ≈ 1 s DB, 0 for spend) | 02 §8; 09 §7 | mo-ops* | 1 | NEW:CI-21, NEW:E34 | todo |
| T-02-031 | Deploys drain-and-restart (≤ 30 s drain, ~10 s retryable errors, zero drift); blue/green deferred | 02 §8; 10 §3 | mo-relay + mo-ops* | 2 | NEW:E33 | todo |
| T-02-032 | Log tiles immutable once full, CDN-cacheable | 02 §8; 09 §3.5 | mo-relay | 3 | NEW:E40 | todo |
| T-02-033 | Go relay stack: stdlib `net/http` ServeMux, `coder/websocket`, `modernc.org/sqlite`, `x/mod/sumdb/tlog`+`note` (C2SP tiles), `x/oauth2` | 02 §9 | mo-relay | 1/3 | NEW:CI-02 | todo |
| T-02-034 | Frontend: `html/template` + HTMX 2 + `htmx-ext-sse`, pages < 50 KB, no Node toolchain at runtime (CSS per CONTRACT §9: hand-written, see §D) | 02 §9; 08 §1 | mo-web | 4 | NEW:CI-09 | todo |
| T-02-035 | Client stack: Rust stable, tokio, rustls-only WS/HTTP (HTTP/2), hyper local server, standard crypto crates, `serde_json`, `zstd`, `rmcp` (stdio + Streamable HTTP), no OpenSSL | 02 §9; 07 §10 | mo-node + mo-proto + mo-worker | 1 | NEW:CI-07 | todo |
| T-02-036 | Secrets at rest: `keyring` (macOS/Windows/Secret Service) + scrypt-encrypted file fallback | 02 §9; 06 §4.1 | mo-node | 1/5 | NEW:E71, NEW:CI-16 | todo |
| T-02-037 | Release: cargo-dist + Sigstore + SLSA provenance + reproducible builds | 02 §9; 07 §11 | mo-release* | 3 | NEW:CI-08 | todo |
| T-02-038 | Repo layout: `spec/protocol.md` (normative wire spec derived from 03) | 02 §10 | integrator | 0 | NEW:REV-02 | todo |
| T-02-039 | Repo layout: `relay/tools/simulate` deterministic scheduler simulator (dev only) | 02 §10; 04 §12 | mo-relay | 2 | NEW:CI-04 | todo |
| T-02-040 | Repo layout: fuzz targets for firewall and frames (placed in the owning crates) | 02 §10; 07 §13 | mo-worker + mo-proto | 1/3 | NEW:CI-03 | todo |
| T-02-041 | Repo layout: `deploy/` (self-host guide, systemd units, container recipe) and `docs/` user guides + public threat model | 02 §10 | mo-ops* + mo-docs* + mo-sec | 6 | NEW:REV-02 | todo |
| T-02-042 | Self-hosting first-class: Nodes choose their relay with one config value; no federation | 02 §10; 10 §10.1 | mo-node + mo-relay | 1 | E01 (custom relay URL) | todo |
| T-02-043 | Latency: zstd before sealing (v1); warm HTTP/2 provider pools; streaming pass-through with no buffering | 02 §11 | mo-node + mo-worker + mo-relay | 1 | E01, NEW:E75, E20 | todo |
| T-02-044 | Added latency budget 50–120 ms in-continent / 150–250 ms intercontinental | 02 §11 | mo-relay + mo-node | 0/2 | NEW:CI-20, NEW:MON-02 | todo |
| T-02-045 | Scale design point on one node: 50k WebSockets (~20–40 KB each), 5k concurrent streams, ≈ 200 task starts/s, ≈ 200 receipts/s, 20k SSE subscribers | 02 §12 | mo-relay + mo-web | 6 | NEW:CI-19 | todo |
| T-02-046 | Scale-out path (only when measured): shard Scheduler + SQLite by `repo_id` with consistent hashing; global users/devices/key log; Workers connect per shard | 02 §12; 10 §9 | mo-relay | D | NEW:MON-03 | todo |

## 03 — Wire protocol (`moochy.v1`)

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-03-001 | One WSS connection per Node carries all roles and all concurrent tasks; local clients share it through the Node | 03 §1.1 | mo-node | 1 | E04, E05, NEW:E72 | todo |
| T-03-002 | Control = small JSON text frames; bulk (bodies, output chunks) = binary frames, never base64 in JSON | 03 §1.2 | mo-proto + mo-relay | 1 | E01, NEW:CI-01 | todo |
| T-03-003 | Relay routes only on the plaintext route header; never chooses keys; every key unique per body and per attempt | 03 §1.3 | mo-proto | 1 | NEW:CI-01, E17 | todo |
| T-03-004 | Sign bytes, not objects: signed artifacts are transmitted and stored as the exact signed byte strings, never re-serialized | 03 §1.4 | mo-proto + mo-relay | 1 | NEW:CI-01, NEW:E38 | todo |
| T-03-005 | Domain separation: every signature, commitment, and KDF input starts with a distinct `lp` label (CONTRACT §2 list) | 03 §1.5 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-006 | Task ids are Gateway-created ULIDs; dedupe scope is `(gateway_device, task_id)` | 03 §1.6 | mo-relay + mo-node | 1 | NEW:E48 | todo |
| T-03-007 | Errors reach clients in the provider's native shapes; policy failures explicitly non-retryable | 03 §1.7 | mo-node | 1/2 | E10, NEW:E52 | todo |
| T-03-008 | Node endpoint `wss://<relay>/v1/node`, any self-hosted relay | 03 §2 | mo-relay + mo-node | 1 | E01 | todo |
| T-03-009 | TLS 1.3 only, terminated in the Relay process (required for channel binding) | 03 §2 | mo-relay + mo-node | 1 | NEW:E21 | todo |
| T-03-010 | WS subprotocol `moochy.v1` required; upgrade rejected without it | 03 §2 | mo-relay | 1 | NEW:E21 | todo |
| T-03-011 | `permessage-deflate` disabled on both ends | 03 §2 | mo-relay + mo-node | 1 | NEW:E23 | todo |
| T-03-012 | WS ping every 15 s; peer dead after 2 missed pongs or TCP close | 03 §2 | mo-relay + mo-node | 1 | NEW:E32 | todo |
| T-03-013 | Ping RTT feeds the Scheduler's latency estimate (EWMA α = 0.2) | 03 §2; 04 §3 | mo-relay | 2 | NEW:CI-04 | todo |
| T-03-014 | Max frame 64 KiB including 23-byte header and 16-byte tag | 03 §2, §4.2 | mo-proto + mo-relay | 1 | NEW:E23, NEW:CI-01 | todo |
| T-03-015 | Max request body 32 MiB decompressed (Worker checks); Relay checks sealed size against the same bound | 03 §2, §16 | mo-worker + mo-relay | 1 | NEW:E23 | todo |
| T-03-016 | Upgrade request carries the client version header | 03 §3 | mo-node | 1 | NEW:E70 | todo |
| T-03-017 | `hello {nonce (32 B random), server_time, min_client_version, relay_release, log_checkpoint}` | 03 §3 | mo-relay | 1 | NEW:E21 | todo |
| T-03-018 | `auth {device_id, roles, sig}` with `sig = Ed25519(lp("moochy/v1/auth", nonce, dialed_origin, tls_exporter, device_id))` | 03 §3; CONTRACT §3 | mo-proto + mo-node | 1 | NEW:CI-01, NEW:E21 | todo |
| T-03-019 | Relay looks up device (not revoked), recomputes with its own origin + exporter, verifies (ZIP-215), checks roles | 03 §3 | mo-relay | 1 | NEW:E21 | todo |
| T-03-020 | `welcome {session_id, granted roles, limits, catalog_version}` | 03 §3 | mo-relay | 1 | E01 | todo |
| T-03-021 | After welcome: Gateway receives `pool.sync`; Worker sends `worker.known_tasks` then `worker.offer` | 03 §3 | mo-relay + mo-node | 1 | E01, NEW:E32 | todo |
| T-03-022 | `dialed_origin` = origin the Node itself dialed and verified with TLS, never taken from `hello` | 03 §3 | mo-node | 1 | NEW:E21 | todo |
| T-03-023 | `tls_exporter` = RFC 9266 `EXPORTER-Channel-Binding`, empty context, 32 bytes, on both sides | 03 §3; CONTRACT §3 | mo-node + mo-relay | 1 | NEW:CI-01, NEW:E21 | todo |
| T-03-024 | No bearer token on the wire; no shared secret stored server-side (DB leak exposes only public keys) | 03 §3 | mo-relay | 1 | NEW:E21, E13 | todo |
| T-03-025 | A new successful auth for a device closes its previous session; events from non-current sessions ignored | 03 §3, §14 | mo-relay | 2 | NEW:E22 | todo |
| T-03-026 | Clock skew > 5 min vs `server_time` → local warning | 03 §3 | mo-node | 1 | NEW:E69 | todo |
| T-03-027 | Text frame: JSON object with mandatory `t`; task-scoped messages carry `task` (ULID) and `attempt` | 03 §4.1 | mo-proto + mo-relay | 1 | NEW:CI-01 | todo |
| T-03-028 | Unknown fields ignored; unknown `t` answered with `error{code:"unknown_type"}` and otherwise ignored | 03 §4.1 | mo-relay + mo-node | 1 | NEW:E23 | todo |
| T-03-029 | Binary header (23 B): `kind` u8, `task_id` 16 B, `attempt` u8 (1–3), `seq` u32 BE from 0, `flags` bit0 = last | 03 §4.2 | mo-proto + mo-relay | 1 | NEW:CI-01, NEW:E23 | todo |
| T-03-030 | Kinds: `0x01` request chunk, `0x02` response chunk, `0x03` reserved (rejected in v1) | 03 §4.2 | mo-proto + mo-relay | 1 | NEW:E23 | todo |
| T-03-031 | Plaintext chunk ≤ 65,497 bytes | 03 §4.2 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-032 | Edge forwards a binary frame only from the connection registered as the task's expected source; others dropped and counted | 03 §4.2 | mo-relay | 1 | NEW:E23, E17 | todo |
| T-03-033 | `pool.sync` (R→G): `repo`, `workers[]{worker_device, enc_pub, key_log_index, approval_log_index, donor_pseudonym, dialects, models[], hint}`, `full`/`delta`; full after welcome, delta on change; `hint` 0–100 at most 1/s | 03 §5.1; 04 §7 | mo-relay | 1/2 | E01, NEW:E25 | todo |
| T-03-034 | Gateway independently verifies from its key-log mirror that each pool worker key is logged and the donor has an owner-signed approval for the repo | 03 §5.1; 06 §10 | mo-node | 3 | NEW:E41 | todo |
| T-03-035 | `task.submit` (G→R): `task`, `route_b64`, `wraps[]{worker_device, wrap}`, `body_len`, `body_chunks`, followed by `0x01` frames | 03 §5.1; CONTRACT §5 | mo-node + mo-relay | 1 | E01 | todo |
| T-03-036 | `task.need_wraps` (R→G, `workers[]`) when no wrapped candidate is eligible; `task.wraps` answers without resending the body | 03 §5.1 | mo-relay + mo-node | 2 | NEW:E25 | todo |
| T-03-037 | `task.accepted {task, attempt, worker_device, R}`; Gateway decrypts only this attempt's stream | 03 §5.1 | mo-relay + mo-node | 1 | E01, NEW:E47 | todo |
| T-03-038 | `task.started` (R→G) forwarded when provider headers arrive; no failover after it, ever | 03 §5.1 | mo-relay | 1 | E06, NEW:E26 | todo |
| T-03-039 | `task.checkpoint {task, attempt, seq, running_hash, sig}` forwarded W→R→G | 03 §5.1–5.2 | mo-relay + mo-worker + mo-node | 3 | NEW:E44 | todo |
| T-03-040 | Response `0x02` frames delivered to the Gateway in `seq` order | 03 §5.1 | mo-relay | 1 | E01 | todo |
| T-03-041 | `task.end {task, attempt, receipt_b64, donor_sig, projection_b64, projection_sig}` (W→R and R→G) | 03 §5; CONTRACT §5 | mo-proto + mo-relay | 1 | E01 | todo |
| T-03-042 | `task.failed {task, code, retryable, retry_after_ms, sealed_detail?}` converted by the Gateway into a native error | 03 §5.1 | mo-relay + mo-node | 1 | E07, E10, NEW:E52 | todo |
| T-03-043 | `task.cancel {task, reason}` (G→R) when the client closes the request | 03 §5.1 | mo-node | 1 | E08 | todo |
| T-03-044 | `receipt.dispute {task, attempt, code, gateway_sig}` only on mismatch | 03 §5.1 | mo-node + mo-relay | 3 | NEW:E43 | todo |
| T-03-045 | `worker.known_tasks {tasks[]{task, attempt, state}}` right after welcome; Relay releases at zero cost any reservation for that Worker not listed | 03 §5.2; 05 §7 | mo-node + mo-relay | 1 | E12, NEW:E32 | todo |
| T-03-046 | `worker.offer {slots_free, models[]{dialect, model, rl_headroom}, pledges[], window_open, local_cap_left}` on connect and on change; only the latest per worker kept (coalesced) | 03 §5.2; 04 §2 | mo-node + mo-relay | 1/2 | E01, NEW:E29 | todo |
| T-03-047 | `task.assign {task, attempt, route_b64, wrap, pledge, deadline_ack_ms}` sent only after the reservation is durably committed, followed by body frames | 03 §5.2; 04 §8.1 | mo-relay | 1 | E12, NEW:CI-04 | todo |
| T-03-048 | `task.ack {task, attempt, R}` within 500 ms of last body frame = authentic, decrypted, firewall passed, local caps reserved, provider call starting | 03 §5.2 | mo-node + mo-worker | 1 | E01, NEW:E26 | todo |
| T-03-049 | `task.nack {task, attempt, R, code, retryable, retry_after_ms, sealed_detail?}`; detail sealed to the Gateway, Relay sees only the code | 03 §5.2 | mo-node + mo-worker | 1 | E09, E07 | todo |
| T-03-050 | Worker `task.started` when provider response headers arrive | 03 §5.2 | mo-worker + mo-node | 1 | E06 | todo |
| T-03-051 | Worker `task.end` also replayed from the outbox after reconnect | 03 §5.2 | mo-node | 1 | E12 | todo |
| T-03-052 | `task.cancel` (R→W): Worker aborts the provider request immediately | 03 §5.2, §13 | mo-node + mo-worker | 1 | E08 | todo |
| T-03-053 | `receipt.ack` only after the receipt commit with `synchronous=FULL`; Worker marks outbox entry acknowledged and keeps it 7 more days | 03 §5.2; 05 §7 | mo-relay + mo-node | 1 | E12, NEW:E83 | todo |
| T-03-054 | `receipt.replay_since {since}` after DR restore: Worker resends every receipt (acked or not) since that time | 03 §5.2 | mo-relay + mo-node | 2 | NEW:E34 | todo |
| T-03-055 | `relay.draining {reconnect_after_ms}`: Gateways 0, Workers jittered 0–10 s | 03 §5.3 | mo-relay + mo-node | 2 | NEW:E33 | todo |
| T-03-056 | `log.checkpoint` pushes the newest signed key-log checkpoint | 03 §5.3 | mo-relay + mo-node | 3 | NEW:E40 | todo |
| T-03-057 | `catalog.update` pushes a new signed catalog; Nodes reject version decreases | 03 §5.3 | mo-relay + mo-node | 1→3 | NEW:E39 | todo |
| T-03-058 | `error {code, message, task?}` in both directions | 03 §5.3 | mo-relay + mo-node | 1 | NEW:E23 | todo |
| T-03-059 | Per-device Ed25519 signing key used for auth, task sigs, receipts, projections, checkpoints, disputes, approvals | 03 §6.1 | mo-node + mo-proto | 1 | NEW:CI-01 | todo |
| T-03-060 | Per-device X25519 encryption key for the Worker role (not converted from Ed25519) | 03 §6.1; ADR-09 | mo-node + mo-proto | 1 | NEW:CI-01 | todo |
| T-03-061 | CK = 32 random bytes fresh for every sealed body, used only as HKDF input | 03 §6.1; CONTRACT §3 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-062 | `K_req = HKDF(salt="", ikm=CK, info=lp("moochy/v1/req", task_id))` | 03 §6.1; CONTRACT §3 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-063 | `R` = 32 random bytes drawn by the Worker for each attempt, sent in ack/nack | 03 §6.1 | mo-proto + mo-node | 1 | NEW:CI-01, E06 | todo |
| T-03-064 | `RK = HKDF(salt=R, ikm=CK, info=lp("moochy/v1/resp", task_id, worker_device, u64(attempt)))`; vector proves two attempts derive different keys | 03 §6.1; CONTRACT §3 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-065 | Commitment salts: `S` 32 B in the sealed payload; `S_req`, `S_resp`, `S_pid` = HKDF(S, lp("moochy/v1/salt", name)) | 03 §6.1 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-066 | Any re-seal uses a fresh CK with fresh wraps (never reuse CK for a second body) | 03 §6.1 | mo-node | 1 | NEW:CI-01 | todo |
| T-03-067 | Inner payload JSON per CONTRACT §4 (`v, body_b64, body_sha256, headers, S, gateway_device, task_sig`), zstd level 3, then chunked + sealed | 03 §6.2; CONTRACT §4 | mo-proto + mo-node | 1 | NEW:CI-01, E01 | todo |
| T-03-068 | Request chunks: ChaCha20-Poly1305 under `K_req`, nonce = `0^8 ‖ u32_be(seq)`, AAD = `lp("moochy/v1/req", kind, task_id_16B, u32(seq), last)` | 03 §6.2; CONTRACT §1, §3 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-069 | Wrap per candidate: HPKE base (X25519/HKDF-SHA256/ChaCha20-Poly1305), `info = lp("moochy/v1/wrap", suite_id, task_id)`, `aad = route_header_bytes`, 80-byte output | 03 §6.2; CONTRACT §3 | mo-proto | 1 | NEW:CI-01, E15 | todo |
| T-03-070 | Body sealed once; adding a recipient costs one more wrap, never a re-upload | 03 §6.2 | mo-node + mo-relay | 2 | NEW:E25 | todo |
| T-03-071 | `suite_id` in HPKE info and in each device's `KEY_ADDED` entry (downgrade protection) | 03 §6.2; 06 §4.1 | mo-proto + mo-relay | 1→3 | NEW:CI-01, NEW:E40 | todo |
| T-03-072 | Response chunks under RK, nonce = seq, AAD = `lp("moochy/v1/resp", task_id_16B, u64(attempt), R, u32(seq), last)` | 03 §6.3; CONTRACT §3 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-073 | Gateway decrypts only frames of the attempt named in `task.accepted`, under that attempt's RK | 03 §6.3 | mo-node | 1 | E17, NEW:E47 | todo |
| T-03-074 | Gateway aborts the task if response frames ever appear for a second started attempt | 03 §6.3 | mo-node | 1 | NEW:E47 | todo |
| T-03-075 | AAD binding rejects reordering, splicing across tasks/attempts, and silent truncation (stream without a `last` frame is an error) | 03 §6.3 | mo-node + mo-proto | 1 | E17, NEW:E47 | todo |
| T-03-076 | Relay sees only route header, sizes/timings, NACK codes, usage + cost; never content, provider headers, NACK details, salts, or raw provider request id | 03 §6.4 | mo-relay + mo-node | 1 | E13 | todo |
| T-03-077 | Route header JSON `{repo_id, dialect, model, effort, max_tokens, est_input_tokens, cache_ttl, stream, affinity, flags}` built by the Gateway | 03 §7.1; CONTRACT §5 | mo-node | 1 | E01, NEW:CI-01 | todo |
| T-03-078 | Worker check: `repo_id` equals the repo of the assigned pledge (Worker's own pledge table) | 03 §7.1 | mo-node + mo-worker | 1 | NEW:E41 | todo |
| T-03-079 | Worker check: `dialect`, `model` (after catalog mapping), effective `effort` (catalog default when absent), `max_tokens` (present, exact), `stream` all match the body | 03 §7.1 | mo-worker | 1 | NEW:E55 | todo |
| T-03-080 | `est_input_tokens = ceil(text_bytes/3) + images × max_image_tokens + pages × max_page_tokens`, recomputed by the Worker and matched exactly | 03 §7.1 | mo-worker + mo-node | 1 | NEW:CI-01, NEW:E55 | todo |
| T-03-081 | `cache_ttl` = longest `cache_control.ttl` present (`none`, `5m`, `1h`), checked by the Worker | 03 §7.1 | mo-worker + mo-node | 1 | NEW:E55 | todo |
| T-03-082 | `affinity` = HMAC(per-device secret, lp(system, tools, first user message)) truncated to 16 B; not checked by the Worker | 03 §7.1; 04 §5 | mo-node | 2 | NEW:E28 | todo |
| T-03-083 | `flags` (`fast`, `images`, `documents`, …) each require the donor's opt-in | 03 §7.1 | mo-worker + mo-relay | 1 | NEW:E55 | todo |
| T-03-084 | Route mismatch → `task.nack{route_mismatch, retryable:false}` and a strike against the submitting member | 03 §7.1 | mo-worker + mo-relay | 1 | NEW:E55 | todo |
| T-03-085 | `task_sig = Ed25519(gw_key, lp("moochy/v1/task", task_id, repo_id, route_header_bytes, body_sha256, headers_sha256))`, inside the sealed payload | 03 §7.2; CONTRACT §3 | mo-proto + mo-node | 1 | NEW:CI-01 | todo |
| T-03-086 | Worker check 1: `task_sig` valid for `gateway_device`, whose key is logged and not revoked | 03 §7.2 | mo-node + mo-worker | 1→3 | E16, NEW:E41 | todo |
| T-03-087 | Worker check 2: owner-signed `MEMBER_ADDED` for that user + `repo_id` in the key log, or the user is the repo owner | 03 §7.2 | mo-node | 3 | NEW:E41 | todo |
| T-03-088 | Worker check 3: assigned pledge belongs to this donor and to `repo_id` | 03 §7.2 | mo-node | 1 | NEW:E41 | todo |
| T-03-089 | Worker check 4: ULID timestamp of `task_id` within ±10 min of the Worker clock | 03 §7.2 | mo-node + mo-worker | 1 | NEW:E56 | todo |
| T-03-090 | Worker check 5: `(gateway_device, task_id)` never served before (persisted set covering the ±10 min window) | 03 §7.2 | mo-worker + mo-node | 1 | E16, NEW:E56 | todo |
| T-03-091 | Worker body handling order: find wrap → HPKE-open CK → K_req → decrypt → zstd-decompress → check `body_sha256` | 03 §8 | mo-node + mo-proto | 1 | E01, E15 | todo |
| T-03-092 | Then verify §7.2, then firewall, then route-header checks, then local reservation, then draw R, ack, call provider | 03 §8 | mo-node + mo-worker | 1 | E09, E11, E16 | todo |
| T-03-093 | Prefix-delta transfer: designed, not built in v1; frame kind `0x03` reserved; build trigger = upload p50 > 150 ms or egress in top-3 costs | 03 §9; ADR-21 | mo-proto + mo-relay + mo-node | D | NEW:MON-03 | todo |
| T-03-094 | When delta transfer is built: every delta and full resend sealed with its own fresh CK; Worker base cache keyed by `(gateway_device, base_task_id)` | 03 §9 | mo-proto + mo-node | D | NEW:CI-01 (future) | todo |
| T-03-095 | Wire task lifecycle states and transitions exactly as 03 §10.1 (Submitted, Assigned, Acked, Started, Reassigning, Ended, Failed, Cancelled) | 03 §10.1 | mo-relay | 1/2 | NEW:CI-04 | todo |
| T-03-096 | No failover after `task.started`; mid-stream failures become native retryable errors | 03 §10.1; ADR-20 | mo-relay + mo-node | 1 | E06, NEW:E26 | todo |
| T-03-097 | Late messages from a superseded attempt answered with `task.cancel` for that attempt; its receipt still settles | 03 §10.1 | mo-relay | 2 | NEW:E26 | todo |
| T-03-098 | Routing deadline (5 s) starts when the last body frame has been received by the Relay | 03 §10.1 | mo-relay | 2 | NEW:E27 | todo |
| T-03-099 | Relay frees its copy of the sealed body at `task.started` | 03 §10.1 | mo-relay | 1 | NEW:E49 | todo |
| T-03-100 | Unstarted bodies bounded by global and per-device byte budgets at the Edge; exceeded → retryable `overloaded` | 03 §10.1, §16 | mo-relay | 2 | NEW:E49 | todo |
| T-03-101 | NACK codes `busy`, `rate_limited`, `overloaded`, `provider_error`, `local_cap`, `model_unavailable` are retryable elsewhere | 03 §10.2 | mo-worker + mo-node + mo-relay | 1 | E07, NEW:E29 | todo |
| T-03-102 | NACK codes `firewall`, `route_mismatch`, `unauthorized_task`, `bad_envelope` are non-retryable | 03 §10.2 | mo-worker + mo-node + mo-relay | 1 | E09, E15, E16 | todo |
| T-03-103 | NACK effects: `rate_limited` cools down (worker, model); `overloaded` short back-off; `provider_error` failure penalty; `local_cap` excluded until next offer; `model_unavailable` removes model from offer | 03 §10.2 | mo-relay + mo-node | 2 | NEW:E29, NEW:E58 | todo |
| T-03-104 | NACK effects: `firewall` → native `invalid_request_error` + strike; `route_mismatch` → native error + strike; `unauthorized_task` and `bad_envelope` → alert | 03 §10.2 | mo-relay + mo-node | 1 | E09, E15, E16, NEW:E80 | todo |
| T-03-105 | Anthropic native errors: HTTP 429/529 with `error` body before streaming; `event: error` SSE (`overloaded_error`, `rate_limit_error`, `api_error`) after | 03 §10.3 | mo-node | 1 | NEW:E52 | todo |
| T-03-106 | OpenAI-style native errors: matching HTTP status and error object, before and after streaming | 03 §10.3 | mo-node | 1 | NEW:E52 | todo |
| T-03-107 | Policy errors non-retryable with explicit messages: `over_task_cap`, `quota_exceeded` (400/403), `model_not_in_pool` (404), `firewall` (400 with sealed detail) | 03 §10.3 | mo-node + mo-relay | 1/2 | E10, NEW:E27, NEW:E52 | todo |
| T-03-108 | Capacity grants: Workers offer `slots_free` (default 4, range 1–64); Relay never pushes beyond it; decrements on assign; subtracts reservation from `local_cap_left`; fresh offer on task end / headroom / window change | 03 §11 | mo-node + mo-relay | 1/2 | E01, E11, NEW:E57 | todo |
| T-03-109 | Receipt fields: `v, task_id, attempt, repo_id, pledge_id, worker_device, gateway_device, dialect, provider, model_reported, usage{input, output, cache_write_5m, cache_write_1h, cache_read, estimated, provider_cost}, catalog_version, cost_uusd, req_commit, resp_commit, provider_req_hash, status, t_start, t_started, t_end` | 03 §12.1 | mo-proto + mo-worker | 1 | NEW:CI-01, E01 | todo |
| T-03-110 | `req_commit = SHA-256(lp("moochy/v1/req-commit", S_req, body as sent by the Gateway before any Worker mutation))` | 03 §12.1 | mo-proto + mo-node | 1 | NEW:CI-01, NEW:E54 | todo |
| T-03-111 | `resp_commit = SHA-256(lp("moochy/v1/resp-commit", S_resp, concatenated plaintext response bytes))`, computed incrementally on both sides | 03 §12.1 | mo-proto + mo-node | 1 | NEW:CI-01, NEW:E43 | todo |
| T-03-112 | `provider_req_hash = SHA-256(lp("moochy/v1/provider-req", S_pid, provider request id))` | 03 §12.1 | mo-proto + mo-worker | 1 | NEW:CI-01 | todo |
| T-03-113 | Receipt `status` ∈ {`ok`, `cancelled`, `provider_error`, `partial`, `not_started`} | 03 §12.1 | mo-worker + mo-node | 1 | E08, NEW:E32 | todo |
| T-03-114 | `donor_sig = Ed25519(worker_key, lp("moochy/v1/receipt", receipt_bytes))` | 03 §12.1 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-115 | Projection `{receipt_ref (random), repo_id, donor pseudonym (per visibility), model, cost_uusd, UTC day, SHA-256(receipt_bytes)}` + `projection_sig = Ed25519(lp("moochy/v1/projection", projection_bytes))` | 03 §12.1 | mo-proto + mo-worker | 1 | NEW:CI-01, E19 | todo |
| T-03-116 | Full receipts stay with the two parties and the Relay DB; projections reveal no device ids, task ids, or sub-day timestamps | 03 §12.1 | mo-relay + mo-web | 1/4 | NEW:E66 | todo |
| T-03-117 | Gateway receipt checks: recompute `req_commit`/`resp_commit`; input + cache within a band of its estimate; `cache_write_1h > 0` only with 1 h TTL; non-reasoning visible output within ±25%; `model_reported` = requested model or catalog alias | 03 §12.2 | mo-node | 3 | NEW:E43 | todo |
| T-03-118 | Silence = acceptance; on mismatch `receipt.dispute{code}` signed over `lp("moochy/v1/dispute", task_id, attempt, code)` | 03 §12.2 | mo-node + mo-proto | 3 | NEW:E43, NEW:CI-01 | todo |
| T-03-119 | Disputed receipts still settle money; excluded from leaderboards; queued for review | 03 §12.2 | mo-relay + mo-web | 3 | NEW:E43 | todo |
| T-03-120 | Worker signs a progress checkpoint at the end of every tool-call block (Anthropic `tool_use`; OpenAI `tool_calls` per index) and on the last chunk: `Ed25519(lp("moochy/v1/resp-progress", task_id, attempt, R, seq, running_sha256))` | 03 §12.3 | mo-worker + mo-node + mo-proto | 3 | NEW:E44, NEW:CI-01 | todo |
| T-03-121 | Gateway releases a tool-call block only after verifying a covering checkpoint; otherwise substitutes an error tool result; text streams immediately | 03 §12.3 | mo-node | 3 | NEW:E44, E18 | todo |
| T-03-122 | Ed25519 verification pinned to ZIP-215 in Go and Rust, with edge-case vectors | 03 §12.4 | mo-proto + mo-relay | 1 | NEW:CI-01 | todo |
| T-03-123 | Cancellation chain: client closes → `task.cancel` → Relay → current-attempt Worker aborts provider → receipt `cancelled` with actual usage; `estimated:true` when final usage missing → pessimistic settle | 03 §13 | mo-node + mo-relay + mo-worker | 1/2 | E08, NEW:E35 | todo |
| T-03-124 | Gateway connection drop (not a planned drain) → Relay cancels all that Gateway's unfinished tasks | 03 §13 | mo-relay | 2 | NEW:E31 | todo |
| T-03-125 | Reconnect with exponential back-off and full jitter (base 250 ms, cap 30 s) | 03 §14 | mo-node | 1 | NEW:E33 | todo |
| T-03-126 | Presence keyed by `(device_id, session_id)`; offers, offline events, and frames from non-current sessions ignored | 03 §14 | mo-relay | 2 | NEW:E22 | todo |
| T-03-127 | Resubmission of the same `task_id` by the same Gateway after reconnect: not started → route moves to the new connection; started → final state replayed | 03 §14 | mo-relay | 2 | NEW:E48 | todo |
| T-03-128 | Worker link loss: abort all in-flight provider calls; outbox receipt for each (`not_started`, zero usage, when the provider was never called); on reconnect `known_tasks` then outbox replay | 03 §14 | mo-node + mo-worker | 1 | E12, NEW:E32 | todo |
| T-03-129 | No stream resume in v1; deferred design: Relay keeps last 256 KiB per stream for 30 s if mid-stream Gateway disconnects > 0.5% of tasks | 03 §14 | mo-relay + mo-node | D | NEW:MON-03 | todo |
| T-03-130 | Breaking change → new subprotocol; a relay serves both for ≥ 90 days | 03 §15 | mo-relay | D | NEW:E70 | todo |
| T-03-131 | Within v1, fields are additive; `hello.min_client_version` refuses Nodes with known security bugs | 03 §15 | mo-relay + mo-node | 1 | NEW:E70 | todo |
| T-03-132 | Labels include `v1` and HPKE info includes the suite id (no cross-version confusion) | 03 §15 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-133 | Limit: ≤ 16 concurrent tasks per Gateway device (Relay) | 03 §16 | mo-relay | 2 | NEW:E50 | todo |
| T-03-134 | Limit: ≤ 120 task submissions per member per minute (Relay token bucket) | 03 §16; 04 §10 | mo-relay | 2 | NEW:E50 | todo |
| T-03-135 | Limit: per-task response buffer at the Relay 1 MiB; task fails if the Gateway cannot keep up | 03 §16 | mo-relay | 2 | NEW:E49 | todo |
| T-03-136 | Limit: ≤ 8 wraps per submit (Relay) | 03 §16 | mo-relay | 1 | NEW:E23 | todo |
| T-03-137 | Limit: 3 attempts per task (Relay) | 03 §16 | mo-relay | 2 | NEW:E27 | todo |
| T-03-138 | Deadlines: ACK 500 ms after last body frame reaches the Worker; start 30 s after ACK; routing 5 s after last body frame reaches the Relay | 03 §16; 04 §8.2 | mo-relay | 2 | NEW:E26, NEW:E27 | todo |
| T-03-139 | Limit: task-id freshness ±10 min (Worker) | 03 §16 | mo-node | 1 | NEW:E56 | todo |
| T-03-140 | Vectors: `lp` encoding and every label | 03 §17 | mo-proto | 0 | NEW:CI-01 | todo |
| T-03-141 | Vectors: auth signature strings with channel binding | 03 §17 | mo-proto | 0 | NEW:CI-01 | todo |
| T-03-142 | Vectors: envelope (fixed CK, recipients, R → exact wraps, K_req, RK, chunk ciphertexts), incl. two-attempts-different-keys vector | 03 §17 | mo-proto | 0 | NEW:CI-01 | todo |
| T-03-143 | Vectors: task signature, receipt, projection, progress checkpoint, dispute bytes + signatures | 03 §17 | mo-proto | 0 | NEW:CI-01 | todo |
| T-03-144 | Vectors: Ed25519 ZIP-215 edge cases (non-canonical encodings, small-order points) | 03 §17 | mo-proto | 0 | NEW:CI-01 | todo |
| T-03-145 | Vectors: binary frame headers (round trip, max sizes) | 03 §17 | mo-proto | 0 | NEW:CI-01 | todo |
| T-03-146 | Vectors: route-header ↔ body consistency cases incl. deterministic input estimate | 03 §17 | mo-proto + mo-worker | 1 | NEW:CI-01 | todo |
| T-03-147 | Vectors: tlog inclusion + consistency proofs and checkpoint note format | 03 §17 | mo-proto + mo-relay | 3 | NEW:CI-01 | todo |
| T-03-148 | Go relay, Rust client, and third-party implementations pass the same vector files; a protocol change is done only when vectors are regenerated and all pass | 03 §17 | mo-proto + mo-relay | 0 | NEW:CI-01 | todo |
| T-03-149 | Receipt reserves an optional `attestation` field (verified-compute research) without breaking v1 | 06 §15; 03 §12.1 | mo-proto | R | NEW:CI-01 | todo |

## 04 — Routing engine (Scheduler)

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-04-001 | One goroutine owns all control-plane state; every change is an ordered message; no locks on that state | 04 §1; ADR-06 | mo-relay | 1 | NEW:CI-04 | todo |
| T-04-002 | Scheduler is a pure state machine `apply(state, event) → (state', commands)`: no I/O, no clock reads (time on the event), seeded PRNG only | 04 §1, §12.1 | mo-relay | 1/2 | NEW:CI-04 | todo |
| T-04-003 | `sync.Map` only for the data-plane forwarding table `task_id → (expected source conn, destination conn)`, written once per attempt | 04 §1 | mo-relay | 1 | E17, NEW:CI-06 | todo |
| T-04-004 | Input queues: bounded **sheddable** submit queue (full → retryable reject at the Edge) | 04 §2 | mo-relay | 2 | NEW:E49 | todo |
| T-04-005 | Lifecycle queue never blocks the Edge and never drops; bounded by in-flight tasks; offers coalesced per worker | 04 §2 | mo-relay | 2 | NEW:E49, NEW:CI-04 | todo |
| T-04-006 | Web-originated changes (pledge / repo / member / approval) enter the Scheduler on the lifecycle queue | 04 §2 | mo-relay | 1 | NEW:E37 | todo |
| T-04-007 | Store writer never back-pressures the Scheduler: op slice swapped on each group commit; completions on their own channel (no cycle) | 04 §2 | mo-relay | 1 | NEW:CI-04 | todo |
| T-04-008 | Commands to connections are non-blocking sends to per-connection writer queues; overflow closes that connection (handled as disconnect) | 04 §2 | mo-relay | 1 | NEW:E49 | todo |
| T-04-009 | SSE hub receives aggregated events by non-blocking send | 04 §2; 08 §7 | mo-relay + mo-web | 4 | NEW:E65 | todo |
| T-04-010 | Timers: min-heap of short deadlines with one `time.Timer` reset to the earliest; long-horizon items are SQL sweeps, not timers | 04 §2 | mo-relay | 2 | NEW:CI-04 | todo |
| T-04-011 | State structures: `sessions`, `workers`, `pledges`, `pools`, `donorWorkers`, `members`, `devices` (capped only), `affinity`, `inflight`, `awaitingReceipt` as specified | 04 §3 | mo-relay | 1/2 | NEW:CI-04 | todo |
| T-04-012 | Live balances authoritative in the Scheduler, loaded at boot, persisted by group commit | 04 §3 | mo-relay | 1 | E12 | todo |
| T-04-013 | Memory ≈ 50 MB at 10k workers / 5k in-flight / 50k affinity entries; sealed bodies live in the Edge, never in Scheduler state | 04 §3 | mo-relay | 2 | NEW:CI-19 | todo |
| T-04-014 | Eligibility rule 1: pledge in `pools[(repo, dialect, model)]` | 04 §4 | mo-relay | 1 | NEW:E27 | todo |
| T-04-015 | Rule 2: pledge `ACTIVE` and approved (Gateways additionally seal only to owner-approved donors) | 04 §4 | mo-relay | 1 | NEW:E37 | todo |
| T-04-016 | Rule 3: worker belongs to the pledge's donor, has a current session, `window_open`, `slots_free > 0` | 04 §4 | mo-relay | 1 | NEW:E57 | todo |
| T-04-017 | Rule 4: worker offers `(dialect, model)` and its rate-limit state is not cooling down | 04 §4 | mo-relay | 2 | NEW:E29 | todo |
| T-04-018 | Rule 5: `effort ≤ policy.max_effort`; every flag allowed by policy | 04 §4 | mo-relay | 1 | NEW:E27 | todo |
| T-04-019 | Rule 6: `reserve(t,p) ≤ per_task_cap` | 04 §4 | mo-relay | 1 | E10 | todo |
| T-04-020 | Rule 7: `reserve(t,p) ≤ budget − spent − reserved` | 04 §4 | mo-relay | 1 | E10 | todo |
| T-04-021 | Rule 8: `reserve(t,p) ≤ w.local_cap_left` | 04 §4 | mo-relay | 1 | E11 | todo |
| T-04-022 | Rule 9: member quota and submitting-device cap headroom | 04 §4 | mo-relay | 2 | NEW:E30 | todo |
| T-04-023 | Rule 10: worker not in `t.tried` (no second attempt on the same worker) | 04 §4 | mo-relay | 2 | E06 | todo |
| T-04-024 | Rule 11: worker has a wrap in `t.wraps` (else candidate for `need_wraps`) | 04 §4 | mo-relay | 2 | NEW:E25 | todo |
| T-04-025 | Rules evaluated cheapest-first; the rule eliminating the most candidates is recorded for precise policy errors | 04 §4, §8.3 | mo-relay | 2 | E10, NEW:E27 | todo |
| T-04-026 | `reserve(t,p)` uses the candidate pledge's own provider price for the model | 04 §4; 05 §5 | mo-relay | 1 | NEW:CI-10 | todo |
| T-04-027 | Affinity key = HMAC(per-device secret, lp(system, tools, first user message)) truncated to 16 B; stable per conversation; unguessable by the Relay | 04 §5 | mo-node | 2 | NEW:E28 | todo |
| T-04-028 | Affinity TTL 5 min sliding; 60 min when `cache_ttl == 1h` | 04 §5 | mo-relay | 2 | NEW:E28 | todo |
| T-04-029 | Affinity selection: choose the affinity worker if eligible unless its score is worse than the best alternative by more than the affinity margin (default 3×) | 04 §5 | mo-relay | 2 | NEW:E28, NEW:CI-05 | todo |
| T-04-030 | On failover the affinity entry moves to the new worker | 04 §5 | mo-relay | 2 | NEW:E28 | todo |
| T-04-031 | Without affinity: collect eligible (w, p), draw two at random weighted by pledge headroom, pick the lower cost score | 04 §6 | mo-relay | 2 | NEW:CI-05 | todo |
| T-04-032 | `score = rtt_ewma_ms + 40 × (inflight/slots_max) + 200 × rl_pressure + fail_penalty`; `fail_penalty` +100 ms per failure in 5 min, linear decay; weights configurable with documented defaults | 04 §6; ADR-32 | mo-relay | 2 | NEW:CI-05 | todo |
| T-04-033 | `rl_pressure` ∈ [0,1] derived from Worker-reported provider rate-limit headers | 04 §6 | mo-relay + mo-worker | 2 | NEW:E29 | todo |
| T-04-034 | Gateway wraps for the affinity worker first, then top workers by `hint` for the model, up to 8 wraps | 04 §7 | mo-node | 2 | NEW:E25, NEW:E28 | todo |
| T-04-035 | Scheduler restricted to wrapped workers; if none eligible, `task.need_wraps{workers}` with its own top choices | 04 §7 | mo-relay | 2 | NEW:E25 | todo |
| T-04-036 | Commit-before-assign: `task.assign` only after the group commit containing the reservation and task row completes (≤ ~10 ms) | 04 §8.1; L8 | mo-relay | 1 | E12, NEW:CI-04 | todo |
| T-04-037 | ACK deadline expiry → cancel attempt; to `awaitingReceipt` unless NACK / zero-usage receipt proves no spend; reassign | 04 §8.2 | mo-relay | 2 | NEW:E26 | todo |
| T-04-038 | Start deadline (30 s after ACK) expiry → same as ACK expiry | 04 §8.2 | mo-relay | 2 | NEW:E26 | todo |
| T-04-039 | Routing deadline (5 s after last body frame, no ACK) → `task.failed{overloaded, retryable}` | 04 §8.2 | mo-relay | 2 | NEW:E27 | todo |
| T-04-040 | Attempts exhausted (3) → `task.failed{overloaded, retryable}` | 04 §8.2 | mo-relay | 2 | NEW:E27 | todo |
| T-04-041 | SQL sweep every minute: attempts awaiting a receipt > 24 h **and** Worker absent all that time → pessimistic settlement at the reservation | 04 §8.2; 05 §5.2 | mo-relay | 2 | NEW:E35 | todo |
| T-04-042 | SQL sweep: receipts older than 24 h without dispute become final for leaderboards | 04 §8.2 | mo-relay | 3 | NEW:E43 | todo |
| T-04-043 | Policy failure mapping: no pledge serves model → `model_not_in_pool` (no retry); rule 6 → `over_task_cap` (with worst-case cost and cap); rules 7/9 → `quota_exceeded`; capacity (3, 4, 8, rate limits) → `overloaded` (retryable) | 04 §8.3 | mo-relay | 2 | E10, NEW:E27, NEW:E30 | todo |
| T-04-044 | Reassignment state machine (Selecting, Committing, NeedWraps, Assigned, Acked, Started, Superseded, Settling, Failed) as 04 §8.4 | 04 §8.4 | mo-relay | 2 | NEW:CI-04 | todo |
| T-04-045 | Superseded attempt kept in `awaitingReceipt` unless proven zero-cost; worker added to `tried[]` | 04 §8.4 | mo-relay | 2 | NEW:E26 | todo |
| T-04-046 | Proof of zero spend = NACK before the provider call (`busy`, `local_cap`, `firewall`, `route_mismatch`, `unauthorized_task`, `bad_envelope`) or a `not_started` receipt; anything else keeps the reservation until the receipt | 04 §8.4 | mo-relay | 1 | E07, E09, NEW:E26 | todo |
| T-04-047 | Workers parse provider rate-limit headers (remaining requests/tokens + reset, `retry-after`; names pinned per adapter) into a compact `rl_headroom` per model | 04 §9 | mo-worker | 2 | NEW:CI-17, NEW:E29 | todo |
| T-04-048 | Offer updates sent when headroom crosses 50%, 20%, or 5% (not per request) | 04 §9 | mo-node + mo-worker | 2 | NEW:E29 | todo |
| T-04-049 | On 429: Worker NACKs with `retry_after_ms`; Scheduler cools down `(worker, model)` and reassigns immediately | 04 §9 | mo-node + mo-relay | 2 | E07, NEW:E29 | todo |
| T-04-050 | Fairness between members: per-member monthly caps (default owner unlimited, members 20% of committed); per-member submission rate limit | 04 §10; 05 §11 | mo-relay | 2 | NEW:E30, NEW:E50 | todo |
| T-04-051 | Fairness for CI devices: own device caps and a single repo scope | 04 §10; 07 §8.4 | mo-relay + mo-node | 2 | NEW:E30 | todo |
| T-04-052 | Between repos sharing a donor: separate budgets per pledge; compete only for slots (first-come); optional `max_slots` per pledge enforced | 04 §10; 05 §4.1 | mo-relay | 2 | NEW:E30 | todo |
| T-04-053 | Donor's own use protected by `slots_max`, schedule windows, rate-limit steering | 04 §10 | mo-node + mo-relay | 2 | NEW:E57, NEW:E29 | todo |
| T-04-054 | Perf: `apply(submit)` incl. eligibility + P2C + reservation p99 < 50 µs (≤ 50 candidates) | 04 §11 | mo-relay | 2 | NEW:CI-06 | todo |
| T-04-055 | Perf: `apply(ack/started/end)` p99 < 10 µs | 04 §11 | mo-relay | 2 | NEW:CI-06 | todo |
| T-04-056 | Perf: chunk forwarding < 5 µs + syscall (one map load, source check, one channel send) | 04 §11 | mo-relay | 1 | NEW:CI-06 | todo |
| T-04-057 | Perf: commit-before-assign delay ≤ 10 ms (one group-commit interval) | 04 §11 | mo-relay | 1 | NEW:CI-06 | todo |
| T-04-058 | Ceiling: ~100k events/s per Scheduler; upgrade = one Scheduler per repo shard | 04 §11 | mo-relay | D | NEW:MON-03 | todo |
| T-04-059 | Invariant: `0 ≤ reserved` and `spent + reserved ≤ budget + overage bound` for every pledge, member, capped device | 04 §12.2 | mo-relay | 1 | NEW:CI-04, NEW:E68 | todo |
| T-04-060 | Invariant: Σ open-attempt reservations == Σ `reserved` (pledges, members, devices) | 04 §12.2; L4 | mo-relay | 1 | NEW:CI-04 | todo |
| T-04-061 | Invariant: `slots_free ≥ 0` and `slots_free + open_attempts == slots_max` (modulo offers in transit) | 04 §12.2 | mo-relay | 2 | NEW:CI-04 | todo |
| T-04-062 | Invariant: no attempt assigned before its reservation's commit completed | 04 §12.2 | mo-relay | 1 | NEW:CI-04 | todo |
| T-04-063 | Invariant: no task has two attempts in `Started` | 04 §12.2 | mo-relay | 2 | NEW:CI-04 | todo |
| T-04-064 | Invariant: no attempt assigned to an ineligible worker (§4 re-checked at assignment) | 04 §12.2 | mo-relay | 1 | NEW:CI-04 | todo |
| T-04-065 | Invariant checks run after every event in tests; available as a production debug flag | 04 §12.2 | mo-relay | 1 | NEW:CI-04 | todo |
| T-04-066 | Deterministic simulator: thousands of virtual workers/gateways, latency, disconnects, 429 storms, restarts, clock jumps, late/duplicated messages; same seed → byte-identical run | 04 §12.3 | mo-relay | 2 | NEW:CI-04 | todo |
| T-04-067 | Property tests: proportional drain over 10k tasks within ±5% of headroom ratios; affinity hit ≥ 95% while the affinity worker is healthy | 04 §12.4 | mo-relay | 2 | NEW:CI-05 | todo |
| T-04-068 | Benchmarks for `apply(submit)` at 10/100/1k/10k candidates with a CI regression budget | 04 §12.5 | mo-relay | 2 | NEW:CI-06 | todo |
| T-04-069 | Rejected: no hedged requests, no failover after start, no global "best worker" ranking, no latency-only routing, no Redis/external queue, no global mutex, no cross-dialect routing | 04 §13 | mo-relay | — | NEW:CI-04, E06 | todo |

## 05 — Ledger and accounting

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-05-001 | Every balance, cap, reservation, goal, and cost is an int64 count of µ$; no floats in money paths; checked arithmetic | 05 §1; ADR-03; AGENTS §3 | mo-relay + mo-worker + mo-node | 1 | NEW:CI-10, NEW:CI-02 | todo |
| T-05-002 | Displays show dollars first, token-equivalents second (render-time, current catalog) | 05 §1; 08 §11 | mo-web | 4 | NEW:E64 | todo |
| T-05-003 | Token-equivalent formula: µ$ ÷ blended price of the pool's most-used model, blended = 0.8 × input + 0.2 × output, uncached | 05 §1 | mo-web | 4 | NEW:CI-09 | todo |
| T-05-004 | Each receipt cost rounded **up** to the next µ$ | 05 §1, §3 | mo-worker + mo-relay | 1 | NEW:CI-10 | todo |
| T-05-005 | Public model ids are OpenRouter-style slugs (`vendor/model`) | 05 §2.1; ADR-18 | mo-relay + mo-node | 1 | E01, NEW:E39 | todo |
| T-05-006 | Gateway accepts native ids and maps them to slugs through the catalog | 05 §2.1 | mo-node | 1 | NEW:E39 | todo |
| T-05-007 | Route header carries the slug; Worker maps slug → its provider's id through the signed catalog; any donor offering the model in that dialect can serve | 05 §2.1 | mo-worker + mo-node | 1 | E03, NEW:E54 | todo |
| T-05-008 | `/v1/models` and `moochy_pool_status` list slugs plus native aliases | 05 §2.1 | mo-node | 1 | NEW:E51, E04 | todo |
| T-05-009 | Catalog entry fields: `version, effective_at, model, provider, provider_model_id, dialects, in, out, cache_write_5m, cache_write_1h, cache_read` (µ$/MTok ints), `max_image_tokens, max_page_tokens, fast_multiplier, default_effort, max_output, source` | 05 §2.2; 09 §3.6 | mo-relay + mo-proto | 1 | NEW:E39 | todo |
| T-05-010 | OpenRouter catalog price = maximum across its upstream endpoints (for reservations) | 05 §2.2 | mo-relay | 1 | E02 | todo |
| T-05-011 | Prices apply to tasks started at or after `effective_at`; Nodes reject version decreases | 05 §2.2 | mo-relay + mo-node | 1 | NEW:E39 | todo |
| T-05-012 | Catalog is signed and logged as a `CATALOG` key-log entry; every Node verifies it | 05 §2.2 | mo-relay + mo-node | 3 | NEW:E39, NEW:E40 | todo |
| T-05-013 | Catalog update = operator action with 24 h `effective_at` delay, except price decreases (may apply immediately); OpenRouter imports reviewed then signed | 05 §2.2 | mo-relay | 1 | NEW:E39, NEW:E77 | todo |
| T-05-014 | Cost function `ceil((in×c.in + out×c.out + cw5m×c.cw5m + cw1h×c.cw1h + cr×c.cr) × fast_multiplier / 1e6)` | 05 §3 | mo-worker + mo-relay | 1 | NEW:CI-10, E01 | todo |
| T-05-015 | OpenRouter: receipt cost = `ceil(provider_cost)` donor-signed; Relay checks `cost ≤ reservation` | 05 §3 | mo-worker + mo-relay | 1 | E02, NEW:E38 | todo |
| T-05-016 | Usage mapping Anthropic: `input_tokens` (uncached), `output_tokens` (incl. thinking), `cache_creation` by TTL, `cache_read_input_tokens`, summed over `usage.iterations` | 05 §3 | mo-worker | 1 | E01, NEW:CI-17 | todo |
| T-05-017 | Usage mapping OpenAI/compatible: input = prompt − cached; output = completion (incl. reasoning); cache_read = cached prompt tokens; cache_write = 0 | 05 §3 | mo-worker | 2 | NEW:E76, NEW:CI-17 | todo |
| T-05-018 | Usage mapping DeepSeek: input = cache-miss prompt tokens; cache_read = cache-hit tokens; output incl. reasoning | 05 §3 | mo-worker | 1 | E03, NEW:CI-17 | todo |
| T-05-019 | Usage mapping OpenRouter: normalized prompt − cached; completion; cache fields when reported; `provider_cost` = charged cost (authoritative) | 05 §3 | mo-worker | 1 | E02, NEW:CI-17 | todo |
| T-05-020 | Worker always turns on stream usage reporting for OpenAI-style streams | 05 §3; 06 §7.2 | mo-worker | 1 | E02, NEW:E54 | todo |
| T-05-021 | Worker computes and signs `cost_uusd`; Relay recomputes from usage + catalog version (or checks OpenRouter bound); mismatch → reject + alert | 05 §3 | mo-relay | 1 | NEW:E38 | todo |
| T-05-022 | Pledge field `budget_per_period` (monthly, anchored on creation day) | 05 §4.1 | mo-relay | 1 | NEW:E36 | todo |
| T-05-023 | Pledge `per_task_cap` default $5 (5,000,000 µ$), donor-lowerable; console shows "requests blocked by task cap" | 05 §4.1 | mo-relay + mo-web | 1/4 | E10, NEW:E64 | todo |
| T-05-024 | Pledge `policy.models` with per-family wildcards (`anthropic/claude-sonnet-*`), `max_effort` (`low`…`max`), `dialects`, `flags` (`fast`, `images`, `documents`, `long_context`, …) | 05 §4.1 | mo-relay | 1 | NEW:E27 | todo |
| T-05-025 | Pledge optional `max_slots` and `schedule` windows; `visibility` public / pseudonymous / anonymous | 05 §4.1 | mo-relay + mo-web | 2/4 | NEW:E30, NEW:E66 | todo |
| T-05-026 | Pledge lifecycle: PendingApproval → Active (owner-signed `DONOR_APPROVED`) / Declined; Active ↔ Paused (donor, `moochy pause`, window); → Ended (full reclaim, owner revoke, repo deleted, ban) | 05 §4.2 | mo-relay | 1→3 | NEW:E37 | todo |
| T-05-027 | Each period a new `pledge_periods` row and `spent → 0` | 05 §4.2, §9 | mo-relay | 1 | NEW:E36 | todo |
| T-05-028 | `reserve(t,p) = ceil((est_input × c.in × m_cache + max_tokens × c.out) × fast_multiplier / 1e6)`, `m_cache` = 1.25 (5m), 2.0 (1h), 1.0 else; worked example 420,000 µ$ / 34,200 µ$ reproduces | 05 §5.1 | mo-relay + mo-worker | 1 | NEW:CI-10 | todo |
| T-05-029 | Reservations, settlements, receipts are per attempt `(task_id, attempt)` | 05 §5.2 | mo-relay | 1 | E06, E12 | todo |
| T-05-030 | Reserve: `reserved += r` on pledge, member, capped device; committed before `task.assign` | 05 §5.2 | mo-relay | 1 | E01, E12 | todo |
| T-05-031 | Settle (not estimated): `reserved −= r`, `spent += cost` on all three, attributed to the attempt's start period | 05 §5.2 | mo-relay | 1 | E01, NEW:E36 | todo |
| T-05-032 | Settle (estimated): pessimistically at `r`; a later donor-signed correction from `moochy audit --provider` may lower it | 05 §5.2 | mo-relay + mo-node | 1/2 | NEW:E35 | todo |
| T-05-033 | Release on proof of zero spend: `reserved −= r`, nothing spent | 05 §5.2 | mo-relay | 1 | E07, E09 | todo |
| T-05-034 | Superseded attempt without proof stays in `awaitingReceipt` until its receipt | 05 §5.2 | mo-relay | 2 | NEW:E26 | todo |
| T-05-035 | No receipt after 24 h and Worker absent → settle at `r`, flagged `pessimistic` | 05 §5.2 | mo-relay | 2 | NEW:E35 | todo |
| T-05-036 | Late receipt after pessimistic settle → correction `spent += cost − r` into the start period, flag cleared, never below 0 | 05 §5.2, §13 | mo-relay | 2 | NEW:E35 | todo |
| T-05-037 | Actual cost > reservation: overage settled honestly; pledge stops accepting new tasks for that period | 05 §5.2 | mo-relay | 1 | NEW:CI-10 | todo |
| T-05-038 | Layer 1 caps: Relay reservations | 05 §6 | mo-relay | 1 | E10 | todo |
| T-05-039 | Layer 2 caps: Worker local reservation per device before ack against monthly device cap (all pledges) and per-pledge counters, counting open attempts; settle to receipt cost; counters persisted with the outbox | 05 §6 | mo-worker + mo-node | 1 | E11 | todo |
| T-05-040 | Layer 3 caps: onboarding strongly recommends dedicated key + provider spend limit with deep links (OpenRouter per-key credit limit) | 05 §6; 07 §8.1 | mo-node + mo-docs* | 1 | NEW:E81, NEW:REV-02 | todo |
| T-05-041 | Worker writes the signed receipt to its outbox (append-only, fsync) **before** sending `task.end` | 05 §7 | mo-worker + mo-node | 1 | E12 | todo |
| T-05-042 | Relay commits the receipt with `synchronous=FULL` and only then sends `receipt.ack` | 05 §7 | mo-relay | 1 | E12 | todo |
| T-05-043 | Worker keeps acked entries 7 days; after DR restore Relay asks every Worker to `receipt.replay_since` | 05 §7 | mo-node + mo-relay | 2 | NEW:E34 | todo |
| T-05-044 | Settlement idempotent by `(task_id, attempt)`: identical bytes → no-op ack; different bytes → reject + alert + freeze device for review | 05 §7, §13 | mo-relay | 1 | E12, NEW:E34 | todo |
| T-05-045 | Receipt for an unknown task = protocol violation (reject + alert), except within a DR-restore window where accepted if the pledge belongs to the signing donor | 05 §7 | mo-relay | 1/2 | NEW:E38, NEW:E34 | todo |
| T-05-046 | Boot reconciliation: load balances, apply missed period rollovers before scheduling, mark open attempts `orphaned` (reservations kept); `known_tasks` releases orphans never held | 05 §7 | mo-relay | 1 | E12, NEW:E67 | todo |
| T-05-047 | Key-log checkpoints signed only for tree sizes Litestream has replicated | 05 §7; 06 §10.1 | mo-relay | 3 | NEW:E40 | todo |
| T-05-048 | Each op in a group commit runs in its own SAVEPOINT; a constraint violation is fatal (exit, restart, reload, outbox replay) | 05 §7; 09 §4 | mo-relay | 1 | NEW:E68 | todo |
| T-05-049 | Nightly audit job (read-only connection) recomputes `spent` per pledge-period, member-month, device-month from receipts; any difference pages | 05 §7 | mo-relay + mo-ops* | 1 | NEW:E68, NEW:MON-01 | todo |
| T-05-050 | `moochy audit --provider`: reconcile local journal with provider bill — Anthropic usage/cost API (admin key, local only) or export; OpenRouter generation stats/key usage; DeepSeek balance diff or export; OpenAI usage API or export | 05 §7.1 | mo-node + mo-worker | 1/2 | NEW:CI-20 | todo |
| T-05-051 | Reconciliation target ≤ 0.5% drift; a correction is a donor-signed entry applied by the Relay into the right period | 05 §7.1 | mo-node + mo-relay | 1/2 | NEW:CI-20, NEW:E35 | todo |
| T-05-052 | Partial reclaim: new headroom = `max(0, new_budget − spent − reserved)` effective at the next Scheduler event | 05 §8 | mo-relay + mo-web | 2 | NEW:E37 | todo |
| T-05-053 | Full reclaim = End pledge: no new reservations, open attempts settle, public page keeps history | 05 §8 | mo-relay | 2 | NEW:E37 | todo |
| T-05-054 | Pause is temporary and reversible; `moochy pause` stops all serving from the device instantly (zero slots, refuses assigns), works offline, no web login | 05 §8 | mo-node + mo-relay | 1 | NEW:E57, NEW:E37 | todo |
| T-05-055 | No "locked balance" / custody wording anywhere in the product | 05 §8 | mo-web + mo-node | 4 | NEW:REV-02 | todo |
| T-05-056 | Monthly periods anchored per pledge (created on the 17th → 17th–16th); member and device counters use calendar months | 05 §9 | mo-relay | 1/2 | NEW:E36 | todo |
| T-05-057 | Rollover (timer event or at boot) writes the `pledge_periods` row (`budget`, `spent`, `tasks`) and starts the new period at 0 | 05 §9 | mo-relay | 1 | NEW:E36 | todo |
| T-05-058 | Attribution to start period: settlement and corrections go into the attempt's start-period row even if closed | 05 §9 | mo-relay | 1 | NEW:E36 | todo |
| T-05-059 | Open reservations from the previous period count against headroom in the new period until settled | 05 §9 | mo-relay | 1 | NEW:E36 | todo |
| T-05-060 | No carry-over by default; `rollover = true` opt-in, capped at 1× budget | 05 §9 | mo-relay | 2 | NEW:E36 | todo |
| T-05-061 | Repo monthly goal ($/month) set by owner, shown on the repo page header | 05 §10 | mo-web + mo-relay | 4 | NEW:E64 | todo |
| T-05-062 | Committed = Σ budgets of Active pledges prorated to the calendar month; Used = Σ settled receipt costs this calendar month; Utilization = Used ÷ Committed | 05 §10 | mo-relay + mo-web | 4 | E19, NEW:CI-10 | todo |
| T-05-063 | Leaderboard = Σ cost of undisputed receipts per donor (month / all time), repo page and global page | 05 §10 | mo-relay + mo-web | 4 | NEW:E43, NEW:E64 | todo |
| T-05-064 | Donor count = distinct donors with an Active pledge (badge, repo page) | 05 §10 | mo-relay + mo-web | 4 | NEW:E64 | todo |
| T-05-065 | Member monthly cap (default 20% of Committed; owner unlimited) and per-device cap use reserve/settle/release, eligibility rule 9, invariants, audit, calendar-month reset | 05 §11 | mo-relay | 2 | NEW:E30, NEW:E68 | todo |
| T-05-066 | L1: `reserved ≥ 0`, `spent ≥ 0` via SQLite CHECK + Scheduler assertions (fatal) | 05 §12 | mo-relay | 1 | NEW:E68, NEW:CI-04 | todo |
| T-05-067 | L2: new reservations only when `spent + reserved + r ≤ budget` (and member/device equivalents) | 05 §12 | mo-relay | 1 | E10, NEW:E30 | todo |
| T-05-068 | L3: every settled attempt has exactly one receipt or a flagged pessimistic settlement | 05 §12 | mo-relay | 1 | NEW:E68 | todo |
| T-05-069 | L4: Σ open-attempt reservations = Σ `reserved`; checked in Scheduler and at boot | 05 §12 | mo-relay | 1 | NEW:CI-04, E12 | todo |
| T-05-070 | L5: Σ receipt costs per pledge-period / member-month / device-month = materialized `spent` | 05 §12 | mo-relay | 1 | NEW:E68 | todo |
| T-05-071 | L6: receipt cost = recomputed cost; OpenRouter `cost ≤ reservation` and = reported cost | 05 §12 | mo-relay | 1 | NEW:E38 | todo |
| T-05-072 | L7: a device never exceeds its local monthly cap counting open attempts (Worker, independent of Relay) | 05 §12 | mo-worker + mo-node | 1 | E11 | todo |
| T-05-073 | L8: no attempt assigned before its reservation is durable | 05 §12 | mo-relay | 1 | NEW:CI-04, E12 | todo |
| T-05-074 | Edge: provider error after partial stream → receipt `provider_error` with real usage, else `estimated` → pessimistic | 05 §13 | mo-worker + mo-node | 1 | NEW:E35 | todo |
| T-05-075 | Edge: refusal stop reason billed per provider usage like any completion | 05 §13 | mo-worker | 1 | NEW:CI-17 | todo |
| T-05-076 | Edge: catalog version in effect at **attempt start** applies (recorded at reservation) | 05 §13 | mo-relay | 1 | NEW:E39 | todo |
| T-05-077 | Edge: two attempts both reached the provider (start-timeout race) → both receipts settle; Gateway uses only the first started stream; visible in metrics | 05 §13 | mo-relay + mo-node | 2 | NEW:E47 | todo |
| T-05-078 | Edge: pledge Ended mid-task → attempt completes and settles to the Ended pledge | 05 §13 | mo-relay | 2 | NEW:E37 | todo |
| T-05-079 | Edge: donor deletes account → pledges Ended, open attempts settle, log entries stay (pseudonymous), pseudonym mapping deleted | 05 §13; 06 §10.3 | mo-relay + mo-web | 4 | NEW:E63 | todo |
| T-05-080 | Edge: period attribution uses the Relay's reservation time (clock skew between Worker and Relay) | 05 §13 | mo-relay | 1 | NEW:E36 | todo |

## 06 — Security and trust

Threat rows (T1–T22) name the mitigation that must exist; the detailed mechanism rows live in the sections below and in 03/05/07. `mo-sec` should add `A-` ids to these rows once `docs/security/attack-catalog.md` lands.

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-06-001 | T1: provider key never leaves the donor machine; OS keychain; sent only to allowlisted provider hosts | 06 §3 T1 | mo-worker + mo-node | 1 | NEW:E59, NEW:E58 | todo |
| T-06-002 | T2: request firewall prevents server-side execution, web fetch, MCP connectors, paid add-ons; provider headers sealed and allowlisted | 06 §3 T2 | mo-worker | 1 | E09, NEW:E55 | todo |
| T-06-003 | T3: firewall rejects any file reference, stored-response reference, or non-chat endpoint at any nesting depth | 06 §3 T3 | mo-worker | 1 | E09, NEW:E55 | todo |
| T-06-004 | T4: three-layer caps, Worker-checked deterministic estimate, route header bound to body | 06 §3 T4 | mo-relay + mo-worker | 1 | E10, E11, E15 | todo |
| T-06-005 | T5: Worker route/body consistency with exact estimate match | 06 §3 T5 | mo-worker | 1 | NEW:E55 | todo |
| T-06-006 | T6: E2E envelopes with per-body request keys and per-attempt response keys; relay DB stores no content | 06 §3 T6 | mo-proto + mo-relay | 1 | E13, E17 | todo |
| T-06-007 | T7: Gateways seal only to logged keys of users holding an owner-signed `DONOR_APPROVED`; Nodes alert on unknown own keys and unsigned approvals/claims; anchored checkpoints | 06 §3 T7 | mo-node + mo-relay | 3 | NEW:E40, NEW:E41, NEW:E42 | todo |
| T-06-008 | T8: owner approval per donor, pinned donors, tool-call checks + tripwire, signed checkpoints on every tool call, human-approval guidance | 06 §3 T8 | mo-node + mo-worker | 3 | E18, NEW:E44 | todo |
| T-06-009 | T9: Gateway task signatures, owner-signed `MEMBER_ADDED`, pledge↔repo check, ULID freshness, served-task set | 06 §3 T9 | mo-node + mo-worker | 1→3 | E16, NEW:E41, NEW:E56 | todo |
| T-06-010 | T10: Gateway checks commitments, usage bands, reported model; signed disputes; leaderboard counts only undisputed receipts | 06 §3 T10 | mo-node + mo-relay | 3 | NEW:E43 | todo |
| T-06-011 | T11: donor-signed receipts/projections, owner-signed approvals, append-only key log with externally anchored signed checkpoints | 06 §3 T11 | mo-relay + mo-node | 3 | NEW:E42, NEW:E61 | todo |
| T-06-012 | T12: auth signature covers dialed origin + TLS channel binding | 06 §3 T12 | mo-node + mo-relay | 1 | NEW:E21 | todo |
| T-06-013 | T13: `moochy logout` / web revoke → `KEY_REVOKED`; Relay drops the device at once | 06 §3 T13 | mo-node + mo-relay + mo-web | 1→3 | NEW:E71, NEW:E63 | todo |
| T-06-014 | T14: loopback only, repo-scoped random tokens, Host check, no CORS, port held by OS service manager, `doctor` checks listening uid | 06 §3 T14 | mo-node | 1/5 | E14, NEW:E81 | todo |
| T-06-015 | T15: MCP `files` root = recorded git top-level ∩ client roots; realpath containment; no symlinks; deny `.git/**` + secret-shaped files; `git check-ignore` | 06 §3 T15 | mo-node | 3 | NEW:E46 | todo |
| T-06-016 | T16: SameSite=Lax cookies; state changes require `HX-Request` + Origin; strict CSP; auto-escaping templates | 06 §3 T16 | mo-web | 4 | NEW:E63 | todo |
| T-06-017 | T17: signed releases with provenance, reproducible Linux builds, dependency vetting, no silent auto-update | 06 §3 T17 | mo-release* + mo-node | 3 | NEW:CI-08, NEW:E81 | todo |
| T-06-018 | T18: GitHub/GitLab identity; repo claims need admin permission; owner approval of donors; rate limits | 06 §3 T18 | mo-relay + mo-web | 1/4 | NEW:E63, NEW:E78 | todo |
| T-06-019 | T19: donors pledge only to repos they choose and that approve them; pseudonymous `metadata.user_id`; local journal; explicit donor consent | 06 §3 T19 | mo-worker + mo-node | 1 | NEW:E54, NEW:E60 | todo |
| T-06-020 | T20: Gateway secret scrubber before sealing (also on MCP files) | 06 §3 T20 | mo-node | 3 | NEW:E45 | todo |
| T-06-021 | T21: prompt-cache timing side channel accepted (low); documented in the public threat model | 06 §3 T21 | mo-sec | 6 | NEW:REV-02 | todo |
| T-06-022 | T22: per-IP connection limits, per-device rate limits, byte budgets for buffered bodies, sheddable submit queue | 06 §3 T22 | mo-relay | 2 | NEW:E78, NEW:E49 | todo |
| T-06-023 | Device keys created by `moochy login` on the device, never exported: one Ed25519 + one X25519 | 06 §4.1 | mo-node | 1 | NEW:E71 | todo |
| T-06-024 | Keys stored in OS keychain; headless fallback: scrypt passphrase-encrypted file, or `systemd-creds` / TPM-bound credentials | 06 §4.1 | mo-node | 1/5 | NEW:E71, NEW:CI-16 | todo |
| T-06-025 | Registration binds `{device, user, sign_pub, enc_pub, roles, suite}` and appends `KEY_ADDED` with a proof-of-possession signature by the new key | 06 §4.1 | mo-relay + mo-node | 1→3 | NEW:E40 | todo |
| T-06-026 | `moochy keys rotate`: new device record; old one revoked after a 24 h grace; both logged | 06 §4.1 | mo-node + mo-relay | 3 | NEW:E71 | todo |
| T-06-027 | `KEY_REVOKED` takes effect immediately at the Relay and is published in the key log | 06 §4.1 | mo-relay | 1→3 | NEW:E71 | todo |
| T-06-028 | Provider keys added via `moochy keys add <provider>` with interactive prompt or stdin — never a CLI argument; stored in keychain | 06 §4.2; CONTRACT §6 | mo-node | 1 | NEW:E58 | todo |
| T-06-029 | Provider key validated on add and periodically with a free models-endpoint call; Worker advertises exactly the models the key can use | 06 §4.2 | mo-worker + mo-node | 1 | NEW:E58 | todo |
| T-06-030 | Provider keys never sent to the Relay, never logged, never in crash reports (redaction unit-tested) | 06 §4.2 | mo-node + mo-worker | 1 | NEW:E59, NEW:CI-12 | todo |
| T-06-031 | Relay log-signing key (Ed25519, signed-note format) generated offline; loaded from encrypted file or KMS at boot; yearly rotation with dual signing during transition | 06 §4.3 | mo-relay + mo-ops* | 3 | NEW:E40, NEW:REV-05 | todo |
| T-06-032 | Relay catalog-signing key handled like the log key | 06 §4.3 | mo-relay + mo-ops* | 3 | NEW:E39 | todo |
| T-06-033 | No Relay key can decrypt user content | 06 §4.3 | mo-relay | — | E13 | todo |
| T-06-034 | Web users authenticate with GitHub/GitLab OAuth → session cookie | 06 §5 | mo-relay + mo-web | 1/5 | NEW:E63 | todo |
| T-06-035 | Node roles granted at approval: `gateway`, `worker`, optionally scoped to one repo | 06 §5 | mo-relay | 1 | E01, NEW:E30 | todo |
| T-06-036 | Repo owner: provider API confirms **admin** permission with the user's OAuth token at claim (used once, not stored); owner's Node signs `REPO_CLAIMED` | 06 §5 | mo-relay + mo-node | 1→3 | NEW:E63, NEW:E82 | todo |
| T-06-037 | Approvals signed by the owner's device (`moochy approve`, `moochy members add`, or confirming in `moochy status`); Relay can show but not forge | 06 §5 | mo-node + mo-relay | 3 | NEW:E82, NEW:E41 | todo |
| T-06-038 | No automatic membership from push access (membership is owner-signed only) | 06 §5 | mo-relay | — | NEW:E41 | todo |
| T-06-039 | Public repositories only on the public instance; private pools via self-hosted relays | 06 §5; ADR-31 | mo-relay | 1 | NEW:E63 | todo |
| T-06-040 | E2E costs paid: validation moves to Worker (firewall) and Gateway (scrubber, tool checks); usage from donor-signed receipts; no relay moderation (documented in terms) | 06 §6 | mo-worker + mo-node | 1 | E09, E18 | todo |
| T-06-041 | Firewall rule: allowlist (never denylist), recursive, per adapter: endpoints, headers + values, top-level fields, content-block types (incl. nested in `tool_result`/documents), tool types; unknown → `nack{firewall}` | 06 §7 | mo-worker | 1 | E09, NEW:E55 | todo |
| T-06-042 | Firewall reason sealed to the Gateway; the Relay sees only the code | 06 §7 | mo-node + mo-worker | 1 | E09 | todo |
| T-06-043 | Anthropic: allow only `POST /v1/messages`; deny `count_tokens` and every other endpoint (batches, files, models, skills, agents) | 06 §7.1 | mo-worker | 1 | NEW:E55 | todo |
| T-06-044 | Anthropic: provider headers sealed in the inner payload, covered by `req_commit`, allowlisted per catalog version; unknown beta values rejected | 06 §7.1 | mo-worker + mo-node | 1 | NEW:E55 | todo |
| T-06-045 | Anthropic: `model` allowed only if in pledge policy and offered by this key (after slug mapping) | 06 §7.1 | mo-worker + mo-node | 1 | NEW:E55 | todo |
| T-06-046 | Anthropic: `max_tokens` required and ≤ catalog `max_output` | 06 §7.1 | mo-worker | 1 | NEW:E55 | todo |
| T-06-047 | Anthropic allow: `messages`, `system`, `stop_sequences`, accepted sampling params, `stream`, `metadata`, `thinking`, `output_config.effort` (≤ pledge `max_effort`), `output_config.format`, `cache_control` top-level and per block | 06 §7.1 | mo-worker | 1 | E01, NEW:CI-13 | todo |
| T-06-048 | Anthropic content blocks allowed: `text`, `image` (base64, needs `images` flag), `document` (base64/plain text, needs `documents` flag; strict denies PDFs), `tool_use`, `tool_result`, `thinking`, `redacted_thinking` | 06 §7.1 | mo-worker | 1 | E09, NEW:E55 | todo |
| T-06-049 | Anthropic: deny any content whose source is a file id or a URL, at any depth | 06 §7.1 | mo-worker | 1 | E09 | todo |
| T-06-050 | Anthropic: allow custom `tools[]` with `input_schema` and Anthropic client-executed tools (bash, text editor, memory, client-side computer use) | 06 §7.1 | mo-worker | 1 | NEW:CI-13 | todo |
| T-06-051 | Anthropic: deny server-executed tools (web search, web fetch, code execution, tool search, advisor, server-hosted computer use) — no opt-in in v1 | 06 §7.1 | mo-worker | 1 | E09 | todo |
| T-06-052 | Anthropic: deny `mcp_servers` / MCP toolsets, `container`, skills, server-side model fallbacks | 06 §7.1 | mo-worker | 1 | E09, NEW:E55 | todo |
| T-06-053 | Anthropic: `speed: fast` denied unless pledge has `fast`; `service_tier`, `inference_geo` denied unless policy allows | 06 §7.1 | mo-worker | 1 | NEW:E55 | todo |
| T-06-054 | Safe mutation: `metadata.user_id` = pseudonymous `H(repo_id ‖ member_id)` | 06 §7.1 | mo-worker | 1 | NEW:E54 | todo |
| T-06-055 | Safe mutation: public model id → provider model id via the signed catalog; `req_commit` computed before any mutation | 06 §7.1 | mo-worker | 1 | NEW:E54 | todo |
| T-06-056 | OpenAI-compatible: allow `POST /v1/chat/completions` with messages, function tools, standard sampling, reasoning effort | 06 §7.2 | mo-worker | 1 | E02 | todo |
| T-06-057 | OpenAI-compatible deny: hosted/built-in tools, web-search options, `n > 1`, predicted outputs, `service_tier`, audio/other modalities, file or stored-response references, non-chat endpoints | 06 §7.2 | mo-worker | 1 | E09, NEW:E55 | todo |
| T-06-058 | OpenAI-compatible safe mutations: force `store: false` where storage exists; force stream usage reporting | 06 §7.2 | mo-worker | 1 | E02, NEW:E54 | todo |
| T-06-059 | OpenRouter (both dialects): deny `models[]` fallbacks, `route`, `plugins`, `:online` and other uncatalogued variants; set max-price to the catalog price; settle on reported cost | 06 §7.2 | mo-worker | 1 | E02, NEW:E54, NEW:E55 | todo |
| T-06-060 | DeepSeek (both dialects): plain chat + reasoning models, text only | 06 §7.2 | mo-worker | 1 | E03, NEW:E55 | todo |
| T-06-061 | Other OpenAI-compatible hosts: only vetted list, each with its own table | 06 §7.2 | mo-worker | 2–5 | NEW:E76 | todo |
| T-06-062 | Exact endpoints and field names per provider pinned in Phase 0 (adapter data tables v0) | 06 §7.2; 11 Ph0 | mo-worker | 0 | NEW:CI-17 | todo |
| T-06-063 | Firewall written as data (per-adapter table) interpreted by a small recursive validator; allowlist changes are small diffs | 06 §7.3 | mo-worker | 1 | NEW:CI-13 | todo |
| T-06-064 | Firewall fuzzed continuously with a corpus of real client traffic + mutations incl. deep nesting | 06 §7.3 | mo-worker | 1/3 | NEW:CI-03 | todo |
| T-06-065 | Two-person review for any change that widens an allowlist (CODEOWNERS / branch rule) | 06 §7.3 | mo-release* + integrator | 1 | NEW:REV-05 | todo |
| T-06-066 | Opt-in Worker telemetry reports rejected **field names only**, never values | 06 §7.3; 10 §5.2 | mo-node + mo-relay | 2 | NEW:E80 | todo |
| T-06-067 | Donor strictness levels: `strict` (default) and `paranoid` (also deny images/documents, lower `max_tokens` ceiling) | 06 §7.3; 07 §6.4 | mo-worker + mo-node | 1 | NEW:E55, NEW:E57 | todo |
| T-06-068 | Repo owner approves each donor by signature (approval required) | 06 §8 | mo-node + mo-relay | 1→3 | NEW:E41 | todo |
| T-06-069 | Pinned donors: maintainer can restrict a session or repo to named donors (default off) | 06 §8; 08 §2 | mo-node + mo-relay + mo-web | 3/4 | NEW:E41 | todo |
| T-06-070 | Structural tool-call checks: hold each tool call until its end; reject names not in request `tools[]`, inputs failing `input_schema`, forbidden block types (`server_tool_use`, `mcp_tool_use`, server tool results), mismatched model | 06 §8 | mo-worker (inspection) + mo-node | 3 | E18 | todo |
| T-06-071 | Tool calls released only after a verified Worker progress signature covering them | 06 §8 | mo-node | 3 | NEW:E44 | todo |
| T-06-072 | Tripwire: pattern scan for pipe-to-shell, credential paths, persistence locations, encoded payloads, raw-IP connections; hit → error tool result with visible warning (warn + block default) | 06 §8 | mo-worker + mo-node | 3 | E18, NEW:CI-14 | todo |
| T-06-073 | `moochy_delegate` results wrapped as "untrusted content from donor X" and scanned like tool calls | 06 §8; 07 §5.1 | mo-node | 3 | E04, NEW:E79 | todo |
| T-06-074 | Onboarding and `moochy connect` state "keep command approval on in your agent when using pooled compute" | 06 §8 | mo-node + mo-docs* | 3 | NEW:E73 | todo |
| T-06-075 | Tripwire documented as a speed bump, not a guarantee (docs + console wording) | 06 §8; 11 Ph3 | mo-sec + mo-docs* | 3 | NEW:REV-02 | todo |
| T-06-076 | `moochy report <task_id>` packages receipt, progress checkpoints, response bytes, and only `S_resp` | 06 §9 | mo-node | 3 | NEW:E62 | todo |
| T-06-077 | Anyone with the bundle verifies donor signatures and recomputes `resp_commit` | 06 §9 | mo-node + mo-relay | 3 | NEW:E62 | todo |
| T-06-078 | Outcomes: warning, owner revokes approval, or ban (`KEY_REVOKED` for all donor devices, pledges Ended) recorded as pseudonymous `MODERATION` entry | 06 §9 | mo-relay | 3 | NEW:E62, NEW:E77 | todo |
| T-06-079 | Disputes against maintainers handled by the same process in reverse (donor journal + signed receipt as evidence) | 06 §9 | mo-relay + human-po* | 3 | NEW:E62 | todo |
| T-06-080 | Key log = one append-only RFC 6962-style Merkle tree (`x/mod/sumdb/tlog` hashing/proofs, C2SP tlog-tiles paths), signed-note checkpoints | 06 §10.1 | mo-relay | 3 | NEW:E40, NEW:CI-01 | todo |
| T-06-081 | Entry kinds and signers: `KEY_ADDED`/`KEY_REVOKED` (Relay + new key PoP), `REPO_CLAIMED` (Relay + owner device), `DONOR_APPROVED`/`DONOR_REVOKED`, `MEMBER_ADDED`/`MEMBER_REMOVED` (owner device), `CATALOG` (catalog key), `MODERATION` (Relay) | 06 §10.1 | mo-relay + mo-proto | 3 | NEW:E40, NEW:E41 | todo |
| T-06-082 | Every Node mirrors the full key log (~100k entries/year) | 06 §10.1 | mo-node | 3 | NEW:E40 | todo |
| T-06-083 | Every Node alerts on any key on its own account it did not create (with the revoke command in the message) | 06 §10.1 | mo-node | 3 | NEW:E40 | todo |
| T-06-084 | Owner's Node alerts on any `REPO_CLAIMED`, approval, or membership for its repos it did not sign | 06 §10.1 | mo-node | 3 | NEW:E41 | todo |
| T-06-085 | Gateways seal only to worker keys logged, unrevoked, with owner-signed `DONOR_APPROVED` for the repo | 06 §10.1 | mo-node | 3 | NEW:E41 | todo |
| T-06-086 | Workers accept tasks only from Gateway keys whose user has owner-signed `MEMBER_ADDED` (or is owner) | 06 §10.1 | mo-node | 3 | NEW:E41 | todo |
| T-06-087 | Checkpoints signed every 60 s while the log grows (replicated sizes only), pushed to Nodes, checked with consistency proofs | 06 §10.1 | mo-relay + mo-node | 3 | NEW:E40 | todo |
| T-06-088 | Hourly checkpoints committed to a public Git repository from day one; Nodes compare relay-served checkpoints against it | 06 §10.1 | mo-relay + mo-node + mo-ops* | 3 | NEW:E42 | todo |
| T-06-089 | Independent witness cosignatures (C2SP witness protocol) after beta | 06 §10.1 | mo-relay + mo-node | D | NEW:MON-03 | todo |
| T-06-090 | Receipts not in the log in v1; public receipt log (Merkle tree of projections + inclusion proofs) post-beta on demand | 06 §10.2 | mo-relay | D | NEW:MON-03 | todo |
| T-06-091 | Log contains only pseudonymous ids, device public keys, repo ids, signatures, catalog data; `pseudonym → username/avatar` lives in the mutable DB and is deleted with the account | 06 §10.3 | mo-relay | 3 | NEW:E40, NEW:E63 | todo |
| T-06-092 | Privacy: prompts/outputs nowhere on the Relay; only local journals (full text opt-in) | 06 §11 | mo-relay + mo-node | 1 | E13, NEW:E60 | todo |
| T-06-093 | Privacy: task metadata 90 days raw, then daily aggregates; only aggregates public | 06 §11 | mo-relay | 1 | NEW:E83 | todo |
| T-06-094 | Privacy: full receipts kept in Relay DB while the account exists, not public | 06 §11 | mo-relay + mo-web | 1 | NEW:E66 | todo |
| T-06-095 | Privacy: projections public forever, pseudonymous, daily granularity | 06 §11 | mo-relay + mo-web | 4 | NEW:E66 | todo |
| T-06-096 | Privacy: presence live in memory only; aggregated by default; per-donor presence only on opt-in | 06 §11; ADR-28 | mo-relay + mo-web | 4 | NEW:E66 | todo |
| T-06-097 | Privacy: IP addresses only in connection logs, retained 7 days | 06 §11 | mo-relay + mo-ops* | 1 | NEW:E83 | todo |
| T-06-098 | Privacy: OAuth identity kept until account deletion, public per pledge visibility | 06 §11 | mo-relay + mo-web | 4 | NEW:E66 | todo |
| T-06-099 | Signed releases (Sigstore keyless, CI identity) with SLSA provenance; users verify externally (`gh attestation verify`, `cosign verify-blob`) | 06 §12 | mo-release* | 3 | NEW:CI-08 | todo |
| T-06-100 | Reproducible builds for Linux musl artifacts required for beta; other platforms when feasible | 06 §12 | mo-release* | 3 | NEW:CI-08 | todo |
| T-06-101 | `cargo-deny` (licenses, advisories, bans) and `cargo-vet` audits; `hpke` explicitly vetted | 06 §12 | mo-release* + mo-proto | 3 | NEW:CI-08 | todo |
| T-06-102 | No silent auto-update; Node announces new versions; `moochy update` verifies signatures before replacing itself | 06 §12 | mo-node | 3/5 | NEW:E81 | todo |
| T-06-103 | Relay built and signed the same way; moochy.dev publishes the release it runs; `hello.relay_release` reports it | 06 §12 | mo-release* + mo-relay | 3 | NEW:E21, NEW:CI-08 | todo |
| T-06-104 | Public `SECURITY.md`, private disclosure channel, coordinated disclosure, reporter credit | 06 §12; 11 Ph0 | mo-sec + mo-docs* | 0 | NEW:REV-02 | todo |
| T-06-105 | Gateway/MCP bind `127.0.0.1` / `::1` only, never `0.0.0.0` | 06 §13 | mo-node | 1 | E14 | todo |
| T-06-106 | Port held by OS service manager (launchd socket / systemd `.socket`); `moochy doctor` checks listening uid | 06 §13 | mo-node | 5 | NEW:E81 | todo |
| T-06-107 | Local tokens random, repo-scoped, prefixed `mooch_local_…`, rotatable (`moochy env --rotate`), constant-time compared | 06 §13; AGENTS §3 | mo-node | 1 | E14, NEW:E74 | todo |
| T-06-108 | `moochy connect --write` writes tokens only to user-scoped configs / env indirection / stdio shim; refuses any git-tracked file | 06 §13 | mo-node | 1 | NEW:E73 | todo |
| T-06-109 | DNS-rebinding defense: reject `Host` not equal to loopback address + port; no CORS headers | 06 §13 | mo-node | 1 | E14 | todo |
| T-06-110 | MCP `files`: root = git top-level recorded with the token ∩ client MCP roots (or shim cwd/recorded root when none); realpath containment; symlinks refused; `.git/**`, `.env*`, `.npmrc`, `.netrc`, `*.pem`, `id_*`, `*.kdbx` denied even when tracked; git-ignored refused; total ≤ 2 MiB default | 06 §13; 07 §5.2 | mo-node | 3 | NEW:E46 | todo |
| T-06-111 | Secret scrubber before sealing (bodies and MCP files): cloud keys, private-key blocks, provider API keys, JWTs, `.env`-style known secret assignments → `[REDACTED:type]`; modes `redact` (default) / `warn` | 06 §13 | mo-node | 3 | NEW:E45 | todo |
| T-06-112 | Own-key fallback (optional, off by default): Gateway calls provider directly with the maintainer's own key when the pool cannot serve | 06 §13; 07 §4.3 | mo-node + mo-worker | 5 | NEW:E84 | todo |
| T-06-113 | API keys only: subscription/consumer credentials refused technically; adapters accept only API-key auth against official hosts | 06 §14; ADR-29 | mo-worker | 1 | NEW:E58 | todo |
| T-06-114 | Donor is customer of record; onboarding obtains explicit consent with the counsel-approved text | 06 §14 | mo-node + human-counsel* | 1/6 | NEW:E81, NEW:REV-01 | todo |
| T-06-115 | Counsel review of each provider's terms: third-party end users with attribution, resale (no payment), abuse handling | 06 §14 | human-counsel* | 0 | NEW:REV-01 | todo |
| T-06-116 | Research: opt-in free verified mode (TLS notarization with the Relay as notary; TEEs for donor cloud hosts) | 06 §15 | mo-proto + mo-worker + mo-relay | R | NEW:MON-03 | todo |

## 07 — Client: the `moochy` binary

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-07-001 | One binary `moochy`; no account tier, no telemetry by default, no paywalled feature | 07 §1 | mo-node | 1 | NEW:E80, NEW:REV-02 | todo |
| T-07-002 | One background Node per machine (`moochy up`, OS service, or headless) holding the only relay connection, unlocked keys, all state | 07 §1; ADR-05 | mo-node | 1 | NEW:E72 | todo |
| T-07-003 | Roles `gateway` and/or `worker` are capabilities of one Node | 07 §1 | mo-node | 1 | E01 | todo |
| T-07-004 | Thin front-ends (stdio MCP shim, CLI commands) talk to the Node over the local control socket | 07 §1, §3 | mo-node | 1 | NEW:E72 | todo |
| T-07-005 | `moochy login` (device-approval flow, keys created, roles); CONTRACT form `--relay --ca-file --roles --headless` with JSON events | 07 §2; CONTRACT §6 | mo-node | 1 | E01 | todo |
| T-07-006 | `moochy logout`: `KEY_REVOKED` and local keys wiped | 07 §2 | mo-node | 1→3 | NEW:E71 | todo |
| T-07-007 | `moochy up` / `down` / `status` (connection, roles, slots, budgets, last checkpoint, pending approvals) | 07 §2 | mo-node | 1 | E01, NEW:E81 | todo |
| T-07-008 | `moochy service install` / `uninstall` (launchd / systemd user unit / Windows) | 07 §2, §9 | mo-node | 1/5 | NEW:E81 | todo |
| T-07-009 | `moochy keys add <provider>` / `list` / `remove` / `rotate` / `revoke <device>` | 07 §2 | mo-node | 1/3 | NEW:E58, NEW:E71 | todo |
| T-07-010 | `moochy donate`: interactive pledge creation | 07 §2 | mo-node | 1 | NEW:E82 | todo |
| T-07-011 | `moochy claim <owner/repo>`: sign repo claim | 07 §2 | mo-node | 1→3 | NEW:E82 | todo |
| T-07-012 | `moochy pledges`: list with budget / spent / reserved | 07 §2 | mo-node | 1 | NEW:E82 | todo |
| T-07-013 | `moochy pause` / `resume`: instant local kill switch for the Worker role, works offline | 07 §2 | mo-node | 1 | NEW:E57 | todo |
| T-07-014 | `moochy env [--repo] [--shell] [--json] [--rotate]`: base URL + repo-scoped token per dialect; detects repo from git remote | 07 §2; CONTRACT §6 | mo-node | 1 | E01, NEW:E74 | todo |
| T-07-015 | `moochy mcp [--repo]`: stdio MCP shim; Streamable HTTP always on in the Node | 07 §2 | mo-node | 1 | E04, E05 | todo |
| T-07-016 | `moochy connect <client> [--write]` for `claude-code, opencode, cursor, cline, continue, zed, goose, windsurf, vscode, claude-desktop, aider, generic-mcp, generic-openai, generic-anthropic`; `--write` shows a diff before merging | 07 §2 | mo-node | 1/5 | NEW:E73 | todo |
| T-07-017 | `moochy journal [--follow] [--full]` | 07 §2 | mo-node | 1 | NEW:E60 | todo |
| T-07-018 | `moochy verify [receipt_ref\|task_id]`: projection vs donor key in mirrored key log, key log vs public Git anchor | 07 §2; 08 §6 | mo-node | 3 | NEW:E61 | todo |
| T-07-019 | `moochy audit --provider` | 07 §2; 05 §7.1 | mo-node | 1/2 | NEW:CI-20 | todo |
| T-07-020 | `moochy report <task_id>`: package and file an evidence bundle | 07 §2 | mo-node | 3 | NEW:E62 | todo |
| T-07-021 | `moochy doctor`: keychain, connectivity, clock skew, provider key health, firewall version, service status, port owner uid | 07 §2 | mo-node | 1/5 | NEW:E81 | todo |
| T-07-022 | `moochy update`: signed update; provenance verified externally | 07 §2 | mo-node + mo-release* | 5 | NEW:E81 | todo |
| T-07-023 | `moochy approve <donor>`, `moochy members add\|remove <user> [--device]`: owner-signed with this device | 07 §2, §8.4 | mo-node | 3 | NEW:E82 | todo |
| T-07-024 | One multi-threaded tokio runtime; lightweight task per request; no thread per connection | 07 §3 | mo-node | 1 | NEW:CI-07 | todo |
| T-07-025 | Gateway endpoint `POST /v1/messages` (Anthropic, streaming + non-streaming) | 07 §4.1 | mo-node | 1 | E01 | todo |
| T-07-026 | `POST /v1/messages/count_tokens` answered locally with the deterministic (pessimistic) estimate; no relay, no slot | 07 §4.1; ADR-23 | mo-node | 1 | NEW:E51 | todo |
| T-07-027 | `POST /v1/chat/completions` (OpenAI, streaming + non-streaming) | 07 §4.1 | mo-node | 1 | E02 | todo |
| T-07-028 | `GET /v1/models` served locally from the pool snapshot: models offered to this repo as slugs + native aliases | 07 §4.1 | mo-node | 1 | NEW:E51 | todo |
| T-07-029 | `POST/GET /mcp` Streamable HTTP with the local token as bearer | 07 §4.1 | mo-node | 1 | E05 | todo |
| T-07-030 | Default port configurable, chosen at first run and stable across restarts; printed by `env` and `connect` | 07 §4.1 | mo-node | 1 | NEW:E74 | todo |
| T-07-031 | Pipeline 1–2: authenticate token → repo; validate shape; require `max_tokens`, inject catalog default if missing and tell the user once | 07 §4.2 | mo-node | 1 | E14, NEW:E51 | todo |
| T-07-032 | Pipeline 3: scrub secrets | 07 §4.2 | mo-node | 3 | NEW:E45 | todo |
| T-07-033 | Pipeline 4: optional Anthropic auto-caching (multi-turn without `cache_control` → top-level 5 min); disable per repo | 07 §4.2 | mo-node | 2 | NEW:E53 | todo |
| T-07-034 | Pipeline 5–6: derive affinity key, look up session table, compute route header, sign task | 07 §4.2 | mo-node | 1/2 | E01, NEW:E28 | todo |
| T-07-035 | Pipeline 7: zstd level 3 → seal under fresh CK → wrap for affinity worker + top candidates (≤ 8), only to owner-approved keys | 07 §4.2 | mo-node | 1→3 | E01, NEW:E41 | todo |
| T-07-036 | Pipeline 8: decrypt accepted attempt only, write the provider's original bytes unchanged, compute `resp_commit` incrementally, hold tool calls until end + checks + signature | 07 §4.2 | mo-node | 1→3 | E01, E18, NEW:E44 | todo |
| T-07-037 | Pipeline 9: check receipt, silent or signed dispute; update session table; write journal entry | 07 §4.2 | mo-node | 1→3 | NEW:E43, NEW:E60 | todo |
| T-07-038 | Pool empty / member quota exhausted → native error with clear message, or own-key fallback when enabled | 07 §4.3 | mo-node | 2/5 | E10, NEW:E84 | todo |
| T-07-039 | Response headers `x-moochy-task`, `x-moochy-donor` (pseudonym), `x-moochy-cost-uusd` | 07 §4.3 | mo-node | 1 | NEW:E51 | todo |
| T-07-040 | Integration: OpenCode on both doors at once; `connect` sets main + small model to pool ids | 07 §4.4 | mo-node | 1 | NEW:CI-20, NEW:E73 | todo |
| T-07-041 | Integration: Claude Code via MCP (user-scoped config / `claude mcp add`) and `ANTHROPIC_BASE_URL` + token, on Anthropic, OpenRouter, DeepSeek donors; `connect` sets small/fast model | 07 §4.4 | mo-node | 1 | NEW:CI-20, E03 | todo |
| T-07-042 | Integration: Cursor (MCP always; API door documented as cloud-routed caveat) | 07 §4.4 | mo-node + mo-docs* | 5 | NEW:CI-20 | todo |
| T-07-043 | Integration: Cline, Continue, Zed, Goose, Windsurf, VS Code agent mode (MCP; API where base URL supported) | 07 §4.4 | mo-node | 5 | NEW:CI-20, NEW:E73 | todo |
| T-07-044 | Integration: Claude Desktop and other MCP chat apps | 07 §4.4 | mo-node | 5 | NEW:CI-20 | todo |
| T-07-045 | Integration: Aider, LiteLLM, Open WebUI, scripts, OpenAI/Anthropic SDKs via base URL `http://127.0.0.1:<port>/v1` | 07 §4.4 | mo-node | 1/5 | NEW:CI-20 | todo |
| T-07-046 | Integration: agent frameworks (OpenAI Agents SDK, LangGraph, Pydantic AI, CrewAI, Mastra, Claude Agent SDK) via `/mcp` or stdio and via base URL, incl. CI/containers | 07 §4.4 | mo-node | 1 | NEW:CI-20, E05 | todo |
| T-07-047 | Remote-HTTPS-only MCP clients: unsupported by default; Phase 5 opt-in self-tunnel exposes the user's own `/mcp` with OAuth 2.1 + Host allowlist | 07 §4.4; ADR-30 | mo-node | 5 | NEW:E85 | todo |
| T-07-048 | One MCP server (built on `rmcp`) over two transports: stdio (shim starts the Node if needed; startup a few ms) and Streamable HTTP | 07 §5 | mo-node | 1 | E04, E05, NEW:E72 | todo |
| T-07-049 | Zero-install `moochy` npm package fetching the signed binary (`npx -y moochy mcp`) | 07 §5, §11 | mo-release* | 5 | NEW:CI-08 | todo |
| T-07-050 | Tool `moochy_delegate`: `prompt` (req), `system?`, `files?`, `model?` (enum of pool ids), `effort?`, `max_tokens?`, `output?` (`text` / `json` + schema) → untrusted-wrapped result + usage/cost line | 07 §5.1 | mo-node | 1 | E04, NEW:E79 | todo |
| T-07-051 | Tool `moochy_pool_status`: pool budget left this month, member quota, models online with providers, donor count | 07 §5.1 | mo-node | 1 | E04 | todo |
| T-07-052 | Exactly two tools; tools-changed notification when pool models change (where supported); server `instructions` carry when-to-delegate guidance | 07 §5.1 | mo-node | 1/2 | E04, NEW:E79 | todo |
| T-07-053 | `files` read by the Node under 06 §13 rules, incl. no-roots fallback to shim cwd / recorded root; scrubbed; content never enters the caller's context | 07 §5.2 | mo-node | 3 | NEW:E46 | todo |
| T-07-054 | MCP progress notifications for long delegations (where supported); cancellation propagates to the provider call | 07 §5.2 | mo-node | 2 | NEW:E79 | todo |
| T-07-055 | Default delegation sized to ~1 min client timeout (`max_tokens` accordingly); `connect` raises tool-timeout settings where they exist | 07 §5.2 | mo-node | 1/5 | NEW:E73, NEW:E79 | todo |
| T-07-056 | Parallel `moochy_delegate` calls run concurrently and spread across donors | 07 §5.2 | mo-node + mo-relay | 2 | NEW:E79 | todo |
| T-07-057 | `model` defaults to the repo default set by the owner; Node builds the request in the dialect the chosen model's donors serve | 07 §5.2 | mo-node | 1 | E04, NEW:E79 | todo |
| T-07-058 | Tool descriptions written for models (when to delegate / when not) | 07 §5.2 | mo-node | 1 | NEW:CI-15 | todo |
| T-07-059 | Worker pipeline steps 1–9 in order (open, authenticity, firewall + route check, local reservation, ack, safe mutations + warm HTTP/2, stream + seal + checkpoints, cost + receipt + projection + sign + outbox + end + settle + journal, cancel/link loss) | 07 §6.1 | mo-node + mo-worker | 1 | E01, E08, E12 | todo |
| T-07-060 | Ack target well under 500 ms (usually ~1 ms) | 07 §6.1 | mo-node + mo-worker | 1 | NEW:CI-06 | todo |
| T-07-061 | Worker parses just enough of the stream to extract usage and reported model (SSE parsers for both dialects) | 07 §6.1 | mo-worker | 1 | E01, E02, NEW:CI-03 | todo |
| T-07-062 | Adapter `anthropic` (`api.anthropic.com`, Messages) | 07 §6.2 | mo-worker | 1 | E01 | todo |
| T-07-063 | Adapter `openrouter` (`openrouter.ai`, OpenAI chat + Anthropic Messages); prices imported from its public model list | 07 §6.2 | mo-worker + mo-relay | 1 | E02, E03 | todo |
| T-07-064 | Adapter `deepseek` (`api.deepseek.com`, OpenAI chat + Anthropic Messages); cache-hit/miss usage fields | 07 §6.2 | mo-worker | 1 | E03 | todo |
| T-07-065 | Adapter `openai` (`api.openai.com`, OpenAI chat, `store:false` forced) | 07 §6.2 | mo-worker | 2 | NEW:E76 | todo |
| T-07-066 | Adapter `openai_compatible`: vetted list (Gemini OpenAI endpoint, Groq, Together, Fireworks, Mistral, xAI); unlisted host requires `--allow-unvetted-host` with a warning | 07 §6.2; 11 Ph5 | mo-worker + mo-node | 5 | NEW:E76 | todo |
| T-07-067 | Adapter `local` (127.0.0.1 vLLM/Ollama/llama.cpp, price 0, token goals) | 07 §6.2 | mo-worker | R | NEW:MON-03 | todo |
| T-07-068 | Adapter = data definition (hosts, auth header, firewall table, usage mapping, rate-limit header names, error mapping, catalog source) + small special-case code | 07 §6.2 | mo-worker | 1 | NEW:CI-17 | todo |
| T-07-069 | Connection warming: HTTP/2 connection per configured provider at startup and on key add; PINGs while idle; re-dial before provider idle timeout | 07 §6.3 | mo-worker + mo-node | 1 | NEW:E75 | todo |
| T-07-070 | Local controls: `device_monthly_cap` required at setup (no default); `slots_max` 4; `schedule` always; `firewall_level` strict; `journal_full_text` off; `models_override` | 07 §6.4 | mo-node | 1 | NEW:E57, E11 | todo |
| T-07-071 | Outbox: append-only signed receipts, fsync before `task.end`, acked on `receipt.ack`, kept 7 more days; local counters persisted with it | 07 §6.5 | mo-worker + mo-node | 1 | E12, NEW:E83 | todo |
| T-07-072 | Served-task set: `(gateway_device, task_id)` within ±10 min, persisted | 07 §6.5 | mo-worker | 1 | E16, NEW:E56 | todo |
| T-07-073 | Journal: daily-rotated append-only; task id, repo, member pseudonym, model, usage, cost, status, timings, optional full text; 90-day retention | 07 §6.5 | mo-node | 1 | NEW:E60, NEW:E83 | todo |
| T-07-074 | Default storage layout per OS (config.toml, state dir, keychain, control socket `$XDG_RUNTIME_DIR/moochy.sock` / `$TMPDIR/moochy-<uid>.sock` 0600 / named pipe user ACL); `--home` overrides | 07 §7; CONTRACT §6 | mo-node | 1/5 | NEW:E72 | todo |
| T-07-075 | Config holds no secrets (safe for dotfiles) | 07 §7 | mo-node | 1 | NEW:E59 | todo |
| T-07-076 | Donor flow: install → login (Donate) → keys add (validated, models listed) → required safety screen (device cap + provider spend-limit checkbox, deep links) → donate → service install → status "waiting for approval" → "serving" | 07 §8.1 | mo-node | 1/4 | NEW:E81, NEW:REV-04 | todo |
| T-07-077 | Maintainer flow: claim on web + `moochy claim`, set goal + default model, approve donors/members, login (Use pooled compute), `connect`, start agent; status shows tasks | 07 §8.2 | mo-node + mo-web | 1/4 | NEW:E82, NEW:REV-04 | todo |
| T-07-078 | One-click always-on donor templates (small VPS / container platforms) using the encrypted-file keystore | 07 §8.3 | mo-ops* + mo-release* | 5 | NEW:REV-02 | todo |
| T-07-079 | Headless: `login --headless` code; owner grants `gateway` role scoped to one repo and adds as member with its own cap (`members add --device`); keystore file + passphrase in CI secrets; `up --headless` | 07 §8.4 | mo-node + mo-relay | 1/2 | NEW:E87, NEW:E30 | todo |
| T-07-080 | No relay-hosted MCP endpoint, ever | 07 §8.4; ADR-30 | mo-relay | — | NEW:REV-02 | todo |
| T-07-081 | Service install: launchd user agent `dev.moochy.node.plist`; systemd user unit (lingering on servers); Windows scheduled task or service | 07 §9 | mo-node | 5 | NEW:E81 | todo |
| T-07-082 | Dependency budget ≤ 25 direct deps; release binary ≤ 15 MB stripped + LTO | 07 §10 | mo-node + integrator | 1 | NEW:CI-07 | todo |
| T-07-083 | cargo-dist builds macOS (arm64, x86_64), Linux (x86_64, arm64; glibc + musl), Windows (x86_64, arm64): shell + PowerShell installers, Homebrew tap, npm package, archives | 07 §11 | mo-release* | 5 | NEW:CI-08 | todo |
| T-07-084 | Minimal container image: static musl binary, non-root | 07 §11 | mo-release* | 5 | NEW:CI-08 | todo |
| T-07-085 | Every artifact Sigstore-signed with SLSA provenance; reproducible builds checked in CI | 07 §11 | mo-release* | 3 | NEW:CI-08 | todo |
| T-07-086 | Client tests: golden vectors; fake providers (scripted SSE, usage, 429/529, mid-stream disconnect, slow start) | 07 §13 | mo-proto + mo-e2e | 1 | NEW:CI-01, E07, E08 | todo |
| T-07-087 | Client tests: recorded harness traffic corpus (Claude Code, OpenCode, Aider, Cline…) accepted by the firewall | 07 §13 | mo-worker | 1 | NEW:CI-13 | todo |
| T-07-088 | Client tests: MCP conformance (official inspector/test clients, stdio + HTTP; scripted OpenCode, Claude Code, one framework); roots enforcement | 07 §13 | mo-node | 1/3 | NEW:CI-15 | todo |
| T-07-089 | Client tests: fuzzing firewall (nested), frame parser, SSE parser, MCP `files` paths | 07 §13 | mo-worker + mo-proto + mo-node | 1/3 | NEW:CI-03 | todo |
| T-07-090 | Client tests: E2E in CI with Relay + 2 Gateways + 3 Workers + fake providers (failover, outbox replay, disputes, relay restart, known_tasks) | 07 §13 | mo-e2e | 1/2 | E06, E12, E20, NEW:E43 | todo |
| T-07-091 | Client tests: redaction (keys/scrubbed secrets never in logs, journals, crash reports, receipts) | 07 §13 | mo-node + mo-worker | 1 | NEW:CI-12, NEW:E59 | todo |
| T-07-092 | Client tests: keystore per OS in a CI matrix (persist, restart, headless fallback) | 07 §13 | mo-node + mo-release* | 5 | NEW:CI-16 | todo |

## 08 — Web app and dashboards

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-08-001 | Server-rendered `html/template` (auto-escaped); HTMX partial updates; `htmx-ext-sse` for live data; no SPA, no client state store | 08 §1.1 | mo-web | 4 | E19, NEW:CI-09 | todo |
| T-08-002 | Read-only pages work without JavaScript | 08 §1.2 | mo-web | 4 | NEW:E64 | todo |
| T-08-003 | Render once, fan out the same bytes to every subscriber | 08 §1.3 | mo-web | 4 | NEW:E65 | todo |
| T-08-004 | Privacy by default: aggregates public, individuals only on opt-in | 08 §1.4 | mo-web + mo-relay | 4 | NEW:E66 | todo |
| T-08-005 | Budgets: ≤ 50 KB transferred for a public repo page (excl. avatars), FCP < 1 s on 4G, Lighthouse accessibility ≥ 95 | 08 §1.5 | mo-web | 4 | NEW:CI-09 | todo |
| T-08-006 | CSS embedded in the binary, content-hashed filename, immutable cache headers (hand-written CSS ≤ 12 KB per CONTRACT §9; see §D) | 08 §1.6; CONTRACT §9 | mo-web | 4 | NEW:CI-09 | todo |
| T-08-007 | Persistent footer on every page + landing statement: "Moochy is 100% open source (Apache-2.0 OR MIT) and 100% free…", linking source, self-host guide, costs page | 08 §1.7 | mo-web | 4 | NEW:E64 | todo |
| T-08-008 | Fixed palette and dark theme via CSS custom properties + `prefers-color-scheme` (white, `#0B1220`, `#7DD3FC`, links `#0369A1`; dark bg `#0B1220`, text `#F8FAFC`) | 08 §11; CONTRACT §9; AGENTS §6 | mo-web | 4 | E19, NEW:CI-09 | todo |
| T-08-009 | `GET /` landing: what Moochy is, open-source/free statement, live global counters, featured repos, "works with any MCP client or OpenAI/Anthropic-compatible tool" | 08 §2 | mo-web | 4 | NEW:E64 | todo |
| T-08-010 | `GET /connect`: per-client snippets for both doors; supported donor providers | 08 §2 | mo-web | 4 | NEW:E64 | todo |
| T-08-011 | `GET /open`: source, license, self-host guide, monthly costs and sponsors (static, updated monthly) | 08 §2; 10 §10.1 | mo-web + human-po* | 4 | NEW:E64 | todo |
| T-08-012 | `GET /explore`: repos seeking compute (goal %, donors, models wanted) with filters | 08 §2 | mo-web + mo-relay | 4 | NEW:E64 | todo |
| T-08-013 | `GET /p/{owner}/{repo}` public repo page | 08 §2–3 | mo-web | 4 | E19 | todo |
| T-08-014 | `GET /p/{owner}/{repo}/events` SSE: presence + goal + audit-feed fragments | 08 §2 | mo-web | 4 | E19 | todo |
| T-08-015 | `GET /p/{owner}/{repo}/badge.svg` | 08 §2, §8 | mo-web | 4 | NEW:E64 | todo |
| T-08-016 | `GET /p/{owner}/{repo}/donate` pledge form (U) and `POST /p/{owner}/{repo}/pledges` create pledge | 08 §2 | mo-web + mo-relay | 1/4 | NEW:E37, NEW:E63 | todo |
| T-08-017 | `GET /station` donor station; `GET /station/events` SSE (live tasks, budgets, device status) | 08 §2, §4 | mo-web | 4 | NEW:E65 | todo |
| T-08-018 | `POST /station/pledges/{id}/pause`, `/resume`, `/reclaim` (HTMX swaps the row) | 08 §2 | mo-web + mo-relay | 4 | NEW:E37 | todo |
| T-08-019 | `GET /console/{owner}/{repo}` maintainer console (owner/admin only) | 08 §2, §5 | mo-web | 4 | NEW:E63 | todo |
| T-08-020 | `POST /console/{owner}/{repo}/donors/{id}/decline` (approval itself signed by `moochy approve`) | 08 §2 | mo-web + mo-relay | 4 | NEW:E37 | todo |
| T-08-021 | `POST /console/{owner}/{repo}/members`: update quotas, request member changes (change itself owner-Node-signed) | 08 §2 | mo-web + mo-relay | 4 | NEW:E30, NEW:E82 | todo |
| T-08-022 | `POST /console/{owner}/{repo}/settings`: goal, default model, pinned donors, auto-caching, tripwire mode, member default cap | 08 §2 | mo-web + mo-relay | 4 | NEW:E53, NEW:E63 | todo |
| T-08-023 | `GET/POST /claim`: repo claim with admin check | 08 §2 | mo-web + mo-relay | 1/4 | NEW:E63 | todo |
| T-08-024 | `GET/POST /device`: device approval (enter code → confirm roles, repo scope) | 08 §2 | mo-web + mo-relay | 1/4 | NEW:E63 | todo |
| T-08-025 | `GET /devices`, `POST /devices/{id}/revoke` | 08 §2 | mo-web + mo-relay | 4 | NEW:E63, NEW:E71 | todo |
| T-08-026 | `GET /r/{receipt_ref}` projection detail + how to verify | 08 §2, §6 | mo-web | 4 | NEW:E64 | todo |
| T-08-027 | `GET /log` key-log explorer: latest checkpoints, Git anchor status, search by pseudonym or repo | 08 §2 | mo-web + mo-relay | 4 | NEW:E64 | todo |
| T-08-028 | `GET /log/checkpoint`, `/log/tile/...`, `/log/keys/...` machine endpoints for tlog clients (static, CDN-cacheable) | 08 §2 | mo-relay | 3 | NEW:E40 | todo |
| T-08-029 | `GET /leaderboard` global donors (opt-in names) | 08 §2 | mo-web | 4 | NEW:E64 | todo |
| T-08-030 | `GET /auth/{provider}`, `/auth/{provider}/callback`, `POST /logout` (OAuth) | 08 §2 | mo-relay + mo-web | 1 | NEW:E63 | todo |
| T-08-031 | `GET /admin/...` minimal moderation + metrics, separate auth by operator device keys | 08 §2; 10 §11 | mo-relay + mo-web | 6 | NEW:E77 | todo |
| T-08-032 | All routing via stdlib `ServeMux` method + path patterns | 08 §2 | mo-web + mo-relay | 1 | NEW:CI-02 | todo |
| T-08-033 | Repo page header + goal (committed %, used %, token-equivalents, donor count); SSE `goal` coalesced ≤ 1 per 30 s | 08 §3 | mo-web | 4 | E19, NEW:E65 | todo |
| T-08-034 | Live pool (aggregated nodes online, models, tasks running, median added latency, opt-in donors); SSE `pool` ≤ 1/s | 08 §3 | mo-web + mo-relay | 4 | E19, NEW:E66 | todo |
| T-08-035 | Top donors this month (undisputed receipts); page load + SSE every 60 s | 08 §3 | mo-web | 4 | NEW:E64 | todo |
| T-08-036 | Audit feed of newest donor-signed projections; SSE `audit` per receipt, ≤ 1/s, max 20 rows; ✓ undisputed / ⚠ disputed; each row links `/r/{ref}`; day only | 08 §3 | mo-web | 4 | E19, NEW:E66 | todo |
| T-08-037 | Log footer (entries, checkpoint time, anchored ✓); SSE `log` event | 08 §3 | mo-web | 4 | NEW:E64 | todo |
| T-08-038 | No per-node RTT or online schedule per person anywhere | 08 §3 | mo-web | 4 | NEW:E66 | todo |
| T-08-039 | Donor Station: devices (role, online, slots, cap usage), pledges (status, policy, budget/spent/reserved, pause/reclaim), live tasks, monthly summary (served, tasks, cache hit %, saved ≈ $X), safety status (spend limit self-reported, device caps) | 08 §4 | mo-web + mo-relay | 4 | NEW:E65 | todo |
| T-08-040 | "Saved ≈ $X" = cost without cache hits computed from receipts (`cost_uncached_uusd`) | 08 §4; 09 §3.6 | mo-relay + mo-web | 4 | NEW:CI-10 | todo |
| T-08-041 | Console panel Pool health: committed vs used, utilization, projected end-of-month headroom, models available vs requested-but-missing | 08 §5 | mo-web + mo-relay | 4 | NEW:E63 | todo |
| T-08-042 | Console panel Donor approvals: pending donors with signals (account age, other repos, past disputes), one-line `moochy approve` command, decline button | 08 §5 | mo-web | 4 | NEW:E82 | todo |
| T-08-043 | Console panel Members (incl. CI devices), quotas, usage, last activity; add/remove via owner's Node | 08 §5 | mo-web | 4 | NEW:E30 | todo |
| T-08-044 | Console panel Policy: pinned donors, tripwire mode, auto-caching, default model, own-key fallback guidance | 08 §5 | mo-web | 4 | NEW:E63 | todo |
| T-08-045 | Console panel Usage: per-member and per-model usage, cache hit ratio, failover rate, added latency | 08 §5 | mo-web + mo-relay | 4 | NEW:E63 | todo |
| T-08-046 | Console panel Goal: amount + public "what we use AI compute for" description | 08 §5 | mo-web | 4 | NEW:E64 | todo |
| T-08-047 | Projection page shows fields, donor signature, donor device's key-log entry, current checkpoint + Git anchor, the `moochy verify r_…` command, and what a receipt does **not** prove | 08 §6 | mo-web | 4 | NEW:E64 | todo |
| T-08-048 | In-browser verifier deferred (verification in the open-source client) | 08 §6 | mo-web | D | NEW:MON-03 | todo |
| T-08-049 | SSE topics `repo:{id}`, `station:{user_id}`, `global`; hub one goroutine per topic shard | 08 §7 | mo-web | 4 | NEW:E65 | todo |
| T-08-050 | Coalescing: per-topic dirty flags, ≤ 1 render per topic per interval regardless of event rate | 08 §7 | mo-web | 4 | NEW:E65, NEW:CI-09 | todo |
| T-08-051 | Backpressure: small bounded queue per subscriber; full → disconnect; hub never blocks the Scheduler | 08 §7 | mo-web | 4 | NEW:E65 | todo |
| T-08-052 | On connect send current full fragments immediately (no `Last-Event-ID` replay) | 08 §7 | mo-web | 4 | E19, NEW:E65 | todo |
| T-08-053 | HTTP/2 for all web traffic | 08 §7 | mo-relay + mo-web | 4 | NEW:E64 | todo |
| T-08-054 | SSE heartbeat comment every 25 s | 08 §7 | mo-web | 4 | NEW:E65 | todo |
| T-08-055 | Badge SVG "AI compute: N donors · X% of goal", template without external fonts, cached 5 min | 08 §8 | mo-web | 4 | NEW:E64 | todo |
| T-08-056 | Each repo page links to other repos the same donors support | 08 §8 | mo-web + mo-relay | 4 | NEW:E64 | todo |
| T-08-057 | Session cookie `HttpOnly`, `Secure`, `SameSite=Lax`, random 256-bit id, only SHA-256 hash stored | 08 §9; 09 §3.1 | mo-relay + mo-web | 1/4 | NEW:E63 | todo |
| T-08-058 | CSRF: state-changing requests require `HX-Request: true` and a matching `Origin`; non-HTMX fallbacks use a per-session token | 08 §9 | mo-web | 4 | NEW:E63 | todo |
| T-08-059 | CSP `default-src 'self'`, self-only scripts (vendored htmx), `frame-ancestors 'none'`; `img-src` limited to provider avatar hosts or proxied avatars | 08 §9 | mo-web | 4 | NEW:E63 | todo |
| T-08-060 | Rate limits per IP and per session on POST routes and SSE connections | 08 §9 | mo-web + mo-relay | 4 | NEW:E78 | todo |
| T-08-061 | Templates: `layouts/`, `pages/` (one per route), `fragments/` shared between first render and SSE/HTMX swaps; no emails in v1 | 08 §10 | mo-web | 4 | NEW:CI-09 | todo |
| T-08-062 | `aria-live="polite"` on audit feed and pool summary, throttled | 08 §11 | mo-web | 4 | NEW:CI-09 | todo |
| T-08-063 | Colour never the only signal (✓/⚠ glyphs + text); ping dots respect `prefers-reduced-motion` | 08 §11 | mo-web | 4 | NEW:CI-09 | todo |
| T-08-064 | Money shows dollars first, tokens in a tooltip / `<details>` without JS | 08 §11 | mo-web | 4 | NEW:E64 | todo |

## 09 — Data model (SQLite)

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-09-001 | Draft fixes: `devices` table (not `users.public_key`); `identities` table (GitHub + GitLab per user); no `mcp_secret`; goals in µ$; history tables; `tasks` + `attempts`; all times INTEGER Unix ms | 09 §1 | mo-relay | 1 | NEW:E67 | todo |
| T-09-002 | Pragmas: `journal_mode=WAL`, `synchronous=FULL`, `foreign_keys=ON`, `busy_timeout=5000`, `temp_store=MEMORY`, `mmap_size=1 GiB`, `wal_autocheckpoint=0` | 09 §2 | mo-relay | 1 | NEW:E67 | todo |
| T-09-003 | One writer connection owned by the Store writer goroutine; pool of read-only (`mode=ro`) connections for web, audit job, tile serving | 09 §2 | mo-relay | 1 | NEW:CI-02 | todo |
| T-09-004 | `users`: `id` PK, `pseudonym` UNIQUE random (only public identifier), `display_name`, `status` (`active`/`suspended`/`deleted`), `created_at` | 09 §3.1 | mo-relay | 1 | NEW:E67 | todo |
| T-09-005 | `identities`: PK (`provider`, `provider_user_id`), `user_id`, `username`, `avatar_url` refreshed at login, `account_created_at` | 09 §3.1 | mo-relay | 1 | NEW:E63 | todo |
| T-09-006 | `devices`: `id` (`d_…`), `user_id`, `name`, `sign_pub` UNIQUE 32 B, `enc_pub` 32 B, `suite`, `roles`, `repo_scope`, `cap_uusd_month`, `key_log_index`, `created_at`, `revoked_at` | 09 §3.1 | mo-relay | 1 | NEW:E67 | todo |
| T-09-007 | `device_usage` (`device_id`, `month`) with non-negative CHECKs, capped devices only | 09 §3.1 | mo-relay | 2 | NEW:E30 | todo |
| T-09-008 | `web_sessions` (`id_hash` PK = SHA-256 of cookie, `user_id`, `created_at`, `expires_at`) | 09 §3.1 | mo-relay | 1 | NEW:E63 | todo |
| T-09-009 | `device_codes` (`user_code` PK, `device_code_hash`, `sign_pub`, `enc_pub`, `requested_roles`, `requested_scope`, `approved_by`, `expires_at`), short-lived | 09 §3.1 | mo-relay | 1 | E01, NEW:E83 | todo |
| T-09-010 | `repos`: `id` (`r_…`), UNIQUE(`provider`, `provider_repo_id`) (rename-stable), UNIQUE(`provider`, `owner`, `name`), `claimed_by`, `claim_log_index`, `goal_uusd_month ≥ 0`, `default_model`, `description`, `settings` JSON, `status` | 09 §3.2 | mo-relay | 1 | NEW:E67 | todo |
| T-09-011 | `members`: PK(`repo_id`, `user_id`), `role`, `log_index`, `cap_uusd_month` (NULL unlimited), current-month `spent/reserved/month` with CHECKs, `removed_at` | 09 §3.2 | mo-relay | 1/2 | NEW:E30 | todo |
| T-09-012 | `member_months` history (`repo_id`, `user_id`, `month`, `spent_uusd`) for start-period attribution and audit | 09 §3.2 | mo-relay | 2 | NEW:E36, NEW:E68 | todo |
| T-09-013 | `pledges`: `id` (`p_…`), `donor_id`, `repo_id`, `status` (`pending/active/paused/ended/declined`), `approval_log_index`, `budget_uusd ≥ 0`, `per_task_cap_uusd > 0` default 5,000,000, `policy` JSON, `visibility`, `rollover`, `period_anchor_day` 1–28, `period_start`, `spent/reserved` with CHECKs, timestamps; partial UNIQUE(`donor_id`, `repo_id`) WHERE status IN active states | 09 §3.3 | mo-relay | 1 | NEW:E37, NEW:E67 | todo |
| T-09-014 | `pledge_periods` (PK `pledge_id`, `period_start`; `budget`, `spent`, `tasks`, `closed_at`); closed periods still receive start-period settlements | 09 §3.3 | mo-relay | 1 | NEW:E36 | todo |
| T-09-015 | `tasks` (metadata only): PK(`gateway_device`, `id`), repo, member, route facts, `body_bytes`, `status`, `fail_code`, `t_submit`, `t_end`; index (`repo_id`, `t_submit`) | 09 §3.4 | mo-relay | 1 | E13, NEW:E67 | todo |
| T-09-016 | `attempts`: PK(`task_id`, `attempt`), devices, pledge, `reserved/cost`, `catalog_version`, `period_start`, `status` (committed … pessimistic), `nack_code`, timestamps; index (`pledge_id`, `period_start`); partial index on `awaiting_receipt`/`orphaned` | 09 §3.4 | mo-relay | 1 | E12, NEW:E35 | todo |
| T-09-017 | `receipts`: PK(`task_id`, `attempt`), exact `body` + `donor_sig`, `projection` + `projection_sig`, UNIQUE `receipt_ref`, `dispute_code/sig`, `pledge_id`, `period_start`, denormalized usage + cost, `estimated`, `received_at`; indexes (`pledge_id`, `period_start`), (`received_at`) | 09 §3.4 | mo-relay | 1 | E01, NEW:E43 | todo |
| T-09-018 | `log_entries` (`log` ∈ {`keys`, reserved `receipts`}, `idx`, `kind`, exact `body`, `sigs`, `created_at`), `log_hashes`, `checkpoints` (`tree_size`, `root_hash`, `note`, `anchored_at`, `created_at`) | 09 §3.5 | mo-relay | 3 | NEW:E40 | todo |
| T-09-019 | Full tiles immutable, computed on demand from `log_hashes`, cached in memory/CDN, never stored twice | 09 §3.5 | mo-relay | 3 | NEW:E40 | todo |
| T-09-020 | `catalog` table (PK `version`, `model`, `provider`; prices, limits, `native_aliases`, `source`, `effective_at`, `log_index`) | 09 §3.6 | mo-relay | 1 | NEW:E39 | todo |
| T-09-021 | `usage_daily` (PK `day`, `repo_id`, `pledge_id`, `model`; tasks, tokens, `cost_uusd`, `cost_uncached_uusd`, `failovers`, `p50/p95_added_ms`), rolled up hourly, kept forever | 09 §3.6 | mo-relay | 4 | NEW:E83 | todo |
| T-09-022 | `reports` (evidence BLOB encrypted to the operator's moderation key) and `strikes` (`route_mismatch`, `firewall`, `dispute_upheld`, …) | 09 §3.6 | mo-relay | 1/3 | NEW:E55, NEW:E62 | todo |
| T-09-023 | Write path: Scheduler group commit every 10 ms or 256 ops, SAVEPOINT per op, completion channel; `task.assign` and `receipt.ack` only after commit returns | 09 §4 | mo-relay | 1 | E12, NEW:CI-06 | todo |
| T-09-024 | Receipt intake atomic with balance update in the same group commit; disputes and key-log appends via group commit | 09 §4 | mo-relay | 1/3 | E12, NEW:E43 | todo |
| T-09-025 | Web handlers write through the writer goroutine (request → reply, typically < 15 ms) | 09 §4 | mo-relay + mo-web | 1/4 | NEW:E37 | todo |
| T-09-026 | Nightly retention: delete `tasks`/`attempts` > 90 days (after rollup), expired sessions and device codes, in small batches | 09 §4 | mo-relay | 2 | NEW:E83 | todo |
| T-09-027 | Read paths use the listed indexes (repo page, station, console, tile server, audit job, boot) | 09 §5 | mo-relay | 1/4 | NEW:CI-06 | todo |
| T-09-028 | Migrations embedded, numbered, forward-only, each in its own transaction, run at boot before accepting connections | 09 §6 | mo-relay | 1 | NEW:E67 | todo |
| T-09-029 | Each migration declares `min_compatible_version`; binary refuses to start only if the DB requires a newer binary (rollback works) | 09 §6 | mo-relay | 2 | NEW:E67 | todo |
| T-09-030 | Expand → migrate → contract across two releases; long index builds run as a background step after boot | 09 §6 | mo-relay | 2 | NEW:CI-11 | todo |
| T-09-031 | Test suite applies all migrations on an empty DB and on a previous-release snapshot | 09 §6 | mo-relay | 1 | NEW:CI-11 | todo |
| T-09-032 | Litestream: continuous WAL to S3-compatible storage, daily snapshots, 30-day retention | 09 §7 | mo-ops* | 1 | NEW:CI-21 | todo |
| T-09-033 | Automated monthly restore drill: restore to scratch VM, boot read-only, run audit job, compare key-log root with published anchor | 09 §7; 10 §4 | mo-ops* + mo-relay | 6 | NEW:CI-21 | todo |
| T-09-034 | Relay supports a read-only boot mode (for the restore drill) | 09 §7 | mo-relay | 6 | NEW:CI-21 | todo |
| T-09-035 | Ceiling: past ~100M receipts archive receipts > 13 months to compressed object storage (projections stay) | 09 §8; 10 R7 | mo-relay + mo-ops* | D | NEW:MON-03 | todo |

## 10 — Operations

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-10-001 | `dev` env: Relay + fake providers + N simulated Nodes from one harness command | 10 §1 | mo-e2e | 1 | E01 | todo |
| T-10-002 | `staging` env: same binary and topology as prod, real providers with test keys and tiny budgets | 10 §1 | mo-ops* | 2 | NEW:CI-20 | todo |
| T-10-003 | Same artifact promoted staging → prod; no environment-specific builds | 10 §1 | mo-release* + mo-ops* | 2 | NEW:CI-08 | todo |
| T-10-004 | Prod: one VM with NVMe (start 4 vCPU / 8 GB), region near early users | 10 §2 | mo-ops* + human-po* | 6 | NEW:REV-06 | todo |
| T-10-005 | One systemd unit for the relay; restarts use drain-and-restart | 10 §2 | mo-ops* | 2 | NEW:CI-21 | todo |
| T-10-006 | Public instance runs exactly the open-source binary + `deploy/` files; self-hosters get the same recipe with own domain, OAuth app, signing keys | 10 §2 | mo-ops* + mo-docs* | 6 | NEW:REV-02 | todo |
| T-10-007 | Optional CDN only in front of `/log/tile/*`, `/static/*`, `/p/*/badge.svg`; WS and SSE straight to origin | 10 §2 | mo-ops* + mo-relay | 6 | NEW:E64 | todo |
| T-10-008 | Signing keys loaded at boot from encrypted file (passphrase via systemd credentials) or KMS; OAuth secrets via systemd credentials; never in child env or logs | 10 §2 | mo-relay + mo-ops* | 3 | NEW:E80 | todo |
| T-10-009 | Configuration: one TOML file + flags; every value has a documented default; effective config printed at boot with secrets redacted | 10 §2; ADR-32 | mo-relay | 1 | NEW:E80 | todo |
| T-10-010 | Drain (≤ 30 s): `relay.draining`, Scheduler stops assigning, new submits retryable error, non-started tasks failed retryable + Workers cancelled, started streams get up to 30 s | 10 §3 | mo-relay | 2 | NEW:E33 | todo |
| T-10-011 | Restart: flush writer, exit, start new binary, migrations, load state, missed rollovers, accept connections | 10 §3 | mo-relay | 2 | NEW:E33, NEW:E67 | todo |
| T-10-012 | Recover: Gateways reconnect immediately, Workers jittered 0–10 s, `known_tasks` + outbox replay | 10 §3 | mo-node | 2 | NEW:E33 | todo |
| T-10-013 | Drain exit criterion: ≤ ~10 s retryable errors per upgrade, zero ledger drift | 10 §3 | mo-relay | 2 | NEW:E33, NEW:CI-22 | todo |
| T-10-014 | Blue/green zero-downtime (SO_REUSEPORT, make-before-break, old process fails non-started then forwards only, settlement via outbox replay) built only when `tasks_total{status="failed",cause="deploy"}` is visible | 10 §3; ADR-22 | mo-relay | D | NEW:MON-03 | todo |
| T-10-015 | DR: process crash RPO 0 / RTO < 10 s (systemd restart) | 10 §4 | mo-ops* + mo-relay | 1 | E12 | todo |
| T-10-016 | DR: VM loss / disk corruption RPO ~1 s DB, 0 spend, RTO < 30 min (provision → restore → boot → `replay_since` → reconnect) | 10 §4 | mo-ops* | 6 | NEW:CI-21, NEW:E34 | todo |
| T-10-017 | DR: region outage RTO < 1 h (restore elsewhere, low-TTL DNS) | 10 §4 | mo-ops* | 6 | NEW:CI-21 | todo |
| T-10-018 | Metrics in Prometheus format on a private port | 10 §5.1 | mo-relay | 2 | NEW:E80 | todo |
| T-10-019 | Metric `relay_added_latency_ms` histogram: last body frame received → first response byte forwarded minus Worker-reported provider TTFT | 10 §5.1 | mo-relay + mo-node | 2 | E20, NEW:E80 | todo |
| T-10-020 | Metric `gateway_overhead_ms` (opt-in Node telemetry) | 10 §5.1 | mo-node | 2 | NEW:E80 | todo |
| T-10-021 | Metrics `scheduler_apply_us` by event type, `ack_latency_ms`, `start_latency_ms` | 10 §5.1 | mo-relay | 2 | NEW:E80 | todo |
| T-10-022 | Metrics `tasks_total` by final status (+ cause), `failovers_total` by NACK code, `routing_deadline_exceeded_total` | 10 §5.1 | mo-relay | 2 | NEW:E80 | todo |
| T-10-023 | Metrics `workers_online` by model, `slots_free_total`, `pool_headroom_uusd` by repo | 10 §5.1 | mo-relay | 2 | NEW:E80 | todo |
| T-10-024 | Metrics `reserved_uusd_total`, `settled_uusd_total`, `pessimistic_settlements_total`, `audit_drift_uusd` | 10 §5.1 | mo-relay | 2 | NEW:E80, NEW:E68 | todo |
| T-10-025 | Metrics `cache_read_ratio` by repo, `affinity_hit_ratio` | 10 §5.1 | mo-relay | 2 | NEW:E80, NEW:E28 | todo |
| T-10-026 | Metric `request_bytes_sealed` histogram (delta-transfer trigger) | 10 §5.1 | mo-relay | 2 | NEW:E80 | todo |
| T-10-027 | Metrics `key_log_size`, `checkpoint_age_s`, `anchor_lag_s` | 10 §5.1 | mo-relay | 3 | NEW:E80 | todo |
| T-10-028 | Metrics `ws_connections`, `ws_writer_queue_overflow_total`, `sse_subscribers`, `sse_dropped_total` | 10 §5.1 | mo-relay + mo-web | 2/4 | NEW:E80 | todo |
| T-10-029 | Metrics `commit_latency_ms`, `group_commit_batch_size`, `wal_size_bytes`, `litestream_lag_s` | 10 §5.1 | mo-relay + mo-ops* | 2 | NEW:E80 | todo |
| T-10-030 | Metrics `firewall_rejections_total` by field name (Worker telemetry), `route_mismatch_total`, `bad_envelope_total`, `unknown_key_alerts_total` | 10 §5.1 | mo-relay | 2/3 | NEW:E80 | todo |
| T-10-031 | Structured JSON `log/slog` logs with `task_id`, `repo_id`, `device_id` on every task-scoped line; never content or secrets (content is opaque bytes with no string formatter) | 10 §5.2 | mo-relay | 1 | E13, NEW:E80 | todo |
| T-10-032 | Optional OpenTelemetry traces for task lifecycles, sampled 1%, staging and prod | 10 §5.2 | mo-relay | 2 | NEW:E80 | todo |
| T-10-033 | Nodes send only opt-in anonymous telemetry (version, OS, firewall rejection field names, latency histograms), never content | 10 §5.2 | mo-node | 2 | NEW:E80 | todo |
| T-10-034 | SLO: relay availability 99.9% monthly via synthetic probes from 3 regions every 30 s | 10 §6 | mo-ops* | 6 | NEW:MON-02 | todo |
| T-10-035 | SLO: task success ≥ 99.5%; relay-added latency p50/p95 ≤ 60/150 ms; scheduler apply p99 ≤ 50 µs | 10 §6 | mo-ops* + mo-relay | 2/6 | NEW:MON-02 | todo |
| T-10-036 | SLO: 100% of donor-signed receipts settled within 24 h; ledger drift 0 µ$; checkpoint freshness ≤ 2 min when the log grew | 10 §6 | mo-ops* + mo-relay | 3/6 | NEW:MON-02 | todo |
| T-10-037 | Page: `audit_drift_uusd != 0` | 10 §7 | mo-ops* | 2 | NEW:MON-01 | todo |
| T-10-038 | Page: availability probe failing for 2 min | 10 §7 | mo-ops* | 6 | NEW:MON-01 | todo |
| T-10-039 | Page: `bad_envelope_total` spike or `unknown_key_alerts_total > 0` | 10 §7 | mo-ops* | 3 | NEW:MON-01 | todo |
| T-10-040 | Page: `litestream_lag_s > 60` | 10 §7 | mo-ops* | 2 | NEW:MON-01 | todo |
| T-10-041 | Ticket → page after 30 min: `checkpoint_age_s > 600` while log grows | 10 §7 | mo-ops* | 3 | NEW:MON-01 | todo |
| T-10-042 | Tickets: failover rate > 5% for 15 min; `scheduler_apply_us` p99 > 200 µs; `ws_writer_queue_overflow_total` rising; new firewall-rejection field from > 50 distinct Workers | 10 §7 | mo-ops* | 2 | NEW:MON-01 | todo |
| T-10-043 | Runbook R1 relay down | 10 §8 | mo-ops* | 6 | NEW:REV-02 | todo |
| T-10-044 | Runbook R2 ledger drift (freeze affected pledges, diff, correct, postmortem); relay supports freezing a pledge's new reservations | 10 §8 | mo-ops* + mo-relay | 6 | NEW:REV-02, NEW:E77 | todo |
| T-10-045 | Runbook R3 mass Worker disconnect | 10 §8 | mo-ops* | 6 | NEW:REV-02 | todo |
| T-10-046 | Runbook R4 provider outage | 10 §8 | mo-ops* | 6 | NEW:REV-02 | todo |
| T-10-047 | Runbook R5 abuse report (verify bundle, suspend donor devices, `MODERATION` entry, notify repo) | 10 §8 | mo-ops* + mo-relay | 6 | NEW:REV-02, NEW:E62 | todo |
| T-10-048 | Runbook R6 log-key compromise (offline new key, transition checkpoint co-signed + anchored, announce, Nodes pin new key via signed release) | 10 §8 | mo-ops* + mo-node | 6 | NEW:REV-02 | todo |
| T-10-049 | Runbook R7 DB growth (retention job, task-row floods, archive receipts > 13 months) | 10 §8 | mo-ops* | 6 | NEW:REV-02 | todo |
| T-10-050 | Runbook R8 firewall bypass (tighter release, raise `min_client_version`, notify donors) | 10 §8 | mo-ops* + mo-worker | 6 | NEW:REV-02, NEW:E70 | todo |
| T-10-051 | Scaling path steps (vertical, split web process over local socket, regional edges, shard by repo) each gated by a metric threshold | 10 §9 | mo-relay + mo-ops* | D | NEW:MON-03 | todo |
| T-10-052 | Cost envelope ≈ $40–60/month early, ≈ $100–180/month at 1M tasks | 10 §10 | mo-ops* + human-po* | 6 | NEW:REV-06 | todo |
| T-10-053 | Open sponsorship (GitHub Sponsors / Open Collective) with public monthly cost page `/open` | 10 §10.1 | human-po* + mo-web | 4 | NEW:REV-06, NEW:E64 | todo |
| T-10-054 | Pools portable: Nodes switch relay with one config value | 10 §10.1 | mo-node | 1 | E01 | todo |
| T-10-055 | `/admin` (operator devices only): user/device/pledge lookup by id or pseudonym, suspend/unsuspend, moderation queue, catalog publishing (two-person approval), feature flags | 10 §11 | mo-relay + mo-web | 6 | NEW:E77 | todo |
| T-10-056 | `relay admin …` subcommands for the same operations from the VM shell | 10 §11 | mo-relay | 6 | NEW:E77 | todo |
| T-10-057 | Every admin action writes an internal audit-log row; public actions (catalog, moderation) also a transparency-log entry | 10 §11 | mo-relay | 6 | NEW:E77 | todo |

## 11 — Roadmap and verification strategy

Phase scopes are traced in their canonical rows above; this table holds what only 11 states: Phase 0 deliverables, every exit criterion, research triggers, cross-cutting verification, and the beta launch checklist.

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-11-001 | Ph0: public monorepo from day one with license, README ("100% open source, 100% free"), CONTRIBUTING, CODE_OF_CONDUCT, SECURITY.md, public roadmap, plan docs | 11 Ph0 | mo-docs* + integrator | 0 | NEW:CI-18, NEW:REV-02 | todo |
| T-11-002 | Ph0: provider-terms review with counsel (Anthropic, OpenRouter, DeepSeek, OpenAI, each planned host) → written go/no-go + donor consent text | 11 Ph0 | human-counsel* | 0 | NEW:REV-01 | todo |
| T-11-003 | Ph0: client compatibility spike for both doors (OpenCode, Claude Code, Cursor, Cline, Zed, Goose, one framework; Aider, Continue, SDKs) → integration matrix + captured traffic for the firewall corpus | 11 Ph0 | mo-e2e* + mo-node | 0 | NEW:CI-20, NEW:CI-13 | todo |
| T-11-004 | Ph0: pin per-provider facts (usage fields, rate-limit headers, error shapes, allowed fields, model defaults) → adapter tables v0 | 11 Ph0 | mo-worker | 0 | NEW:CI-17 | todo |
| T-11-005 | Ph0: crypto spike (HPKE wrap + chunked AEAD in Rust, Go forwarding opaque frames) → first golden vectors | 11 Ph0 | mo-proto + mo-relay | 0 | NEW:CI-01 | todo |
| T-11-006 | Ph0: latency spike (fake provider, three Nodes in three regions, with/without compression and warm pools) | 11 Ph0 | mo-e2e* + mo-ops* | 0 | NEW:CI-20 | todo |
| T-11-007 | Ph0 exit: counsel go for ≥ Anthropic, OpenRouter, DeepSeek; ≥ 3 clients unmodified per door; vectors pass in both languages; added latency within 2× budget | 11 Ph0 | human-po* | 0 | NEW:REV-01, NEW:CI-01, NEW:CI-20 | todo |
| T-11-008 | Ph1 exit 1: real Claude Code session completes a multi-step task via two env vars, once on an Anthropic donor and once on OpenRouter or DeepSeek (Anthropic dialect) | 11 Ph1 | mo-e2e* + mo-node | 1 | NEW:CI-20 | todo |
| T-11-009 | Ph1 exit 2: real OpenCode session on an OpenRouter donor via the API door **and** `moochy_delegate` via MCP against a DeepSeek donor in the same session | 11 Ph1 | mo-e2e* + mo-node | 1 | NEW:CI-20 | todo |
| T-11-010 | Ph1 exit 3: an agent framework completes a scripted task using only the Streamable HTTP MCP endpoint | 11 Ph1 | mo-e2e* + mo-node | 1 | NEW:CI-20, E05 | todo |
| T-11-011 | Ph1 exit 4: `moochy audit --provider` ≤ 0.5% drift over 200 tasks per provider | 11 Ph1 | mo-node + human-po* | 1 | NEW:CI-20 | todo |
| T-11-012 | Ph1 exit 5: `kill -9` mid-stream → exactly one settled receipt per provider-reached attempt, others released via `known_tasks`, nothing double-settled | 11 Ph1 | mo-e2e | 1 | E12 | todo |
| T-11-013 | Ph1 exit 5b: vectors prove two attempts never share a response key; Worker refuses replayed/forged tasks (bad sig, stale ULID, foreign repo) | 11 Ph1 | mo-proto + mo-node | 1 | NEW:CI-01, E16, NEW:E56, NEW:E41 | todo |
| T-11-014 | Ph1 exit 6: firewall rejects 100% of the seeded forbidden corpus and accepts 100% of captured real traffic from clients of criteria 1–3 | 11 Ph1 | mo-worker | 1 | NEW:CI-13, E09 | todo |
| T-11-015 | Ph1 exit 7: relay DB holds no prompt/output bytes (canary grep) | 11 Ph1 | mo-e2e | 1 | E13 | todo |
| T-11-016 | Ph1–2 run with design partners only while keys and approvals are relay-asserted | 11 Ph1 | human-po* | 1–2 | NEW:REV-06 | todo |
| T-11-017 | Ph2 exit 1: simulator 1M tasks / 2,000 workers with faults → zero invariant violations; same seed identical | 11 Ph2 | mo-relay | 2 | NEW:CI-04 | todo |
| T-11-018 | Ph2 exit 2: chaos (real binaries, fake providers: random kills, 429 storms, 2 relay upgrades under load) → success ≥ 99.5%, ≤ 10 s retryable errors per upgrade, zero drift | 11 Ph2 | mo-e2e | 2 | NEW:CI-22 | todo |
| T-11-019 | Ph2 exit 3: real agent sessions `affinity_hit_ratio` ≥ 95%, `cache_read_ratio` ≥ 80% | 11 Ph2 | mo-e2e* + mo-relay | 2 | NEW:CI-20, NEW:E28 | todo |
| T-11-020 | Ph2 exit 4: added latency p50 ≤ 60 ms in-continent | 11 Ph2 | mo-relay | 2 | NEW:CI-20, E20 | todo |
| T-11-021 | Ph2 scope includes SLO dashboards | 11 Ph2 | mo-ops* | 2 | NEW:MON-02 | todo |
| T-11-022 | Ph3 exit 1: injected rogue device key for user U flagged by U's Node within 2 checkpoint intervals | 11 Ph3 | mo-node | 3 | NEW:E40 | todo |
| T-11-023 | Ph3 exit 2: relay-forged donor approval refused by Gateways; forged repo claim flagged by the real owner's Node | 11 Ph3 | mo-node | 3 | NEW:E41 | todo |
| T-11-024 | Ph3 exit 3: forked log detected by Nodes against the public Git anchor | 11 Ph3 | mo-node | 3 | NEW:E42 | todo |
| T-11-025 | Ph3 exit 4: structural checks reject 100% of undeclared, schema-failing, or unsigned tool calls; tripwire blocks the documented baseline corpus and is documented as a speed bump | 11 Ph3 | mo-node + mo-worker | 3 | E18, NEW:E44, NEW:CI-14 | todo |
| T-11-026 | Ph3 exit 5: MCP `files` refuses every case of the path-escape corpus | 11 Ph3 | mo-node | 3 | NEW:E46 | todo |
| T-11-027 | Ph3 exit 6: independent rebuild of the Linux musl release is bit-identical | 11 Ph3 | mo-release* | 3 | NEW:CI-08 | todo |
| T-11-028 | Ph4 exit: page budgets met; 10k simulated SSE subscribers on one repo page < 1 core; accessibility ≥ 95 | 11 Ph4 | mo-web | 4 | NEW:CI-09 | todo |
| T-11-029 | Ph4 exit: usability test — 5 developers donate < 5 min, 5 maintainers get an agent running < 3 min, unaided | 11 Ph4 | human-po* | 4 | NEW:REV-04 | todo |
| T-11-030 | Ph5: more adapters (Gemini OpenAI-compatible, Groq, Together, Fireworks, Mistral, xAI), one table + fixtures each | 11 Ph5 | mo-worker | 5 | NEW:E76, NEW:CI-17 | todo |
| T-11-031 | Ph5: `moochy connect` coverage for every client in the matrix; `npx -y moochy mcp`; container image | 11 Ph5 | mo-node + mo-release* | 5 | NEW:E73, NEW:CI-08 | todo |
| T-11-032 | Ph5: GitLab identity and repos (same flows as GitHub) | 11 Ph5 | mo-relay + mo-web | 5 | NEW:E86 | todo |
| T-11-033 | Ph5: `service install` on all OSes; one-click always-on templates | 11 Ph5 | mo-node + mo-ops* | 5 | NEW:E81, NEW:CI-16 | todo |
| T-11-034 | Ph5: Windows support (named pipes, Credential Manager) | 11 Ph5 | mo-node | 5 | NEW:CI-16 | todo |
| T-11-035 | Ph5: own-key fallback | 11 Ph5 | mo-node | 5 | NEW:E84 | todo |
| T-11-036 | Ph5: remote-MCP self-tunnel mode (opt-in, OAuth 2.1, Host allowlist) | 11 Ph5 | mo-node | 5 | NEW:E85 | todo |
| T-11-037 | Ph5 exit: compatibility matrix green for targeted tools; all CI OS matrix jobs green | 11 Ph5 | mo-release* + mo-e2e* | 5 | NEW:CI-20, NEW:CI-16 | todo |
| T-11-038 | Ph6: external security review / pentest (firewall, envelopes, Gateway localhost surface, web); all high/critical fixed | 11 Ph6 | human-po* + mo-sec | 6 | NEW:REV-03 | todo |
| T-11-039 | Ph6: load test at 2× design point; SLOs hold | 11 Ph6 | mo-e2e* + mo-ops* | 6 | NEW:CI-19 | todo |
| T-11-040 | Ph6: DR drill (VM loss) achieves RTO < 30 min | 11 Ph6 | mo-ops* | 6 | NEW:CI-21 | todo |
| T-11-041 | Ph6: docs published — donor guide (incl. provider spend limits), maintainer guide, protocol spec, public threat model | 11 Ph6 | mo-docs* + integrator + mo-sec | 6 | NEW:REV-02 | todo |
| T-11-042 | Ph6: terms of service and privacy policy reflecting 06 §14, counsel sign-off | 11 Ph6 | human-counsel* | 6 | NEW:REV-01 | todo |
| T-11-043 | Research: verified mode (TLS notarization, Relay as notary) — trigger: maintainer demand + acceptable overhead | 11 Research | mo-proto + mo-worker | R | NEW:MON-03 | todo |
| T-11-044 | Research: public receipt log + witnesses + in-browser verifier — trigger: demand for third-party audit of omissions | 11 Research | mo-relay + mo-web | R | NEW:MON-03 | todo |
| T-11-045 | Research: prefix-delta (upload p50 > 150 ms or egress top-3) | 11 Research | mo-proto + mo-relay + mo-node | R | NEW:MON-03 | todo |
| T-11-046 | Research: blue/green deploys (deploy-caused failures visible) | 11 Research | mo-relay + mo-ops* | R | NEW:MON-03 | todo |
| T-11-047 | Research: trust tiers / auto-approval of donors (owners ask for less manual approval) | 11 Research; 12 §2 | mo-relay + mo-node | R | NEW:MON-03 | todo |
| T-11-048 | Research: regional Edges (p50 added latency > 100 ms for > 25% of traffic) | 11 Research | mo-relay + mo-ops* | R | NEW:MON-03 | todo |
| T-11-049 | Research: local-model donors (GPU, vLLM/Ollama) with token-based goal display | 11 Research | mo-worker + mo-web | R | NEW:MON-03 | todo |
| T-11-050 | Research: cross-dialect translation (dialect mismatch > 10% unserved) | 11 Research; ADR-19 | mo-node + mo-worker | R | NEW:MON-03 | todo |
| T-11-051 | Research: stream resume after Gateway reconnect (mid-stream disconnects > 0.5%) | 11 Research | mo-relay + mo-node | R | NEW:MON-03 | todo |
| T-11-052 | Research: direct peer transport / NAT traversal (egress top-3 or latency gain) | 11 Research; ADR-27 | mo-node + mo-relay | R | NEW:MON-03 | todo |
| T-11-053 | Verification: golden vectors in both CIs | 11 §3 | mo-proto + mo-relay | 0 | NEW:CI-01 | todo |
| T-11-054 | Verification: Scheduler pure core + invariants after every event + seeded simulation in CI | 11 §3 | mo-relay | 2 | NEW:CI-04 | todo |
| T-11-055 | Verification: ledger property tests (reserve/settle/release sequences), nightly prod audit, provider reconciliation | 11 §3 | mo-relay + mo-node | 1/2 | NEW:CI-10, NEW:E68, NEW:CI-20 | todo |
| T-11-056 | Verification: fuzzing (firewall, frames, SSE parser, MCP paths), red-team corpora (firewall, tripwire), canary no-content test | 11 §3 | mo-worker + mo-proto + mo-node + mo-sec | 1/3 | NEW:CI-03, NEW:CI-13, NEW:CI-14, E13 | todo |
| T-11-057 | Verification: one-command integration harness (Relay + Nodes + fake providers) with happy path, failover, cancel, outbox replay, upgrade during load | 11 §3 | mo-e2e | 1/2 | E01, E06, E08, E12, NEW:E33 | todo |
| T-11-058 | Verification: nightly staging run with real providers and tiny budgets — one real agent session per supported harness | 11 §3 | mo-ops* + mo-e2e* | 2 | NEW:CI-20 | todo |
| T-11-059 | Verification: benchmarks with regression budgets (Scheduler apply, frame forwarding, seal/open throughput); periodic load tests | 11 §3 | mo-relay + mo-proto | 2 | NEW:CI-06, NEW:CI-19 | todo |
| T-11-060 | Verification: web template snapshot tests, accessibility checks, SSE load test | 11 §3 | mo-web | 4 | NEW:CI-09 | todo |
| T-11-061 | Definition of done for any feature: its exit criterion is automated (test, simulator scenario, or monitored metric) | 11 §3 | integrator | — | this file | todo |
| T-11-062 | Launch: counsel sign-off on terms and per-provider guidance | 11 §5 | human-counsel* | 6 | NEW:REV-01 | todo |
| T-11-063 | Launch: Phase 1–6 exit criteria all automated and green | 11 §5 | integrator | 6 | this file | todo |
| T-11-064 | Launch: public threat model, protocol spec, self-host guide published | 11 §5 | mo-sec + integrator + mo-docs* | 6 | NEW:REV-02 | todo |
| T-11-065 | Launch: onboarding enforces device caps and promotes provider-side spend limits | 11 §5 | mo-node | 1 | NEW:E81 | todo |
| T-11-066 | Launch: status page and incident contact | 11 §5 | human-po* + mo-ops* | 6 | NEW:REV-06 | todo |
| T-11-067 | Launch: `/open` page live (license, source, self-host guide, monthly costs, sponsors) | 11 §5 | mo-web + human-po* | 4 | NEW:E64 | todo |
| T-11-068 | Launch: key log live with hourly public Git anchoring | 11 §5 | mo-relay + mo-ops* | 3 | NEW:E42 | todo |
| T-11-069 | Launch: public beta never runs with relay-asserted keys or approvals (Phase 1 dev shortcuts compiled out or refused outside `--dev`) | 11 §5 | mo-relay + mo-node | 6 | NEW:E41 | todo |
| T-11-070 | Launch: 10 design-partner repos and 50 donors recruited before opening sign-ups | 11 §5 | human-po* | 6 | NEW:REV-06 | todo |

## 12 — Decisions, rejected ideas, open questions

ADRs are binding design constraints; each row points to the canonical rows that implement it.

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-12-001 | ADR-01 everything open source, Apache-2.0 OR MIT (→ T-00-001) | ADR-01 | integrator | 0 | NEW:CI-18 | todo |
| T-12-002 | ADR-02 free forever, no paid verified mode, never hold money (→ T-00-002) | ADR-02 | human-po* | — | NEW:REV-02 | todo |
| T-12-003 | ADR-03 µ$ int64 unit of account (→ T-05-001) | ADR-03 | mo-relay + mo-worker | 1 | NEW:CI-10 | todo |
| T-12-004 | ADR-04 two doors, one pipeline (→ T-07-025…T-07-058) | ADR-04 | mo-node | 1 | E01, E04, E05 | todo |
| T-12-005 | ADR-05 one Node process per machine with thin front-ends (→ T-07-002) | ADR-05 | mo-node | 1 | NEW:E72 | todo |
| T-12-006 | ADR-06 actor Scheduler, sheddable submit / never-blocking lifecycle queue, `sync.Map` only for forwarding; revisit at p99 > 200 µs or > 50k events/s | ADR-06 | mo-relay | 1 | NEW:CI-04, NEW:MON-01 | todo |
| T-12-007 | ADR-07 sealed envelopes: fresh CK per body, HPKE wraps, Worker-salted per-attempt RK (→ T-03-061…T-03-075) | ADR-07 | mo-proto | 1 | NEW:CI-01 | todo |
| T-12-008 | ADR-08 Gateway-signed tasks; Workers accept only owner-approved members, fresh, never-seen ids (→ T-03-085…T-03-090) | ADR-08 | mo-node | 1→3 | E16, NEW:E41 | todo |
| T-12-009 | ADR-09 Ed25519 (ZIP-215) + X25519 per device; no GPG; `lp` labels | ADR-09 | mo-proto | 1 | NEW:CI-01 | todo |
| T-12-010 | ADR-10 OS keychain + encrypted-file / systemd-creds fallback | ADR-10 | mo-node | 1/5 | NEW:E71 | todo |
| T-12-011 | ADR-11 signatures = accountability: donor receipts, signed checkpoints per tool call, signed disputes; countersigning only if leaderboard fraud appears | ADR-11 | mo-node + mo-worker | 3 | NEW:E43, NEW:E44 | todo |
| T-12-012 | ADR-12 owner-signed approvals in a Node-mirrored key log with Git anchor (→ T-06-080…T-06-091) | ADR-12 | mo-relay + mo-node | 3 | NEW:E41 | todo |
| T-12-013 | ADR-13 public receipt projections only (→ T-03-115) | ADR-13 | mo-proto + mo-web | 1/4 | NEW:E66 | todo |
| T-12-014 | ADR-14 strict recursive allowlist firewall incl. headers; only the listed safe mutations (attribution id, model mapping, stream usage, `store:false`) | ADR-14 | mo-worker | 1 | E09, NEW:E54 | todo |
| T-12-015 | ADR-15 money durability rules (FULL, ack after commit, commit before assign, release only on proof, outbox 7 days, start-period attribution) | ADR-15 | mo-relay + mo-node | 1 | E12, NEW:E36 | todo |
| T-12-016 | ADR-16 three-layer caps with Worker local reservations per device | ADR-16 | mo-worker + mo-node | 1 | E11 | todo |
| T-12-017 | ADR-17 affinity aligned with cache TTL, HMAC key under per-device secret | ADR-17 | mo-relay + mo-node | 2 | NEW:E28 | todo |
| T-12-018 | ADR-18 OpenRouter-style slugs, native ids accepted, signed catalog mapping | ADR-18 | mo-relay + mo-node + mo-worker | 1 | NEW:E39 | todo |
| T-12-019 | ADR-19 no cross-dialect translation; OpenRouter and DeepSeek serve both dialects; revisit at > 10% unserved | ADR-19 | mo-worker | 1 | E03, NEW:MON-03 | todo |
| T-12-020 | ADR-20 no hedged requests, no failover after start | ADR-20 | mo-relay | 1 | E06, NEW:CI-04 | todo |
| T-12-021 | ADR-21 prefix-delta deferred (→ T-03-093) | ADR-21 | mo-relay | D | NEW:MON-03 | todo |
| T-12-022 | ADR-22 drain-and-restart deploys in v1 (→ T-10-010) | ADR-22 | mo-relay | 2 | NEW:E33 | todo |
| T-12-023 | ADR-23 `count_tokens` answered locally (→ T-07-026) | ADR-23 | mo-node | 1 | NEW:E51 | todo |
| T-12-024 | ADR-24 Go stdlib `ServeMux`; Rust `serde_json` (subject to CONTRACT §1 strict-parse rule) | ADR-24 | mo-relay + mo-node | 1 | NEW:CI-02, NEW:E24 | todo |
| T-12-025 | ADR-25 single-node relay; partition by repo later | ADR-25 | mo-relay | — | NEW:MON-03 | todo |
| T-12-026 | ADR-26 no content moderation at the relay | ADR-26 | mo-relay | — | E13 | todo |
| T-12-027 | ADR-27 no direct peer-to-peer transport in v1 | ADR-27 | mo-node | — | NEW:REV-02 | todo |
| T-12-028 | ADR-28 presence aggregated by default; per-donor display opt-in | ADR-28 | mo-web | 4 | NEW:E66 | todo |
| T-12-029 | ADR-29 API keys only; consumer credentials refused | ADR-29 | mo-worker | 1 | NEW:E58 | todo |
| T-12-030 | ADR-30 never host donor keys; no relay-hosted MCP; self-tunnel opt-in Phase 5 | ADR-30 | mo-relay + mo-node | — | NEW:REV-02, NEW:E85 | todo |
| T-12-031 | ADR-31 public repositories only on the public instance | ADR-31 | mo-relay | 1 | NEW:E63 | todo |
| T-12-032 | ADR-32 durations, deadlines, weights are configuration values with documented defaults | ADR-32 | mo-relay + mo-node | 1 | NEW:E80 | todo |
| T-12-033 | Rejected (must not appear): crypto tokens / on-chain ledger; Moochy-run cloud workers holding keys; relay-hosted MCP/API; relay moderation; hedging / failover after start / stream splicing; GPG; lock-free multi-index registry; `moochy self-verify` | 12 §2 | integrator | — | NEW:REV-02 | todo |
| T-12-034 | Deferred (tracked, not built): trust tiers/auto-approval, countersigning, receipt log + witnesses + browser verifier, prefix-delta, blue/green, stream resume, federation, cross-dialect, email notifications | 12 §2 | integrator | D | NEW:MON-03 | todo |
| T-12-035 | Q1: license wording + DCO (recommended) decided before first external contribution | 12 Q1 | human-po* | 0 | NEW:REV-02 | todo |
| T-12-036 | Q2: private repos on public instance — recommended no | 12 Q2 | human-po* | 5 | NEW:REV-02 | todo |
| T-12-037 | Q3: which providers get a counsel "go" | 12 Q3 | human-counsel* | 0 | NEW:REV-01 | todo |
| T-12-038 | Q4: which IDEs reach a loopback base URL; which MCP clients send roots, honor progress, allow longer timeouts → encoded in matrix + `connect` | 12 Q4 | mo-e2e* + mo-node | 0 | NEW:CI-20 | todo |
| T-12-039 | Q5: exact Anthropic-compatible endpoints and usage fields for OpenRouter and DeepSeek | 12 Q5 | mo-worker | 0 | NEW:CI-17 | todo |
| T-12-040 | Q6: public instance region | 12 Q6 | human-po* | 1 | NEW:REV-06 | todo |
| T-12-041 | Q7: governance — two maintainers with hardware tokens hold log/catalog keys; Open Collective fiscal host; `GOVERNANCE.md` | 12 Q7 | human-po* + mo-docs* | 6 | NEW:REV-02 | todo |
| T-12-042 | Q8: task metadata retention 90 days raw, aggregates forever (→ T-06-093) | 12 Q8 | human-po* | 1 | NEW:E83 | todo |
| T-12-043 | Q9: default per-member quota 20% and per-task cap $5, editable | 12 Q9 | human-po* | 2 | NEW:E30, E10 | todo |
| T-12-044 | Q10: donors restricting which members use their pledge — not in v1, revisit | 12 Q10 | human-po* | 4 | NEW:REV-02 | todo |
| T-12-045 | Q11: project name check with design partners | 12 Q11 | human-po* | 0 | NEW:REV-06 | todo |

## 13 — Review log (regression guards)

Every accepted or adapted finding is a fix that must stay fixed. Each row names the guard; the mechanism is in the canonical row cited.

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-13-001 | Pass 0: open-source monorepo, free forever, MCP first-class door, OpenRouter + DeepSeek first-class in Phase 1 stay true (→ T-00-001, T-00-002, T-07-048, T-07-063, T-07-064) | 13 P0 | integrator | 1 | E02, E03, E04 | todo |
| T-13-002 | Pass 1 + 5 doc consistency: every `[NN §X]` reference resolves; shared parameters (ACK 500 ms, start 30 s, routing 5 s after last body frame, ≤ 8 wraps, ≤ 3 attempts, ±10 min, 7-day outbox, `synchronous=FULL`, $5 cap, 90-day retention) identical across plan, contract, and code defaults | 13 P1, P5 | integrator | — | NEW:CI-18 | todo |
| T-13-003 | 2.1/3.1/4.1 (critical): no key/nonce reuse — fresh CK per body, Worker-salted RK, attempt + R in AAD, accepted-attempt-only decrypt, abort on second started stream, distinct-key vector | 13 2.1 | mo-proto + mo-node | 1 | NEW:CI-01, NEW:E47 | todo |
| T-13-004 | 2.2 (critical): relay cannot invent an approved donor — owner-signed claims/approvals/memberships, sealing only to owner-approved keys, owner alerts, Git anchor | 13 2.2 | mo-node + mo-relay | 3 | NEW:E41, NEW:E42 | todo |
| T-13-005 | 2.3: task authenticity — Gateway task signature, `repo_id` in route header, membership, pledge↔repo, ULID freshness, served set | 13 2.3 | mo-node | 1→3 | E16, NEW:E41, NEW:E56 | todo |
| T-13-006 | 2.4: poisoned tool call before any signature impossible — signed progress checkpoints gate release | 13 2.4 | mo-node + mo-worker | 3 | NEW:E44 | todo |
| T-13-007 | 2.5: MCP `files` hardening (recorded root ∩ roots, realpath, no symlinks, deny lists, `git check-ignore`) | 13 2.5 | mo-node | 3 | NEW:E46 | todo |
| T-13-008 | 2.6: no under-counting — stream usage forced; estimated receipts settle at reservation | 13 2.6 | mo-worker + mo-relay | 1 | E02, NEW:E35 | todo |
| T-13-009 | 2.7: deterministic exact estimate; PDFs behind a flag; overage bound restated; Worker local reservations per device | 13 2.7 | mo-worker + mo-node | 1 | E11, NEW:E55 | todo |
| T-13-010 | 2.8: headers sealed + allowlisted; OpenAI `n`, predictions, service tier, audio, web-search denied; OpenRouter routing/plugins/variants denied + max-price; recursive validation + fuzzing | 13 2.8 | mo-worker | 1 | NEW:E55, NEW:CI-03 | todo |
| T-13-011 | 2.9: tripwire covers OpenAI `tool_calls`; name + schema checks; forbidden block types; model match; MCP results framed untrusted | 13 2.9 | mo-node + mo-worker | 3 | E18, NEW:E79 | todo |
| T-13-012 | 2.10: auth signs dialed origin + TLS exporter inside `lp` | 13 2.10 | mo-node + mo-relay | 1 | NEW:E21 | todo |
| T-13-013 | 2.11: projections hide device ids and fine timestamps; affinity key is an HMAC | 13 2.11 | mo-proto + mo-node | 1/2 | NEW:E66, NEW:E28 | todo |
| T-13-014 | 2.12: `connect --write` never commits tokens; token rotation; port held by service manager; `doctor` uid check | 13 2.12 | mo-node | 1/5 | NEW:E73, NEW:E74, NEW:E81 | todo |
| T-13-015 | 2.13 (adapted): plausibility checks live in dispute rules | 13 2.13 | mo-node | 3 | NEW:E43 | todo |
| T-13-016 | 2.14: `lp` labels, HKDF-derived salts/keys, ZIP-215 vectors, suite id in HPKE info and `KEY_ADDED`, monotonic catalog | 13 2.14 | mo-proto + mo-relay | 1 | NEW:CI-01, NEW:E39 | todo |
| T-13-017 | 2.15 (adapted): tlog path layer own or Tessera; `hpke` under `cargo-vet`; client-executed computer use allowed | 13 2.15 | mo-relay + mo-release* + mo-worker | 3 | NEW:CI-08, NEW:CI-13 | todo |
| T-13-018 | 3.2 (critical): receipts and reservations per attempt; release only on proof of zero spend; "started" = provider headers; no failover after start | 13 3.2 | mo-relay | 1 | E06, E07, NEW:E26 | todo |
| T-13-019 | 3.3: `synchronous=FULL`; ack after commit; checkpoints only for replicated sizes; 7-day outbox; `replay_since` | 13 3.3 | mo-relay + mo-node | 1/2 | E12, NEW:E34 | todo |
| T-13-020 | 3.4: commit-before-assign; Workers abort + receipt on link loss; `known_tasks` releases orphans; pessimistic only for long-absent Workers | 13 3.4 | mo-relay + mo-node | 1 | E12, NEW:E32 | todo |
| T-13-021 | 3.5 (adapted): deploy handoff safe via drain-and-restart; blue/green requirements recorded | 13 3.5 | mo-relay | 2 | NEW:E33 | todo |
| T-13-022 | 3.6: Worker device cap counts reservations, not only settled spend; Relay decrements `local_cap_left` | 13 3.6 | mo-worker + mo-relay | 1 | E11 | todo |
| T-13-023 | 3.7: start-period attribution; boot applies missed rollovers; SAVEPOINT per op; constraint violation fatal + replay | 13 3.7 | mo-relay | 1 | NEW:E36, NEW:E68 | todo |
| T-13-024 | 3.8: cancel on Gateway disconnect; dedupe per `(gateway_device, task_id)`; resubmission rules; source-checked forwarding | 13 3.8 | mo-relay | 2 | NEW:E31, NEW:E48, NEW:E23 | todo |
| T-13-025 | 3.9: sheddable submit queue, never-blocking lifecycle queue, slice-swap writer, separate completion channel | 13 3.9 | mo-relay | 2 | NEW:E49, NEW:CI-04 | todo |
| T-13-026 | 3.10: presence keyed by `(device, session)` | 13 3.10 | mo-relay | 2 | NEW:E22 | todo |
| T-13-027 | 3.11: device caps have counters (`device_usage`), state, invariants, audit | 13 3.11 | mo-relay | 2 | NEW:E30, NEW:E68 | todo |
| T-13-028 | 3.12: 24 h waits are SQL sweeps; Edge byte budgets | 13 3.12 | mo-relay | 2 | NEW:E35, NEW:E49 | todo |
| T-13-029 | 3.13 (adapted): migrations with no second writer; `min_compatible_version`; long index builds after boot | 13 3.13 | mo-relay | 2 | NEW:E67 | todo |
| T-13-030 | 3.14: non-retryable `over_task_cap`, `quota_exceeded`, `model_not_in_pool`; default cap $5 with console visibility | 13 3.14 | mo-relay + mo-node + mo-web | 2 | E10, NEW:E27 | todo |
| T-13-031 | 3.15: ≈ 200 starts/s math; 65,497-byte chunks; exact estimate; late-message rule; routing deadline from last body frame; `wal_autocheckpoint=0` | 13 3.15 | mo-relay + mo-proto | 1/2 | NEW:CI-01, NEW:E26, NEW:E67 | todo |
| T-13-032 | 4.2: v1 trust layer = one key log + Git anchor + projections + CLI verification + disputes (receipt log, witnesses, countersign, browser verifier deferred) | 13 4.2 | mo-relay + mo-node | 3 | NEW:E40, NEW:E61 | todo |
| T-13-033 | 4.3: OpenRouter and DeepSeek adapters serve both dialects | 13 4.3 | mo-worker | 1 | E03 | todo |
| T-13-034 | 4.4: slugs from Phase 1; native ids accepted; `connect` sets main and small models | 13 4.4 | mo-node + mo-relay | 1 | NEW:E39, NEW:E73 | todo |
| T-13-035 | 4.5: MCP door robust to optional client features (roots fallback, timeout budget, model enum, `instructions`, "where supported") | 13 4.5 | mo-node | 1 | E04, NEW:E79 | todo |
| T-13-036 | 4.6: prefix-delta deferred with metric trigger | 13 4.6 | mo-relay | D | NEW:MON-03 | todo |
| T-13-037 | 4.7: settle on OpenRouter reported cost bounded by reservation; stream usage forced | 13 4.7 | mo-worker + mo-relay | 1 | E02, NEW:E38 | todo |
| T-13-038 | 4.8: open-source/free wording without holes; `draft-spec.md` unmodified | 13 4.8 | integrator + mo-web | 0 | NEW:REV-02 | todo |
| T-13-039 | 4.9: drain-and-restart in v1, blue/green metric-triggered | 13 4.9 | mo-relay | 2 | NEW:E33 | todo |
| T-13-040 | 4.10: remote-HTTPS-only MCP clients stated in matrix; self-tunnel Phase 5 | 13 4.10 | mo-node + mo-docs* | 5 | NEW:E85 | todo |
| T-13-041 | 4.11: no trust tiers / auto-approve / tier header; pinned donors; tripwire = speed bump | 13 4.11 | mo-node + mo-relay | 3 | NEW:E41, NEW:CI-14 | todo |
| T-13-042 | 4.12: no self-verify; reproducible Linux musl builds for beta | 13 4.12 | mo-release* | 3 | NEW:CI-08 | todo |
| T-13-043 | 4.13: reconciliation method per provider | 13 4.13 | mo-node | 1/2 | NEW:CI-20 | todo |
| T-13-044 | 4.14: `count_tokens` local | 13 4.14 | mo-node | 1 | NEW:E51 | todo |
| T-13-045 | 4.15: telemetry opt-in everywhere; NACK details sealed; browser verifier deferred | 13 4.15 | mo-node + mo-worker | 1 | E09, NEW:E80 | todo |

