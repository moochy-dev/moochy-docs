# Moochy — Requirements Traceability Matrix

Owner: `mo-trace`. Source of truth for "is everything in `docs/plan/*.md` implemented?". Every concrete requirement of the 14 plan documents (00 → 13), plus the requirements that exist only in `spec/CONTRACT.md` (incl. §11–§13), `spec/proto/moochy/v1/link.proto`, and `AGENTS.md`, has exactly one row here. Deferred and research items are included and flagged; they are still in scope for later waves.

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

- `E01`–`E22`: CONTRACT §8 and §13 scenarios (E21 unique usernames, E22 responsiveness budgets).
- `NEW:E23`…`NEW:E89`: proposed E2E scenarios, defined in §B.1.
- `NEW:CI-nn`: proposed automated non-E2E checks (vectors, fuzz, simulator, benchmarks, lint, build), §B.2.
- `NEW:MON-nn`: verified by an exported metric + tested alert/SLO rule, §B.3.
- `NEW:REV-nn`: human/document deliverable with a recorded sign-off, §B.4.
- `A-…`: attack-catalog ids. `docs/security/attack-catalog.md` does not exist on `main` yet; when it lands, `mo-sec` ids are added next to the E-ids of rows in 06 §3 and 03 §7.

Status: every row starts `todo`. `superseded` = replaced by a later contract decision (ADR-33/34); the row stays for history and points to its replacement.

---

## 00 — PLAN (master index)

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-00-001 | Everything (relay, client, spec, docs) is open source, one public monorepo, dual-licensed Apache-2.0 OR MIT (root license files + per-crate/module license metadata) | 00 header; 01 §3.1 | integrator + mo-docs* | 0 | NEW:CI-18 | todo |
| T-00-002 | 100% free: no fees, no commission, no paid tier, no feature gating, Moochy never holds money; nothing in code or UI implies custody | 00 header; 01 §3.2; 05 §8 | human-po* | — | NEW:REV-02 | todo |
| T-00-003 | Works with any MCP client/agent and any tool with a base URL; donors on Anthropic, OpenRouter, DeepSeek, OpenAI, vetted OpenAI-compatible hosts | 00 header | mo-node + mo-worker | 1–5 | E01, E02, E03, E04, E05, NEW:E78, NEW:CI-20 | todo |
| T-00-004 | `draft-spec.md` stays unchanged; the plan supersedes it (its closed-source section is void) | 00 status | integrator | 0 | NEW:REV-02 | todo |
| T-00-005 | First artifacts written are the cross-language golden vectors in `spec/vectors/` | 00 §5 | mo-proto | 0 | NEW:CI-01 | todo |
| T-00-006 | Idea 1–17 table (µ$, sealed body + wraps, per-attempt keys, route header AAD + task sig, affinity, P2C, actor + commit-before-assign, outbox, owner-signed key log, signed checkpoints, disputes, projections, recursive firewall, MCP `files`, three-layer caps, native errors, README badge) is fully implemented — each idea is traced in its canonical doc section below | 00 §2 | integrator | 1–4 | rows of 03–08 | todo |
| T-00-007 | Glossary terms are used consistently in code identifiers and user-facing text (Node, Gateway, Worker, Relay, Door, Dialect, Pledge, Approval, Pool, Attempt, Route header, Envelope, Receipt, Projection, Dispute, Progress checkpoint, Reservation, Affinity, Firewall, Tripwire, Key log, µ$) | 00 §4 | integrator | — | NEW:REV-02 | todo |

## 01 — Vision, scope, and draft review

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-01-001 | Principle "works with anything": MCP door for any MCP client, API door for any base-URL tool, all major providers on the donor side | 01 §3.3 | mo-node | 1–5 | E01, E04, E05, NEW:CI-20 | todo |
| T-01-002 | Principle "trust no operator": confidentiality and integrity are enforced cryptographically in the client, never by trusting the relay | 01 §3.4 | mo-proto + mo-node + mo-worker | 1→3 | E13, E15, E16, E17 | todo |
| T-01-003 | Principle "donated money is sacred": cache affinity, cancellation propagation, no hedging, budget-proportional routing | 01 §3.5 | mo-relay | 2 | E08, NEW:E30, NEW:E33 | todo |
| T-01-004 | Principle "boring infrastructure": one Go binary + one SQLite file + one Rust binary; no queue, cache cluster, or microservice | 01 §3.6 | mo-relay + mo-node | — | NEW:REV-02, NEW:CI-07 | todo |
| T-01-005 | I1: a provider API key never leaves the donor's machine (keystore + Worker-only use, sent only to allowlisted provider hosts) | 01 §4 I1 | mo-node + mo-worker | 1 | E13, NEW:E61 | todo |
| T-01-006 | I2: the relay cannot read prompts or outputs | 01 §4 I2 | mo-proto + mo-node | 1 | E13, E17 | todo |
| T-01-007 | I3: a donor never spends more than their caps (bounded by open-attempt overages) | 01 §4 I3 | mo-relay + mo-worker | 1 | E10, E11 | todo |
| T-01-008 | I4: a donor's account never executes anything server-side or touches account data for a maintainer | 01 §4 I4 | mo-worker | 1 | E09, NEW:E57 | todo |
| T-01-009 | I5: every unit of spend has a donor-signed receipt checked by the Gateway (signed dispute on mismatch) and a donor-signed projection; every executed tool call carries a donor signature | 01 §4 I5 | mo-node + mo-worker + mo-relay | 1→3 | E01, NEW:E45, NEW:E46 | todo |
| T-01-010 | I6: maintainers' tools work unmodified (two doors) | 01 §4 I6 | mo-node | 1 | E01, E04, E05, NEW:CI-20 | todo |
| T-01-011 | I7: no personal data in the append-only log (pseudonyms + salted commitments) | 01 §4 I7 | mo-relay | 3 | NEW:E42 | todo |
| T-01-012 | I8: no silent spend — every cent is in the donor's local journal | 01 §4 I8 | mo-node + mo-worker | 1 | NEW:E62 | todo |
| T-01-013 | I9: the relay can neither invent a donor, member, or key, nor originate or replay a task, without published evidence | 01 §4 I9 | mo-node + mo-worker + mo-relay | 1→3 | E15, E16, NEW:E43 | todo |
| T-01-014 | Goal: donors pledge µ$ budgets to public repos using Anthropic, OpenRouter, DeepSeek, or OpenAI keys | 01 §5.1 | mo-relay + mo-web + mo-node | 1–4 | E01, E02, E03, NEW:E78 | todo |
| T-01-015 | Goal: maintainers and members consume through MCP or provider-compatible APIs from any client | 01 §5.1 | mo-node | 1 | E01, E04, E05 | todo |
| T-01-016 | Goal: real-time public pages, README badges, verifiable receipts | 01 §5.1 | mo-web + mo-node | 4 | E19, NEW:E63, NEW:E66 | todo |
| T-01-017 | Goal: self-hostable relay with a documented recipe | 01 §5.1 | mo-ops* + mo-docs* | 6 | NEW:REV-02, NEW:CI-21 | todo |
| T-01-018 | Non-goal: no payments, escrow, crypto tokens, or money flow | 01 §5.2 | human-po* | — | NEW:REV-02 | todo |
| T-01-019 | Non-goal: never host donor keys or run inference on Moochy servers | 01 §5.2 | mo-relay | — | NEW:REV-02, E13 | todo |
| T-01-020 | Non-goal: no arbitrary compute (shell, containers, binaries) | 01 §5.2 | mo-worker | — | E09, NEW:E57 | todo |
| T-01-021 | Non-goal: no content moderation by the relay | 01 §5.2 | mo-relay | — | E13 | todo |
| T-01-022 | Non-goal: no private repositories on the public instance (v1); repo claim of a private repo is refused when the instance is configured public-only | 01 §5.2; 06 §5 | mo-relay | 1 | NEW:E65 | todo |
| T-01-023 | Non-goal: no cross-dialect request translation (v1) | 01 §5.2 | mo-relay + mo-node | — | NEW:E29 | todo |
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
| T-01-034 | Draft per-repo `mcp_secret` dropped: no shared secret stored server-side; device-key handshake instead | 01 §6; 03 §3 | mo-relay | 1 | NEW:E23 | todo |
| T-01-035 | Ed25519 only; no GPG/OpenPGP anywhere | 01 §6 | mo-proto | 1 | NEW:CI-07 | todo |
| T-01-036 | Models never hard-coded: signed, versioned catalog fed from provider model lists | 01 §6; 05 §2 | mo-relay + mo-node | 1→3 | NEW:E41 | todo |
| T-01-037 | Draft verdict: public presence aggregated, per-node RTT/"verified" panel removed; honest verification via `moochy verify` | 01 §6 | mo-web + mo-node | 4 | NEW:E68, NEW:E63 | todo |

## 02 — Architecture overview

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-02-001 | Relay **Edge**: TLS 1.3 termination in-process (autocert in prod; cert/key flags for tests), gRPC `NodeLink` server on its own listener (`--grpc-addr`), per-HTTP/2-connection device auth, per-task stream handling, data-plane forwarding | 02 §3.1; CONTRACT §12 | mo-relay | 1 | E01, NEW:E23 | todo |
| T-02-002 | Relay **Scheduler**: single goroutine owning all routing and budget state (workers, pledges, pools, affinity, in-flight) | 02 §3.1; 04 §1 | mo-relay | 1 | NEW:CI-04 | todo |
| T-02-003 | Relay **Ledger**: pure accounting rules (cost, reservation math, settlement) + persistence; no in-memory state of its own | 02 §3.1 | mo-relay | 1 | NEW:CI-10 | todo |
| T-02-004 | Relay **Key log** component: append entries, tree hashes, checkpoints only for replicated sizes, hourly Git anchor, tile serving | 02 §3.1; 06 §10 | mo-relay | 3 | NEW:E42, NEW:E44 | todo |
| T-02-005 | Relay **Identity**: GitHub/GitLab OAuth, device-approval flow, repo-claim verification; users, identities, devices, sessions | 02 §3.1 | mo-relay | 1/5 | NEW:E65 | todo |
| T-02-006 | Relay **Web**: HTMX pages, SSE hub (render once, fan out), badges, public verification pages | 02 §3.1 | mo-web | 4 | E19, NEW:E66, NEW:E67 | todo |
| T-02-007 | Relay **Store**: one writer goroutine with group commit, read-only connection pool, embedded forward-only migrations | 02 §3.1; 09 §2 | mo-relay | 1 | NEW:E69, E12 | todo |
| T-02-008 | Relay **Catalog**: versioned price/model catalog, signed, published to Nodes | 02 §3.1; 05 §2 | mo-relay | 1→3 | NEW:E41 | todo |
| T-02-009 | Node **Relay link**: one gRPC HTTP/2 connection = one authenticated session; reconnect with jittered backoff; channel rebuilt and re-authenticated on any transport error | 02 §3.2; CONTRACT §12 | mo-node | 1 | E01, E12, NEW:E35 | todo |
| T-02-010 | Node **Keystore**: Ed25519 signing key, X25519 encryption key, provider keys; OS keychain + encrypted-file fallback | 02 §3.2; 06 §4 | mo-node | 1/5 | NEW:E73, NEW:CI-16 | todo |
| T-02-011 | Node **Gateway**: loopback provider APIs, repo-scoped tokens, affinity key, task signing, compression + sealing to owner-approved donors, scrubber, tool-call checks, native errors, receipt checks + disputes, optional own-key fallback | 02 §3.2; 07 §4 | mo-node | 1→3 | E01, E14, E18, NEW:E45 | todo |
| T-02-012 | Node **MCP server**: stdio (`moochy mcp`, forwards to running Node over local socket) + Streamable HTTP on loopback; same tools | 02 §3.2; 07 §5 | mo-node | 1 | E04, E05 | todo |
| T-02-013 | Node **Worker**: slot grants, envelope opening, firewall, adapters with warm pools, usage extraction, cancellation, local caps, receipt signing, outbox | 02 §3.2; 07 §6 | mo-worker + mo-node | 1 | E01, E09, E11, E12 | todo |
| T-02-014 | Node **Monitor**: mirror key log, check checkpoint consistency and Git anchor, alert on unknown own-account keys and (owners) unsigned claims/approvals/memberships | 02 §3.2; 06 §10 | mo-node | 3 | NEW:E42, NEW:E43, NEW:E44 | todo |
| T-02-015 | Node **Local journal**: append-only record of every task served or consumed (metadata always, full text opt-in) | 02 §3.2; 07 §6.5 | mo-node | 1 | NEW:E62 | todo |
| T-02-016 | Trust boundary: relay sees routing metadata only; donor output is treated as UNTRUSTED by the Gateway | 02 §4 | mo-node | 1→3 | E13, E18 | todo |
| T-02-017 | Primary flow sequence (submit → schedule → reserve → commit → assign → ack → accepted → started → chunks → end → settle → receipt.ack → Gateway check → dispute on mismatch) implemented end to end | 02 §5 | mo-relay + mo-node + mo-worker | 1 | E01 | todo |
| T-02-018 | `moochy_delegate` builds the same request inside the Node and follows the identical pipeline from signing onward | 02 §5 | mo-node | 1 | E04 | todo |
| T-02-019 | Money settles on the donor-signed receipt; public feed shows the donor-signed projection (daily granularity, no device ids) | 02 §5 | mo-relay + mo-web | 1/4 | E01, E19, NEW:E68 | todo |
| T-02-020 | Secondary flow: device login (keys created, code + URL, browser approval, `KEY_ADDED`, device id returned) | 02 §6 | mo-node + mo-relay + mo-web | 1→3 | E01 (login step), NEW:E65, NEW:E42 | todo |
| T-02-021 | Secondary flow: repo claim (OAuth admin check at claim time, token not stored, owner's Node signs `REPO_CLAIMED`) | 02 §6; 06 §5 | mo-relay + mo-node | 1→3 | NEW:E65, NEW:E84 | todo |
| T-02-022 | Secondary flow: pledge (repo, budget µ$, per-task cap, models, max effort, schedule → owner signs `DONOR_APPROVED` → Scheduler indexes → Gateways may seal) | 02 §6 | mo-web + mo-relay + mo-node | 1→3 | NEW:E39, NEW:E84 | todo |
| T-02-023 | Secondary flow: reclaim / pause stops new reservations at once; in-flight settle; unspent released | 02 §6; 05 §8 | mo-relay | 2 | NEW:E39 | todo |
| T-02-024 | Secondary flow: settlement recovery (Workers abort + receipt on relay loss, `known_tasks`, outbox replay, idempotent by `(task_id, attempt)`, orphans released) | 02 §6; 05 §7 | mo-relay + mo-worker + mo-node | 1 | E12, NEW:E34 | todo |
| T-02-025 | Secondary flow: log monitoring by every Node | 02 §6 | mo-node | 3 | NEW:E42, NEW:E44 | todo |
| T-02-026 | Control plane = one goroutine (actor); data plane = `sync.Map` forwarding table `task_id → destination`, one lookup + one channel send per chunk | 02 §7 | mo-relay | 1 | NEW:CI-06 | todo |
| T-02-027 | Control-plane latency target p99 < 50 µs per event at 10k online workers | 02 §7 | mo-relay | 2 | NEW:CI-06 | todo |
| T-02-028 | Deployment: one process, one SQLite file, Litestream sidecar; no reverse proxy, Redis, or queue | 02 §8 | mo-ops* + mo-relay | 1 | NEW:REV-02, NEW:CI-21 | todo |
| T-02-029 | TLS via ACME autocert inside the Go process | 02 §8; 10 §2 | mo-relay | 6 | NEW:CI-21 | todo |
| T-02-030 | Litestream continuous WAL shipping (RPO ≈ 1 s DB, 0 for spend) | 02 §8; 09 §7 | mo-ops* | 1 | NEW:CI-21, NEW:E36 | todo |
| T-02-031 | Deploys drain-and-restart (≤ 30 s drain, ~10 s retryable errors, zero drift); blue/green deferred | 02 §8; 10 §3 | mo-relay + mo-ops* | 2 | NEW:E35 | todo |
| T-02-032 | Log tiles immutable once full, CDN-cacheable | 02 §8; 09 §3.5 | mo-relay | 3 | NEW:E42 | todo |
| T-02-033 | Go relay stack: stdlib `net/http` ServeMux, `google.golang.org/grpc` + `protobuf` (replaces `coder/websocket`, ADR-33), `modernc.org/sqlite`, `x/mod/sumdb/tlog`+`note` (C2SP tiles), `x/oauth2` | 02 §9; ADR-33; AGENTS §4 | mo-relay | 1/3 | NEW:CI-02 | todo |
| T-02-034 | Frontend: `html/template` + HTMX 2 + `htmx-ext-sse`, pages < 50 KB, no Node toolchain at runtime (CSS per CONTRACT §9: hand-written, see §D) | 02 §9; 08 §1 | mo-web | 4 | NEW:CI-09 | todo |
| T-02-035 | Client stack: Rust stable, tokio, rustls-only WS/HTTP (HTTP/2), hyper local server, standard crypto crates, `serde_json`, `zstd`, `rmcp` (stdio + Streamable HTTP), no OpenSSL | 02 §9; 07 §10 | mo-node + mo-proto + mo-worker | 1 | NEW:CI-07 | todo |
| T-02-036 | Secrets at rest: `keyring` (macOS/Windows/Secret Service) + scrypt-encrypted file fallback | 02 §9; 06 §4.1 | mo-node | 1/5 | NEW:E73, NEW:CI-16 | todo |
| T-02-037 | Release: cargo-dist + Sigstore + SLSA provenance + reproducible builds | 02 §9; 07 §11 | mo-release* | 3 | NEW:CI-08 | todo |
| T-02-038 | Repo layout: `spec/protocol.md` (normative wire spec derived from 03) | 02 §10 | integrator | 0 | NEW:REV-02 | todo |
| T-02-039 | Repo layout: `relay/tools/simulate` deterministic scheduler simulator (dev only) | 02 §10; 04 §12 | mo-relay | 2 | NEW:CI-04 | todo |
| T-02-040 | Repo layout: fuzz targets for firewall and frames (placed in the owning crates) | 02 §10; 07 §13 | mo-worker + mo-proto | 1/3 | NEW:CI-03 | todo |
| T-02-041 | Repo layout: `deploy/` (self-host guide, systemd units, container recipe) and `docs/` user guides + public threat model | 02 §10 | mo-ops* + mo-docs* + mo-sec | 6 | NEW:REV-02 | todo |
| T-02-042 | Self-hosting first-class: Nodes choose their relay with one config value; no federation | 02 §10; 10 §10.1 | mo-node + mo-relay | 1 | E01 (custom relay URL) | todo |
| T-02-043 | Latency: zstd before sealing (v1); warm HTTP/2 provider pools; streaming pass-through with no buffering | 02 §11 | mo-node + mo-worker + mo-relay | 1 | E01, NEW:E77, E20 | todo |
| T-02-044 | Added latency budget 50–120 ms in-continent / 150–250 ms intercontinental | 02 §11 | mo-relay + mo-node | 0/2 | NEW:CI-20, NEW:MON-02 | todo |
| T-02-045 | Scale design point on one node: 50k WebSockets (~20–40 KB each), 5k concurrent streams, ≈ 200 task starts/s, ≈ 200 receipts/s, 20k SSE subscribers | 02 §12 | mo-relay + mo-web | 6 | NEW:CI-19 | todo |
| T-02-046 | Scale-out path (only when measured): shard Scheduler + SQLite by `repo_id` with consistent hashing; global users/devices/key log; Workers connect per shard | 02 §12; 10 §9 | mo-relay | D | NEW:MON-03 | todo |

## 03 — Wire protocol (`moochy.v1`)

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-03-001 | One authenticated gRPC HTTP/2 connection per Node carries the Session stream and all per-task streams for all roles; local clients share it through the Node | 03 §1.1; CONTRACT §12 | mo-node | 1 | E04, E05, NEW:E74 | todo |
| T-03-002 | ~~Control = JSON text frames, bulk = binary frames~~ → replaced by protobuf messages with ciphertext in `bytes` fields (T-C12-003) | 03 §1.2; ADR-33 | mo-proto + mo-relay | 1 | — | superseded |
| T-03-003 | Relay routes only on the plaintext route header; never chooses keys; every key unique per body and per attempt | 03 §1.3 | mo-proto | 1 | NEW:CI-01, E17 | todo |
| T-03-004 | Sign bytes, not objects: signed artifacts are transmitted and stored as the exact signed byte strings, never re-serialized | 03 §1.4 | mo-proto + mo-relay | 1 | NEW:CI-01, NEW:E40 | todo |
| T-03-005 | Domain separation: every signature, commitment, and KDF input starts with a distinct `lp` label (CONTRACT §2 list) | 03 §1.5 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-006 | Task ids are Gateway-created ULIDs; dedupe scope is `(gateway_device, task_id)` | 03 §1.6 | mo-relay + mo-node | 1 | NEW:E50 | todo |
| T-03-007 | Errors reach clients in the provider's native shapes; policy failures explicitly non-retryable | 03 §1.7 | mo-node | 1/2 | E10, NEW:E54 | todo |
| T-03-008 | ~~Node endpoint `wss://<relay>/v1/node`~~ → gRPC `moochy.v1.NodeLink` on `--grpc-addr` (T-C12-001) | 03 §2; CONTRACT §6, §12 | mo-relay + mo-node | 1 | — | superseded |
| T-03-009 | TLS 1.3 only, terminated in the Relay process (required for channel binding) | 03 §2 | mo-relay + mo-node | 1 | NEW:E23 | todo |
| T-03-010 | ~~WS subprotocol `moochy.v1`~~ → gRPC service `moochy.v1.NodeLink`, ALPN `h2` (T-C12-013) | 03 §2; ADR-33 | mo-relay | 1 | — | superseded |
| T-03-011 | ~~`permessage-deflate` disabled~~ → no gRPC compression on either side (T-C12-019, link.proto header) | 03 §2; link.proto header | mo-relay + mo-node | 1 | — | superseded |
| T-03-012 | Liveness: server HTTP/2 pings every 15 s, peer dead after 2 missed pongs or TCP close; keepalive enforcement `MinTime` 10 s, `PermitWithoutStream` | 03 §2; CONTRACT §12 | mo-relay + mo-node | 1 | NEW:E34, NEW:E25 | todo |
| T-03-013 | Session `Ping`/`Pong` RTT feeds the Scheduler's latency estimate (EWMA α = 0.2) | 03 §2; 04 §3; link.proto | mo-relay | 2 | NEW:CI-04 | todo |
| T-03-014 | Chunk ciphertext ≤ 64 KiB (plaintext ≤ 65,497 B, see T-03-031); gRPC `MaxRecvMsgSize`/`MaxSendMsgSize` 128 KiB on both sides | 03 §2; CONTRACT §12 | mo-proto + mo-relay + mo-node | 1 | NEW:E25, NEW:CI-01 | todo |
| T-03-015 | Max request body 32 MiB decompressed (Worker checks); Relay checks sealed size against the same bound | 03 §2, §16 | mo-worker + mo-relay | 1 | NEW:E25 | todo |
| T-03-016 | `Auth.client_version` carries the Node version (was the upgrade header) | 03 §3; link.proto | mo-node | 1 | NEW:E72 | todo |
| T-03-017 | `hello {nonce (32 B random), server_time, min_client_version, relay_release, log_checkpoint}` | 03 §3 | mo-relay | 1 | NEW:E23 | todo |
| T-03-018 | `auth {device_id, roles, sig}` with `sig = Ed25519(lp("moochy/v1/auth", nonce, dialed_origin, tls_exporter, device_id))` | 03 §3; CONTRACT §3 | mo-proto + mo-node | 1 | NEW:CI-01, NEW:E23 | todo |
| T-03-019 | Relay looks up device (not revoked), recomputes with its own origin + exporter, verifies (ZIP-215), checks roles | 03 §3 | mo-relay | 1 | NEW:E23 | todo |
| T-03-020 | `welcome {session_id, granted roles, limits, catalog_version}` | 03 §3 | mo-relay | 1 | E01 | todo |
| T-03-021 | After welcome: Gateway receives `pool.sync`; Worker sends `worker.known_tasks` then `worker.offer` | 03 §3 | mo-relay + mo-node | 1 | E01, NEW:E34 | todo |
| T-03-022 | `dialed_origin` = origin the Node itself dialed and verified with TLS, never taken from `hello` | 03 §3 | mo-node | 1 | NEW:E23 | todo |
| T-03-023 | `tls_exporter` = RFC 9266 `EXPORTER-Channel-Binding`, empty context, 32 bytes, on both sides | 03 §3; CONTRACT §3 | mo-node + mo-relay | 1 | NEW:CI-01, NEW:E23 | todo |
| T-03-024 | No bearer token on the wire; no shared secret stored server-side (DB leak exposes only public keys) | 03 §3 | mo-relay | 1 | NEW:E23, E13 | todo |
| T-03-025 | A new successful auth for a device closes its previous session; events from non-current sessions ignored | 03 §3, §14 | mo-relay | 2 | NEW:E24 | todo |
| T-03-026 | Clock skew > 5 min vs `server_time` → local warning | 03 §3 | mo-node | 1 | NEW:E71 | todo |
| T-03-027 | ~~Text frame JSON with mandatory `t`~~ → `NodeMsg`/`RelayMsg`/`SubmitUp`/`SubmitDown`/`ServeUp`/`ServeDown` oneofs; the stream identifies the task (T-LP-004, T-LP-005, T-LP-009, T-LP-011) | 03 §4.1; link.proto | mo-proto + mo-relay | 1 | — | superseded |
| T-03-028 | Unknown protobuf fields ignored; an empty/unknown `oneof` message answered with `Error{code:"unknown_type"}` and otherwise ignored | 03 §4.1; link.proto | mo-relay + mo-node | 1 | NEW:E25 | todo |
| T-03-029 | ~~23-byte binary header~~ → `Chunk{attempt, seq, last, ct}` (T-C12-004); AEAD AAD unchanged | 03 §4.2; CONTRACT §5; ADR-33 | mo-proto + mo-relay | 1 | — | superseded |
| T-03-030 | ~~Frame kinds `0x01`/`0x02`/`0x03`~~ → request chunks on `Submit`/`Serve` body, response chunks on `Serve`/`Submit` down; `kind_byte` survives only inside the AAD (`0x01` req, `0x02` resp); delta bodies would be a new oneof field | 03 §4.2; ADR-33 | mo-proto + mo-relay | 1 | — | superseded |
| T-03-031 | Plaintext chunk ≤ 65,497 bytes | 03 §4.2 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-032 | Task data accepted only on that task's own stream: a `Serve` stream for (task, attempt) only from the assigned worker's authenticated connection, a `Submit` stream only from the submitting Gateway's; streams from any other connection get `UNAUTHENTICATED` (counted) | 03 §4.2; link.proto header | mo-relay | 1 | NEW:E25, E17 | todo |
| T-03-033 | `pool.sync` (R→G): `repo`, `workers[]{worker_device, enc_pub, key_log_index, approval_log_index, donor_pseudonym, dialects, models[], hint}`, `full`/`delta`; full after welcome, delta on change; `hint` 0–100 at most 1/s | 03 §5.1; 04 §7 | mo-relay | 1/2 | E01, NEW:E27 | todo |
| T-03-034 | Gateway independently verifies from its key-log mirror that each pool worker key is logged and the donor has an owner-signed approval for the repo | 03 §5.1; 06 §10 | mo-node | 3 | NEW:E43 | todo |
| T-03-035 | `task.submit` (G→R): `task`, `route_b64`, `wraps[]{worker_device, wrap}`, `body_len`, `body_chunks`, followed by `0x01` frames | 03 §5.1; CONTRACT §5 | mo-node + mo-relay | 1 | E01 | todo |
| T-03-036 | `task.need_wraps` (R→G, `workers[]`) when no wrapped candidate is eligible; `task.wraps` answers without resending the body | 03 §5.1 | mo-relay + mo-node | 2 | NEW:E27 | todo |
| T-03-037 | `task.accepted {task, attempt, worker_device, R}`; Gateway decrypts only this attempt's stream | 03 §5.1 | mo-relay + mo-node | 1 | E01, NEW:E49 | todo |
| T-03-038 | `task.started` (R→G) forwarded when provider headers arrive; no failover after it, ever | 03 §5.1 | mo-relay | 1 | E06, NEW:E28 | todo |
| T-03-039 | `task.checkpoint {task, attempt, seq, running_hash, sig}` forwarded W→R→G | 03 §5.1–5.2 | mo-relay + mo-worker + mo-node | 3 | NEW:E46 | todo |
| T-03-040 | Response `0x02` frames delivered to the Gateway in `seq` order | 03 §5.1 | mo-relay | 1 | E01 | todo |
| T-03-041 | `task.end {task, attempt, receipt_b64, donor_sig, projection_b64, projection_sig}` (W→R and R→G) | 03 §5; CONTRACT §5 | mo-proto + mo-relay | 1 | E01 | todo |
| T-03-042 | `task.failed {task, code, retryable, retry_after_ms, sealed_detail?}` converted by the Gateway into a native error | 03 §5.1 | mo-relay + mo-node | 1 | E07, E10, NEW:E54 | todo |
| T-03-043 | `task.cancel {task, reason}` (G→R) when the client closes the request | 03 §5.1 | mo-node | 1 | E08 | todo |
| T-03-044 | `receipt.dispute {task, attempt, code, gateway_sig}` only on mismatch | 03 §5.1 | mo-node + mo-relay | 3 | NEW:E45 | todo |
| T-03-045 | `worker.known_tasks {tasks[]{task, attempt, state}}` right after welcome; Relay releases at zero cost any reservation for that Worker not listed | 03 §5.2; 05 §7 | mo-node + mo-relay | 1 | E12, NEW:E34 | todo |
| T-03-046 | `worker.offer {slots_free, models[]{dialect, model, rl_headroom}, pledges[], window_open, local_cap_left}` on connect and on change; only the latest per worker kept (coalesced) | 03 §5.2; 04 §2 | mo-node + mo-relay | 1/2 | E01, NEW:E31 | todo |
| T-03-047 | `task.assign {task, attempt, route_b64, wrap, pledge, deadline_ack_ms}` sent only after the reservation is durably committed, followed by body frames | 03 §5.2; 04 §8.1 | mo-relay | 1 | E12, NEW:CI-04 | todo |
| T-03-048 | `task.ack {task, attempt, R}` within 500 ms of last body frame = authentic, decrypted, firewall passed, local caps reserved, provider call starting | 03 §5.2 | mo-node + mo-worker | 1 | E01, NEW:E28 | todo |
| T-03-049 | `task.nack {task, attempt, R, code, retryable, retry_after_ms, sealed_detail?}`; detail sealed to the Gateway, Relay sees only the code | 03 §5.2 | mo-node + mo-worker | 1 | E09, E07 | todo |
| T-03-050 | Worker `task.started` when provider response headers arrive | 03 §5.2 | mo-worker + mo-node | 1 | E06 | todo |
| T-03-051 | Worker `task.end` also replayed from the outbox after reconnect | 03 §5.2 | mo-node | 1 | E12 | todo |
| T-03-052 | `task.cancel` (R→W): Worker aborts the provider request immediately | 03 §5.2, §13 | mo-node + mo-worker | 1 | E08 | todo |
| T-03-053 | `receipt.ack` only after the receipt commit with `synchronous=FULL`; Worker marks outbox entry acknowledged and keeps it 7 more days | 03 §5.2; 05 §7 | mo-relay + mo-node | 1 | E12, NEW:E85 | todo |
| T-03-054 | `receipt.replay_since {since}` after DR restore: Worker resends every receipt (acked or not) since that time | 03 §5.2 | mo-relay + mo-node | 2 | NEW:E36 | todo |
| T-03-055 | `relay.draining {reconnect_after_ms}`: Gateways 0, Workers jittered 0–10 s | 03 §5.3 | mo-relay + mo-node | 2 | NEW:E35 | todo |
| T-03-056 | `log.checkpoint` pushes the newest signed key-log checkpoint | 03 §5.3 | mo-relay + mo-node | 3 | NEW:E42 | todo |
| T-03-057 | `catalog.update` pushes a new signed catalog; Nodes reject version decreases | 03 §5.3 | mo-relay + mo-node | 1→3 | NEW:E41 | todo |
| T-03-058 | `Error {code, message, task}` on the Session stream; transport/auth failures use gRPC status codes only | 03 §5.3; CONTRACT §12 | mo-relay + mo-node | 1 | NEW:E25 | todo |
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
| T-03-070 | Body sealed once; adding a recipient costs one more wrap, never a re-upload | 03 §6.2 | mo-node + mo-relay | 2 | NEW:E27 | todo |
| T-03-071 | `suite_id` in HPKE info and in each device's `KEY_ADDED` entry (downgrade protection) | 03 §6.2; 06 §4.1 | mo-proto + mo-relay | 1→3 | NEW:CI-01, NEW:E42 | todo |
| T-03-072 | Response chunks under RK, nonce = seq, AAD = `lp("moochy/v1/resp", task_id_16B, u64(attempt), R, u32(seq), last)` | 03 §6.3; CONTRACT §3 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-073 | Gateway decrypts only frames of the attempt named in `task.accepted`, under that attempt's RK | 03 §6.3 | mo-node | 1 | E17, NEW:E49 | todo |
| T-03-074 | Gateway aborts the task if response frames ever appear for a second started attempt | 03 §6.3 | mo-node | 1 | NEW:E49 | todo |
| T-03-075 | AAD binding rejects reordering, splicing across tasks/attempts, and silent truncation (stream without a `last` frame is an error) | 03 §6.3 | mo-node + mo-proto | 1 | E17, NEW:E49 | todo |
| T-03-076 | Relay sees only route header, sizes/timings, NACK codes, usage + cost; never content, provider headers, NACK details, salts, or raw provider request id | 03 §6.4 | mo-relay + mo-node | 1 | E13 | todo |
| T-03-077 | Route header JSON `{repo_id, dialect, model, effort, max_tokens, est_input_tokens, cache_ttl, stream, affinity, flags}` built by the Gateway | 03 §7.1; CONTRACT §5 | mo-node | 1 | E01, NEW:CI-01 | todo |
| T-03-078 | Worker check: `repo_id` equals the repo of the assigned pledge (Worker's own pledge table) | 03 §7.1 | mo-node + mo-worker | 1 | NEW:E43 | todo |
| T-03-079 | Worker check: `dialect`, `model` (after catalog mapping), effective `effort` (catalog default when absent), `max_tokens` (present, exact), `stream` all match the body | 03 §7.1 | mo-worker | 1 | NEW:E57 | todo |
| T-03-080 | `est_input_tokens = ceil(text_bytes/3) + images × max_image_tokens + pages × max_page_tokens`, recomputed by the Worker and matched exactly | 03 §7.1 | mo-worker + mo-node | 1 | NEW:CI-01, NEW:E57 | todo |
| T-03-081 | `cache_ttl` = longest `cache_control.ttl` present (`none`, `5m`, `1h`), checked by the Worker | 03 §7.1 | mo-worker + mo-node | 1 | NEW:E57 | todo |
| T-03-082 | `affinity` = HMAC(per-device secret, lp(system, tools, first user message)) truncated to 16 B; not checked by the Worker | 03 §7.1; 04 §5 | mo-node | 2 | NEW:E30 | todo |
| T-03-083 | `flags` (`fast`, `images`, `documents`, …) each require the donor's opt-in | 03 §7.1 | mo-worker + mo-relay | 1 | NEW:E57 | todo |
| T-03-084 | Route mismatch → `task.nack{route_mismatch, retryable:false}` and a strike against the submitting member | 03 §7.1 | mo-worker + mo-relay | 1 | NEW:E57 | todo |
| T-03-085 | `task_sig = Ed25519(gw_key, lp("moochy/v1/task", task_id, repo_id, route_header_bytes, body_sha256, headers_sha256))`, inside the sealed payload | 03 §7.2; CONTRACT §3 | mo-proto + mo-node | 1 | NEW:CI-01 | todo |
| T-03-086 | Worker check 1: `task_sig` valid for `gateway_device`, whose key is logged and not revoked | 03 §7.2 | mo-node + mo-worker | 1→3 | E16, NEW:E43 | todo |
| T-03-087 | Worker check 2: owner-signed `MEMBER_ADDED` for that user + `repo_id` in the key log, or the user is the repo owner | 03 §7.2 | mo-node | 3 | NEW:E43 | todo |
| T-03-088 | Worker check 3: assigned pledge belongs to this donor and to `repo_id` | 03 §7.2 | mo-node | 1 | NEW:E43 | todo |
| T-03-089 | Worker check 4: ULID timestamp of `task_id` within ±10 min of the Worker clock | 03 §7.2 | mo-node + mo-worker | 1 | NEW:E58 | todo |
| T-03-090 | Worker check 5: `(gateway_device, task_id)` never served before (persisted set covering the ±10 min window) | 03 §7.2 | mo-worker + mo-node | 1 | E16, NEW:E58 | todo |
| T-03-091 | Worker body handling order: find wrap → HPKE-open CK → K_req → decrypt → zstd-decompress → check `body_sha256` | 03 §8 | mo-node + mo-proto | 1 | E01, E15 | todo |
| T-03-092 | Then verify §7.2, then firewall, then route-header checks, then local reservation, then draw R, ack, call provider | 03 §8 | mo-node + mo-worker | 1 | E09, E11, E16 | todo |
| T-03-093 | Prefix-delta transfer: designed, not built in v1; frame kind `0x03` reserved; build trigger = upload p50 > 150 ms or egress in top-3 costs | 03 §9; ADR-21 | mo-proto + mo-relay + mo-node | D | NEW:MON-03 | todo |
| T-03-094 | When delta transfer is built: every delta and full resend sealed with its own fresh CK; Worker base cache keyed by `(gateway_device, base_task_id)` | 03 §9 | mo-proto + mo-node | D | NEW:CI-01 (future) | todo |
| T-03-095 | Wire task lifecycle states and transitions exactly as 03 §10.1 (Submitted, Assigned, Acked, Started, Reassigning, Ended, Failed, Cancelled) | 03 §10.1 | mo-relay | 1/2 | NEW:CI-04 | todo |
| T-03-096 | No failover after `task.started`; mid-stream failures become native retryable errors | 03 §10.1; ADR-20 | mo-relay + mo-node | 1 | E06, NEW:E28 | todo |
| T-03-097 | Late messages from a superseded attempt answered with `task.cancel` for that attempt; its receipt still settles | 03 §10.1 | mo-relay | 2 | NEW:E28 | todo |
| T-03-098 | Routing deadline (5 s) starts when the last body frame has been received by the Relay | 03 §10.1 | mo-relay | 2 | NEW:E29 | todo |
| T-03-099 | Relay frees its copy of the sealed body at `task.started` | 03 §10.1 | mo-relay | 1 | NEW:E51 | todo |
| T-03-100 | Unstarted bodies bounded by global and per-device byte budgets at the Edge; exceeded → retryable `overloaded` | 03 §10.1, §16 | mo-relay | 2 | NEW:E51 | todo |
| T-03-101 | NACK codes `busy`, `rate_limited`, `overloaded`, `provider_error`, `local_cap`, `model_unavailable` are retryable elsewhere | 03 §10.2 | mo-worker + mo-node + mo-relay | 1 | E07, NEW:E31 | todo |
| T-03-102 | NACK codes `firewall`, `route_mismatch`, `unauthorized_task`, `bad_envelope` are non-retryable | 03 §10.2 | mo-worker + mo-node + mo-relay | 1 | E09, E15, E16 | todo |
| T-03-103 | NACK effects: `rate_limited` cools down (worker, model); `overloaded` short back-off; `provider_error` failure penalty; `local_cap` excluded until next offer; `model_unavailable` removes model from offer | 03 §10.2 | mo-relay + mo-node | 2 | NEW:E31, NEW:E60 | todo |
| T-03-104 | NACK effects: `firewall` → native `invalid_request_error` + strike; `route_mismatch` → native error + strike; `unauthorized_task` and `bad_envelope` → alert | 03 §10.2 | mo-relay + mo-node | 1 | E09, E15, E16, NEW:E82 | todo |
| T-03-105 | Anthropic native errors: HTTP 429/529 with `error` body before streaming; `event: error` SSE (`overloaded_error`, `rate_limit_error`, `api_error`) after | 03 §10.3 | mo-node | 1 | NEW:E54 | todo |
| T-03-106 | OpenAI-style native errors: matching HTTP status and error object, before and after streaming | 03 §10.3 | mo-node | 1 | NEW:E54 | todo |
| T-03-107 | Policy errors non-retryable with explicit messages: `over_task_cap`, `quota_exceeded` (400/403), `model_not_in_pool` (404), `firewall` (400 with sealed detail) | 03 §10.3 | mo-node + mo-relay | 1/2 | E10, NEW:E29, NEW:E54 | todo |
| T-03-108 | Capacity grants: Workers offer `slots_free` (default 4, range 1–64); Relay never pushes beyond it; decrements on assign; subtracts reservation from `local_cap_left`; fresh offer on task end / headroom / window change | 03 §11 | mo-node + mo-relay | 1/2 | E01, E11, NEW:E59 | todo |
| T-03-109 | Receipt fields: `v, task_id, attempt, repo_id, pledge_id, worker_device, gateway_device, dialect, provider, model_reported, usage{input, output, cache_write_5m, cache_write_1h, cache_read, estimated, provider_cost}, catalog_version, cost_uusd, req_commit, resp_commit, provider_req_hash, status, t_start, t_started, t_end` | 03 §12.1 | mo-proto + mo-worker | 1 | NEW:CI-01, E01 | todo |
| T-03-110 | `req_commit = SHA-256(lp("moochy/v1/req-commit", S_req, body as sent by the Gateway before any Worker mutation))` | 03 §12.1 | mo-proto + mo-node | 1 | NEW:CI-01, NEW:E56 | todo |
| T-03-111 | `resp_commit = SHA-256(lp("moochy/v1/resp-commit", S_resp, concatenated plaintext response bytes))`, computed incrementally on both sides | 03 §12.1 | mo-proto + mo-node | 1 | NEW:CI-01, NEW:E45 | todo |
| T-03-112 | `provider_req_hash = SHA-256(lp("moochy/v1/provider-req", S_pid, provider request id))` | 03 §12.1 | mo-proto + mo-worker | 1 | NEW:CI-01 | todo |
| T-03-113 | Receipt `status` ∈ {`ok`, `cancelled`, `provider_error`, `partial`, `not_started`} | 03 §12.1 | mo-worker + mo-node | 1 | E08, NEW:E34 | todo |
| T-03-114 | `donor_sig = Ed25519(worker_key, lp("moochy/v1/receipt", receipt_bytes))` | 03 §12.1 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-115 | Projection `{receipt_ref (random), repo_id, donor pseudonym (per visibility), model, cost_uusd, UTC day, SHA-256(receipt_bytes)}` + `projection_sig = Ed25519(lp("moochy/v1/projection", projection_bytes))` | 03 §12.1 | mo-proto + mo-worker | 1 | NEW:CI-01, E19 | todo |
| T-03-116 | Full receipts stay with the two parties and the Relay DB; projections reveal no device ids, task ids, or sub-day timestamps | 03 §12.1 | mo-relay + mo-web | 1/4 | NEW:E68 | todo |
| T-03-117 | Gateway receipt checks: recompute `req_commit`/`resp_commit`; input + cache within a band of its estimate; `cache_write_1h > 0` only with 1 h TTL; non-reasoning visible output within ±25%; `model_reported` = requested model or catalog alias | 03 §12.2 | mo-node | 3 | NEW:E45 | todo |
| T-03-118 | Silence = acceptance; on mismatch `receipt.dispute{code}` signed over `lp("moochy/v1/dispute", task_id, attempt, code)` | 03 §12.2 | mo-node + mo-proto | 3 | NEW:E45, NEW:CI-01 | todo |
| T-03-119 | Disputed receipts still settle money; excluded from leaderboards; queued for review | 03 §12.2 | mo-relay + mo-web | 3 | NEW:E45 | todo |
| T-03-120 | Worker signs a progress checkpoint at the end of every tool-call block (Anthropic `tool_use`; OpenAI `tool_calls` per index) and on the last chunk: `Ed25519(lp("moochy/v1/resp-progress", task_id, attempt, R, seq, running_sha256))` | 03 §12.3 | mo-worker + mo-node + mo-proto | 3 | NEW:E46, NEW:CI-01 | todo |
| T-03-121 | Gateway releases a tool-call block only after verifying a covering checkpoint; otherwise substitutes an error tool result; text streams immediately | 03 §12.3 | mo-node | 3 | NEW:E46, E18 | todo |
| T-03-122 | Ed25519 verification pinned to ZIP-215 in Go and Rust, with edge-case vectors | 03 §12.4 | mo-proto + mo-relay | 1 | NEW:CI-01 | todo |
| T-03-123 | Cancellation chain: client closes → `task.cancel` → Relay → current-attempt Worker aborts provider → receipt `cancelled` with actual usage; `estimated:true` when final usage missing → pessimistic settle | 03 §13 | mo-node + mo-relay + mo-worker | 1/2 | E08, NEW:E37 | todo |
| T-03-124 | Gateway connection drop (not a planned drain) → Relay cancels all that Gateway's unfinished tasks | 03 §13 | mo-relay | 2 | NEW:E33 | todo |
| T-03-125 | Reconnect with exponential back-off and full jitter (base 250 ms, cap 30 s) | 03 §14 | mo-node | 1 | NEW:E35 | todo |
| T-03-126 | Presence keyed by `(device_id, session_id)`; offers, offline events, and frames from non-current sessions ignored | 03 §14 | mo-relay | 2 | NEW:E24 | todo |
| T-03-127 | Resubmission of the same `task_id` by the same Gateway after reconnect: not started → route moves to the new connection; started → final state replayed | 03 §14 | mo-relay | 2 | NEW:E50 | todo |
| T-03-128 | Worker link loss: abort all in-flight provider calls; outbox receipt for each (`not_started`, zero usage, when the provider was never called); on reconnect `known_tasks` then outbox replay | 03 §14 | mo-node + mo-worker | 1 | E12, NEW:E34 | todo |
| T-03-129 | No stream resume in v1; deferred design: Relay keeps last 256 KiB per stream for 30 s if mid-stream Gateway disconnects > 0.5% of tasks | 03 §14 | mo-relay + mo-node | D | NEW:MON-03 | todo |
| T-03-130 | Breaking change → new subprotocol; a relay serves both for ≥ 90 days | 03 §15 | mo-relay | D | NEW:E72 | todo |
| T-03-131 | Within v1, fields are additive; `hello.min_client_version` refuses Nodes with known security bugs | 03 §15 | mo-relay + mo-node | 1 | NEW:E72 | todo |
| T-03-132 | Labels include `v1` and HPKE info includes the suite id (no cross-version confusion) | 03 §15 | mo-proto | 1 | NEW:CI-01 | todo |
| T-03-133 | Limit: ≤ 16 concurrent tasks per Gateway device (Relay) | 03 §16 | mo-relay | 2 | NEW:E52 | todo |
| T-03-134 | Limit: ≤ 120 task submissions per member per minute (Relay token bucket) | 03 §16; 04 §10 | mo-relay | 2 | NEW:E52 | todo |
| T-03-135 | Limit: per-task response buffer at the Relay 1 MiB; task fails if the Gateway cannot keep up | 03 §16 | mo-relay | 2 | NEW:E51 | todo |
| T-03-136 | Limit: ≤ 8 wraps per submit (Relay) | 03 §16 | mo-relay | 1 | NEW:E25 | todo |
| T-03-137 | Limit: 3 attempts per task (Relay) | 03 §16 | mo-relay | 2 | NEW:E29 | todo |
| T-03-138 | Deadlines: ACK 500 ms after last body frame reaches the Worker; start 30 s after ACK; routing 5 s after last body frame reaches the Relay | 03 §16; 04 §8.2 | mo-relay | 2 | NEW:E28, NEW:E29 | todo |
| T-03-139 | Limit: task-id freshness ±10 min (Worker) | 03 §16 | mo-node | 1 | NEW:E58 | todo |
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
| T-03-150 | Transport update (ADR-33): the 03 §5 message catalog maps 1:1 onto `link.proto`; all cryptography, AAD, signatures, receipts, deadlines, and semantics of 03 stay normative; only framing changed | 03 §1 note; CONTRACT §5 | integrator + mo-proto + mo-relay + mo-node | 1 | NEW:CI-01, E01 | todo |

## 04 — Routing engine (Scheduler)

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-04-001 | One goroutine owns all control-plane state; every change is an ordered message; no locks on that state | 04 §1; ADR-06 | mo-relay | 1 | NEW:CI-04 | todo |
| T-04-002 | Scheduler is a pure state machine `apply(state, event) → (state', commands)`: no I/O, no clock reads (time on the event), seeded PRNG only | 04 §1, §12.1 | mo-relay | 1/2 | NEW:CI-04 | todo |
| T-04-003 | `sync.Map` only for the data-plane forwarding table `task_id → (expected source conn, destination conn)`, written once per attempt | 04 §1 | mo-relay | 1 | E17, NEW:CI-06 | todo |
| T-04-004 | Input queues: bounded **sheddable** submit queue (full → retryable reject at the Edge) | 04 §2 | mo-relay | 2 | NEW:E51 | todo |
| T-04-005 | Lifecycle queue never blocks the Edge and never drops; bounded by in-flight tasks; offers coalesced per worker | 04 §2 | mo-relay | 2 | NEW:E51, NEW:CI-04 | todo |
| T-04-006 | Web-originated changes (pledge / repo / member / approval) enter the Scheduler on the lifecycle queue | 04 §2 | mo-relay | 1 | NEW:E39 | todo |
| T-04-007 | Store writer never back-pressures the Scheduler: op slice swapped on each group commit; completions on their own channel (no cycle) | 04 §2 | mo-relay | 1 | NEW:CI-04 | todo |
| T-04-008 | Commands to connections are non-blocking sends to per-connection writer queues; overflow closes that connection (handled as disconnect) | 04 §2 | mo-relay | 1 | NEW:E51 | todo |
| T-04-009 | SSE hub receives aggregated events by non-blocking send | 04 §2; 08 §7 | mo-relay + mo-web | 4 | NEW:E67 | todo |
| T-04-010 | Timers: min-heap of short deadlines with one `time.Timer` reset to the earliest; long-horizon items are SQL sweeps, not timers | 04 §2 | mo-relay | 2 | NEW:CI-04 | todo |
| T-04-011 | State structures: `sessions`, `workers`, `pledges`, `pools`, `donorWorkers`, `members`, `devices` (capped only), `affinity`, `inflight`, `awaitingReceipt` as specified | 04 §3 | mo-relay | 1/2 | NEW:CI-04 | todo |
| T-04-012 | Live balances authoritative in the Scheduler, loaded at boot, persisted by group commit | 04 §3 | mo-relay | 1 | E12 | todo |
| T-04-013 | Memory ≈ 50 MB at 10k workers / 5k in-flight / 50k affinity entries; sealed bodies live in the Edge, never in Scheduler state | 04 §3 | mo-relay | 2 | NEW:CI-19 | todo |
| T-04-014 | Eligibility rule 1: pledge in `pools[(repo, dialect, model)]` | 04 §4 | mo-relay | 1 | NEW:E29 | todo |
| T-04-015 | Rule 2: pledge `ACTIVE` and approved (Gateways additionally seal only to owner-approved donors) | 04 §4 | mo-relay | 1 | NEW:E39 | todo |
| T-04-016 | Rule 3: worker belongs to the pledge's donor, has a current session, `window_open`, `slots_free > 0` | 04 §4 | mo-relay | 1 | NEW:E59 | todo |
| T-04-017 | Rule 4: worker offers `(dialect, model)` and its rate-limit state is not cooling down | 04 §4 | mo-relay | 2 | NEW:E31 | todo |
| T-04-018 | Rule 5: `effort ≤ policy.max_effort`; every flag allowed by policy | 04 §4 | mo-relay | 1 | NEW:E29 | todo |
| T-04-019 | Rule 6: `reserve(t,p) ≤ per_task_cap` | 04 §4 | mo-relay | 1 | E10 | todo |
| T-04-020 | Rule 7: `reserve(t,p) ≤ budget − spent − reserved` | 04 §4 | mo-relay | 1 | E10 | todo |
| T-04-021 | Rule 8: `reserve(t,p) ≤ w.local_cap_left` | 04 §4 | mo-relay | 1 | E11 | todo |
| T-04-022 | Rule 9: member quota and submitting-device cap headroom | 04 §4 | mo-relay | 2 | NEW:E32 | todo |
| T-04-023 | Rule 10: worker not in `t.tried` (no second attempt on the same worker) | 04 §4 | mo-relay | 2 | E06 | todo |
| T-04-024 | Rule 11: worker has a wrap in `t.wraps` (else candidate for `need_wraps`) | 04 §4 | mo-relay | 2 | NEW:E27 | todo |
| T-04-025 | Rules evaluated cheapest-first; the rule eliminating the most candidates is recorded for precise policy errors | 04 §4, §8.3 | mo-relay | 2 | E10, NEW:E29 | todo |
| T-04-026 | `reserve(t,p)` uses the candidate pledge's own provider price for the model | 04 §4; 05 §5 | mo-relay | 1 | NEW:CI-10 | todo |
| T-04-027 | Affinity key = HMAC(per-device secret, lp(system, tools, first user message)) truncated to 16 B; stable per conversation; unguessable by the Relay | 04 §5 | mo-node | 2 | NEW:E30 | todo |
| T-04-028 | Affinity TTL 5 min sliding; 60 min when `cache_ttl == 1h` | 04 §5 | mo-relay | 2 | NEW:E30 | todo |
| T-04-029 | Affinity selection: choose the affinity worker if eligible unless its score is worse than the best alternative by more than the affinity margin (default 3×) | 04 §5 | mo-relay | 2 | NEW:E30, NEW:CI-05 | todo |
| T-04-030 | On failover the affinity entry moves to the new worker | 04 §5 | mo-relay | 2 | NEW:E30 | todo |
| T-04-031 | Without affinity: collect eligible (w, p), draw two at random weighted by pledge headroom, pick the lower cost score | 04 §6 | mo-relay | 2 | NEW:CI-05 | todo |
| T-04-032 | `score = rtt_ewma_ms + 40 × (inflight/slots_max) + 200 × rl_pressure + fail_penalty`; `fail_penalty` +100 ms per failure in 5 min, linear decay; weights configurable with documented defaults | 04 §6; ADR-32 | mo-relay | 2 | NEW:CI-05 | todo |
| T-04-033 | `rl_pressure` ∈ [0,1] derived from Worker-reported provider rate-limit headers | 04 §6 | mo-relay + mo-worker | 2 | NEW:E31 | todo |
| T-04-034 | Gateway wraps for the affinity worker first, then top workers by `hint` for the model, up to 8 wraps | 04 §7 | mo-node | 2 | NEW:E27, NEW:E30 | todo |
| T-04-035 | Scheduler restricted to wrapped workers; if none eligible, `task.need_wraps{workers}` with its own top choices | 04 §7 | mo-relay | 2 | NEW:E27 | todo |
| T-04-036 | Commit-before-assign: `Assign` only after the group commit containing the reservation and task row completes; **adaptive group commit** (commit at once when the writer is idle, batch only while a commit is in flight) | 04 §8.1; L8; ADR-34; CONTRACT §13 | mo-relay | 1 | E12, E22, NEW:CI-04 | todo |
| T-04-037 | ACK deadline expiry → cancel attempt; to `awaitingReceipt` unless NACK / zero-usage receipt proves no spend; reassign | 04 §8.2 | mo-relay | 2 | NEW:E28 | todo |
| T-04-038 | Start deadline (30 s after ACK) expiry → same as ACK expiry | 04 §8.2 | mo-relay | 2 | NEW:E28 | todo |
| T-04-039 | Routing deadline (5 s after last body frame, no ACK) → `task.failed{overloaded, retryable}` | 04 §8.2 | mo-relay | 2 | NEW:E29 | todo |
| T-04-040 | Attempts exhausted (3) → `task.failed{overloaded, retryable}` | 04 §8.2 | mo-relay | 2 | NEW:E29 | todo |
| T-04-041 | SQL sweep every minute: attempts awaiting a receipt > 24 h **and** Worker absent all that time → pessimistic settlement at the reservation | 04 §8.2; 05 §5.2 | mo-relay | 2 | NEW:E37 | todo |
| T-04-042 | SQL sweep: receipts older than 24 h without dispute become final for leaderboards | 04 §8.2 | mo-relay | 3 | NEW:E45 | todo |
| T-04-043 | Policy failure mapping: no pledge serves model → `model_not_in_pool` (no retry); rule 6 → `over_task_cap` (with worst-case cost and cap); rules 7/9 → `quota_exceeded`; capacity (3, 4, 8, rate limits) → `overloaded` (retryable) | 04 §8.3 | mo-relay | 2 | E10, NEW:E29, NEW:E32 | todo |
| T-04-044 | Reassignment state machine (Selecting, Committing, NeedWraps, Assigned, Acked, Started, Superseded, Settling, Failed) as 04 §8.4 | 04 §8.4 | mo-relay | 2 | NEW:CI-04 | todo |
| T-04-045 | Superseded attempt kept in `awaitingReceipt` unless proven zero-cost; worker added to `tried[]` | 04 §8.4 | mo-relay | 2 | NEW:E28 | todo |
| T-04-046 | Proof of zero spend = NACK before the provider call (`busy`, `local_cap`, `firewall`, `route_mismatch`, `unauthorized_task`, `bad_envelope`) or a `not_started` receipt; anything else keeps the reservation until the receipt | 04 §8.4 | mo-relay | 1 | E07, E09, NEW:E28 | todo |
| T-04-047 | Workers parse provider rate-limit headers (remaining requests/tokens + reset, `retry-after`; names pinned per adapter) into a compact `rl_headroom` per model | 04 §9 | mo-worker | 2 | NEW:CI-17, NEW:E31 | todo |
| T-04-048 | Offer updates sent when headroom crosses 50%, 20%, or 5% (not per request) | 04 §9 | mo-node + mo-worker | 2 | NEW:E31 | todo |
| T-04-049 | On 429: Worker NACKs with `retry_after_ms`; Scheduler cools down `(worker, model)` and reassigns immediately | 04 §9 | mo-node + mo-relay | 2 | E07, NEW:E31 | todo |
| T-04-050 | Fairness between members: per-member monthly caps (default owner unlimited, members 20% of committed); per-member submission rate limit | 04 §10; 05 §11 | mo-relay | 2 | NEW:E32, NEW:E52 | todo |
| T-04-051 | Fairness for CI devices: own device caps and a single repo scope | 04 §10; 07 §8.4 | mo-relay + mo-node | 2 | NEW:E32 | todo |
| T-04-052 | Between repos sharing a donor: separate budgets per pledge; compete only for slots (first-come); optional `max_slots` per pledge enforced | 04 §10; 05 §4.1 | mo-relay | 2 | NEW:E32 | todo |
| T-04-053 | Donor's own use protected by `slots_max`, schedule windows, rate-limit steering | 04 §10 | mo-node + mo-relay | 2 | NEW:E59, NEW:E31 | todo |
| T-04-054 | Perf: `apply(submit)` incl. eligibility + P2C + reservation p99 < 50 µs (≤ 50 candidates) | 04 §11 | mo-relay | 2 | NEW:CI-06 | todo |
| T-04-055 | Perf: `apply(ack/started/end)` p99 < 10 µs | 04 §11 | mo-relay | 2 | NEW:CI-06 | todo |
| T-04-056 | Perf: chunk forwarding < 5 µs + syscall (one map load, source check, one channel send) | 04 §11 | mo-relay | 1 | NEW:CI-06 | todo |
| T-04-057 | Perf: Submit received → Assign sent (scheduler + durable reservation) p50 ≤ 2 ms / p99 ≤ 8 ms (replaces the fixed 10 ms window) | 04 §11; ADR-34; CONTRACT §13 | mo-relay | 1 | E22, NEW:CI-06 | todo |
| T-04-058 | Ceiling: ~100k events/s per Scheduler; upgrade = one Scheduler per repo shard | 04 §11 | mo-relay | D | NEW:MON-03 | todo |
| T-04-059 | Invariant: `0 ≤ reserved` and `spent + reserved ≤ budget + overage bound` for every pledge, member, capped device | 04 §12.2 | mo-relay | 1 | NEW:CI-04, NEW:E70 | todo |
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
| T-05-002 | Displays show dollars first, token-equivalents second (render-time, current catalog) | 05 §1; 08 §11 | mo-web | 4 | NEW:E66 | todo |
| T-05-003 | Token-equivalent formula: µ$ ÷ blended price of the pool's most-used model, blended = 0.8 × input + 0.2 × output, uncached | 05 §1 | mo-web | 4 | NEW:CI-09 | todo |
| T-05-004 | Each receipt cost rounded **up** to the next µ$ | 05 §1, §3 | mo-worker + mo-relay | 1 | NEW:CI-10 | todo |
| T-05-005 | Public model ids are OpenRouter-style slugs (`vendor/model`) | 05 §2.1; ADR-18 | mo-relay + mo-node | 1 | E01, NEW:E41 | todo |
| T-05-006 | Gateway accepts native ids and maps them to slugs through the catalog | 05 §2.1 | mo-node | 1 | NEW:E41 | todo |
| T-05-007 | Route header carries the slug; Worker maps slug → its provider's id through the signed catalog; any donor offering the model in that dialect can serve | 05 §2.1 | mo-worker + mo-node | 1 | E03, NEW:E56 | todo |
| T-05-008 | `/v1/models` and `moochy_pool_status` list slugs plus native aliases | 05 §2.1 | mo-node | 1 | NEW:E53, E04 | todo |
| T-05-009 | Catalog entry fields: `version, effective_at, model, provider, provider_model_id, dialects, in, out, cache_write_5m, cache_write_1h, cache_read` (µ$/MTok ints), `max_image_tokens, max_page_tokens, fast_multiplier, default_effort, max_output, source` | 05 §2.2; 09 §3.6 | mo-relay + mo-proto | 1 | NEW:E41 | todo |
| T-05-010 | OpenRouter catalog price = maximum across its upstream endpoints (for reservations) | 05 §2.2 | mo-relay | 1 | E02 | todo |
| T-05-011 | Prices apply to tasks started at or after `effective_at`; Nodes reject version decreases | 05 §2.2 | mo-relay + mo-node | 1 | NEW:E41 | todo |
| T-05-012 | Catalog is signed and logged as a `CATALOG` key-log entry; every Node verifies it | 05 §2.2 | mo-relay + mo-node | 3 | NEW:E41, NEW:E42 | todo |
| T-05-013 | Catalog update = operator action with 24 h `effective_at` delay, except price decreases (may apply immediately); OpenRouter imports reviewed then signed | 05 §2.2 | mo-relay | 1 | NEW:E41, NEW:E79 | todo |
| T-05-014 | Cost function `ceil((in×c.in + out×c.out + cw5m×c.cw5m + cw1h×c.cw1h + cr×c.cr) × fast_multiplier / 1e6)` | 05 §3 | mo-worker + mo-relay | 1 | NEW:CI-10, E01 | todo |
| T-05-015 | OpenRouter: receipt cost = `ceil(provider_cost)` donor-signed; Relay checks `cost ≤ reservation` | 05 §3 | mo-worker + mo-relay | 1 | E02, NEW:E40 | todo |
| T-05-016 | Usage mapping Anthropic: `input_tokens` (uncached), `output_tokens` (incl. thinking), `cache_creation` by TTL, `cache_read_input_tokens`, summed over `usage.iterations` | 05 §3 | mo-worker | 1 | E01, NEW:CI-17 | todo |
| T-05-017 | Usage mapping OpenAI/compatible: input = prompt − cached; output = completion (incl. reasoning); cache_read = cached prompt tokens; cache_write = 0 | 05 §3 | mo-worker | 2 | NEW:E78, NEW:CI-17 | todo |
| T-05-018 | Usage mapping DeepSeek: input = cache-miss prompt tokens; cache_read = cache-hit tokens; output incl. reasoning | 05 §3 | mo-worker | 1 | E03, NEW:CI-17 | todo |
| T-05-019 | Usage mapping OpenRouter: normalized prompt − cached; completion; cache fields when reported; `provider_cost` = charged cost (authoritative) | 05 §3 | mo-worker | 1 | E02, NEW:CI-17 | todo |
| T-05-020 | Worker always turns on stream usage reporting for OpenAI-style streams | 05 §3; 06 §7.2 | mo-worker | 1 | E02, NEW:E56 | todo |
| T-05-021 | Worker computes and signs `cost_uusd`; Relay recomputes from usage + catalog version (or checks OpenRouter bound); mismatch → reject + alert | 05 §3 | mo-relay | 1 | NEW:E40 | todo |
| T-05-022 | Pledge field `budget_per_period` (monthly, anchored on creation day) | 05 §4.1 | mo-relay | 1 | NEW:E38 | todo |
| T-05-023 | Pledge `per_task_cap` default $5 (5,000,000 µ$), donor-lowerable; console shows "requests blocked by task cap" | 05 §4.1 | mo-relay + mo-web | 1/4 | E10, NEW:E66 | todo |
| T-05-024 | Pledge `policy.models` with per-family wildcards (`anthropic/claude-sonnet-*`), `max_effort` (`low`…`max`), `dialects`, `flags` (`fast`, `images`, `documents`, `long_context`, …) | 05 §4.1 | mo-relay | 1 | NEW:E29 | todo |
| T-05-025 | Pledge optional `max_slots` and `schedule` windows; `visibility` public / pseudonymous / anonymous | 05 §4.1 | mo-relay + mo-web | 2/4 | NEW:E32, NEW:E68 | todo |
| T-05-026 | Pledge lifecycle: PendingApproval → Active (owner-signed `DONOR_APPROVED`) / Declined; Active ↔ Paused (donor, `moochy pause`, window); → Ended (full reclaim, owner revoke, repo deleted, ban) | 05 §4.2 | mo-relay | 1→3 | NEW:E39 | todo |
| T-05-027 | Each period a new `pledge_periods` row and `spent → 0` | 05 §4.2, §9 | mo-relay | 1 | NEW:E38 | todo |
| T-05-028 | `reserve(t,p) = ceil((est_input × c.in × m_cache + max_tokens × c.out) × fast_multiplier / 1e6)`, `m_cache` = 1.25 (5m), 2.0 (1h), 1.0 else; worked example 420,000 µ$ / 34,200 µ$ reproduces | 05 §5.1 | mo-relay + mo-worker | 1 | NEW:CI-10 | todo |
| T-05-029 | Reservations, settlements, receipts are per attempt `(task_id, attempt)` | 05 §5.2 | mo-relay | 1 | E06, E12 | todo |
| T-05-030 | Reserve: `reserved += r` on pledge, member, capped device; committed before `task.assign` | 05 §5.2 | mo-relay | 1 | E01, E12 | todo |
| T-05-031 | Settle (not estimated): `reserved −= r`, `spent += cost` on all three, attributed to the attempt's start period | 05 §5.2 | mo-relay | 1 | E01, NEW:E38 | todo |
| T-05-032 | Settle (estimated): pessimistically at `r`; a later donor-signed correction from `moochy audit --provider` may lower it | 05 §5.2 | mo-relay + mo-node | 1/2 | NEW:E37 | todo |
| T-05-033 | Release on proof of zero spend: `reserved −= r`, nothing spent | 05 §5.2 | mo-relay | 1 | E07, E09 | todo |
| T-05-034 | Superseded attempt without proof stays in `awaitingReceipt` until its receipt | 05 §5.2 | mo-relay | 2 | NEW:E28 | todo |
| T-05-035 | No receipt after 24 h and Worker absent → settle at `r`, flagged `pessimistic` | 05 §5.2 | mo-relay | 2 | NEW:E37 | todo |
| T-05-036 | Late receipt after pessimistic settle → correction `spent += cost − r` into the start period, flag cleared, never below 0 | 05 §5.2, §13 | mo-relay | 2 | NEW:E37 | todo |
| T-05-037 | Actual cost > reservation: overage settled honestly; pledge stops accepting new tasks for that period | 05 §5.2 | mo-relay | 1 | NEW:CI-10 | todo |
| T-05-038 | Layer 1 caps: Relay reservations | 05 §6 | mo-relay | 1 | E10 | todo |
| T-05-039 | Layer 2 caps: Worker local reservation per device before ack against monthly device cap (all pledges) and per-pledge counters, counting open attempts; settle to receipt cost; counters persisted with the outbox | 05 §6 | mo-worker + mo-node | 1 | E11 | todo |
| T-05-040 | Layer 3 caps: onboarding strongly recommends dedicated key + provider spend limit with deep links (OpenRouter per-key credit limit) | 05 §6; 07 §8.1 | mo-node + mo-docs* | 1 | NEW:E83, NEW:REV-02 | todo |
| T-05-041 | Worker writes the signed receipt to its outbox (append-only, fsync) **before** sending `task.end` | 05 §7 | mo-worker + mo-node | 1 | E12 | todo |
| T-05-042 | Relay commits the receipt with `synchronous=FULL` and only then sends `receipt.ack` | 05 §7 | mo-relay | 1 | E12 | todo |
| T-05-043 | Worker keeps acked entries 7 days; after DR restore Relay asks every Worker to `receipt.replay_since` | 05 §7 | mo-node + mo-relay | 2 | NEW:E36 | todo |
| T-05-044 | Settlement idempotent by `(task_id, attempt)`: identical bytes → no-op ack; different bytes → reject + alert + freeze device for review | 05 §7, §13 | mo-relay | 1 | E12, NEW:E36 | todo |
| T-05-045 | Receipt for an unknown task = protocol violation (reject + alert), except within a DR-restore window where accepted if the pledge belongs to the signing donor | 05 §7 | mo-relay | 1/2 | NEW:E40, NEW:E36 | todo |
| T-05-046 | Boot reconciliation: load balances, apply missed period rollovers before scheduling, mark open attempts `orphaned` (reservations kept); `known_tasks` releases orphans never held | 05 §7 | mo-relay | 1 | E12, NEW:E69 | todo |
| T-05-047 | Key-log checkpoints signed only for tree sizes Litestream has replicated | 05 §7; 06 §10.1 | mo-relay | 3 | NEW:E42 | todo |
| T-05-048 | Each op in a group commit runs in its own SAVEPOINT; a constraint violation is fatal (exit, restart, reload, outbox replay) | 05 §7; 09 §4 | mo-relay | 1 | NEW:E70 | todo |
| T-05-049 | Nightly audit job (read-only connection) recomputes `spent` per pledge-period, member-month, device-month from receipts; any difference pages | 05 §7 | mo-relay + mo-ops* | 1 | NEW:E70, NEW:MON-01 | todo |
| T-05-050 | `moochy audit --provider`: reconcile local journal with provider bill — Anthropic usage/cost API (admin key, local only) or export; OpenRouter generation stats/key usage; DeepSeek balance diff or export; OpenAI usage API or export | 05 §7.1 | mo-node + mo-worker | 1/2 | NEW:CI-20 | todo |
| T-05-051 | Reconciliation target ≤ 0.5% drift; a correction is a donor-signed entry applied by the Relay into the right period | 05 §7.1 | mo-node + mo-relay | 1/2 | NEW:CI-20, NEW:E37 | todo |
| T-05-052 | Partial reclaim: new headroom = `max(0, new_budget − spent − reserved)` effective at the next Scheduler event | 05 §8 | mo-relay + mo-web | 2 | NEW:E39 | todo |
| T-05-053 | Full reclaim = End pledge: no new reservations, open attempts settle, public page keeps history | 05 §8 | mo-relay | 2 | NEW:E39 | todo |
| T-05-054 | Pause is temporary and reversible; `moochy pause` stops all serving from the device instantly (zero slots, refuses assigns), works offline, no web login | 05 §8 | mo-node + mo-relay | 1 | NEW:E59, NEW:E39 | todo |
| T-05-055 | No "locked balance" / custody wording anywhere in the product | 05 §8 | mo-web + mo-node | 4 | NEW:REV-02 | todo |
| T-05-056 | Monthly periods anchored per pledge (created on the 17th → 17th–16th); member and device counters use calendar months | 05 §9 | mo-relay | 1/2 | NEW:E38 | todo |
| T-05-057 | Rollover (timer event or at boot) writes the `pledge_periods` row (`budget`, `spent`, `tasks`) and starts the new period at 0 | 05 §9 | mo-relay | 1 | NEW:E38 | todo |
| T-05-058 | Attribution to start period: settlement and corrections go into the attempt's start-period row even if closed | 05 §9 | mo-relay | 1 | NEW:E38 | todo |
| T-05-059 | Open reservations from the previous period count against headroom in the new period until settled | 05 §9 | mo-relay | 1 | NEW:E38 | todo |
| T-05-060 | No carry-over by default; `rollover = true` opt-in, capped at 1× budget | 05 §9 | mo-relay | 2 | NEW:E38 | todo |
| T-05-061 | Repo monthly goal ($/month) set by owner, shown on the repo page header | 05 §10 | mo-web + mo-relay | 4 | NEW:E66 | todo |
| T-05-062 | Committed = Σ budgets of Active pledges prorated to the calendar month; Used = Σ settled receipt costs this calendar month; Utilization = Used ÷ Committed | 05 §10 | mo-relay + mo-web | 4 | E19, NEW:CI-10 | todo |
| T-05-063 | Leaderboard = Σ cost of undisputed receipts per donor (month / all time), repo page and global page | 05 §10 | mo-relay + mo-web | 4 | NEW:E45, NEW:E66 | todo |
| T-05-064 | Donor count = distinct donors with an Active pledge (badge, repo page) | 05 §10 | mo-relay + mo-web | 4 | NEW:E66 | todo |
| T-05-065 | Member monthly cap (default 20% of Committed; owner unlimited) and per-device cap use reserve/settle/release, eligibility rule 9, invariants, audit, calendar-month reset | 05 §11 | mo-relay | 2 | NEW:E32, NEW:E70 | todo |
| T-05-066 | L1: `reserved ≥ 0`, `spent ≥ 0` via SQLite CHECK + Scheduler assertions (fatal) | 05 §12 | mo-relay | 1 | NEW:E70, NEW:CI-04 | todo |
| T-05-067 | L2: new reservations only when `spent + reserved + r ≤ budget` (and member/device equivalents) | 05 §12 | mo-relay | 1 | E10, NEW:E32 | todo |
| T-05-068 | L3: every settled attempt has exactly one receipt or a flagged pessimistic settlement | 05 §12 | mo-relay | 1 | NEW:E70 | todo |
| T-05-069 | L4: Σ open-attempt reservations = Σ `reserved`; checked in Scheduler and at boot | 05 §12 | mo-relay | 1 | NEW:CI-04, E12 | todo |
| T-05-070 | L5: Σ receipt costs per pledge-period / member-month / device-month = materialized `spent` | 05 §12 | mo-relay | 1 | NEW:E70 | todo |
| T-05-071 | L6: receipt cost = recomputed cost; OpenRouter `cost ≤ reservation` and = reported cost | 05 §12 | mo-relay | 1 | NEW:E40 | todo |
| T-05-072 | L7: a device never exceeds its local monthly cap counting open attempts (Worker, independent of Relay) | 05 §12 | mo-worker + mo-node | 1 | E11 | todo |
| T-05-073 | L8: no attempt assigned before its reservation is durable | 05 §12 | mo-relay | 1 | NEW:CI-04, E12 | todo |
| T-05-074 | Edge: provider error after partial stream → receipt `provider_error` with real usage, else `estimated` → pessimistic | 05 §13 | mo-worker + mo-node | 1 | NEW:E37 | todo |
| T-05-075 | Edge: refusal stop reason billed per provider usage like any completion | 05 §13 | mo-worker | 1 | NEW:CI-17 | todo |
| T-05-076 | Edge: catalog version in effect at **attempt start** applies (recorded at reservation) | 05 §13 | mo-relay | 1 | NEW:E41 | todo |
| T-05-077 | Edge: two attempts both reached the provider (start-timeout race) → both receipts settle; Gateway uses only the first started stream; visible in metrics | 05 §13 | mo-relay + mo-node | 2 | NEW:E49 | todo |
| T-05-078 | Edge: pledge Ended mid-task → attempt completes and settles to the Ended pledge | 05 §13 | mo-relay | 2 | NEW:E39 | todo |
| T-05-079 | Edge: donor deletes account → pledges Ended, open attempts settle, log entries stay (pseudonymous), pseudonym mapping deleted | 05 §13; 06 §10.3 | mo-relay + mo-web | 4 | NEW:E65 | todo |
| T-05-080 | Edge: period attribution uses the Relay's reservation time (clock skew between Worker and Relay) | 05 §13 | mo-relay | 1 | NEW:E38 | todo |

## 06 — Security and trust

Threat rows (T1–T22) name the mitigation that must exist; the detailed mechanism rows live in the sections below and in 03/05/07. `mo-sec` should add `A-` ids to these rows once `docs/security/attack-catalog.md` lands.

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-06-001 | T1: provider key never leaves the donor machine; OS keychain; sent only to allowlisted provider hosts | 06 §3 T1 | mo-worker + mo-node | 1 | NEW:E61, NEW:E60 | todo |
| T-06-002 | T2: request firewall prevents server-side execution, web fetch, MCP connectors, paid add-ons; provider headers sealed and allowlisted | 06 §3 T2 | mo-worker | 1 | E09, NEW:E57 | todo |
| T-06-003 | T3: firewall rejects any file reference, stored-response reference, or non-chat endpoint at any nesting depth | 06 §3 T3 | mo-worker | 1 | E09, NEW:E57 | todo |
| T-06-004 | T4: three-layer caps, Worker-checked deterministic estimate, route header bound to body | 06 §3 T4 | mo-relay + mo-worker | 1 | E10, E11, E15 | todo |
| T-06-005 | T5: Worker route/body consistency with exact estimate match | 06 §3 T5 | mo-worker | 1 | NEW:E57 | todo |
| T-06-006 | T6: E2E envelopes with per-body request keys and per-attempt response keys; relay DB stores no content | 06 §3 T6 | mo-proto + mo-relay | 1 | E13, E17 | todo |
| T-06-007 | T7: Gateways seal only to logged keys of users holding an owner-signed `DONOR_APPROVED`; Nodes alert on unknown own keys and unsigned approvals/claims; anchored checkpoints | 06 §3 T7 | mo-node + mo-relay | 3 | NEW:E42, NEW:E43, NEW:E44 | todo |
| T-06-008 | T8: owner approval per donor, pinned donors, tool-call checks + tripwire, signed checkpoints on every tool call, human-approval guidance | 06 §3 T8 | mo-node + mo-worker | 3 | E18, NEW:E46 | todo |
| T-06-009 | T9: Gateway task signatures, owner-signed `MEMBER_ADDED`, pledge↔repo check, ULID freshness, served-task set | 06 §3 T9 | mo-node + mo-worker | 1→3 | E16, NEW:E43, NEW:E58 | todo |
| T-06-010 | T10: Gateway checks commitments, usage bands, reported model; signed disputes; leaderboard counts only undisputed receipts | 06 §3 T10 | mo-node + mo-relay | 3 | NEW:E45 | todo |
| T-06-011 | T11: donor-signed receipts/projections, owner-signed approvals, append-only key log with externally anchored signed checkpoints | 06 §3 T11 | mo-relay + mo-node | 3 | NEW:E44, NEW:E63 | todo |
| T-06-012 | T12: auth signature covers dialed origin + TLS channel binding | 06 §3 T12 | mo-node + mo-relay | 1 | NEW:E23 | todo |
| T-06-013 | T13: `moochy logout` / web revoke → `KEY_REVOKED`; Relay drops the device at once | 06 §3 T13 | mo-node + mo-relay + mo-web | 1→3 | NEW:E73, NEW:E65 | todo |
| T-06-014 | T14: loopback only, repo-scoped random tokens, Host check, no CORS, port held by OS service manager, `doctor` checks listening uid | 06 §3 T14 | mo-node | 1/5 | E14, NEW:E83 | todo |
| T-06-015 | T15: MCP `files` root = recorded git top-level ∩ client roots; realpath containment; no symlinks; deny `.git/**` + secret-shaped files; `git check-ignore` | 06 §3 T15 | mo-node | 3 | NEW:E48 | todo |
| T-06-016 | T16: SameSite=Lax cookies; state changes require `HX-Request` + Origin; strict CSP; auto-escaping templates | 06 §3 T16 | mo-web | 4 | NEW:E65 | todo |
| T-06-017 | T17: signed releases with provenance, reproducible Linux builds, dependency vetting, no silent auto-update | 06 §3 T17 | mo-release* + mo-node | 3 | NEW:CI-08, NEW:E83 | todo |
| T-06-018 | T18: GitHub/GitLab identity; repo claims need admin permission; owner approval of donors; rate limits | 06 §3 T18 | mo-relay + mo-web | 1/4 | NEW:E65, NEW:E80 | todo |
| T-06-019 | T19: donors pledge only to repos they choose and that approve them; pseudonymous `metadata.user_id`; local journal; explicit donor consent | 06 §3 T19 | mo-worker + mo-node | 1 | NEW:E56, NEW:E62 | todo |
| T-06-020 | T20: Gateway secret scrubber before sealing (also on MCP files) | 06 §3 T20 | mo-node | 3 | NEW:E47 | todo |
| T-06-021 | T21: prompt-cache timing side channel accepted (low); documented in the public threat model | 06 §3 T21 | mo-sec | 6 | NEW:REV-02 | todo |
| T-06-022 | T22: per-IP connection limits, per-device rate limits, byte budgets for buffered bodies, sheddable submit queue | 06 §3 T22 | mo-relay | 2 | NEW:E80, NEW:E51 | todo |
| T-06-023 | Device keys created by `moochy login` on the device, never exported: one Ed25519 + one X25519 | 06 §4.1 | mo-node | 1 | NEW:E73 | todo |
| T-06-024 | Keys stored in OS keychain; headless fallback: scrypt passphrase-encrypted file, or `systemd-creds` / TPM-bound credentials | 06 §4.1 | mo-node | 1/5 | NEW:E73, NEW:CI-16 | todo |
| T-06-025 | Registration binds `{device, user, sign_pub, enc_pub, roles, suite}` and appends `KEY_ADDED` with a proof-of-possession signature by the new key | 06 §4.1 | mo-relay + mo-node | 1→3 | NEW:E42 | todo |
| T-06-026 | `moochy keys rotate`: new device record; old one revoked after a 24 h grace; both logged | 06 §4.1 | mo-node + mo-relay | 3 | NEW:E73 | todo |
| T-06-027 | `KEY_REVOKED` takes effect immediately at the Relay and is published in the key log | 06 §4.1 | mo-relay | 1→3 | NEW:E73 | todo |
| T-06-028 | Provider keys added via `moochy keys add <provider>` with interactive prompt or stdin — never a CLI argument; stored in keychain | 06 §4.2; CONTRACT §6 | mo-node | 1 | NEW:E60 | todo |
| T-06-029 | Provider key validated on add and periodically with a free models-endpoint call; Worker advertises exactly the models the key can use | 06 §4.2 | mo-worker + mo-node | 1 | NEW:E60 | todo |
| T-06-030 | Provider keys never sent to the Relay, never logged, never in crash reports (redaction unit-tested) | 06 §4.2 | mo-node + mo-worker | 1 | NEW:E61, NEW:CI-12 | todo |
| T-06-031 | Relay log-signing key (Ed25519, signed-note format) generated offline; loaded from encrypted file or KMS at boot; yearly rotation with dual signing during transition | 06 §4.3 | mo-relay + mo-ops* | 3 | NEW:E42, NEW:REV-05 | todo |
| T-06-032 | Relay catalog-signing key handled like the log key | 06 §4.3 | mo-relay + mo-ops* | 3 | NEW:E41 | todo |
| T-06-033 | No Relay key can decrypt user content | 06 §4.3 | mo-relay | — | E13 | todo |
| T-06-034 | Web users authenticate with GitHub/GitLab OAuth → session cookie | 06 §5 | mo-relay + mo-web | 1/5 | NEW:E65 | todo |
| T-06-035 | Node roles granted at approval: `gateway`, `worker`, optionally scoped to one repo | 06 §5 | mo-relay | 1 | E01, NEW:E32 | todo |
| T-06-036 | Repo owner: provider API confirms **admin** permission with the user's OAuth token at claim (used once, not stored); owner's Node signs `REPO_CLAIMED` | 06 §5 | mo-relay + mo-node | 1→3 | NEW:E65, NEW:E84 | todo |
| T-06-037 | Approvals signed by the owner's device (`moochy approve`, `moochy members add`, or confirming in `moochy status`); Relay can show but not forge | 06 §5 | mo-node + mo-relay | 3 | NEW:E84, NEW:E43 | todo |
| T-06-038 | No automatic membership from push access (membership is owner-signed only) | 06 §5 | mo-relay | — | NEW:E43 | todo |
| T-06-039 | Public repositories only on the public instance; private pools via self-hosted relays | 06 §5; ADR-31 | mo-relay | 1 | NEW:E65 | todo |
| T-06-040 | E2E costs paid: validation moves to Worker (firewall) and Gateway (scrubber, tool checks); usage from donor-signed receipts; no relay moderation (documented in terms) | 06 §6 | mo-worker + mo-node | 1 | E09, E18 | todo |
| T-06-041 | Firewall rule: allowlist (never denylist), recursive, per adapter: endpoints, headers + values, top-level fields, content-block types (incl. nested in `tool_result`/documents), tool types; unknown → `nack{firewall}` | 06 §7 | mo-worker | 1 | E09, NEW:E57 | todo |
| T-06-042 | Firewall reason sealed to the Gateway; the Relay sees only the code | 06 §7 | mo-node + mo-worker | 1 | E09 | todo |
| T-06-043 | Anthropic: allow only `POST /v1/messages`; deny `count_tokens` and every other endpoint (batches, files, models, skills, agents) | 06 §7.1 | mo-worker | 1 | NEW:E57 | todo |
| T-06-044 | Anthropic: provider headers sealed in the inner payload, covered by `req_commit`, allowlisted per catalog version; unknown beta values rejected | 06 §7.1 | mo-worker + mo-node | 1 | NEW:E57 | todo |
| T-06-045 | Anthropic: `model` allowed only if in pledge policy and offered by this key (after slug mapping) | 06 §7.1 | mo-worker + mo-node | 1 | NEW:E57 | todo |
| T-06-046 | Anthropic: `max_tokens` required and ≤ catalog `max_output` | 06 §7.1 | mo-worker | 1 | NEW:E57 | todo |
| T-06-047 | Anthropic allow: `messages`, `system`, `stop_sequences`, accepted sampling params, `stream`, `metadata`, `thinking`, `output_config.effort` (≤ pledge `max_effort`), `output_config.format`, `cache_control` top-level and per block | 06 §7.1 | mo-worker | 1 | E01, NEW:CI-13 | todo |
| T-06-048 | Anthropic content blocks allowed: `text`, `image` (base64, needs `images` flag), `document` (base64/plain text, needs `documents` flag; strict denies PDFs), `tool_use`, `tool_result`, `thinking`, `redacted_thinking` | 06 §7.1 | mo-worker | 1 | E09, NEW:E57 | todo |
| T-06-049 | Anthropic: deny any content whose source is a file id or a URL, at any depth | 06 §7.1 | mo-worker | 1 | E09 | todo |
| T-06-050 | Anthropic: allow custom `tools[]` with `input_schema` and Anthropic client-executed tools (bash, text editor, memory, client-side computer use) | 06 §7.1 | mo-worker | 1 | NEW:CI-13 | todo |
| T-06-051 | Anthropic: deny server-executed tools (web search, web fetch, code execution, tool search, advisor, server-hosted computer use) — no opt-in in v1 | 06 §7.1 | mo-worker | 1 | E09 | todo |
| T-06-052 | Anthropic: deny `mcp_servers` / MCP toolsets, `container`, skills, server-side model fallbacks | 06 §7.1 | mo-worker | 1 | E09, NEW:E57 | todo |
| T-06-053 | Anthropic: `speed: fast` denied unless pledge has `fast`; `service_tier`, `inference_geo` denied unless policy allows | 06 §7.1 | mo-worker | 1 | NEW:E57 | todo |
| T-06-054 | Safe mutation: `metadata.user_id` = pseudonymous `H(repo_id ‖ member_id)` | 06 §7.1 | mo-worker | 1 | NEW:E56 | todo |
| T-06-055 | Safe mutation: public model id → provider model id via the signed catalog; `req_commit` computed before any mutation | 06 §7.1 | mo-worker | 1 | NEW:E56 | todo |
| T-06-056 | OpenAI-compatible: allow `POST /v1/chat/completions` with messages, function tools, standard sampling, reasoning effort | 06 §7.2 | mo-worker | 1 | E02 | todo |
| T-06-057 | OpenAI-compatible deny: hosted/built-in tools, web-search options, `n > 1`, predicted outputs, `service_tier`, audio/other modalities, file or stored-response references, non-chat endpoints | 06 §7.2 | mo-worker | 1 | E09, NEW:E57 | todo |
| T-06-058 | OpenAI-compatible safe mutations: force `store: false` where storage exists; force stream usage reporting | 06 §7.2 | mo-worker | 1 | E02, NEW:E56 | todo |
| T-06-059 | OpenRouter (both dialects): deny `models[]` fallbacks, `route`, `plugins`, `:online` and other uncatalogued variants; set max-price to the catalog price; settle on reported cost | 06 §7.2 | mo-worker | 1 | E02, NEW:E56, NEW:E57 | todo |
| T-06-060 | DeepSeek (both dialects): plain chat + reasoning models, text only | 06 §7.2 | mo-worker | 1 | E03, NEW:E57 | todo |
| T-06-061 | Other OpenAI-compatible hosts: only vetted list, each with its own table | 06 §7.2 | mo-worker | 2–5 | NEW:E78 | todo |
| T-06-062 | Exact endpoints and field names per provider pinned in Phase 0 (adapter data tables v0) | 06 §7.2; 11 Ph0 | mo-worker | 0 | NEW:CI-17 | todo |
| T-06-063 | Firewall written as data (per-adapter table) interpreted by a small recursive validator; allowlist changes are small diffs | 06 §7.3 | mo-worker | 1 | NEW:CI-13 | todo |
| T-06-064 | Firewall fuzzed continuously with a corpus of real client traffic + mutations incl. deep nesting | 06 §7.3 | mo-worker | 1/3 | NEW:CI-03 | todo |
| T-06-065 | Two-person review for any change that widens an allowlist (CODEOWNERS / branch rule) | 06 §7.3 | mo-release* + integrator | 1 | NEW:REV-05 | todo |
| T-06-066 | Opt-in Worker telemetry reports rejected **field names only**, never values | 06 §7.3; 10 §5.2 | mo-node + mo-relay | 2 | NEW:E82 | todo |
| T-06-067 | Donor strictness levels: `strict` (default) and `paranoid` (also deny images/documents, lower `max_tokens` ceiling) | 06 §7.3; 07 §6.4 | mo-worker + mo-node | 1 | NEW:E57, NEW:E59 | todo |
| T-06-068 | Repo owner approves each donor by signature (approval required) | 06 §8 | mo-node + mo-relay | 1→3 | NEW:E43 | todo |
| T-06-069 | Pinned donors: maintainer can restrict a session or repo to named donors (default off) | 06 §8; 08 §2 | mo-node + mo-relay + mo-web | 3/4 | NEW:E43 | todo |
| T-06-070 | Structural tool-call checks: hold each tool call until its end; reject names not in request `tools[]`, inputs failing `input_schema`, forbidden block types (`server_tool_use`, `mcp_tool_use`, server tool results), mismatched model | 06 §8 | mo-worker (inspection) + mo-node | 3 | E18 | todo |
| T-06-071 | Tool calls released only after a verified Worker progress signature covering them | 06 §8 | mo-node | 3 | NEW:E46 | todo |
| T-06-072 | Tripwire: pattern scan for pipe-to-shell, credential paths, persistence locations, encoded payloads, raw-IP connections; hit → error tool result with visible warning (warn + block default) | 06 §8 | mo-worker + mo-node | 3 | E18, NEW:CI-14 | todo |
| T-06-073 | `moochy_delegate` results wrapped as "untrusted content from donor X" and scanned like tool calls | 06 §8; 07 §5.1 | mo-node | 3 | E04, NEW:E81 | todo |
| T-06-074 | Onboarding and `moochy connect` state "keep command approval on in your agent when using pooled compute" | 06 §8 | mo-node + mo-docs* | 3 | NEW:E75 | todo |
| T-06-075 | Tripwire documented as a speed bump, not a guarantee (docs + console wording) | 06 §8; 11 Ph3 | mo-sec + mo-docs* | 3 | NEW:REV-02 | todo |
| T-06-076 | `moochy report <task_id>` packages receipt, progress checkpoints, response bytes, and only `S_resp` | 06 §9 | mo-node | 3 | NEW:E64 | todo |
| T-06-077 | Anyone with the bundle verifies donor signatures and recomputes `resp_commit` | 06 §9 | mo-node + mo-relay | 3 | NEW:E64 | todo |
| T-06-078 | Outcomes: warning, owner revokes approval, or ban (`KEY_REVOKED` for all donor devices, pledges Ended) recorded as pseudonymous `MODERATION` entry | 06 §9 | mo-relay | 3 | NEW:E64, NEW:E79 | todo |
| T-06-079 | Disputes against maintainers handled by the same process in reverse (donor journal + signed receipt as evidence) | 06 §9 | mo-relay + human-po* | 3 | NEW:E64 | todo |
| T-06-080 | Key log = one append-only RFC 6962-style Merkle tree (`x/mod/sumdb/tlog` hashing/proofs, C2SP tlog-tiles paths), signed-note checkpoints | 06 §10.1 | mo-relay | 3 | NEW:E42, NEW:CI-01 | todo |
| T-06-081 | Entry kinds and signers: `KEY_ADDED`/`KEY_REVOKED` (Relay + new key PoP), `REPO_CLAIMED` (Relay + owner device), `DONOR_APPROVED`/`DONOR_REVOKED`, `MEMBER_ADDED`/`MEMBER_REMOVED` (owner device), `CATALOG` (catalog key), `MODERATION` (Relay) | 06 §10.1 | mo-relay + mo-proto | 3 | NEW:E42, NEW:E43 | todo |
| T-06-082 | Every Node mirrors the full key log (~100k entries/year) | 06 §10.1 | mo-node | 3 | NEW:E42 | todo |
| T-06-083 | Every Node alerts on any key on its own account it did not create (with the revoke command in the message) | 06 §10.1 | mo-node | 3 | NEW:E42 | todo |
| T-06-084 | Owner's Node alerts on any `REPO_CLAIMED`, approval, or membership for its repos it did not sign | 06 §10.1 | mo-node | 3 | NEW:E43 | todo |
| T-06-085 | Gateways seal only to worker keys logged, unrevoked, with owner-signed `DONOR_APPROVED` for the repo | 06 §10.1 | mo-node | 3 | NEW:E43 | todo |
| T-06-086 | Workers accept tasks only from Gateway keys whose user has owner-signed `MEMBER_ADDED` (or is owner) | 06 §10.1 | mo-node | 3 | NEW:E43 | todo |
| T-06-087 | Checkpoints signed every 60 s while the log grows (replicated sizes only), pushed to Nodes, checked with consistency proofs | 06 §10.1 | mo-relay + mo-node | 3 | NEW:E42 | todo |
| T-06-088 | Hourly checkpoints committed to a public Git repository from day one; Nodes compare relay-served checkpoints against it | 06 §10.1 | mo-relay + mo-node + mo-ops* | 3 | NEW:E44 | todo |
| T-06-089 | Independent witness cosignatures (C2SP witness protocol) after beta | 06 §10.1 | mo-relay + mo-node | D | NEW:MON-03 | todo |
| T-06-090 | Receipts not in the log in v1; public receipt log (Merkle tree of projections + inclusion proofs) post-beta on demand | 06 §10.2 | mo-relay | D | NEW:MON-03 | todo |
| T-06-091 | Log contains only pseudonymous ids, device public keys, repo ids, signatures, catalog data; `pseudonym → username/avatar` lives in the mutable DB and is deleted with the account | 06 §10.3 | mo-relay | 3 | NEW:E42, NEW:E65 | todo |
| T-06-092 | Privacy: prompts/outputs nowhere on the Relay; only local journals (full text opt-in) | 06 §11 | mo-relay + mo-node | 1 | E13, NEW:E62 | todo |
| T-06-093 | Privacy: task metadata 90 days raw, then daily aggregates; only aggregates public | 06 §11 | mo-relay | 1 | NEW:E85 | todo |
| T-06-094 | Privacy: full receipts kept in Relay DB while the account exists, not public | 06 §11 | mo-relay + mo-web | 1 | NEW:E68 | todo |
| T-06-095 | Privacy: projections public forever, pseudonymous, daily granularity | 06 §11 | mo-relay + mo-web | 4 | NEW:E68 | todo |
| T-06-096 | Privacy: presence live in memory only; aggregated by default; per-donor presence only on opt-in | 06 §11; ADR-28 | mo-relay + mo-web | 4 | NEW:E68 | todo |
| T-06-097 | Privacy: IP addresses only in connection logs, retained 7 days | 06 §11 | mo-relay + mo-ops* | 1 | NEW:E85 | todo |
| T-06-098 | Privacy: OAuth identity kept until account deletion, public per pledge visibility | 06 §11 | mo-relay + mo-web | 4 | NEW:E68 | todo |
| T-06-099 | Signed releases (Sigstore keyless, CI identity) with SLSA provenance; users verify externally (`gh attestation verify`, `cosign verify-blob`) | 06 §12 | mo-release* | 3 | NEW:CI-08 | todo |
| T-06-100 | Reproducible builds for Linux musl artifacts required for beta; other platforms when feasible | 06 §12 | mo-release* | 3 | NEW:CI-08 | todo |
| T-06-101 | `cargo-deny` (licenses, advisories, bans) and `cargo-vet` audits; `hpke` explicitly vetted | 06 §12 | mo-release* + mo-proto | 3 | NEW:CI-08 | todo |
| T-06-102 | No silent auto-update; Node announces new versions; `moochy update` verifies signatures before replacing itself | 06 §12 | mo-node | 3/5 | NEW:E83 | todo |
| T-06-103 | Relay built and signed the same way; moochy.dev publishes the release it runs; `hello.relay_release` reports it | 06 §12 | mo-release* + mo-relay | 3 | NEW:E23, NEW:CI-08 | todo |
| T-06-104 | Public `SECURITY.md`, private disclosure channel, coordinated disclosure, reporter credit | 06 §12; 11 Ph0 | mo-sec + mo-docs* | 0 | NEW:REV-02 | todo |
| T-06-105 | Gateway/MCP bind `127.0.0.1` / `::1` only, never `0.0.0.0` | 06 §13 | mo-node | 1 | E14 | todo |
| T-06-106 | Port held by OS service manager (launchd socket / systemd `.socket`); `moochy doctor` checks listening uid | 06 §13 | mo-node | 5 | NEW:E83 | todo |
| T-06-107 | Local tokens random, repo-scoped, prefixed `mooch_local_…`, rotatable (`moochy env --rotate`), constant-time compared | 06 §13; AGENTS §3 | mo-node | 1 | E14, NEW:E76 | todo |
| T-06-108 | `moochy connect --write` writes tokens only to user-scoped configs / env indirection / stdio shim; refuses any git-tracked file | 06 §13 | mo-node | 1 | NEW:E75 | todo |
| T-06-109 | DNS-rebinding defense: reject `Host` not equal to loopback address + port; no CORS headers | 06 §13 | mo-node | 1 | E14 | todo |
| T-06-110 | MCP `files`: root = git top-level recorded with the token ∩ client MCP roots (or shim cwd/recorded root when none); realpath containment; symlinks refused; `.git/**`, `.env*`, `.npmrc`, `.netrc`, `*.pem`, `id_*`, `*.kdbx` denied even when tracked; git-ignored refused; total ≤ 2 MiB default | 06 §13; 07 §5.2 | mo-node | 3 | NEW:E48 | todo |
| T-06-111 | Secret scrubber before sealing (bodies and MCP files): cloud keys, private-key blocks, provider API keys, JWTs, `.env`-style known secret assignments → `[REDACTED:type]`; modes `redact` (default) / `warn` | 06 §13 | mo-node | 3 | NEW:E47 | todo |
| T-06-112 | Own-key fallback (optional, off by default): Gateway calls provider directly with the maintainer's own key when the pool cannot serve | 06 §13; 07 §4.3 | mo-node + mo-worker | 5 | NEW:E86 | todo |
| T-06-113 | API keys only: subscription/consumer credentials refused technically; adapters accept only API-key auth against official hosts | 06 §14; ADR-29 | mo-worker | 1 | NEW:E60 | todo |
| T-06-114 | Donor is customer of record; onboarding obtains explicit consent with the counsel-approved text | 06 §14 | mo-node + human-counsel* | 1/6 | NEW:E83, NEW:REV-01 | todo |
| T-06-115 | Counsel review of each provider's terms: third-party end users with attribution, resale (no payment), abuse handling | 06 §14 | human-counsel* | 0 | NEW:REV-01 | todo |
| T-06-116 | Research: opt-in free verified mode (TLS notarization with the Relay as notary; TEEs for donor cloud hosts) | 06 §15 | mo-proto + mo-worker + mo-relay | R | NEW:MON-03 | todo |
| T-06-117 | T23: unique ASCII-only lowercase handles, case-insensitive uniqueness, reserved words, permanent tombstones, control characters escaped wherever printed | 06 §3 T23; CONTRACT §11 | mo-relay + mo-node + mo-web | 1 | E21 | todo |

## 07 — Client: the `moochy` binary

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-07-001 | One binary `moochy`; no account tier, no telemetry by default, no paywalled feature | 07 §1 | mo-node | 1 | NEW:E82, NEW:REV-02 | todo |
| T-07-002 | One background Node per machine (`moochy up`, OS service, or headless) holding the only relay connection, unlocked keys, all state | 07 §1; ADR-05 | mo-node | 1 | NEW:E74 | todo |
| T-07-003 | Roles `gateway` and/or `worker` are capabilities of one Node | 07 §1 | mo-node | 1 | E01 | todo |
| T-07-004 | Thin front-ends (stdio MCP shim, CLI `status/pause/resume/approve/members/journal`) talk to the Node through gRPC `LocalControl` on the local Unix socket | 07 §1, §3; CONTRACT §6, §12 | mo-node | 1 | NEW:E74 | todo |
| T-07-005 | `moochy login` (device-approval flow, keys created, roles); CONTRACT form `--relay --ca-file --roles --headless` with JSON events | 07 §2; CONTRACT §6 | mo-node | 1 | E01 | todo |
| T-07-006 | `moochy logout`: `KEY_REVOKED` and local keys wiped | 07 §2 | mo-node | 1→3 | NEW:E73 | todo |
| T-07-007 | `moochy up` / `down` / `status` (connection, roles, slots, budgets, last checkpoint, pending approvals) | 07 §2 | mo-node | 1 | E01, NEW:E83 | todo |
| T-07-008 | `moochy service install` / `uninstall` (launchd / systemd user unit / Windows) | 07 §2, §9 | mo-node | 1/5 | NEW:E83 | todo |
| T-07-009 | `moochy keys add <provider>` / `list` / `remove` / `rotate` / `revoke <device>` | 07 §2 | mo-node | 1/3 | NEW:E60, NEW:E73 | todo |
| T-07-010 | `moochy donate`: interactive pledge creation | 07 §2 | mo-node | 1 | NEW:E84 | todo |
| T-07-011 | `moochy claim <owner/repo>`: sign repo claim | 07 §2 | mo-node | 1→3 | NEW:E84 | todo |
| T-07-012 | `moochy pledges`: list with budget / spent / reserved | 07 §2 | mo-node | 1 | NEW:E84 | todo |
| T-07-013 | `moochy pause` / `resume`: instant local kill switch for the Worker role, works offline | 07 §2 | mo-node | 1 | NEW:E59 | todo |
| T-07-014 | `moochy env [--repo] [--shell] [--json] [--rotate]`: base URL + repo-scoped token per dialect; detects repo from git remote | 07 §2; CONTRACT §6 | mo-node | 1 | E01, NEW:E76 | todo |
| T-07-015 | `moochy mcp [--repo]`: stdio MCP shim; Streamable HTTP always on in the Node | 07 §2 | mo-node | 1 | E04, E05 | todo |
| T-07-016 | `moochy connect <client> [--write]` for `claude-code, opencode, cursor, cline, continue, zed, goose, windsurf, vscode, claude-desktop, aider, generic-mcp, generic-openai, generic-anthropic`; `--write` shows a diff before merging | 07 §2 | mo-node | 1/5 | NEW:E75 | todo |
| T-07-017 | `moochy journal [--follow] [--full]` | 07 §2 | mo-node | 1 | NEW:E62 | todo |
| T-07-018 | `moochy verify [receipt_ref\|task_id]`: projection vs donor key in mirrored key log, key log vs public Git anchor | 07 §2; 08 §6 | mo-node | 3 | NEW:E63 | todo |
| T-07-019 | `moochy audit --provider` | 07 §2; 05 §7.1 | mo-node | 1/2 | NEW:CI-20 | todo |
| T-07-020 | `moochy report <task_id>`: package and file an evidence bundle | 07 §2 | mo-node | 3 | NEW:E64 | todo |
| T-07-021 | `moochy doctor`: keychain, connectivity, clock skew, provider key health, firewall version, service status, port owner uid | 07 §2 | mo-node | 1/5 | NEW:E83 | todo |
| T-07-022 | `moochy update`: signed update; provenance verified externally | 07 §2 | mo-node + mo-release* | 5 | NEW:E83 | todo |
| T-07-023 | `moochy approve <donor>`, `moochy members add\|remove <user> [--device]`: owner-signed with this device | 07 §2, §8.4 | mo-node | 3 | NEW:E84 | todo |
| T-07-024 | One multi-threaded tokio runtime; lightweight task per request; no thread per connection | 07 §3 | mo-node | 1 | NEW:CI-07 | todo |
| T-07-025 | Gateway endpoint `POST /v1/messages` (Anthropic, streaming + non-streaming) | 07 §4.1 | mo-node | 1 | E01 | todo |
| T-07-026 | `POST /v1/messages/count_tokens` answered locally with the deterministic (pessimistic) estimate; no relay, no slot | 07 §4.1; ADR-23 | mo-node | 1 | NEW:E53 | todo |
| T-07-027 | `POST /v1/chat/completions` (OpenAI, streaming + non-streaming) | 07 §4.1 | mo-node | 1 | E02 | todo |
| T-07-028 | `GET /v1/models` served locally from the pool snapshot: models offered to this repo as slugs + native aliases | 07 §4.1 | mo-node | 1 | NEW:E53 | todo |
| T-07-029 | `POST/GET /mcp` Streamable HTTP with the local token as bearer | 07 §4.1 | mo-node | 1 | E05 | todo |
| T-07-030 | Default port configurable, chosen at first run and stable across restarts; printed by `env` and `connect` | 07 §4.1 | mo-node | 1 | NEW:E76 | todo |
| T-07-031 | Pipeline 1–2: authenticate token → repo; validate shape; require `max_tokens`, inject catalog default if missing and tell the user once | 07 §4.2 | mo-node | 1 | E14, NEW:E53 | todo |
| T-07-032 | Pipeline 3: scrub secrets | 07 §4.2 | mo-node | 3 | NEW:E47 | todo |
| T-07-033 | Pipeline 4: optional Anthropic auto-caching (multi-turn without `cache_control` → top-level 5 min); disable per repo | 07 §4.2 | mo-node | 2 | NEW:E55 | todo |
| T-07-034 | Pipeline 5–6: derive affinity key, look up session table, compute route header, sign task | 07 §4.2 | mo-node | 1/2 | E01, NEW:E30 | todo |
| T-07-035 | Pipeline 7: zstd level 3 → seal under fresh CK → wrap for affinity worker + top candidates (≤ 8), only to owner-approved keys | 07 §4.2 | mo-node | 1→3 | E01, NEW:E43 | todo |
| T-07-036 | Pipeline 8: decrypt accepted attempt only, write the provider's original bytes unchanged, compute `resp_commit` incrementally, hold tool calls until end + checks + signature | 07 §4.2 | mo-node | 1→3 | E01, E18, NEW:E46 | todo |
| T-07-037 | Pipeline 9: check receipt, silent or signed dispute; update session table; write journal entry | 07 §4.2 | mo-node | 1→3 | NEW:E45, NEW:E62 | todo |
| T-07-038 | Pool empty / member quota exhausted → native error with clear message, or own-key fallback when enabled | 07 §4.3 | mo-node | 2/5 | E10, NEW:E86 | todo |
| T-07-039 | Response headers `x-moochy-task`, `x-moochy-donor` (pseudonym), `x-moochy-cost-uusd` | 07 §4.3 | mo-node | 1 | NEW:E53 | todo |
| T-07-040 | Integration: OpenCode on both doors at once; `connect` sets main + small model to pool ids | 07 §4.4 | mo-node | 1 | NEW:CI-20, NEW:E75 | todo |
| T-07-041 | Integration: Claude Code via MCP (user-scoped config / `claude mcp add`) and `ANTHROPIC_BASE_URL` + token, on Anthropic, OpenRouter, DeepSeek donors; `connect` sets small/fast model | 07 §4.4 | mo-node | 1 | NEW:CI-20, E03 | todo |
| T-07-042 | Integration: Cursor (MCP always; API door documented as cloud-routed caveat) | 07 §4.4 | mo-node + mo-docs* | 5 | NEW:CI-20 | todo |
| T-07-043 | Integration: Cline, Continue, Zed, Goose, Windsurf, VS Code agent mode (MCP; API where base URL supported) | 07 §4.4 | mo-node | 5 | NEW:CI-20, NEW:E75 | todo |
| T-07-044 | Integration: Claude Desktop and other MCP chat apps | 07 §4.4 | mo-node | 5 | NEW:CI-20 | todo |
| T-07-045 | Integration: Aider, LiteLLM, Open WebUI, scripts, OpenAI/Anthropic SDKs via base URL `http://127.0.0.1:<port>/v1` | 07 §4.4 | mo-node | 1/5 | NEW:CI-20 | todo |
| T-07-046 | Integration: agent frameworks (OpenAI Agents SDK, LangGraph, Pydantic AI, CrewAI, Mastra, Claude Agent SDK) via `/mcp` or stdio and via base URL, incl. CI/containers | 07 §4.4 | mo-node | 1 | NEW:CI-20, E05 | todo |
| T-07-047 | Remote-HTTPS-only MCP clients: unsupported by default; Phase 5 opt-in self-tunnel exposes the user's own `/mcp` with OAuth 2.1 + Host allowlist | 07 §4.4; ADR-30 | mo-node | 5 | NEW:E87 | todo |
| T-07-048 | One MCP server (built on `rmcp`) over two transports: stdio (shim starts the Node if needed; startup a few ms) and Streamable HTTP | 07 §5 | mo-node | 1 | E04, E05, NEW:E74 | todo |
| T-07-049 | Zero-install `moochy` npm package fetching the signed binary (`npx -y moochy mcp`) | 07 §5, §11 | mo-release* | 5 | NEW:CI-08 | todo |
| T-07-050 | Tool `moochy_delegate`: `prompt` (req), `system?`, `files?`, `model?` (enum of pool ids), `effort?`, `max_tokens?`, `output?` (`text` / `json` + schema) → untrusted-wrapped result + usage/cost line | 07 §5.1 | mo-node | 1 | E04, NEW:E81 | todo |
| T-07-051 | Tool `moochy_pool_status`: pool budget left this month, member quota, models online with providers, donor count | 07 §5.1 | mo-node | 1 | E04 | todo |
| T-07-052 | Exactly two tools; tools-changed notification when pool models change (where supported); server `instructions` carry when-to-delegate guidance | 07 §5.1 | mo-node | 1/2 | E04, NEW:E81 | todo |
| T-07-053 | `files` read by the Node under 06 §13 rules, incl. no-roots fallback to shim cwd / recorded root; scrubbed; content never enters the caller's context | 07 §5.2 | mo-node | 3 | NEW:E48 | todo |
| T-07-054 | MCP progress notifications for long delegations (where supported); cancellation propagates to the provider call | 07 §5.2 | mo-node | 2 | NEW:E81 | todo |
| T-07-055 | Default delegation sized to ~1 min client timeout (`max_tokens` accordingly); `connect` raises tool-timeout settings where they exist | 07 §5.2 | mo-node | 1/5 | NEW:E75, NEW:E81 | todo |
| T-07-056 | Parallel `moochy_delegate` calls run concurrently and spread across donors | 07 §5.2 | mo-node + mo-relay | 2 | NEW:E81 | todo |
| T-07-057 | `model` defaults to the repo default set by the owner; Node builds the request in the dialect the chosen model's donors serve | 07 §5.2 | mo-node | 1 | E04, NEW:E81 | todo |
| T-07-058 | Tool descriptions written for models (when to delegate / when not) | 07 §5.2 | mo-node | 1 | NEW:CI-15 | todo |
| T-07-059 | Worker pipeline steps 1–9 in order (open, authenticity, firewall + route check, local reservation, ack, safe mutations + warm HTTP/2, stream + seal + checkpoints, cost + receipt + projection + sign + outbox + end + settle + journal, cancel/link loss) | 07 §6.1 | mo-node + mo-worker | 1 | E01, E08, E12 | todo |
| T-07-060 | Ack target well under 500 ms (usually ~1 ms) | 07 §6.1 | mo-node + mo-worker | 1 | NEW:CI-06 | todo |
| T-07-061 | Worker parses just enough of the stream to extract usage and reported model (SSE parsers for both dialects) | 07 §6.1 | mo-worker | 1 | E01, E02, NEW:CI-03 | todo |
| T-07-062 | Adapter `anthropic` (`api.anthropic.com`, Messages) | 07 §6.2 | mo-worker | 1 | E01 | todo |
| T-07-063 | Adapter `openrouter` (`openrouter.ai`, OpenAI chat + Anthropic Messages); prices imported from its public model list | 07 §6.2 | mo-worker + mo-relay | 1 | E02, E03 | todo |
| T-07-064 | Adapter `deepseek` (`api.deepseek.com`, OpenAI chat + Anthropic Messages); cache-hit/miss usage fields | 07 §6.2 | mo-worker | 1 | E03 | todo |
| T-07-065 | Adapter `openai` (`api.openai.com`, OpenAI chat, `store:false` forced) | 07 §6.2 | mo-worker | 2 | NEW:E78 | todo |
| T-07-066 | Adapter `openai_compatible`: vetted list (Gemini OpenAI endpoint, Groq, Together, Fireworks, Mistral, xAI); unlisted host requires `--allow-unvetted-host` with a warning | 07 §6.2; 11 Ph5 | mo-worker + mo-node | 5 | NEW:E78 | todo |
| T-07-067 | Adapter `local` (127.0.0.1 vLLM/Ollama/llama.cpp, price 0, token goals) | 07 §6.2 | mo-worker | R | NEW:MON-03 | todo |
| T-07-068 | Adapter = data definition (hosts, auth header, firewall table, usage mapping, rate-limit header names, error mapping, catalog source) + small special-case code | 07 §6.2 | mo-worker | 1 | NEW:CI-17 | todo |
| T-07-069 | Connection warming: HTTP/2 connection per configured provider at startup and on key add; PINGs while idle; re-dial before provider idle timeout | 07 §6.3 | mo-worker + mo-node | 1 | NEW:E77 | todo |
| T-07-070 | Local controls: `device_monthly_cap` required at setup (no default); `slots_max` 4; `schedule` always; `firewall_level` strict; `journal_full_text` off; `models_override` | 07 §6.4 | mo-node | 1 | NEW:E59, E11 | todo |
| T-07-071 | Outbox: append-only signed receipts, fsync before `task.end`, acked on `receipt.ack`, kept 7 more days; local counters persisted with it | 07 §6.5 | mo-worker + mo-node | 1 | E12, NEW:E85 | todo |
| T-07-072 | Served-task set: `(gateway_device, task_id)` within ±10 min, persisted | 07 §6.5 | mo-worker | 1 | E16, NEW:E58 | todo |
| T-07-073 | Journal: daily-rotated append-only; task id, repo, member pseudonym, model, usage, cost, status, timings, optional full text; 90-day retention | 07 §6.5 | mo-node | 1 | NEW:E62, NEW:E85 | todo |
| T-07-074 | Default storage layout per OS (config.toml, state dir, keychain; control socket 0600 / named pipe with user ACL); with `--home` all state under `<home>`, socket `<home>/state/node.sock` | 07 §7; CONTRACT §6, §12 | mo-node | 1/5 | NEW:E74 | todo |
| T-07-075 | Config holds no secrets (safe for dotfiles) | 07 §7 | mo-node | 1 | NEW:E61 | todo |
| T-07-076 | Donor flow: install → login (Donate) → keys add (validated, models listed) → required safety screen (device cap + provider spend-limit checkbox, deep links) → donate → service install → status "waiting for approval" → "serving" | 07 §8.1 | mo-node | 1/4 | NEW:E83, NEW:REV-04 | todo |
| T-07-077 | Maintainer flow: claim on web + `moochy claim`, set goal + default model, approve donors/members, login (Use pooled compute), `connect`, start agent; status shows tasks | 07 §8.2 | mo-node + mo-web | 1/4 | NEW:E84, NEW:REV-04 | todo |
| T-07-078 | One-click always-on donor templates (small VPS / container platforms) using the encrypted-file keystore | 07 §8.3 | mo-ops* + mo-release* | 5 | NEW:REV-02 | todo |
| T-07-079 | Headless: `login --headless` code; owner grants `gateway` role scoped to one repo and adds as member with its own cap (`members add --device`); keystore file + passphrase in CI secrets; `up --headless` | 07 §8.4 | mo-node + mo-relay | 1/2 | NEW:E89, NEW:E32 | todo |
| T-07-080 | No relay-hosted MCP endpoint, ever | 07 §8.4; ADR-30 | mo-relay | — | NEW:REV-02 | todo |
| T-07-081 | Service install: launchd user agent `dev.moochy.node.plist`; systemd user unit (lingering on servers); Windows scheduled task or service | 07 §9 | mo-node | 5 | NEW:E83 | todo |
| T-07-082 | Dependency budget ≤ 25 direct deps; release binary ≤ 15 MB stripped + LTO | 07 §10 | mo-node + integrator | 1 | NEW:CI-07 | todo |
| T-07-083 | cargo-dist builds macOS (arm64, x86_64), Linux (x86_64, arm64; glibc + musl), Windows (x86_64, arm64): shell + PowerShell installers, Homebrew tap, npm package, archives | 07 §11 | mo-release* | 5 | NEW:CI-08 | todo |
| T-07-084 | Minimal container image: static musl binary, non-root | 07 §11 | mo-release* | 5 | NEW:CI-08 | todo |
| T-07-085 | Every artifact Sigstore-signed with SLSA provenance; reproducible builds checked in CI | 07 §11 | mo-release* | 3 | NEW:CI-08 | todo |
| T-07-086 | Client tests: golden vectors; fake providers (scripted SSE, usage, 429/529, mid-stream disconnect, slow start) | 07 §13 | mo-proto + mo-e2e | 1 | NEW:CI-01, E07, E08 | todo |
| T-07-087 | Client tests: recorded harness traffic corpus (Claude Code, OpenCode, Aider, Cline…) accepted by the firewall | 07 §13 | mo-worker | 1 | NEW:CI-13 | todo |
| T-07-088 | Client tests: MCP conformance (official inspector/test clients, stdio + HTTP; scripted OpenCode, Claude Code, one framework); roots enforcement | 07 §13 | mo-node | 1/3 | NEW:CI-15 | todo |
| T-07-089 | Client tests: fuzzing firewall (nested), frame parser, SSE parser, MCP `files` paths | 07 §13 | mo-worker + mo-proto + mo-node | 1/3 | NEW:CI-03 | todo |
| T-07-090 | Client tests: E2E in CI with Relay + 2 Gateways + 3 Workers + fake providers (failover, outbox replay, disputes, relay restart, known_tasks) | 07 §13 | mo-e2e | 1/2 | E06, E12, E20, NEW:E45 | todo |
| T-07-091 | Client tests: redaction (keys/scrubbed secrets never in logs, journals, crash reports, receipts) | 07 §13 | mo-node + mo-worker | 1 | NEW:CI-12, NEW:E61 | todo |
| T-07-092 | Client tests: keystore per OS in a CI matrix (persist, restart, headless fallback) | 07 §13 | mo-node + mo-release* | 5 | NEW:CI-16 | todo |

## 08 — Web app and dashboards

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-08-001 | Server-rendered `html/template` (auto-escaped); HTMX partial updates; `htmx-ext-sse` for live data; no SPA, no client state store | 08 §1.1 | mo-web | 4 | E19, NEW:CI-09 | todo |
| T-08-002 | Read-only pages work without JavaScript | 08 §1.2 | mo-web | 4 | NEW:E66 | todo |
| T-08-003 | Render once, fan out the same bytes to every subscriber | 08 §1.3 | mo-web | 4 | NEW:E67 | todo |
| T-08-004 | Privacy by default: aggregates public, individuals only on opt-in | 08 §1.4 | mo-web + mo-relay | 4 | NEW:E68 | todo |
| T-08-005 | Budgets: ≤ 50 KB transferred for a public repo page (excl. avatars), FCP < 1 s on 4G, Lighthouse accessibility ≥ 95 | 08 §1.5 | mo-web | 4 | NEW:CI-09 | todo |
| T-08-006 | CSS embedded in the binary, content-hashed filename, immutable cache headers (hand-written CSS ≤ 12 KB per CONTRACT §9; see §D) | 08 §1.6; CONTRACT §9 | mo-web | 4 | NEW:CI-09 | todo |
| T-08-007 | Persistent footer on every page + landing statement: "Moochy is 100% open source (Apache-2.0 OR MIT) and 100% free…", linking source, self-host guide, costs page | 08 §1.7 | mo-web | 4 | NEW:E66 | todo |
| T-08-008 | Fixed palette and dark theme via CSS custom properties + `prefers-color-scheme` (white, `#0B1220`, `#7DD3FC`, links `#0369A1`; dark bg `#0B1220`, text `#F8FAFC`) | 08 §11; CONTRACT §9; AGENTS §6 | mo-web | 4 | E19, NEW:CI-09 | todo |
| T-08-009 | `GET /` landing: what Moochy is, open-source/free statement, live global counters, featured repos, "works with any MCP client or OpenAI/Anthropic-compatible tool" | 08 §2 | mo-web | 4 | NEW:E66 | todo |
| T-08-010 | `GET /connect`: per-client snippets for both doors; supported donor providers | 08 §2 | mo-web | 4 | NEW:E66 | todo |
| T-08-011 | `GET /open`: source, license, self-host guide, monthly costs and sponsors (static, updated monthly) | 08 §2; 10 §10.1 | mo-web + human-po* | 4 | NEW:E66 | todo |
| T-08-012 | `GET /explore`: repos seeking compute (goal %, donors, models wanted) with filters | 08 §2 | mo-web + mo-relay | 4 | NEW:E66 | todo |
| T-08-013 | `GET /p/{owner}/{repo}` public repo page | 08 §2–3 | mo-web | 4 | E19 | todo |
| T-08-014 | `GET /p/{owner}/{repo}/events` SSE: presence + goal + audit-feed fragments | 08 §2 | mo-web | 4 | E19 | todo |
| T-08-015 | `GET /p/{owner}/{repo}/badge.svg` | 08 §2, §8 | mo-web | 4 | NEW:E66 | todo |
| T-08-016 | `GET /p/{owner}/{repo}/donate` pledge form (U) and `POST /p/{owner}/{repo}/pledges` create pledge | 08 §2 | mo-web + mo-relay | 1/4 | NEW:E39, NEW:E65 | todo |
| T-08-017 | `GET /station` donor station; `GET /station/events` SSE (live tasks, budgets, device status) | 08 §2, §4 | mo-web | 4 | NEW:E67 | todo |
| T-08-018 | `POST /station/pledges/{id}/pause`, `/resume`, `/reclaim` (HTMX swaps the row) | 08 §2 | mo-web + mo-relay | 4 | NEW:E39 | todo |
| T-08-019 | `GET /console/{owner}/{repo}` maintainer console (owner/admin only) | 08 §2, §5 | mo-web | 4 | NEW:E65 | todo |
| T-08-020 | `POST /console/{owner}/{repo}/donors/{id}/decline` (approval itself signed by `moochy approve`) | 08 §2 | mo-web + mo-relay | 4 | NEW:E39 | todo |
| T-08-021 | `POST /console/{owner}/{repo}/members`: update quotas, request member changes (change itself owner-Node-signed) | 08 §2 | mo-web + mo-relay | 4 | NEW:E32, NEW:E84 | todo |
| T-08-022 | `POST /console/{owner}/{repo}/settings`: goal, default model, pinned donors, auto-caching, tripwire mode, member default cap | 08 §2 | mo-web + mo-relay | 4 | NEW:E55, NEW:E65 | todo |
| T-08-023 | `GET/POST /claim`: repo claim with admin check | 08 §2 | mo-web + mo-relay | 1/4 | NEW:E65 | todo |
| T-08-024 | `GET/POST /device`: device approval (enter code → confirm roles, repo scope) | 08 §2 | mo-web + mo-relay | 1/4 | NEW:E65 | todo |
| T-08-025 | `GET /devices`, `POST /devices/{id}/revoke` | 08 §2 | mo-web + mo-relay | 4 | NEW:E65, NEW:E73 | todo |
| T-08-026 | `GET /r/{receipt_ref}` projection detail + how to verify | 08 §2, §6 | mo-web | 4 | NEW:E66 | todo |
| T-08-027 | `GET /log` key-log explorer: latest checkpoints, Git anchor status, search by pseudonym or repo | 08 §2 | mo-web + mo-relay | 4 | NEW:E66 | todo |
| T-08-028 | `GET /log/checkpoint`, `/log/tile/...`, `/log/keys/...` machine endpoints for tlog clients (static, CDN-cacheable) | 08 §2 | mo-relay | 3 | NEW:E42 | todo |
| T-08-029 | `GET /leaderboard` global donors (opt-in names) | 08 §2 | mo-web | 4 | NEW:E66 | todo |
| T-08-030 | `GET /auth/{provider}`, `/auth/{provider}/callback`, `POST /logout` (OAuth) | 08 §2 | mo-relay + mo-web | 1 | NEW:E65 | todo |
| T-08-031 | `GET /admin/...` minimal moderation + metrics, separate auth by operator device keys | 08 §2; 10 §11 | mo-relay + mo-web | 6 | NEW:E79 | todo |
| T-08-032 | All routing via stdlib `ServeMux` method + path patterns | 08 §2 | mo-web + mo-relay | 1 | NEW:CI-02 | todo |
| T-08-033 | Repo page header + goal (committed %, used %, token-equivalents, donor count); SSE `goal` coalesced ≤ 1 per 30 s | 08 §3 | mo-web | 4 | E19, NEW:E67 | todo |
| T-08-034 | Live pool (aggregated nodes online, models, tasks running, median added latency, opt-in donors); SSE `pool` ≤ 1/s | 08 §3 | mo-web + mo-relay | 4 | E19, NEW:E68 | todo |
| T-08-035 | Top donors this month (undisputed receipts); page load + SSE every 60 s | 08 §3 | mo-web | 4 | NEW:E66 | todo |
| T-08-036 | Audit feed of newest donor-signed projections; SSE `audit` per receipt, ≤ 1/s, max 20 rows; ✓ undisputed / ⚠ disputed; each row links `/r/{ref}`; day only | 08 §3 | mo-web | 4 | E19, NEW:E68 | todo |
| T-08-037 | Log footer (entries, checkpoint time, anchored ✓); SSE `log` event | 08 §3 | mo-web | 4 | NEW:E66 | todo |
| T-08-038 | No per-node RTT or online schedule per person anywhere | 08 §3 | mo-web | 4 | NEW:E68 | todo |
| T-08-039 | Donor Station: devices (role, online, slots, cap usage), pledges (status, policy, budget/spent/reserved, pause/reclaim), live tasks, monthly summary (served, tasks, cache hit %, saved ≈ $X), safety status (spend limit self-reported, device caps) | 08 §4 | mo-web + mo-relay | 4 | NEW:E67 | todo |
| T-08-040 | "Saved ≈ $X" = cost without cache hits computed from receipts (`cost_uncached_uusd`) | 08 §4; 09 §3.6 | mo-relay + mo-web | 4 | NEW:CI-10 | todo |
| T-08-041 | Console panel Pool health: committed vs used, utilization, projected end-of-month headroom, models available vs requested-but-missing | 08 §5 | mo-web + mo-relay | 4 | NEW:E65 | todo |
| T-08-042 | Console panel Donor approvals: pending donors with signals (account age, other repos, past disputes), one-line `moochy approve` command, decline button | 08 §5 | mo-web | 4 | NEW:E84 | todo |
| T-08-043 | Console panel Members (incl. CI devices), quotas, usage, last activity; add/remove via owner's Node | 08 §5 | mo-web | 4 | NEW:E32 | todo |
| T-08-044 | Console panel Policy: pinned donors, tripwire mode, auto-caching, default model, own-key fallback guidance | 08 §5 | mo-web | 4 | NEW:E65 | todo |
| T-08-045 | Console panel Usage: per-member and per-model usage, cache hit ratio, failover rate, added latency | 08 §5 | mo-web + mo-relay | 4 | NEW:E65 | todo |
| T-08-046 | Console panel Goal: amount + public "what we use AI compute for" description | 08 §5 | mo-web | 4 | NEW:E66 | todo |
| T-08-047 | Projection page shows fields, donor signature, donor device's key-log entry, current checkpoint + Git anchor, the `moochy verify r_…` command, and what a receipt does **not** prove | 08 §6 | mo-web | 4 | NEW:E66 | todo |
| T-08-048 | In-browser verifier deferred (verification in the open-source client) | 08 §6 | mo-web | D | NEW:MON-03 | todo |
| T-08-049 | SSE topics `repo:{id}`, `station:{user_id}`, `global`; hub one goroutine per topic shard | 08 §7 | mo-web | 4 | NEW:E67 | todo |
| T-08-050 | Coalescing: per-topic dirty flags, ≤ 1 render per topic per window regardless of event rate; live-update window 250 ms so a settled task is visible ≤ 500 ms (CONTRACT §13; see §C conflict with 08 §3) | 08 §7; CONTRACT §13 | mo-web | 4 | E22, NEW:E67, NEW:CI-09 | todo |
| T-08-051 | Backpressure: small bounded queue per subscriber; full → disconnect; hub never blocks the Scheduler | 08 §7 | mo-web | 4 | NEW:E67 | todo |
| T-08-052 | On connect send current full fragments immediately (no `Last-Event-ID` replay) | 08 §7 | mo-web | 4 | E19, NEW:E67 | todo |
| T-08-053 | HTTP/2 for all web traffic | 08 §7 | mo-relay + mo-web | 4 | NEW:E66 | todo |
| T-08-054 | SSE heartbeat comment every 25 s | 08 §7 | mo-web | 4 | NEW:E67 | todo |
| T-08-055 | Badge SVG "AI compute: N donors · X% of goal", template without external fonts, cached 5 min | 08 §8 | mo-web | 4 | NEW:E66 | todo |
| T-08-056 | Each repo page links to other repos the same donors support | 08 §8 | mo-web + mo-relay | 4 | NEW:E66 | todo |
| T-08-057 | Session cookie `HttpOnly`, `Secure`, `SameSite=Lax`, random 256-bit id, only SHA-256 hash stored | 08 §9; 09 §3.1 | mo-relay + mo-web | 1/4 | NEW:E65 | todo |
| T-08-058 | CSRF: state-changing requests require `HX-Request: true` and a matching `Origin`; non-HTMX fallbacks use a per-session token | 08 §9 | mo-web | 4 | NEW:E65 | todo |
| T-08-059 | CSP `default-src 'self'`, self-only scripts (vendored htmx), `frame-ancestors 'none'`; `img-src` limited to provider avatar hosts or proxied avatars | 08 §9 | mo-web | 4 | NEW:E65 | todo |
| T-08-060 | Rate limits per IP and per session on POST routes and SSE connections | 08 §9 | mo-web + mo-relay | 4 | NEW:E80 | todo |
| T-08-061 | Templates: `layouts/`, `pages/` (one per route), `fragments/` shared between first render and SSE/HTMX swaps; no emails in v1 | 08 §10 | mo-web | 4 | NEW:CI-09 | todo |
| T-08-062 | `aria-live="polite"` on audit feed and pool summary, throttled | 08 §11 | mo-web | 4 | NEW:CI-09 | todo |
| T-08-063 | Colour never the only signal (✓/⚠ glyphs + text); ping dots respect `prefers-reduced-motion` | 08 §11 | mo-web | 4 | NEW:CI-09 | todo |
| T-08-064 | Money shows dollars first, tokens in a tooltip / `<details>` without JS | 08 §11 | mo-web | 4 | NEW:E66 | todo |

## 09 — Data model (SQLite)

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-09-001 | Draft fixes: `devices` table (not `users.public_key`); `identities` table (GitHub + GitLab per user); no `mcp_secret`; goals in µ$; history tables; `tasks` + `attempts`; all times INTEGER Unix ms | 09 §1 | mo-relay | 1 | NEW:E69 | todo |
| T-09-002 | Pragmas: `journal_mode=WAL`, `synchronous=FULL`, `foreign_keys=ON`, `busy_timeout=5000`, `temp_store=MEMORY`, `mmap_size=1 GiB`, `wal_autocheckpoint=0` | 09 §2 | mo-relay | 1 | NEW:E69 | todo |
| T-09-003 | One writer connection owned by the Store writer goroutine; pool of read-only (`mode=ro`) connections for web, audit job, tile serving | 09 §2 | mo-relay | 1 | NEW:CI-02 | todo |
| T-09-004 | `users`: `id` PK, `pseudonym` UNIQUE random (only public identifier), `display_name`, `status` (`active`/`suspended`/`deleted`), `created_at` | 09 §3.1 | mo-relay | 1 | NEW:E69 | todo |
| T-09-005 | `identities`: PK (`provider`, `provider_user_id`), `user_id`, `username`, `avatar_url` refreshed at login, `account_created_at` | 09 §3.1 | mo-relay | 1 | NEW:E65 | todo |
| T-09-006 | `devices`: `id` (`d_…`), `user_id`, `name`, `sign_pub` UNIQUE 32 B, `enc_pub` 32 B, `suite`, `roles`, `repo_scope`, `cap_uusd_month`, `key_log_index`, `created_at`, `revoked_at` | 09 §3.1 | mo-relay | 1 | NEW:E69 | todo |
| T-09-007 | `device_usage` (`device_id`, `month`) with non-negative CHECKs, capped devices only | 09 §3.1 | mo-relay | 2 | NEW:E32 | todo |
| T-09-008 | `web_sessions` (`id_hash` PK = SHA-256 of cookie, `user_id`, `created_at`, `expires_at`) | 09 §3.1 | mo-relay | 1 | NEW:E65 | todo |
| T-09-009 | `device_codes` (`user_code` PK, `device_code_hash`, `sign_pub`, `enc_pub`, `requested_roles`, `requested_scope`, `approved_by`, `expires_at`), short-lived | 09 §3.1 | mo-relay | 1 | E01, NEW:E85 | todo |
| T-09-010 | `repos`: `id` (`r_…`), UNIQUE(`provider`, `provider_repo_id`) (rename-stable), UNIQUE(`provider`, `owner`, `name`), `claimed_by`, `claim_log_index`, `goal_uusd_month ≥ 0`, `default_model`, `description`, `settings` JSON, `status` | 09 §3.2 | mo-relay | 1 | NEW:E69 | todo |
| T-09-011 | `members`: PK(`repo_id`, `user_id`), `role`, `log_index`, `cap_uusd_month` (NULL unlimited), current-month `spent/reserved/month` with CHECKs, `removed_at` | 09 §3.2 | mo-relay | 1/2 | NEW:E32 | todo |
| T-09-012 | `member_months` history (`repo_id`, `user_id`, `month`, `spent_uusd`) for start-period attribution and audit | 09 §3.2 | mo-relay | 2 | NEW:E38, NEW:E70 | todo |
| T-09-013 | `pledges`: `id` (`p_…`), `donor_id`, `repo_id`, `status` (`pending/active/paused/ended/declined`), `approval_log_index`, `budget_uusd ≥ 0`, `per_task_cap_uusd > 0` default 5,000,000, `policy` JSON, `visibility`, `rollover`, `period_anchor_day` 1–28, `period_start`, `spent/reserved` with CHECKs, timestamps; partial UNIQUE(`donor_id`, `repo_id`) WHERE status IN active states | 09 §3.3 | mo-relay | 1 | NEW:E39, NEW:E69 | todo |
| T-09-014 | `pledge_periods` (PK `pledge_id`, `period_start`; `budget`, `spent`, `tasks`, `closed_at`); closed periods still receive start-period settlements | 09 §3.3 | mo-relay | 1 | NEW:E38 | todo |
| T-09-015 | `tasks` (metadata only): PK(`gateway_device`, `id`), repo, member, route facts, `body_bytes`, `status`, `fail_code`, `t_submit`, `t_end`; index (`repo_id`, `t_submit`) | 09 §3.4 | mo-relay | 1 | E13, NEW:E69 | todo |
| T-09-016 | `attempts`: PK(`task_id`, `attempt`), devices, pledge, `reserved/cost`, `catalog_version`, `period_start`, `status` (committed … pessimistic), `nack_code`, timestamps; index (`pledge_id`, `period_start`); partial index on `awaiting_receipt`/`orphaned` | 09 §3.4 | mo-relay | 1 | E12, NEW:E37 | todo |
| T-09-017 | `receipts`: PK(`task_id`, `attempt`), exact `body` + `donor_sig`, `projection` + `projection_sig`, UNIQUE `receipt_ref`, `dispute_code/sig`, `pledge_id`, `period_start`, denormalized usage + cost, `estimated`, `received_at`; indexes (`pledge_id`, `period_start`), (`received_at`) | 09 §3.4 | mo-relay | 1 | E01, NEW:E45 | todo |
| T-09-018 | `log_entries` (`log` ∈ {`keys`, reserved `receipts`}, `idx`, `kind`, exact `body`, `sigs`, `created_at`), `log_hashes`, `checkpoints` (`tree_size`, `root_hash`, `note`, `anchored_at`, `created_at`) | 09 §3.5 | mo-relay | 3 | NEW:E42 | todo |
| T-09-019 | Full tiles immutable, computed on demand from `log_hashes`, cached in memory/CDN, never stored twice | 09 §3.5 | mo-relay | 3 | NEW:E42 | todo |
| T-09-020 | `catalog` table (PK `version`, `model`, `provider`; prices, limits, `native_aliases`, `source`, `effective_at`, `log_index`) | 09 §3.6 | mo-relay | 1 | NEW:E41 | todo |
| T-09-021 | `usage_daily` (PK `day`, `repo_id`, `pledge_id`, `model`; tasks, tokens, `cost_uusd`, `cost_uncached_uusd`, `failovers`, `p50/p95_added_ms`), rolled up hourly, kept forever | 09 §3.6 | mo-relay | 4 | NEW:E85 | todo |
| T-09-022 | `reports` (evidence BLOB encrypted to the operator's moderation key) and `strikes` (`route_mismatch`, `firewall`, `dispute_upheld`, …) | 09 §3.6 | mo-relay | 1/3 | NEW:E57, NEW:E64 | todo |
| T-09-023 | Write path: Scheduler adaptive group commit (immediate when idle, batched while a commit is in flight; cap 256 ops), SAVEPOINT per op, completion channel; `Assign` and `ReceiptAck` only after the commit returns | 09 §4; ADR-34 | mo-relay | 1 | E12, E22, NEW:CI-06 | todo |
| T-09-024 | Receipt intake atomic with balance update in the same group commit; disputes and key-log appends via group commit | 09 §4 | mo-relay | 1/3 | E12, NEW:E45 | todo |
| T-09-025 | Web handlers write through the writer goroutine (request → reply, typically < 15 ms) | 09 §4 | mo-relay + mo-web | 1/4 | NEW:E39 | todo |
| T-09-026 | Nightly retention: delete `tasks`/`attempts` > 90 days (after rollup), expired sessions and device codes, in small batches | 09 §4 | mo-relay | 2 | NEW:E85 | todo |
| T-09-027 | Read paths use the listed indexes (repo page, station, console, tile server, audit job, boot) | 09 §5 | mo-relay | 1/4 | NEW:CI-06 | todo |
| T-09-028 | Migrations embedded, numbered, forward-only, each in its own transaction, run at boot before accepting connections | 09 §6 | mo-relay | 1 | NEW:E69 | todo |
| T-09-029 | Each migration declares `min_compatible_version`; binary refuses to start only if the DB requires a newer binary (rollback works) | 09 §6 | mo-relay | 2 | NEW:E69 | todo |
| T-09-030 | Expand → migrate → contract across two releases; long index builds run as a background step after boot | 09 §6 | mo-relay | 2 | NEW:CI-11 | todo |
| T-09-031 | Test suite applies all migrations on an empty DB and on a previous-release snapshot | 09 §6 | mo-relay | 1 | NEW:CI-11 | todo |
| T-09-032 | Litestream: continuous WAL to S3-compatible storage, daily snapshots, 30-day retention | 09 §7 | mo-ops* | 1 | NEW:CI-21 | todo |
| T-09-033 | Automated monthly restore drill: restore to scratch VM, boot read-only, run audit job, compare key-log root with published anchor | 09 §7; 10 §4 | mo-ops* + mo-relay | 6 | NEW:CI-21 | todo |
| T-09-034 | Relay supports a read-only boot mode (for the restore drill) | 09 §7 | mo-relay | 6 | NEW:CI-21 | todo |
| T-09-035 | Ceiling: past ~100M receipts archive receipts > 13 months to compressed object storage (projections stay) | 09 §8; 10 R7 | mo-relay + mo-ops* | D | NEW:MON-03 | todo |
| T-09-036 | `users.username` unique handle (`UNIQUE COLLATE NOCASE`, ASCII `[a-z0-9-]`, 3–32, reserved words refused) + `username_changed_at` (rename once per 30 days) | 09 §3.1; CONTRACT §11 | mo-relay | 1 | E21 | todo |
| T-09-037 | `username_tombstones` (`username` PK case-insensitive, `user_id`, `retired_at`, `redirect_until`): a handle ever used is never reassigned | 09 §3.1; CONTRACT §11 | mo-relay | 1 | E21 | todo |

## 10 — Operations

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-10-001 | `dev` env: Relay + fake providers + N simulated Nodes from one harness command | 10 §1 | mo-e2e | 1 | E01 | todo |
| T-10-002 | `staging` env: same binary and topology as prod, real providers with test keys and tiny budgets | 10 §1 | mo-ops* | 2 | NEW:CI-20 | todo |
| T-10-003 | Same artifact promoted staging → prod; no environment-specific builds | 10 §1 | mo-release* + mo-ops* | 2 | NEW:CI-08 | todo |
| T-10-004 | Prod: one VM with NVMe (start 4 vCPU / 8 GB), region near early users | 10 §2 | mo-ops* + human-po* | 6 | NEW:REV-06 | todo |
| T-10-005 | One systemd unit for the relay; restarts use drain-and-restart | 10 §2 | mo-ops* | 2 | NEW:CI-21 | todo |
| T-10-006 | Public instance runs exactly the open-source binary + `deploy/` files; self-hosters get the same recipe with own domain, OAuth app, signing keys | 10 §2 | mo-ops* + mo-docs* | 6 | NEW:REV-02 | todo |
| T-10-007 | Optional CDN only in front of `/log/tile/*`, `/static/*`, `/p/*/badge.svg`; WS and SSE straight to origin | 10 §2 | mo-ops* + mo-relay | 6 | NEW:E66 | todo |
| T-10-008 | Signing keys loaded at boot from encrypted file (passphrase via systemd credentials) or KMS; OAuth secrets via systemd credentials; never in child env or logs | 10 §2 | mo-relay + mo-ops* | 3 | NEW:E82 | todo |
| T-10-009 | Configuration: one TOML file + flags; every value has a documented default; effective config printed at boot with secrets redacted | 10 §2; ADR-32 | mo-relay | 1 | NEW:E82 | todo |
| T-10-010 | Drain (≤ 30 s): `relay.draining`, Scheduler stops assigning, new submits retryable error, non-started tasks failed retryable + Workers cancelled, started streams get up to 30 s | 10 §3 | mo-relay | 2 | NEW:E35 | todo |
| T-10-011 | Restart: flush writer, exit, start new binary, migrations, load state, missed rollovers, accept connections | 10 §3 | mo-relay | 2 | NEW:E35, NEW:E69 | todo |
| T-10-012 | Recover: Gateways reconnect immediately, Workers jittered 0–10 s, `known_tasks` + outbox replay | 10 §3 | mo-node | 2 | NEW:E35 | todo |
| T-10-013 | Drain exit criterion: ≤ ~10 s retryable errors per upgrade, zero ledger drift | 10 §3 | mo-relay | 2 | NEW:E35, NEW:CI-22 | todo |
| T-10-014 | Blue/green zero-downtime (SO_REUSEPORT, make-before-break, old process fails non-started then forwards only, settlement via outbox replay) built only when `tasks_total{status="failed",cause="deploy"}` is visible | 10 §3; ADR-22 | mo-relay | D | NEW:MON-03 | todo |
| T-10-015 | DR: process crash RPO 0 / RTO < 10 s (systemd restart) | 10 §4 | mo-ops* + mo-relay | 1 | E12 | todo |
| T-10-016 | DR: VM loss / disk corruption RPO ~1 s DB, 0 spend, RTO < 30 min (provision → restore → boot → `replay_since` → reconnect) | 10 §4 | mo-ops* | 6 | NEW:CI-21, NEW:E36 | todo |
| T-10-017 | DR: region outage RTO < 1 h (restore elsewhere, low-TTL DNS) | 10 §4 | mo-ops* | 6 | NEW:CI-21 | todo |
| T-10-018 | Metrics in Prometheus format on a private port | 10 §5.1 | mo-relay | 2 | NEW:E82 | todo |
| T-10-019 | Metric `relay_added_latency_ms` histogram: last body frame received → first response byte forwarded minus Worker-reported provider TTFT | 10 §5.1 | mo-relay + mo-node | 2 | E20, NEW:E82 | todo |
| T-10-020 | Metric `gateway_overhead_ms` (opt-in Node telemetry) | 10 §5.1 | mo-node | 2 | NEW:E82 | todo |
| T-10-021 | Metrics `scheduler_apply_us` by event type, `ack_latency_ms`, `start_latency_ms` | 10 §5.1 | mo-relay | 2 | NEW:E82 | todo |
| T-10-022 | Metrics `tasks_total` by final status (+ cause), `failovers_total` by NACK code, `routing_deadline_exceeded_total` | 10 §5.1 | mo-relay | 2 | NEW:E82 | todo |
| T-10-023 | Metrics `workers_online` by model, `slots_free_total`, `pool_headroom_uusd` by repo | 10 §5.1 | mo-relay | 2 | NEW:E82 | todo |
| T-10-024 | Metrics `reserved_uusd_total`, `settled_uusd_total`, `pessimistic_settlements_total`, `audit_drift_uusd` | 10 §5.1 | mo-relay | 2 | NEW:E82, NEW:E70 | todo |
| T-10-025 | Metrics `cache_read_ratio` by repo, `affinity_hit_ratio` | 10 §5.1 | mo-relay | 2 | NEW:E82, NEW:E30 | todo |
| T-10-026 | Metric `request_bytes_sealed` histogram (delta-transfer trigger) | 10 §5.1 | mo-relay | 2 | NEW:E82 | todo |
| T-10-027 | Metrics `key_log_size`, `checkpoint_age_s`, `anchor_lag_s` | 10 §5.1 | mo-relay | 3 | NEW:E82 | todo |
| T-10-028 | Metrics `ws_connections`, `ws_writer_queue_overflow_total`, `sse_subscribers`, `sse_dropped_total` | 10 §5.1 | mo-relay + mo-web | 2/4 | NEW:E82 | todo |
| T-10-029 | Metrics `commit_latency_ms`, `group_commit_batch_size`, `wal_size_bytes`, `litestream_lag_s` | 10 §5.1 | mo-relay + mo-ops* | 2 | NEW:E82 | todo |
| T-10-030 | Metrics `firewall_rejections_total` by field name (Worker telemetry), `route_mismatch_total`, `bad_envelope_total`, `unknown_key_alerts_total` | 10 §5.1 | mo-relay | 2/3 | NEW:E82 | todo |
| T-10-031 | Structured JSON `log/slog` logs with `task_id`, `repo_id`, `device_id` on every task-scoped line; never content or secrets (content is opaque bytes with no string formatter) | 10 §5.2 | mo-relay | 1 | E13, NEW:E82 | todo |
| T-10-032 | Optional OpenTelemetry traces for task lifecycles, sampled 1%, staging and prod | 10 §5.2 | mo-relay | 2 | NEW:E82 | todo |
| T-10-033 | Nodes send only opt-in anonymous telemetry (version, OS, firewall rejection field names, latency histograms), never content | 10 §5.2 | mo-node | 2 | NEW:E82 | todo |
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
| T-10-044 | Runbook R2 ledger drift (freeze affected pledges, diff, correct, postmortem); relay supports freezing a pledge's new reservations | 10 §8 | mo-ops* + mo-relay | 6 | NEW:REV-02, NEW:E79 | todo |
| T-10-045 | Runbook R3 mass Worker disconnect | 10 §8 | mo-ops* | 6 | NEW:REV-02 | todo |
| T-10-046 | Runbook R4 provider outage | 10 §8 | mo-ops* | 6 | NEW:REV-02 | todo |
| T-10-047 | Runbook R5 abuse report (verify bundle, suspend donor devices, `MODERATION` entry, notify repo) | 10 §8 | mo-ops* + mo-relay | 6 | NEW:REV-02, NEW:E64 | todo |
| T-10-048 | Runbook R6 log-key compromise (offline new key, transition checkpoint co-signed + anchored, announce, Nodes pin new key via signed release) | 10 §8 | mo-ops* + mo-node | 6 | NEW:REV-02 | todo |
| T-10-049 | Runbook R7 DB growth (retention job, task-row floods, archive receipts > 13 months) | 10 §8 | mo-ops* | 6 | NEW:REV-02 | todo |
| T-10-050 | Runbook R8 firewall bypass (tighter release, raise `min_client_version`, notify donors) | 10 §8 | mo-ops* + mo-worker | 6 | NEW:REV-02, NEW:E72 | todo |
| T-10-051 | Scaling path steps (vertical, split web process over local socket, regional edges, shard by repo) each gated by a metric threshold | 10 §9 | mo-relay + mo-ops* | D | NEW:MON-03 | todo |
| T-10-052 | Cost envelope ≈ $40–60/month early, ≈ $100–180/month at 1M tasks | 10 §10 | mo-ops* + human-po* | 6 | NEW:REV-06 | todo |
| T-10-053 | Open sponsorship (GitHub Sponsors / Open Collective) with public monthly cost page `/open` | 10 §10.1 | human-po* + mo-web | 4 | NEW:REV-06, NEW:E66 | todo |
| T-10-054 | Pools portable: Nodes switch relay with one config value | 10 §10.1 | mo-node | 1 | E01 | todo |
| T-10-055 | `/admin` (operator devices only): user/device/pledge lookup by id or pseudonym, suspend/unsuspend, moderation queue, catalog publishing (two-person approval), feature flags | 10 §11 | mo-relay + mo-web | 6 | NEW:E79 | todo |
| T-10-056 | `relay admin …` subcommands for the same operations from the VM shell | 10 §11 | mo-relay | 6 | NEW:E79 | todo |
| T-10-057 | Every admin action writes an internal audit-log row; public actions (catalog, moderation) also a transparency-log entry | 10 §11 | mo-relay | 6 | NEW:E79 | todo |

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
| T-11-013 | Ph1 exit 5b: vectors prove two attempts never share a response key; Worker refuses replayed/forged tasks (bad sig, stale ULID, foreign repo) | 11 Ph1 | mo-proto + mo-node | 1 | NEW:CI-01, E16, NEW:E58, NEW:E43 | todo |
| T-11-014 | Ph1 exit 6: firewall rejects 100% of the seeded forbidden corpus and accepts 100% of captured real traffic from clients of criteria 1–3 | 11 Ph1 | mo-worker | 1 | NEW:CI-13, E09 | todo |
| T-11-015 | Ph1 exit 7: relay DB holds no prompt/output bytes (canary grep) | 11 Ph1 | mo-e2e | 1 | E13 | todo |
| T-11-016 | Ph1–2 run with design partners only while keys and approvals are relay-asserted | 11 Ph1 | human-po* | 1–2 | NEW:REV-06 | todo |
| T-11-017 | Ph2 exit 1: simulator 1M tasks / 2,000 workers with faults → zero invariant violations; same seed identical | 11 Ph2 | mo-relay | 2 | NEW:CI-04 | todo |
| T-11-018 | Ph2 exit 2: chaos (real binaries, fake providers: random kills, 429 storms, 2 relay upgrades under load) → success ≥ 99.5%, ≤ 10 s retryable errors per upgrade, zero drift | 11 Ph2 | mo-e2e | 2 | NEW:CI-22 | todo |
| T-11-019 | Ph2 exit 3: real agent sessions `affinity_hit_ratio` ≥ 95%, `cache_read_ratio` ≥ 80% | 11 Ph2 | mo-e2e* + mo-relay | 2 | NEW:CI-20, NEW:E30 | todo |
| T-11-020 | Ph2 exit 4: added latency p50 ≤ 60 ms in-continent | 11 Ph2 | mo-relay | 2 | NEW:CI-20, E20 | todo |
| T-11-021 | Ph2 scope includes SLO dashboards | 11 Ph2 | mo-ops* | 2 | NEW:MON-02 | todo |
| T-11-022 | Ph3 exit 1: injected rogue device key for user U flagged by U's Node within 2 checkpoint intervals | 11 Ph3 | mo-node | 3 | NEW:E42 | todo |
| T-11-023 | Ph3 exit 2: relay-forged donor approval refused by Gateways; forged repo claim flagged by the real owner's Node | 11 Ph3 | mo-node | 3 | NEW:E43 | todo |
| T-11-024 | Ph3 exit 3: forked log detected by Nodes against the public Git anchor | 11 Ph3 | mo-node | 3 | NEW:E44 | todo |
| T-11-025 | Ph3 exit 4: structural checks reject 100% of undeclared, schema-failing, or unsigned tool calls; tripwire blocks the documented baseline corpus and is documented as a speed bump | 11 Ph3 | mo-node + mo-worker | 3 | E18, NEW:E46, NEW:CI-14 | todo |
| T-11-026 | Ph3 exit 5: MCP `files` refuses every case of the path-escape corpus | 11 Ph3 | mo-node | 3 | NEW:E48 | todo |
| T-11-027 | Ph3 exit 6: independent rebuild of the Linux musl release is bit-identical | 11 Ph3 | mo-release* | 3 | NEW:CI-08 | todo |
| T-11-028 | Ph4 exit: page budgets met; 10k simulated SSE subscribers on one repo page < 1 core; accessibility ≥ 95 | 11 Ph4 | mo-web | 4 | NEW:CI-09 | todo |
| T-11-029 | Ph4 exit: usability test — 5 developers donate < 5 min, 5 maintainers get an agent running < 3 min, unaided | 11 Ph4 | human-po* | 4 | NEW:REV-04 | todo |
| T-11-030 | Ph5: more adapters (Gemini OpenAI-compatible, Groq, Together, Fireworks, Mistral, xAI), one table + fixtures each | 11 Ph5 | mo-worker | 5 | NEW:E78, NEW:CI-17 | todo |
| T-11-031 | Ph5: `moochy connect` coverage for every client in the matrix; `npx -y moochy mcp`; container image | 11 Ph5 | mo-node + mo-release* | 5 | NEW:E75, NEW:CI-08 | todo |
| T-11-032 | Ph5: GitLab identity and repos (same flows as GitHub) | 11 Ph5 | mo-relay + mo-web | 5 | NEW:E88 | todo |
| T-11-033 | Ph5: `service install` on all OSes; one-click always-on templates | 11 Ph5 | mo-node + mo-ops* | 5 | NEW:E83, NEW:CI-16 | todo |
| T-11-034 | Ph5: Windows support (named pipes, Credential Manager) | 11 Ph5 | mo-node | 5 | NEW:CI-16 | todo |
| T-11-035 | Ph5: own-key fallback | 11 Ph5 | mo-node | 5 | NEW:E86 | todo |
| T-11-036 | Ph5: remote-MCP self-tunnel mode (opt-in, OAuth 2.1, Host allowlist) | 11 Ph5 | mo-node | 5 | NEW:E87 | todo |
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
| T-11-055 | Verification: ledger property tests (reserve/settle/release sequences), nightly prod audit, provider reconciliation | 11 §3 | mo-relay + mo-node | 1/2 | NEW:CI-10, NEW:E70, NEW:CI-20 | todo |
| T-11-056 | Verification: fuzzing (firewall, frames, SSE parser, MCP paths), red-team corpora (firewall, tripwire), canary no-content test | 11 §3 | mo-worker + mo-proto + mo-node + mo-sec | 1/3 | NEW:CI-03, NEW:CI-13, NEW:CI-14, E13 | todo |
| T-11-057 | Verification: one-command integration harness (Relay + Nodes + fake providers) with happy path, failover, cancel, outbox replay, upgrade during load | 11 §3 | mo-e2e | 1/2 | E01, E06, E08, E12, NEW:E35 | todo |
| T-11-058 | Verification: nightly staging run with real providers and tiny budgets — one real agent session per supported harness | 11 §3 | mo-ops* + mo-e2e* | 2 | NEW:CI-20 | todo |
| T-11-059 | Verification: benchmarks with regression budgets (Scheduler apply, frame forwarding, seal/open throughput); periodic load tests | 11 §3 | mo-relay + mo-proto | 2 | NEW:CI-06, NEW:CI-19 | todo |
| T-11-060 | Verification: web template snapshot tests, accessibility checks, SSE load test | 11 §3 | mo-web | 4 | NEW:CI-09 | todo |
| T-11-061 | Definition of done for any feature: its exit criterion is automated (test, simulator scenario, or monitored metric) | 11 §3 | integrator | — | this file | todo |
| T-11-062 | Launch: counsel sign-off on terms and per-provider guidance | 11 §5 | human-counsel* | 6 | NEW:REV-01 | todo |
| T-11-063 | Launch: Phase 1–6 exit criteria all automated and green | 11 §5 | integrator | 6 | this file | todo |
| T-11-064 | Launch: public threat model, protocol spec, self-host guide published | 11 §5 | mo-sec + integrator + mo-docs* | 6 | NEW:REV-02 | todo |
| T-11-065 | Launch: onboarding enforces device caps and promotes provider-side spend limits | 11 §5 | mo-node | 1 | NEW:E83 | todo |
| T-11-066 | Launch: status page and incident contact | 11 §5 | human-po* + mo-ops* | 6 | NEW:REV-06 | todo |
| T-11-067 | Launch: `/open` page live (license, source, self-host guide, monthly costs, sponsors) | 11 §5 | mo-web + human-po* | 4 | NEW:E66 | todo |
| T-11-068 | Launch: key log live with hourly public Git anchoring | 11 §5 | mo-relay + mo-ops* | 3 | NEW:E44 | todo |
| T-11-069 | Launch: public beta never runs with relay-asserted keys or approvals (Phase 1 dev shortcuts compiled out or refused outside `--dev`) | 11 §5 | mo-relay + mo-node | 6 | NEW:E43 | todo |
| T-11-070 | Launch: 10 design-partner repos and 50 donors recruited before opening sign-ups | 11 §5 | human-po* | 6 | NEW:REV-06 | todo |

## 12 — Decisions, rejected ideas, open questions

ADRs are binding design constraints; each row points to the canonical rows that implement it.

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-12-001 | ADR-01 everything open source, Apache-2.0 OR MIT (→ T-00-001) | ADR-01 | integrator | 0 | NEW:CI-18 | todo |
| T-12-002 | ADR-02 free forever, no paid verified mode, never hold money (→ T-00-002) | ADR-02 | human-po* | — | NEW:REV-02 | todo |
| T-12-003 | ADR-03 µ$ int64 unit of account (→ T-05-001) | ADR-03 | mo-relay + mo-worker | 1 | NEW:CI-10 | todo |
| T-12-004 | ADR-04 two doors, one pipeline (→ T-07-025…T-07-058) | ADR-04 | mo-node | 1 | E01, E04, E05 | todo |
| T-12-005 | ADR-05 one Node process per machine with thin front-ends (→ T-07-002) | ADR-05 | mo-node | 1 | NEW:E74 | todo |
| T-12-006 | ADR-06 actor Scheduler, sheddable submit / never-blocking lifecycle queue, `sync.Map` only for forwarding; revisit at p99 > 200 µs or > 50k events/s | ADR-06 | mo-relay | 1 | NEW:CI-04, NEW:MON-01 | todo |
| T-12-007 | ADR-07 sealed envelopes: fresh CK per body, HPKE wraps, Worker-salted per-attempt RK (→ T-03-061…T-03-075) | ADR-07 | mo-proto | 1 | NEW:CI-01 | todo |
| T-12-008 | ADR-08 Gateway-signed tasks; Workers accept only owner-approved members, fresh, never-seen ids (→ T-03-085…T-03-090) | ADR-08 | mo-node | 1→3 | E16, NEW:E43 | todo |
| T-12-009 | ADR-09 Ed25519 (ZIP-215) + X25519 per device; no GPG; `lp` labels | ADR-09 | mo-proto | 1 | NEW:CI-01 | todo |
| T-12-010 | ADR-10 OS keychain + encrypted-file / systemd-creds fallback | ADR-10 | mo-node | 1/5 | NEW:E73 | todo |
| T-12-011 | ADR-11 signatures = accountability: donor receipts, signed checkpoints per tool call, signed disputes; countersigning only if leaderboard fraud appears | ADR-11 | mo-node + mo-worker | 3 | NEW:E45, NEW:E46 | todo |
| T-12-012 | ADR-12 owner-signed approvals in a Node-mirrored key log with Git anchor (→ T-06-080…T-06-091) | ADR-12 | mo-relay + mo-node | 3 | NEW:E43 | todo |
| T-12-013 | ADR-13 public receipt projections only (→ T-03-115) | ADR-13 | mo-proto + mo-web | 1/4 | NEW:E68 | todo |
| T-12-014 | ADR-14 strict recursive allowlist firewall incl. headers; only the listed safe mutations (attribution id, model mapping, stream usage, `store:false`) | ADR-14 | mo-worker | 1 | E09, NEW:E56 | todo |
| T-12-015 | ADR-15 money durability rules (FULL, ack after commit, commit before assign, release only on proof, outbox 7 days, start-period attribution) | ADR-15 | mo-relay + mo-node | 1 | E12, NEW:E38 | todo |
| T-12-016 | ADR-16 three-layer caps with Worker local reservations per device | ADR-16 | mo-worker + mo-node | 1 | E11 | todo |
| T-12-017 | ADR-17 affinity aligned with cache TTL, HMAC key under per-device secret | ADR-17 | mo-relay + mo-node | 2 | NEW:E30 | todo |
| T-12-018 | ADR-18 OpenRouter-style slugs, native ids accepted, signed catalog mapping | ADR-18 | mo-relay + mo-node + mo-worker | 1 | NEW:E41 | todo |
| T-12-019 | ADR-19 no cross-dialect translation; OpenRouter and DeepSeek serve both dialects; revisit at > 10% unserved | ADR-19 | mo-worker | 1 | E03, NEW:MON-03 | todo |
| T-12-020 | ADR-20 no hedged requests, no failover after start | ADR-20 | mo-relay | 1 | E06, NEW:CI-04 | todo |
| T-12-021 | ADR-21 prefix-delta deferred (→ T-03-093) | ADR-21 | mo-relay | D | NEW:MON-03 | todo |
| T-12-022 | ADR-22 drain-and-restart deploys in v1 (→ T-10-010) | ADR-22 | mo-relay | 2 | NEW:E35 | todo |
| T-12-023 | ADR-23 `count_tokens` answered locally (→ T-07-026) | ADR-23 | mo-node | 1 | NEW:E53 | todo |
| T-12-024 | ADR-24 Go stdlib `ServeMux`; Rust `serde_json` (subject to CONTRACT §1 strict-parse rule) | ADR-24 | mo-relay + mo-node | 1 | NEW:CI-02, NEW:E26 | todo |
| T-12-025 | ADR-25 single-node relay; partition by repo later | ADR-25 | mo-relay | — | NEW:MON-03 | todo |
| T-12-026 | ADR-26 no content moderation at the relay | ADR-26 | mo-relay | — | E13 | todo |
| T-12-027 | ADR-27 no direct peer-to-peer transport in v1 | ADR-27 | mo-node | — | NEW:REV-02 | todo |
| T-12-028 | ADR-28 presence aggregated by default; per-donor display opt-in | ADR-28 | mo-web | 4 | NEW:E68 | todo |
| T-12-029 | ADR-29 API keys only; consumer credentials refused | ADR-29 | mo-worker | 1 | NEW:E60 | todo |
| T-12-030 | ADR-30 never host donor keys; no relay-hosted MCP; self-tunnel opt-in Phase 5 | ADR-30 | mo-relay + mo-node | — | NEW:REV-02, NEW:E87 | todo |
| T-12-031 | ADR-31 public repositories only on the public instance | ADR-31 | mo-relay | 1 | NEW:E65 | todo |
| T-12-032 | ADR-32 durations, deadlines, weights are configuration values with documented defaults | ADR-32 | mo-relay + mo-node | 1 | NEW:E82 | todo |
| T-12-033 | Rejected (must not appear): crypto tokens / on-chain ledger; Moochy-run cloud workers holding keys; relay-hosted MCP/API; relay moderation; hedging / failover after start / stream splicing; GPG; lock-free multi-index registry; `moochy self-verify` | 12 §2 | integrator | — | NEW:REV-02 | todo |
| T-12-034 | Deferred (tracked, not built): trust tiers/auto-approval, countersigning, receipt log + witnesses + browser verifier, prefix-delta, blue/green, stream resume, federation, cross-dialect, email notifications | 12 §2 | integrator | D | NEW:MON-03 | todo |
| T-12-035 | Q1: license wording + DCO (recommended) decided before first external contribution | 12 Q1 | human-po* | 0 | NEW:REV-02 | todo |
| T-12-036 | Q2: private repos on public instance — recommended no | 12 Q2 | human-po* | 5 | NEW:REV-02 | todo |
| T-12-037 | Q3: which providers get a counsel "go" | 12 Q3 | human-counsel* | 0 | NEW:REV-01 | todo |
| T-12-038 | Q4: which IDEs reach a loopback base URL; which MCP clients send roots, honor progress, allow longer timeouts → encoded in matrix + `connect` | 12 Q4 | mo-e2e* + mo-node | 0 | NEW:CI-20 | todo |
| T-12-039 | Q5: exact Anthropic-compatible endpoints and usage fields for OpenRouter and DeepSeek | 12 Q5 | mo-worker | 0 | NEW:CI-17 | todo |
| T-12-040 | Q6: public instance region | 12 Q6 | human-po* | 1 | NEW:REV-06 | todo |
| T-12-041 | Q7: governance — two maintainers with hardware tokens hold log/catalog keys; Open Collective fiscal host; `GOVERNANCE.md` | 12 Q7 | human-po* + mo-docs* | 6 | NEW:REV-02 | todo |
| T-12-042 | Q8: task metadata retention 90 days raw, aggregates forever (→ T-06-093) | 12 Q8 | human-po* | 1 | NEW:E85 | todo |
| T-12-043 | Q9: default per-member quota 20% and per-task cap $5, editable | 12 Q9 | human-po* | 2 | NEW:E32, E10 | todo |
| T-12-044 | Q10: donors restricting which members use their pledge — not in v1, revisit | 12 Q10 | human-po* | 4 | NEW:REV-02 | todo |
| T-12-045 | Q11: project name check with design partners | 12 Q11 | human-po* | 0 | NEW:REV-06 | todo |
| T-12-046 | ADR-33 gRPC (HTTP/2, protobuf) for every machine-to-machine link: `NodeLink`, `LocalControl` (0600 Unix socket), `RelayAdmin` (Unix socket); HTTP/JSON/SSE only where external compatibility requires; signed artifacts stay exact JSON bytes in `bytes` (→ T-C12-*) | ADR-33 | integrator + mo-relay + mo-node | 1 | NEW:E23, NEW:E25, NEW:E74 | todo |
| T-12-047 | ADR-34 responsiveness budgets are release blockers; adaptive group commit replaces the fixed 10 ms window (→ T-C13-*, T-04-036, T-09-023) | ADR-34 | mo-relay + mo-node + mo-worker + mo-web | 1 | E22 | todo |

## 13 — Review log (regression guards)

Every accepted or adapted finding is a fix that must stay fixed. Each row names the guard; the mechanism is in the canonical row cited.

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-13-001 | Pass 0: open-source monorepo, free forever, MCP first-class door, OpenRouter + DeepSeek first-class in Phase 1 stay true (→ T-00-001, T-00-002, T-07-048, T-07-063, T-07-064) | 13 P0 | integrator | 1 | E02, E03, E04 | todo |
| T-13-002 | Pass 1 + 5 doc consistency: every `[NN §X]` reference resolves; shared parameters (ACK 500 ms, start 30 s, routing 5 s after last body frame, ≤ 8 wraps, ≤ 3 attempts, ±10 min, 7-day outbox, `synchronous=FULL`, $5 cap, 90-day retention) identical across plan, contract, and code defaults | 13 P1, P5 | integrator | — | NEW:CI-18 | todo |
| T-13-003 | 2.1/3.1/4.1 (critical): no key/nonce reuse — fresh CK per body, Worker-salted RK, attempt + R in AAD, accepted-attempt-only decrypt, abort on second started stream, distinct-key vector | 13 2.1 | mo-proto + mo-node | 1 | NEW:CI-01, NEW:E49 | todo |
| T-13-004 | 2.2 (critical): relay cannot invent an approved donor — owner-signed claims/approvals/memberships, sealing only to owner-approved keys, owner alerts, Git anchor | 13 2.2 | mo-node + mo-relay | 3 | NEW:E43, NEW:E44 | todo |
| T-13-005 | 2.3: task authenticity — Gateway task signature, `repo_id` in route header, membership, pledge↔repo, ULID freshness, served set | 13 2.3 | mo-node | 1→3 | E16, NEW:E43, NEW:E58 | todo |
| T-13-006 | 2.4: poisoned tool call before any signature impossible — signed progress checkpoints gate release | 13 2.4 | mo-node + mo-worker | 3 | NEW:E46 | todo |
| T-13-007 | 2.5: MCP `files` hardening (recorded root ∩ roots, realpath, no symlinks, deny lists, `git check-ignore`) | 13 2.5 | mo-node | 3 | NEW:E48 | todo |
| T-13-008 | 2.6: no under-counting — stream usage forced; estimated receipts settle at reservation | 13 2.6 | mo-worker + mo-relay | 1 | E02, NEW:E37 | todo |
| T-13-009 | 2.7: deterministic exact estimate; PDFs behind a flag; overage bound restated; Worker local reservations per device | 13 2.7 | mo-worker + mo-node | 1 | E11, NEW:E57 | todo |
| T-13-010 | 2.8: headers sealed + allowlisted; OpenAI `n`, predictions, service tier, audio, web-search denied; OpenRouter routing/plugins/variants denied + max-price; recursive validation + fuzzing | 13 2.8 | mo-worker | 1 | NEW:E57, NEW:CI-03 | todo |
| T-13-011 | 2.9: tripwire covers OpenAI `tool_calls`; name + schema checks; forbidden block types; model match; MCP results framed untrusted | 13 2.9 | mo-node + mo-worker | 3 | E18, NEW:E81 | todo |
| T-13-012 | 2.10: auth signs dialed origin + TLS exporter inside `lp` | 13 2.10 | mo-node + mo-relay | 1 | NEW:E23 | todo |
| T-13-013 | 2.11: projections hide device ids and fine timestamps; affinity key is an HMAC | 13 2.11 | mo-proto + mo-node | 1/2 | NEW:E68, NEW:E30 | todo |
| T-13-014 | 2.12: `connect --write` never commits tokens; token rotation; port held by service manager; `doctor` uid check | 13 2.12 | mo-node | 1/5 | NEW:E75, NEW:E76, NEW:E83 | todo |
| T-13-015 | 2.13 (adapted): plausibility checks live in dispute rules | 13 2.13 | mo-node | 3 | NEW:E45 | todo |
| T-13-016 | 2.14: `lp` labels, HKDF-derived salts/keys, ZIP-215 vectors, suite id in HPKE info and `KEY_ADDED`, monotonic catalog | 13 2.14 | mo-proto + mo-relay | 1 | NEW:CI-01, NEW:E41 | todo |
| T-13-017 | 2.15 (adapted): tlog path layer own or Tessera; `hpke` under `cargo-vet`; client-executed computer use allowed | 13 2.15 | mo-relay + mo-release* + mo-worker | 3 | NEW:CI-08, NEW:CI-13 | todo |
| T-13-018 | 3.2 (critical): receipts and reservations per attempt; release only on proof of zero spend; "started" = provider headers; no failover after start | 13 3.2 | mo-relay | 1 | E06, E07, NEW:E28 | todo |
| T-13-019 | 3.3: `synchronous=FULL`; ack after commit; checkpoints only for replicated sizes; 7-day outbox; `replay_since` | 13 3.3 | mo-relay + mo-node | 1/2 | E12, NEW:E36 | todo |
| T-13-020 | 3.4: commit-before-assign; Workers abort + receipt on link loss; `known_tasks` releases orphans; pessimistic only for long-absent Workers | 13 3.4 | mo-relay + mo-node | 1 | E12, NEW:E34 | todo |
| T-13-021 | 3.5 (adapted): deploy handoff safe via drain-and-restart; blue/green requirements recorded | 13 3.5 | mo-relay | 2 | NEW:E35 | todo |
| T-13-022 | 3.6: Worker device cap counts reservations, not only settled spend; Relay decrements `local_cap_left` | 13 3.6 | mo-worker + mo-relay | 1 | E11 | todo |
| T-13-023 | 3.7: start-period attribution; boot applies missed rollovers; SAVEPOINT per op; constraint violation fatal + replay | 13 3.7 | mo-relay | 1 | NEW:E38, NEW:E70 | todo |
| T-13-024 | 3.8: cancel on Gateway disconnect; dedupe per `(gateway_device, task_id)`; resubmission rules; source-checked forwarding | 13 3.8 | mo-relay | 2 | NEW:E33, NEW:E50, NEW:E25 | todo |
| T-13-025 | 3.9: sheddable submit queue, never-blocking lifecycle queue, slice-swap writer, separate completion channel | 13 3.9 | mo-relay | 2 | NEW:E51, NEW:CI-04 | todo |
| T-13-026 | 3.10: presence keyed by `(device, session)` | 13 3.10 | mo-relay | 2 | NEW:E24 | todo |
| T-13-027 | 3.11: device caps have counters (`device_usage`), state, invariants, audit | 13 3.11 | mo-relay | 2 | NEW:E32, NEW:E70 | todo |
| T-13-028 | 3.12: 24 h waits are SQL sweeps; Edge byte budgets | 13 3.12 | mo-relay | 2 | NEW:E37, NEW:E51 | todo |
| T-13-029 | 3.13 (adapted): migrations with no second writer; `min_compatible_version`; long index builds after boot | 13 3.13 | mo-relay | 2 | NEW:E69 | todo |
| T-13-030 | 3.14: non-retryable `over_task_cap`, `quota_exceeded`, `model_not_in_pool`; default cap $5 with console visibility | 13 3.14 | mo-relay + mo-node + mo-web | 2 | E10, NEW:E29 | todo |
| T-13-031 | 3.15: ≈ 200 starts/s math; 65,497-byte chunks; exact estimate; late-message rule; routing deadline from last body frame; `wal_autocheckpoint=0` | 13 3.15 | mo-relay + mo-proto | 1/2 | NEW:CI-01, NEW:E28, NEW:E69 | todo |
| T-13-032 | 4.2: v1 trust layer = one key log + Git anchor + projections + CLI verification + disputes (receipt log, witnesses, countersign, browser verifier deferred) | 13 4.2 | mo-relay + mo-node | 3 | NEW:E42, NEW:E63 | todo |
| T-13-033 | 4.3: OpenRouter and DeepSeek adapters serve both dialects | 13 4.3 | mo-worker | 1 | E03 | todo |
| T-13-034 | 4.4: slugs from Phase 1; native ids accepted; `connect` sets main and small models | 13 4.4 | mo-node + mo-relay | 1 | NEW:E41, NEW:E75 | todo |
| T-13-035 | 4.5: MCP door robust to optional client features (roots fallback, timeout budget, model enum, `instructions`, "where supported") | 13 4.5 | mo-node | 1 | E04, NEW:E81 | todo |
| T-13-036 | 4.6: prefix-delta deferred with metric trigger | 13 4.6 | mo-relay | D | NEW:MON-03 | todo |
| T-13-037 | 4.7: settle on OpenRouter reported cost bounded by reservation; stream usage forced | 13 4.7 | mo-worker + mo-relay | 1 | E02, NEW:E40 | todo |
| T-13-038 | 4.8: open-source/free wording without holes; `draft-spec.md` unmodified | 13 4.8 | integrator + mo-web | 0 | NEW:REV-02 | todo |
| T-13-039 | 4.9: drain-and-restart in v1, blue/green metric-triggered | 13 4.9 | mo-relay | 2 | NEW:E35 | todo |
| T-13-040 | 4.10: remote-HTTPS-only MCP clients stated in matrix; self-tunnel Phase 5 | 13 4.10 | mo-node + mo-docs* | 5 | NEW:E87 | todo |
| T-13-041 | 4.11: no trust tiers / auto-approve / tier header; pinned donors; tripwire = speed bump | 13 4.11 | mo-node + mo-relay | 3 | NEW:E43, NEW:CI-14 | todo |
| T-13-042 | 4.12: no self-verify; reproducible Linux musl builds for beta | 13 4.12 | mo-release* | 3 | NEW:CI-08 | todo |
| T-13-043 | 4.13: reconciliation method per provider | 13 4.13 | mo-node | 1/2 | NEW:CI-20 | todo |
| T-13-044 | 4.14: `count_tokens` local | 13 4.14 | mo-node | 1 | NEW:E53 | todo |
| T-13-045 | 4.15: telemetry opt-in everywhere; NACK details sealed; browser verifier deferred | 13 4.15 | mo-node + mo-worker | 1 | E09, NEW:E82 | todo |

## CONTRACT — `spec/CONTRACT.md` (requirements not already traced to a plan row)

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-C00-001 | `spec/proto/moochy/v1/local.proto` (`LocalControl`) exists, owned and kept current by `mo-node` | CONTRACT §0 | mo-node | 1 | NEW:CI-23 | todo |
| T-C00-002 | `spec/proto/moochy/v1/admin.proto` (`RelayAdmin`) exists, owned and kept current by `mo-relay` | CONTRACT §0 | mo-relay | 2 | NEW:CI-23 | todo |
| T-C00-003 | `moochy-worker` crate has **no dependency on `moochy-proto`**; the node crate wires the two | CONTRACT §0 | mo-worker + integrator | 1 | NEW:CI-07 | todo |
| T-C01-001 | Machine-to-machine messages are protobuf over gRPC; signed artifacts (route header, inner payload, receipts, projections, catalog) stay exact JSON bytes in `bytes` fields | CONTRACT §1 | mo-proto + mo-relay + mo-node | 1 | NEW:CI-01, E01 | todo |
| T-C01-002 | Strict JSON parse (reject duplicate keys, invalid UTF-8, lone surrogates, numbers outside i64/f64, depth > 64) for the **route header** at Relay and Worker | CONTRACT §1 | mo-relay + mo-worker | 1 | NEW:E26, NEW:CI-03 | todo |
| T-C01-003 | Strict parse for **receipts/projections** at Relay and Gateway | CONTRACT §1 | mo-relay + mo-proto | 1 | NEW:E26 | todo |
| T-C01-004 | Strict parse for **provider request bodies** in the Worker firewall; mutated bodies re-serialized from the validated tree, never forwarding bytes another parser could read differently | CONTRACT §1 | mo-worker | 1 | NEW:E26, E09 | todo |
| T-C01-005 | Strict parse for **provider responses used for usage** | CONTRACT §1 | mo-worker | 1 | NEW:E26, NEW:CI-03 | todo |
| T-C01-006 | Strict parse for **MCP messages** (stdio and Streamable HTTP) | CONTRACT §1 | mo-node | 1 | NEW:E26 | todo |
| T-C01-007 | Go never uses plain `encoding/json` for those parses; Rust never relies on last-key-wins `serde_json::Value` | CONTRACT §1 | mo-relay + mo-proto + mo-worker + mo-node | 1 | NEW:CI-02 | todo |
| T-C01-008 | JSON bytes as base64url without padding; ids `task` ULID, `d_`, `u_`, `r_`, `p_` + ULID; money as JSON integer µ$ `*_uusd` | CONTRACT §1 | mo-proto + mo-relay | 1 | NEW:CI-01 | todo |
| T-C01-009 | `lp` = `u32_be(len) ‖ x`; integers inside `lp` as `u64_be` unless a width is stated; HKDF Expand length 32; SHA-256 | CONTRACT §1 | mo-proto | 0 | NEW:CI-01 | todo |
| T-C01-010 | ZIP-215 verification libraries: Rust `ed25519-zebra` (or equivalent), Go `hdevalence/ed25519consensus`; RFC 8032 signing | CONTRACT §1 | mo-proto + mo-relay | 1 | NEW:CI-01 | todo |
| T-C01-011 | HPKE suite KEM 0x0020 / KDF 0x0001 / AEAD 0x0003, `suite_id` = `moochy.v1.hpke.x25519-sha256-chacha20poly1305` | CONTRACT §1 | mo-proto | 1 | NEW:CI-01 | todo |
| T-C02-001 | Exact label set incl. `moochy/v1/device-start` (DeviceStart proof of possession) | CONTRACT §2 | mo-proto + mo-relay | 0 | NEW:CI-01 | todo |
| T-C03-001 | `dialed_origin` is the origin string exactly as dialed (see §D on `wss://` vs `https://`) | CONTRACT §3 | mo-node + mo-relay | 1 | NEW:E23, NEW:CI-01 | todo |
| T-C03-002 | Route header transmitted as its exact UTF-8 JSON bytes (`SubmitOpen.route`, `Assign.route`), no decoded convenience copy; the Relay parses those bytes (strictly) | CONTRACT §3 | mo-node + mo-relay | 1 | E15, NEW:E26 | todo |
| T-C06-001 | `relay serve --addr --grpc-addr --db --tls-cert --tls-key [--admin-socket] [--dev] [--catalog]`; HTTP and gRPC on separate listeners | CONTRACT §6 | mo-relay | 1 | E01 | todo |
| T-C06-002 | Relay prints exactly one ready line `{"event":"ready","addr":…,"grpc_addr":…}` on stdout; JSON `slog` logs on stderr | CONTRACT §6 | mo-relay | 1 | E01 | todo |
| T-C06-003 | `--dev` refused unless `--addr` is loopback; dev API exists only with `--dev` | CONTRACT §6 | mo-relay | 1 | NEW:E90 | todo |
| T-C06-004 | Dev API: `POST /dev/user`, `/dev/repo`, `/dev/member`, `/dev/pledge` (approved immediately, relay-asserted), `/dev/device/approve`, `GET /dev/state` | CONTRACT §6 | mo-relay | 1 | E01, E10 | todo |
| T-C06-005 | Dev chaos `POST /dev/chaos {ignore_caps, tamper_route, replay_assign, inject_frame}` makes the relay misbehave like a malicious operator | CONTRACT §6 | mo-relay | 1 | E11, E15, E16, E17 | todo |
| T-C06-006 | `--catalog` JSON per 05 §2.2; built-in test catalog when absent | CONTRACT §6 | mo-relay | 1 | E01 | todo |
| T-C06-007 | `moochy --home <dir> <command>`; all state under `<dir>`; test keystore = encrypted file with `MOOCHY_PASSPHRASE` | CONTRACT §6 | mo-node | 1 | E01, NEW:E73 | todo |
| T-C06-008 | `moochy login --relay https://… --ca-file --roles --headless` prints `device_code` then `logged_in` JSON events (via gRPC `DeviceStart`/`DevicePoll`) | CONTRACT §6 | mo-node | 1 | E01 | todo |
| T-C06-009 | `moochy keys add … --key-stdin [--base-url]`: `--base-url` accepted only for loopback hosts **and** `MOOCHY_INSECURE_DEV=1`; else refused | CONTRACT §6 | mo-node | 1 | NEW:E60 | todo |
| T-C06-010 | `moochy config set` for `device_monthly_cap_uusd`, `slots_max`, `gateway_addr` | CONTRACT §6 | mo-node | 1 | E01, E11 | todo |
| T-C06-011 | `moochy up --foreground` writes `<dir>/state/node.json {device_id, gateway_url, mcp_url, pid}` and prints the same `ready` event | CONTRACT §6 | mo-node | 1 | E01 | todo |
| T-C06-012 | `moochy env --repo owner/name --json` → `{anthropic_base_url, openai_base_url, token}` | CONTRACT §6 | mo-node | 1 | E01 | todo |
| T-C06-013 | `moochy mcp --repo` stdio JSON-RPC 2.0 newline-delimited, shim via `LocalControl` on `<dir>/state/node.sock` | CONTRACT §6 | mo-node | 1 | E04 | todo |
| T-C06-014 | Exit codes: 0 ok, 2 usage, 3 auth/approval refused, 4 network, 10 internal | CONTRACT §6 | mo-node | 1 | NEW:E73, NEW:E23 | todo |
| T-C07-001 | Fake providers (Go `httptest`) driven by tags `#tokens:N`, `#fail:429\|529\|500`, `#cut:K`, `#slow:MS`, `#tool:<json>`, `#model:<id>` | CONTRACT §7 | mo-e2e | 1 | E01–E22 | todo |
| T-C07-002 | Anthropic fake: `POST /v1/messages` SSE identical in shape to the real API (message_start/message_delta usage, cache fields), `GET /v1/models` | CONTRACT §7 | mo-e2e | 1 | E01 | todo |
| T-C07-003 | OpenAI-style fakes (`openai`, `deepseek`, `openrouter`): `/v1/chat/completions` SSE, usage only with `include_usage`, DeepSeek cache fields, OpenRouter `usage.cost`, `/v1/models`; OpenRouter + DeepSeek also serve the Anthropic shape | CONTRACT §7 | mo-e2e | 1 | E02, E03 | todo |
| T-C07-004 | Every fake records received requests (headers + body) for assertions | CONTRACT §7 | mo-e2e | 1 | E09, NEW:E56 | todo |
| T-C08-001 | Each scenario is one Go test `TestE<NN>_<name>`; may `t.Skip("pending: …")`, never deleted or weakened | CONTRACT §8; AGENTS §2 | mo-e2e | 1 | NEW:CI-18 | todo |
| T-C09-001 | `moochy.dev/relay/internal/web` exports `New(src Source) http.Handler`, the read-only `Source` interface (repo by slug, pool summary, goal numbers, recent projections, donor station data) and `Publish(topic, ev)`; `mo-web` ships a fake `Source`, `mo-relay` implements it | CONTRACT §9 | mo-web + mo-relay | 4 | E19 | todo |
| T-C09-002 | Hand-written CSS with custom properties, no framework, no web fonts, total CSS ≤ 12 KB; htmx + sse extension vendored | CONTRACT §9 | mo-web | 4 | NEW:CI-09 | todo |
| T-C10-001 | Build entry points: `cargo build --release`, `cargo clippy --all-targets -- -D warnings`, `go build -trimpath -o bin/relay ./cmd/relay`, `go vet ./...`, `go test -race -count=1 ./...` with `MOOCHY_BIN`/`RELAY_BIN` | CONTRACT §10 | integrator + mo-e2e | 1 | NEW:CI-02 | todo |
| T-C11-001 | Username format `^[a-z0-9](?:[a-z0-9-]{1,30}[a-z0-9])$`, 3–32 chars, ASCII lowercase, no `--` | CONTRACT §11 | mo-relay + mo-node | 1 | E21 | todo |
| T-C11-002 | Case-insensitive uniqueness: stored lowercase + `UNIQUE COLLATE NOCASE` | CONTRACT §11 | mo-relay | 1 | E21 | todo |
| T-C11-003 | Handle chosen at first sign-in: default = provider login lowercased if valid and free, otherwise the user must pick; no silent auto-suffixing | CONTRACT §11 | mo-relay + mo-web | 1 | E21, NEW:E65 | todo |
| T-C11-004 | Reserved handles refused at signup and rename: every first path segment of web/API routes, staff/system words list, every handle ever used | CONTRACT §11 | mo-relay | 1 | E21 | todo |
| T-C11-005 | Reserved list stays in sync with the route map (a new top-level route adds its segment) | CONTRACT §11; 08 §2 | mo-relay + mo-web | 1 | NEW:CI-24 | todo |
| T-C11-006 | Rename at most once per 30 days; old handle becomes a permanent tombstone redirecting for 90 days | CONTRACT §11 | mo-relay + mo-web | 1 | E21 | todo |
| T-C11-007 | Shared vectors `spec/vectors/usernames.json` (valid, invalid, reserved, confusables, case variants), passed identically by Go and Rust | CONTRACT §11 | mo-proto + mo-relay | 1 | NEW:CI-01 | todo |
| T-C11-008 | Rust CLI and logs never print server-provided strings raw (handles, repo names, …): control characters stripped/escaped | CONTRACT §11 | mo-node | 1 | NEW:E91 | todo |
| T-C11-009 | DB uniqueness: provider identity (`provider`, `provider_user_id`) and at most one identity per provider per user | CONTRACT §11 | mo-relay | 1 | NEW:E69 | todo |
| T-C11-010 | DB uniqueness: device name per user, case-insensitive (`user_id`, lower(`name`)) | CONTRACT §11 | mo-relay | 1 | NEW:E69 | todo |
| T-C11-011 | DB uniqueness: repository (`provider`, lower(`owner`), lower(`name`)) case-insensitive, plus (`provider`, `provider_repo_id`) | CONTRACT §11 | mo-relay | 1 | NEW:E69 | todo |
| T-C11-012 | DB uniqueness: `users.pseudonym`, `devices.sign_pub`, live pledge, membership, task, receipt + `receipt_ref`, web session `id_hash` | CONTRACT §11 | mo-relay | 1 | NEW:E69 | todo |
| T-C11-013 | Local tokens ≥ 256-bit random, stored hashed, unique | CONTRACT §11 | mo-node | 1 | E14, NEW:E76 | todo |
| T-C11-014 | Dev API `username` = this handle | CONTRACT §11 | mo-relay | 1 | E21 | todo |
| T-C12-001 | Node ↔ Relay = gRPC `moochy.v1.NodeLink` (Session, Submit per task, Serve per attempt, DeviceStart, DevicePoll) | CONTRACT §12 | mo-relay + mo-node | 1 | E01 | todo |
| T-C12-002 | Per-task streams: stream cancel = provider call aborted; deadlines and HTTP/2 flow control per task | CONTRACT §12 | mo-relay + mo-node | 1 | E08, NEW:E33 | todo |
| T-C12-003 | Ciphertext and signed JSON travel in protobuf `bytes`; no JSON control messages on the link | CONTRACT §12; link.proto | mo-proto + mo-relay + mo-node | 1 | E01 | todo |
| T-C12-004 | `Chunk{attempt, seq, last, ct}` carries every body/response chunk; request bodies use `attempt = 0` | CONTRACT §5; link.proto | mo-proto + mo-relay + mo-node | 1 | E01, NEW:CI-01 | todo |
| T-C12-005 | CLI / MCP shim ↔ Node = gRPC `LocalControl` over `<home>/state/node.sock`, mode 0600, **peer uid checked**, plaintext h2c only on this socket | CONTRACT §12 | mo-node | 1 | NEW:E74 | todo |
| T-C12-006 | Operator ↔ Relay = gRPC `RelayAdmin` over a 0600 Unix socket (`--admin-socket`), used by `relay admin …` (suspend, catalog publish, drain, state); never exposed on the network | CONTRACT §12 | mo-relay | 2 | NEW:E79 | todo |
| T-C12-007 | gRPC NOT used for: API door, MCP door, browser, OAuth callbacks, badges, dev API | CONTRACT §12 | mo-node + mo-web + mo-relay | — | E01, E04, E19 | todo |
| T-C12-008 | Later: regional Edge ↔ central Scheduler reuses `NodeLink` messages | CONTRACT §12 | mo-relay | D | NEW:MON-03 | todo |
| T-C12-009 | Libraries: Go `google.golang.org/grpc` + `protobuf`; Rust `tonic` (no default TLS features, own rustls connector) + `prost` | CONTRACT §12; AGENTS §3–4 | mo-relay + mo-node + mo-proto | 1 | NEW:CI-07 | todo |
| T-C12-010 | Generated code committed (Go `relay/internal/pb`, Rust `cli/crates/proto/src/pb/`); builds never need `protoc`; `spec/proto/gen.sh` regenerates with pinned `protoc` + plugins; CI checks generated code is up to date | CONTRACT §12 | integrator + mo-relay + mo-proto | 1 | NEW:CI-23 | todo |
| T-C12-011 | One HTTP/2 connection = one authenticated session; Go `TransportCredentials` tags each connection with an id + RFC 9266 exporter, read via `peer.FromContext` | CONTRACT §12 | mo-relay | 1 | NEW:E23 | todo |
| T-C12-012 | Rust custom tonic connector (`connect_with_connector`, `tokio-rustls`) captures `export_keying_material`; one `Channel` per TLS connection, rebuilt and re-authenticated on any transport error | CONTRACT §12 | mo-node | 1 | NEW:E23, E12 | todo |
| T-C12-013 | TLS 1.3 only, ALPN `h2`; no plaintext h2c except the local Unix sockets | CONTRACT §12 | mo-relay + mo-node | 1 | NEW:E23 | todo |
| T-C12-014 | Server limits: `MaxConcurrentStreams` 64/connection; msg size 128 KiB; `MaxHeaderListSize` 16 KiB | CONTRACT §12 | mo-relay | 1 | NEW:E25 | todo |
| T-C12-015 | Keepalive enforcement (`MinTime` 10 s, `PermitWithoutStream`), server pings 15 s, 2 missed = dead | CONTRACT §12 | mo-relay | 1 | NEW:E25, NEW:E34 | todo |
| T-C12-016 | Per-connection limits on stream-open rate and resets (HTTP/2 Rapid Reset CVE-2023-44487); grpc-go / x/net versions with CONTINUATION-flood fixes and HPACK limits | CONTRACT §12 | mo-relay + mo-sec | 1 | NEW:E25, NEW:CI-08 | todo |
| T-C12-017 | Per-IP connection cap; `DeviceStart`/`DevicePoll` rate-limited per IP | CONTRACT §12 | mo-relay | 1 | NEW:E80 | todo |
| T-C12-018 | Unauthenticated calls other than Session/Device* rejected before any allocation of task state | CONTRACT §12 | mo-relay | 1 | NEW:E23, NEW:E25 | todo |
| T-C12-019 | Rust client: same message-size caps, `http2_max_header_list_size`, connect/request timeouts, bounded per-stream buffers, no gRPC compression | CONTRACT §12 | mo-node | 1 | NEW:E25 | todo |
| T-C12-020 | gRPC reflection and channelz disabled in production; `grpc.health.v1` allowed | CONTRACT §12 | mo-relay | 1 | NEW:E25 | todo |
| T-C12-021 | Relay policy errors travel as `Failed{code, retryable}` inside the stream; gRPC status codes only for transport/auth (`UNAUTHENTICATED`, `RESOURCE_EXHAUSTED`, `UNAVAILABLE`, `DEADLINE_EXCEEDED`) | CONTRACT §12 | mo-relay + mo-node | 1 | E10, NEW:E54 | todo |
| T-C12-022 | Protobuf decoding never trusted for strict security/money decisions: those read the signed JSON bytes with the strict parser | CONTRACT §12 | mo-relay + mo-node | 1 | NEW:E26 | todo |
| T-C13-001 | Gateway: client request accepted → first sealed byte on the gRPC stream (100 KB body) p50 ≤ 1 ms / p99 ≤ 3 ms; zstd level 1–3 by size, sealing streamed while compressing, no full-body copies | CONTRACT §13 | mo-node + mo-proto | 1 | E22 | todo |
| T-C13-002 | Relay: Submit → Assign p50 ≤ 2 ms / p99 ≤ 8 ms with adaptive group commit | CONTRACT §13 | mo-relay | 1 | E22 | todo |
| T-C13-003 | Worker: last body chunk → Ack p50 ≤ 1 ms / p99 ≤ 3 ms; no re-copying; local reservation in memory, persisted before the receipt | CONTRACT §13 | mo-node + mo-worker | 1 | E22 | todo |
| T-C13-004 | Per response chunk, provider byte → client byte added p50 ≤ 300 µs / p99 ≤ 1 ms; no token batching; every chunk flushed (gRPC message, HTTP/2, SSE event) | CONTRACT §13 | mo-worker + mo-node + mo-relay | 1 | E22 | todo |
| T-C13-005 | End-to-end added TTFT on loopback with an instant fake p50 ≤ 5 ms / p99 ≤ 15 ms | CONTRACT §13 | mo-node + mo-relay + mo-worker | 1 | E22 | todo |
| T-C13-006 | `moochy status` / MCP shim start / `moochy env` ≤ 20 ms (Unix-socket gRPC to the warm Node) | CONTRACT §13 | mo-node | 1 | E22 | todo |
| T-C13-007 | Node `up` → ready ≤ 300 ms (keys cached after one unlock, connection pre-warm) | CONTRACT §13 | mo-node | 1 | E22 | todo |
| T-C13-008 | Web TTFB for `/` and `/p/{owner}/{repo}` p50 ≤ 30 ms / p99 ≤ 80 ms (precompiled templates, in-memory aggregates, no N+1) | CONTRACT §13 | mo-web + mo-relay | 4 | E22 | todo |
| T-C13-009 | Web live update visible ≤ 500 ms after a task settles (SSE coalescing window 250 ms) | CONTRACT §13 | mo-web | 4 | E22 | todo |
| T-C13-010 | `TCP_NODELAY` on every socket; warm connections everywhere (provider pools, relay link, local socket) | CONTRACT §13; AGENTS §3 | mo-node + mo-worker + mo-relay | 1 | E22 | todo |
| T-C13-011 | HTTP/2 windows: initial stream window ≥ 1 MiB, connection window ≥ 4 MiB (a 1 MiB body never stalls) | CONTRACT §13 | mo-relay + mo-node | 1 | E22 | todo |
| T-C13-012 | No avoidable lock or allocation and no synchronous fsync in the per-chunk path | CONTRACT §13; AGENTS §3 | mo-worker + mo-node + mo-relay | 1 | E22, NEW:CI-06 | todo |
| T-C13-013 | Any change that regresses a budget shows the measurement in its commit message | CONTRACT §13 | integrator | — | NEW:REV-05 | todo |
| T-C13-014 | E22 harness: 1,000 tasks with an instant fake; every §13 row measured from client, Gateway, Relay, Worker, and fake timestamps; table printed; any exceeded budget fails | CONTRACT §13 | mo-e2e | 1 | E22 | todo |

## PROTO — `spec/proto/moochy/v1/link.proto`

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-LP-001 | Exactly one `Session` per connection; first server message `Hello{nonce 32 B, server_time_ms, min_client_version, relay_release, log_checkpoint}` | link.proto Session | mo-relay | 1 | NEW:E23 | todo |
| T-LP-002 | `Auth{device_id, roles, sig, client_version}` → `Welcome{session_id, roles, max_concurrent_tasks, catalog_version}` | link.proto | mo-node + mo-relay | 1 | E01, NEW:E23 | todo |
| T-LP-003 | `Submit`/`Serve` accepted only on the same underlying connection as the authenticated Session and only with metadata `x-moochy-session: <session_id>`; otherwise `UNAUTHENTICATED` | link.proto header | mo-relay + mo-node | 1 | NEW:E23, E17 | todo |
| T-LP-004 | Session up (`NodeMsg`): `Auth`, `WorkerOffer`, `KnownTasks`, `ReceiptDispute`, `ReplayReceipt`, `Ping` | link.proto | mo-node + mo-relay | 1 | E01, E12 | todo |
| T-LP-005 | Session down (`RelayMsg`): `Hello`, `Welcome`, `PoolSync`, `AssignNotice`, `LogCheckpoint`, `CatalogUpdate`, `Draining`, `ReceiptReplaySince`, `ReceiptAck`, `Pong`, `Error` | link.proto | mo-relay + mo-node | 1 | E01 | todo |
| T-LP-006 | `PoolSync{repo_id, full, workers[], removed_worker_devices[]}`; `full=false` = upsert listed workers and remove listed ids | link.proto | mo-relay + mo-node | 1/2 | NEW:E27 | todo |
| T-LP-007 | `WorkerOffer{slots_free, models[{dialect, model, rl_headroom 0–100}], pledges, window_open, local_cap_left_uusd}` | link.proto | mo-node + mo-relay | 1 | E11, NEW:E31 | todo |
| T-LP-008 | `KnownTask.state` ∈ {`running`, `outbox`} | link.proto | mo-node + mo-relay | 1 | E12, NEW:E34 | todo |
| T-LP-009 | Worker flow: `AssignNotice{task, attempt}` on Session → Worker opens `Serve` with `ServeOpen{task, attempt}` → first server message `Assign{task, attempt, route, wrap, pledge_id, repo_id, deadline_ack_ms, body_len, body_chunks}` → body `Chunk`s | link.proto Serve | mo-relay + mo-node | 1 | E01 | todo |
| T-LP-010 | `ServeUp`: `Ack{r}`, `Nack{r, code, retryable, retry_after_ms, sealed_detail}`, `Started`, `Chunk`, `Checkpoint`, `SignedReceipt` end; `ServeDown`: `Cancel`, `ReceiptAck` | link.proto | mo-node + mo-relay | 1 | E01, E07, E08 | todo |
| T-LP-011 | Gateway flow: `Submit` with first message `SubmitOpen{task, route, wraps ≤ 8, body_len, body_chunks}`, then body `Chunk`s, `Wraps` (answer to `NeedWraps`), `Cancel{reason}` | link.proto Submit | mo-node + mo-relay | 1 | E01, NEW:E27, E08 | todo |
| T-LP-012 | `SubmitDown`: `NeedWraps`, `Accepted{attempt, worker_device, r}`, `Started`, `Chunk`, `Checkpoint`, `SignedReceipt` end, `Failed{code, retryable, retry_after_ms, sealed_detail}` | link.proto | mo-relay + mo-node | 1 | E01, E10 | todo |
| T-LP-013 | `ReceiptDispute.gateway_sig` = Ed25519 over `lp("moochy/v1/dispute", task, u64(attempt), code)` | link.proto | mo-proto + mo-node | 3 | NEW:CI-01, NEW:E45 | todo |
| T-LP-014 | `ReplayReceipt` (Session) answers `ReceiptReplaySince{since_ms}`; `ReceiptAck` on Session for replayed receipts and on `ServeDown` for live ones | link.proto | mo-node + mo-relay | 1/2 | E12, NEW:E36 | todo |
| T-LP-015 | `CatalogUpdate{version, catalog_json (exact signed bytes), sig}`; `LogCheckpoint{note}`; `Draining{reconnect_after_ms}` | link.proto | mo-relay + mo-node | 1–3 | NEW:E41, NEW:E42, NEW:E35 | todo |
| T-LP-016 | `SignedReceipt{task, attempt, receipt, donor_sig, projection, projection_sig}` with exact signed JSON bytes | link.proto | mo-proto + mo-relay | 1 | E01 | todo |
| T-LP-017 | `DeviceStart{sign_pub, enc_pub, roles, name, suite, sig}` with `sig = Ed25519(lp("moochy/v1/device-start", sign_pub, enc_pub, roles_csv, name, suite))` verified by the Relay (proof of possession) | link.proto | mo-node + mo-relay + mo-proto | 1 | E01, NEW:CI-01 | todo |
| T-LP-018 | `DeviceStartResponse{user_code "XXXX-XXXX", device_code (secret, polling only, stored hashed), poll_interval_ms, expires_at_ms}`; `DevicePoll` → `{PENDING, APPROVED, DENIED, EXPIRED}` with `device_id`, `user_pseudonym`, `username` | link.proto; 09 §3.1 | mo-relay + mo-node | 1 | E01, NEW:E65 | todo |
| T-LP-019 | `Error{code, message, task}`; `Ping`/`Pong{t_ms}` | link.proto | mo-relay + mo-node | 1 | NEW:E25 | todo |
| T-LP-020 | `go_package` `moochy.dev/relay/internal/pb`; the proto file is integrator-owned and changes go through spec review | link.proto header | integrator | 1 | NEW:CI-23 | todo |

## AGENTS — `AGENTS.md` (engineering requirements on every component)

| ID | Requirement | Source | Owner | Phase | Verification | Status |
|---|---|---|---|---|---|---|
| T-AG-001 | E2E first: "working" = the CONTRACT §8 table; no mocks of our own components in E2E (real binaries, fake providers only); unit tests only for pure tricky logic | AGENTS §2 | mo-e2e + all | — | NEW:REV-05 | todo |
| T-AG-002 | Rust: `#![forbid(unsafe_code)]` in every crate; clippy pedantic `-D warnings`; deny `unwrap_used`, `expect_used`, `panic`, `indexing_slicing`, `arithmetic_side_effects` outside tests | AGENTS §3 | mo-proto + mo-worker + mo-node | 1 | NEW:CI-02 | todo |
| T-AG-003 | Integer money math checked (`checked_*`), never wrapping | AGENTS §3 | mo-worker + mo-node + mo-proto | 1 | NEW:CI-02, NEW:CI-10 | todo |
| T-AG-004 | Release profile: `opt-level=3`, `lto="fat"`, `codegen-units=1`, `panic="abort"`, `strip=true` | AGENTS §3 | integrator | 1 | NEW:CI-07 | todo |
| T-AG-005 | Hot path: zero-copy `bytes::Bytes`, no avoidable per-chunk allocation, no `String` building in the data plane, bounded channels everywhere, no blocking calls on the runtime | AGENTS §3 | mo-node + mo-worker + mo-proto | 1 | E22, NEW:CI-06 | todo |
| T-AG-006 | Crypto/TLS crates: `rustls` (ring), `ed25519-zebra`, `x25519-dalek`, `hpke`, `chacha20poly1305`, `hkdf`, `sha2`; no OpenSSL; no home-made crypto | AGENTS §3 | mo-proto + mo-node | 1 | NEW:CI-08 | todo |
| T-AG-007 | `zeroize` on every secret; `subtle` for every token/MAC comparison | AGENTS §3 | mo-proto + mo-node + mo-worker | 1 | NEW:REV-05, E14 | todo |
| T-AG-008 | Every new crate justified in its commit message; `default-features = false` preferred; `Cargo.lock` committed | AGENTS §3 | all Rust owners | 1 | NEW:REV-05 | todo |
| T-AG-009 | Release binary ≤ 15 MB; idle RSS ≤ 20 MB | AGENTS §3 | mo-node | 1 | NEW:CI-07 | todo |
| T-AG-010 | Every external input hostile: lengths bounded before allocation; typed structs with `deny_unknown_fields` where the contract says so; timeouts on every network operation | AGENTS §3 | mo-node + mo-worker + mo-proto | 1 | NEW:CI-03, NEW:E25 | todo |
| T-AG-011 | Go 1.25, stdlib first; third-party limited to the allowlist (grpc, protobuf, modernc sqlite, x/crypto, ed25519consensus, x/mod tlog+note, x/oauth2) | AGENTS §4 | mo-relay + mo-web + mo-e2e | 1 | NEW:CI-02 | todo |
| T-AG-012 | `http.Server` with `ReadHeaderTimeout`, `ReadTimeout`, `IdleTimeout`, `MaxHeaderBytes`; `http.MaxBytesReader` on every body; bounded queues; context deadlines everywhere | AGENTS §4 | mo-relay + mo-web | 1 | NEW:E80, NEW:CI-02 | todo |
| T-AG-013 | `go vet` and `-race` clean | AGENTS §4 | mo-relay + mo-web + mo-e2e | 1 | NEW:CI-02 | todo |
| T-AG-014 | Fail closed: on any doubt (bad signature, unknown field, oversize, wrong state) refuse with a specific code | AGENTS §5 | all | — | E09, E15, E16, NEW:E25, NEW:E26 | todo |
| T-AG-015 | Each component checked against `docs/security/attack-catalog.md` once it exists | AGENTS §5 | mo-sec + all | 3 | NEW:REV-03 | todo |

---

## A. Requirements with no owner in CONTRACT §0

120 rows name a proposed owner (`*`). Proposed paths are in the legend. Until the integrator assigns them, these rows cannot progress.

| Proposed owner | Scope | Rows |
|---|---|---|
| `mo-ops*` | deploy recipe, systemd units, Litestream, staging, probes, alert rules, runbooks, DR drills, CDN, public Git anchor repo hosting | T-01-017, T-01-024, T-01-031, T-02-028, T-02-030, T-02-031, T-02-041, T-05-049, T-06-031, T-06-032, T-06-088, T-06-097, T-07-078, T-09-032, T-09-033, T-09-035, T-10-002, T-10-003, T-10-004, T-10-005, T-10-006, T-10-007, T-10-008, T-10-015, T-10-016, T-10-017, T-10-029, T-10-034, T-10-035, T-10-036, T-10-037, T-10-038, T-10-039, T-10-040, T-10-041, T-10-042, T-10-043, T-10-044, T-10-045, T-10-046, T-10-047, T-10-048, T-10-049, T-10-050, T-10-051, T-10-052, T-11-006, T-11-021, T-11-033, T-11-039, T-11-040, T-11-046, T-11-048, T-11-058, T-11-066, T-11-068 |
| `human-po*` | product decisions, recruiting, usability tests, sponsorship, status page, open questions | T-00-002, T-01-018, T-01-028, T-01-029, T-06-079, T-08-011, T-10-004, T-10-052, T-10-053, T-11-007, T-11-011, T-11-016, T-11-029, T-11-038, T-11-066, T-11-067, T-11-070, T-12-002, T-12-035, T-12-036, T-12-040, T-12-041, T-12-042, T-12-043, T-12-044, T-12-045 |
| `mo-release*` | CI pipelines, cargo-dist, Sigstore/SLSA, reproducible builds, cargo-deny/vet, npm wrapper, container image, Homebrew tap, OS CI matrix | T-02-037, T-06-017, T-06-065, T-06-099, T-06-100, T-06-101, T-06-103, T-07-022, T-07-049, T-07-078, T-07-083, T-07-084, T-07-085, T-07-092, T-10-003, T-11-027, T-11-031, T-11-037, T-13-017, T-13-042 |
| `mo-docs*` | README, CONTRIBUTING, CODE_OF_CONDUCT, GOVERNANCE, donor/maintainer/self-host guides | T-00-001, T-01-017, T-02-041, T-05-040, T-06-074, T-06-075, T-06-104, T-07-042, T-10-006, T-11-001, T-11-041, T-11-064, T-12-041, T-13-040 |
| `mo-e2e*` | real-client compatibility matrix, staging real-provider runs, load tests (beyond the Go fake-provider harness) | T-01-030, T-11-003, T-11-006, T-11-008, T-11-009, T-11-010, T-11-019, T-11-037, T-11-039, T-11-058, T-12-038 |
| `human-counsel*` | provider terms review, consent text, ToS, privacy policy | T-06-114, T-06-115, T-11-002, T-11-042, T-11-062, T-12-037 |

---

## B. Requirements with no verification today → proposed checks

CONTRACT §8/§13 defines E01–E22. Every row whose verification column says `NEW:` has no existing check; these are the proposals. The `Rows` column of B.1 is generated from the tables above.

### B.1 Proposed E2E scenarios (E23+, same conventions as CONTRACT §8: one `TestE<NN>_<name>`, real binaries, fake providers only)

| ID | Proposed scenario (one line) | Suggested owner |
|---|---|---|
| E23 | Link auth: TLS < 1.3, missing ALPN `h2`, wrong `dialed_origin`, an `Auth` sig replayed on another TLS connection (exporter mismatch), unknown or revoked device, and `Submit`/`Serve` streams on a different connection or without `x-moochy-session` are all refused (`UNAUTHENTICATED`, Node exit 3) | mo-e2e (+ mo-sec) |
| E24 | Session takeover: a second auth for the same device closes the first session; offers, offline events and streams from the old session are ignored (the worker stays online) | mo-e2e |
| E25 | Link limits: messages > 128 KiB, header list > 16 KiB, > 64 concurrent streams, rapid stream open/reset (CVE-2023-44487 pattern), > 8 wraps, attempt ∉ 1–3, sealed body > 32 MiB, empty/unknown `oneof` (→ `Error{unknown_type}`), keepalive abuse — each refused while the relay stays healthy for other Nodes | mo-sec + mo-e2e |
| E26 | Parser differential: duplicate keys, lone surrogates, invalid UTF-8, out-of-range numbers, depth > 64 in route header, receipt, provider body, provider usage, and MCP messages → rejected by every parser (Relay and Node); protobuf repeated-field merging cannot change a security decision | mo-sec |
| E27 | Stale pool snapshot: wraps only for an offline worker → `NeedWraps` → `Wraps` → served; body uploaded exactly once; `PoolSync` delta upsert/remove applied | mo-e2e |
| E28 | ACK/start deadlines: worker never acks (500 ms) or acks and never starts (30 s, shortened by config) → reassigned; superseded attempt awaits its receipt; late ack/start answered with `Cancel`; exactly the real spend settles | mo-e2e |
| E29 | Exhaustion and policy: 3 attempts exhausted or routing deadline (5 s) → `overloaded` retryable; model in no pledge → `model_not_in_pool` 404; effort above `max_effort` or flag not allowed → policy error, non-retryable | mo-e2e |
| E30 | Affinity and P2C: a 20-turn agent session stays on one worker (≥ 95%), TTL 5 m / 1 h honoured, entry moves after failover, 3× margin respected; two donors drain in proportion to headroom (±5%) | mo-e2e |
| E31 | Rate-limit steering: `rl_headroom` crossing 50/20/5% triggers offers and steers traffic away; a 429 with `retry-after` cools down (worker, model) and reassigns immediately | mo-e2e |
| E32 | Member and device quotas: member monthly cap and CI device cap → `quota_exceeded`; device `repo_scope` blocks another repo; owner unlimited; default member cap = 20% of committed; pledge `max_slots` honoured | mo-e2e |
| E33 | Gateway disconnect (not drain) → Relay cancels all its unfinished tasks; Workers abort provider calls; receipts `cancelled` | mo-e2e |
| E34 | Worker link loss: Worker aborts in-flight provider calls, writes outbox receipts (`not_started`, zero usage, when never called), reconnects, sends `KnownTasks`, replays; unlisted reservations released at zero cost; dead peer detected after 2 missed pings | mo-e2e |
| E35 | Drain-and-restart under load: `Draining` (Gateways 0, Workers 0–10 s jitter), non-started tasks failed retryable, started streams finish ≤ 30 s, ≤ 10 s of retryable errors, zero ledger drift, migrations before accept, Node back-off 250 ms → 30 s with full jitter | mo-e2e |
| E36 | Disaster recovery: restore the relay DB to an earlier point → `ReceiptReplaySince` → all spend restored; identical replay = no-op ack; different bytes for the same (task, attempt) → rejected, alerted, device frozen | mo-e2e |
| E37 | Pessimistic settlement: usage missing (`#cut`) → `estimated` receipt settles at the reservation; with an injected clock, a 24 h-absent Worker's attempt settles pessimistically and a late receipt corrects it into the start period, never below 0 | mo-e2e |
| E38 | Period rollover: an attempt started before a pledge rollover settles into its start-period row; missed rollovers applied at boot; member/device calendar months; `rollover=true` capped at 1× | mo-e2e |
| E39 | Pledge lifecycle: pending → active → paused → resumed → partially reclaimed → ended (web, `moochy pause`/`resume`), owner decline and revoke; no new reservations when not active; in-flight attempts settle | mo-e2e |
| E40 | Receipt validation at the Relay: wrong `cost_uusd`, OpenRouter cost > reservation, receipt for an unknown task, bad `donor_sig` → rejected + alert; nothing settled | mo-sec + mo-e2e |
| E41 | Catalog: signed `CatalogUpdate` delivered; Node rejects a version decrease and a bad signature; price increase effective after 24 h, decrease immediate; version at attempt start used; native ids mapped to slugs | mo-e2e |
| E42 | Key log: login appends `KEY_ADDED` (PoP sig, suite); checkpoints signed ≤ 60 s after growth and only for replicated sizes; Nodes mirror and verify consistency; a rogue key on user U is flagged by U's Node within 2 checkpoint intervals; log entries hold no usernames/emails; tile endpoints serve valid proofs | mo-e2e (+ mo-sec) |
| E43 | Owner-signed approvals: relay-forged `DONOR_APPROVED` → Gateway refuses to seal; forged `REPO_CLAIMED`/`MEMBER_ADDED` flagged by the owner's Node; Worker NACKs `unauthorized_task` for a non-member and for a pledge↔repo mismatch; pinned donors honoured | mo-sec + mo-e2e |
| E44 | Log fork: the relay serves two inconsistent checkpoints → Nodes detect it via consistency proof and the public Git anchor | mo-sec |
| E45 | Disputes: worker inflates usage, reports another model, mismatches `resp_commit`, or claims `cache_write_1h` without 1 h TTL → Gateway sends a signed `ReceiptDispute`; money still settles; leaderboard excludes it; a matching receipt produces no message | mo-e2e |
| E46 | Progress signatures: tool call with missing/invalid checkpoint, or worker disconnecting before signing → error tool result; text streamed immediately; valid checkpoint → tool call released | mo-sec + mo-e2e |
| E47 | Secret scrubber: AWS key, private-key block, provider key, JWT, `.env` assignment in a prompt and in MCP `files` → provider fake receives `[REDACTED:type]`; `warn` mode passes with a warning | mo-e2e |
| E48 | MCP `files` path-escape corpus: `..`, absolute paths outside root, symlinks, `.git/config`, `.env*`, `.npmrc`, `.netrc`, `*.pem`, `id_*`, `*.kdbx`, git-ignored files, > 2 MiB, roots intersection, no-roots fallback → all refused; an allowed file is read by the Node and scrubbed | mo-sec |
| E49 | Stream integrity: chaos makes two attempts start, or reorders/drops/truncates response chunks → Gateway aborts the task with a native retryable error; both started attempts' receipts settle | mo-sec |
| E50 | Dedupe and resubmission: same task id resubmitted after Gateway reconnect → not-started route moves, started → final state replayed; no double charge; the same ULID from another device does not collide | mo-e2e |
| E51 | Backpressure: full submit queue → retryable reject; slow Gateway exceeds the 1 MiB per-task buffer → task fails cleanly; writer-queue overflow closes only that connection; Edge byte budgets → `overloaded`; pings keep flowing under load | mo-e2e |
| E52 | Gateway rate limits: > 16 concurrent tasks per Gateway device and > 120 submits/min per member → retryable reject | mo-e2e |
| E53 | Local endpoints: `count_tokens` answered locally (relay sees nothing), `/v1/models` = pool snapshot slugs + aliases, missing `max_tokens` injected (one notice), `x-moochy-task/donor/cost-uusd` headers present | mo-e2e |
| E54 | Native errors per dialect: Anthropic 429/529 JSON before stream and `event: error` after; OpenAI status + error object; `over_task_cap`/`quota_exceeded`/`model_not_in_pool`/`firewall` non-retryable with explicit messages (firewall shows the sealed detail) | mo-e2e |
| E55 | Auto-caching: multi-turn Anthropic request without `cache_control` gets top-level 5 m caching; disabled by the repo setting | mo-e2e |
| E56 | Safe mutations at the fake: `metadata.user_id = H(repo_id ‖ member_id)`, mapped provider model id, `stream_options.include_usage`, `store:false`, OpenRouter max-price; `req_commit` over pre-mutation bytes (no dispute) | mo-e2e |
| E57 | Firewall extended corpus: unknown beta header, `service_tier`, `inference_geo`, `speed:fast` without flag, images/documents without flags, `container`, skills, fallbacks, OpenAI predictions/audio/modalities/hosted tools/web-search options, OpenRouter `models[]`/`route`/`plugins`/`:online`, non-chat endpoints, `paranoid` level; header ≠ body and estimate mismatch → `route_mismatch` + strike | mo-sec + mo-e2e |
| E58 | Worker authenticity persistence: served-task set survives Worker restart (replay after restart refused); ULID outside ±10 min → `unauthorized_task` | mo-sec |
| E59 | Local controls: `moochy pause` offline → zero slots, assigns refused; `resume`; schedule window closed → `local_cap`; `slots_max`, `models_override`, `firewall_level` honoured | mo-e2e |
| E60 | Provider key lifecycle: `keys add` validates with a free models call; advertised models = the key's models; invalid key refused; `keys list/remove`; `--base-url` refused unless loopback + `MOOCHY_INSECURE_DEV=1`; subscription/consumer credentials refused | mo-e2e |
| E61 | Redaction and secrets at rest: provider keys and scrubbed secrets never appear in Node logs, journal, outbox, receipts, crash output, state files, or anywhere on the relay; config files contain no secrets | mo-sec |
| E62 | Journal: every served and consumed task appears (metadata), full text only when opted in; `journal --follow` streams | mo-e2e |
| E63 | `moochy verify`: a projection verifies against the mirrored key log and the anchor; a tampered projection or unlogged key fails | mo-e2e |
| E64 | `moochy report`: evidence bundle (receipt, checkpoints, response, `S_resp` only) verifies independently and does not reveal the request; moderation → `MODERATION` entry + `KEY_REVOKED` + pledges Ended | mo-e2e |
| E65 | Web auth and safety: OAuth via a fake GitHub, handle pick on first sign-in, `/device` approval, `/claim` admin check (private repo refused on a public-only instance), `/devices` revoke → relay drops the device; CSRF (no `HX-Request` / bad `Origin` → 403); CSP and cookie flags; account deletion | mo-e2e (+ mo-web) |
| E66 | Public pages: `/`, `/connect`, `/open`, `/explore`, `/leaderboard`, `/log`, `/r/{ref}`, `badge.svg` (5 min cache, no external fonts), footer statement on every page, works without JS, ≤ 50 KB | mo-web + mo-e2e |
| E67 | SSE hub: N subscribers receive identical bytes from one render; coalescing per topic; slow subscriber dropped; 25 s heartbeat; full snapshot on connect; `station:{user}` topic isolation | mo-web |
| E68 | Public privacy: no page, fragment, badge or projection exposes device ids, task ids, or sub-day times; presence aggregated unless opted in; visibility public/pseudonymous/anonymous honoured | mo-sec + mo-web |
| E69 | Migrations and DB constraints: fresh DB and previous-release snapshot migrate; binary refuses a DB needing a newer version; connections accepted only after migrations + reconciliation; every CONTRACT §11 uniqueness key rejects a duplicate at the DB level | mo-relay + mo-e2e |
| E70 | Ledger audit: after a full suite run the audit job finds 0 drift for pledge-periods, member-months, device-months; an injected constraint violation exits the process and recovers via outbox replay | mo-e2e |
| E71 | Clock: Node skew > 5 min warns; Worker with a skewed clock refuses stale ULIDs | mo-e2e |
| E72 | Version gates: `min_client_version` refuses an old Node with a clear message; `client_version` recorded | mo-e2e |
| E73 | Keystore and device keys: encrypted-file keystore persists across restarts; wrong passphrase → exit 3; `keys rotate` (24 h grace); `logout` → `KEY_REVOKED`, relay drops the device at once, local keys wiped | mo-e2e |
| E74 | Local control: `node.sock` is 0600, another uid is refused (peer uid check), stdio shim starts the Node if absent, many MCP clients share one relay connection | mo-e2e |
| E75 | `moochy connect`: snippets for every listed client; `--write` shows a diff, writes user-scoped config only, refuses git-tracked files, sets main/small models to pool ids, raises tool timeouts where supported | mo-e2e |
| E76 | `moochy env`: repo detected from git remote; `--rotate` invalidates the old token; a token for repo A is never accepted for repo B; port stable across restarts | mo-e2e |
| E77 | Warm pools: after idle, the first provider request reuses the warm HTTP/2 connection (fake counts handshakes) | mo-e2e |
| E78 | OpenAI and vetted hosts: OpenAI adapter end to end (usage mapping, `store:false`); a vetted OpenAI-compatible host works; an unvetted host is refused without `--allow-unvetted-host` | mo-e2e |
| E79 | Admin: `RelayAdmin` socket (0600) and `/admin` require operator credentials; suspend/unsuspend, drain, state, catalog publish needs two approvals; every action audit-logged; public ones also logged in tlog | mo-e2e |
| E80 | DoS limits: per-IP connection cap, `DeviceStart`/`DevicePoll` rate limit, per-session POST/SSE limits, `http.Server` timeouts and body caps → refused gracefully, relay healthy for others | mo-sec |
| E81 | MCP extras: tools-changed notification on pool model change, `instructions`, progress notifications, MCP cancel aborts the provider call, delegate with `files` and `output: json`, parallel delegates spread across donors, results scanned by the tripwire | mo-e2e |
| E82 | Observability: metrics on a private address expose the 10 §5.1 names; task-scoped log lines carry `task_id`/`repo_id`/`device_id`; effective config printed with secrets redacted; Node telemetry off unless opted in (field names only) | mo-e2e |
| E83 | Node lifecycle: `up/down/status`, `service install/uninstall` (systemd user unit in CI), `doctor` (keychain, connectivity, skew, key health, firewall version, port uid), required onboarding safety screen (device cap + spend-limit checkbox + consent), `update` verifies the signature before replacing | mo-e2e |
| E84 | Owner flows via Node: `moochy claim`, `approve`, `members add/remove [--device]`, pending requests in `status`; `moochy donate` creates a pending pledge; `moochy pledges` lists balances | mo-e2e |
| E85 | Retention jobs: tasks/attempts > 90 days deleted after rollup; `usage_daily` hourly rollup correct; expired sessions/device codes purged; IP logs 7 days; acked outbox entries pruned after 7 days; journal 90 days | mo-e2e |
| E86 | Own-key fallback (Phase 5): pool empty + fallback enabled → direct call with the maintainer's own key; disabled by default | mo-e2e |
| E87 | Remote-MCP self-tunnel (Phase 5): exposed `/mcp` requires OAuth 2.1 and the Host allowlist; off by default | mo-e2e |
| E88 | GitLab identity and repos (Phase 5): same flows as GitHub | mo-e2e |
| E89 | Headless CI device: `login --headless`, scoped `gateway` role, member with its own cap, `up --headless` in a container, both doors usable inside the job | mo-e2e |
| E90 | `relay serve --dev` with a non-loopback `--addr` refuses to start; `/dev/*` returns 404 without `--dev` | mo-e2e |
| E91 | Terminal-escape injection: handles, repo names and other server strings containing control/escape sequences are printed escaped by every CLI command and log line | mo-sec |

### B.2 Proposed automated non-E2E checks

| ID | Check | Suggested owner |
|---|---|---|
| CI-01 | Golden vectors (`spec/vectors/*.json`) pass in Go and Rust: `lp`, labels, auth, device-start, envelope (incl. distinct per-attempt keys), task sig, receipt, projection, checkpoint, dispute, ZIP-215 edge cases, chunk sizes, route↔body estimate, tlog proofs, usernames | mo-proto + mo-relay |
| CI-02 | Lint and safety gates: clippy pedantic `-D warnings` with the AGENTS denies, `forbid(unsafe_code)`, `go vet`, `-race`, dependency allowlist (no plain `encoding/json`/`serde_json::Value` in strict paths, stdlib router only) | integrator |
| CI-03 | Fuzzing: firewall validator (nested), strict JSON parser, SSE parsers, chunk/stream handling, MCP `files` paths; no panic, no bypass | mo-worker + mo-proto + mo-node + mo-sec |
| CI-04 | Scheduler deterministic simulator: 1M tasks / 2,000 workers with faults, invariant checks after every event, same seed → identical run | mo-relay |
| CI-05 | Scheduler property tests: proportional drain ±5% over 10k tasks; affinity hit ≥ 95% | mo-relay |
| CI-06 | Benchmarks with regression budgets: `apply(submit)` at 10…10k candidates, per-event apply, chunk forwarding, seal/open throughput, group-commit latency | mo-relay + mo-proto |
| CI-07 | Build budgets: release binary ≤ 15 MB, idle RSS ≤ 20 MB, ≤ 25 direct deps, release profile, worker-crate dependency rule, no OpenSSL/GPG/SIMD-JSON | integrator |
| CI-08 | Supply chain: `cargo-deny`, `cargo-vet` (hpke vetted), Go module audit (`govulncheck`), bit-identical Linux musl rebuild, Sigstore + SLSA attestations verifiable, container image, npm wrapper | mo-release* |
| CI-09 | Web: template snapshots, Lighthouse a11y ≥ 95, page weight ≤ 50 KB, CSS ≤ 12 KB, palette tokens, SSE load (10k subscribers < 1 core), token-equivalent formula | mo-web |
| CI-10 | Ledger unit/property tests: cost function, reservation formula, worked examples of 05 §5.1, rounding up, checked arithmetic, settle/release sequences | mo-relay + mo-worker |
| CI-11 | Migration tests: empty DB and previous-release snapshot; expand/contract discipline | mo-relay |
| CI-12 | Redaction unit tests (keys never formatted into logs/crash output) | mo-node + mo-worker |
| CI-13 | Firewall corpora: seeded forbidden corpus 100% rejected, captured real-client traffic 100% accepted | mo-worker |
| CI-14 | Tripwire baseline corpus blocked | mo-worker + mo-sec |
| CI-15 | MCP conformance with the official inspector/test clients over stdio and Streamable HTTP | mo-node |
| CI-16 | Keystore and service install per OS (macOS, Linux, Windows CI matrix) | mo-node + mo-release* |
| CI-17 | Adapter fixtures per provider: usage mapping, rate-limit headers, error mapping, endpoints pinned | mo-worker |
| CI-18 | Repo hygiene: license files + headers, README statement, doc reference resolver and shared-parameter consistency (plan ↔ contract ↔ code defaults), E-scenario naming/no-deletion guard | integrator + mo-trace |
| CI-19 | Load test at 2× design point (100k connections, 10k concurrent streams) with SLOs | mo-e2e* + mo-ops* |
| CI-20 | Nightly staging with real providers and tiny budgets: one real session per supported harness (Claude Code, OpenCode, framework…), `audit --provider` drift ≤ 0.5%, latency and cache ratios | mo-ops* + mo-e2e* |
| CI-21 | Ops drills: Litestream replication + monthly automated restore (read-only boot, audit job, key-log root vs anchor), DR RTO, autocert in staging | mo-ops* |
| CI-22 | Chaos suite with real binaries: random kills, 429 storms, 2 relay upgrades under load → ≥ 99.5% success, ≤ 10 s errors per upgrade, zero drift | mo-e2e |
| CI-23 | Proto hygiene: `gen.sh` output equals committed generated code (Go + Rust); `buf`-style breaking-change check on `link.proto`, `local.proto`, `admin.proto` | integrator |
| CI-24 | Reserved-handle list ⊇ every first path segment of the registered routes | mo-relay + mo-web |

### B.3 Monitored verification

| ID | Meaning |
|---|---|
| MON-01 | Metric exported and its alert rule unit-tested (e.g. `promtool test rules`) |
| MON-02 | SLO dashboard with the target, checked at the beta gate on staging/prod data |
| MON-03 | Build-trigger metric for a deferred/research item is exported and alerting (upload p50, egress share, deploy failures, mid-stream disconnects, dialect mismatch, regional latency, scheduler load) |

### B.4 Human sign-offs (non-code deliverables)

| ID | Deliverable |
|---|---|
| REV-01 | Counsel: per-provider go/no-go, donor consent text, ToS, privacy policy |
| REV-02 | Published document or recorded decision (README, SECURITY.md, GOVERNANCE.md, guides, threat model, runbooks, ADR compliance) |
| REV-03 | External pentest report with all high/critical findings closed; attack-catalog review |
| REV-04 | Usability test (5 donors < 5 min, 5 maintainers < 3 min) |
| REV-05 | Process rule enforced by review (CODEOWNERS two-person allowlist widening, dependency justification, budget-measurement in commit messages, key ceremonies) |
| REV-06 | Operational/product milestone (region, costs, sponsors, status page, design partners, naming) |

### B.5 Rows waiting on each proposed check (generated)

| Check | Rows |
|---|---|
| E23 | T-01-034, T-02-001, T-03-009, T-03-017, T-03-018, T-03-019, T-03-022, T-03-023, T-03-024, T-06-012, T-06-103, T-12-046, T-13-012, T-C03-001, T-C06-014, T-C12-011, T-C12-012, T-C12-013, T-C12-018, T-LP-001, T-LP-002, T-LP-003 |
| E24 | T-03-025, T-03-126, T-13-026 |
| E25 | T-03-012, T-03-014, T-03-015, T-03-028, T-03-032, T-03-058, T-03-136, T-12-046, T-13-024, T-C12-014, T-C12-015, T-C12-016, T-C12-018, T-C12-019, T-C12-020, T-LP-019, T-AG-010, T-AG-014 |
| E26 | T-12-024, T-C01-002, T-C01-003, T-C01-004, T-C01-005, T-C01-006, T-C03-002, T-C12-022, T-AG-014 |
| E27 | T-03-033, T-03-036, T-03-070, T-04-024, T-04-034, T-04-035, T-LP-006, T-LP-011 |
| E28 | T-03-038, T-03-048, T-03-096, T-03-097, T-03-138, T-04-037, T-04-038, T-04-045, T-04-046, T-05-034, T-13-018, T-13-031 |
| E29 | T-01-023, T-03-098, T-03-107, T-03-137, T-03-138, T-04-014, T-04-018, T-04-025, T-04-039, T-04-040, T-04-043, T-05-024, T-13-030 |
| E30 | T-01-003, T-03-082, T-04-027, T-04-028, T-04-029, T-04-030, T-04-034, T-07-034, T-10-025, T-11-019, T-12-017, T-13-013 |
| E31 | T-03-046, T-03-101, T-03-103, T-04-017, T-04-033, T-04-047, T-04-048, T-04-049, T-04-053, T-LP-007 |
| E32 | T-04-022, T-04-043, T-04-050, T-04-051, T-04-052, T-05-025, T-05-065, T-05-067, T-06-035, T-07-079, T-08-021, T-08-043, T-09-007, T-09-011, T-12-043, T-13-027 |
| E33 | T-01-003, T-03-124, T-13-024, T-C12-002 |
| E34 | T-02-024, T-03-012, T-03-021, T-03-045, T-03-113, T-03-128, T-13-020, T-C12-015, T-LP-008 |
| E35 | T-02-009, T-02-031, T-03-055, T-03-125, T-10-010, T-10-011, T-10-012, T-10-013, T-11-057, T-12-022, T-13-021, T-13-039, T-LP-015 |
| E36 | T-02-030, T-03-054, T-05-043, T-05-044, T-05-045, T-10-016, T-13-019, T-LP-014 |
| E37 | T-03-123, T-04-041, T-05-032, T-05-035, T-05-036, T-05-051, T-05-074, T-09-016, T-13-008, T-13-028 |
| E38 | T-05-022, T-05-027, T-05-031, T-05-056, T-05-057, T-05-058, T-05-059, T-05-060, T-05-080, T-09-012, T-09-014, T-12-015, T-13-023 |
| E39 | T-02-022, T-02-023, T-04-006, T-04-015, T-05-026, T-05-052, T-05-053, T-05-054, T-05-078, T-08-016, T-08-018, T-08-020, T-09-013, T-09-025 |
| E40 | T-03-004, T-05-015, T-05-021, T-05-045, T-05-071, T-13-037 |
| E41 | T-01-036, T-02-008, T-03-057, T-05-005, T-05-006, T-05-009, T-05-011, T-05-012, T-05-013, T-05-076, T-06-032, T-09-020, T-12-018, T-13-016, T-13-034, T-LP-015 |
| E42 | T-01-011, T-02-004, T-02-014, T-02-020, T-02-025, T-02-032, T-03-056, T-03-071, T-05-012, T-05-047, T-06-007, T-06-025, T-06-031, T-06-080, T-06-081, T-06-082, T-06-083, T-06-087, T-06-091, T-08-028, T-09-018, T-09-019, T-11-022, T-13-032, T-LP-015 |
| E43 | T-01-013, T-02-014, T-03-034, T-03-078, T-03-086, T-03-087, T-03-088, T-06-007, T-06-009, T-06-037, T-06-038, T-06-068, T-06-069, T-06-081, T-06-084, T-06-085, T-06-086, T-07-035, T-11-013, T-11-023, T-11-069, T-12-008, T-12-012, T-13-004, T-13-005, T-13-041 |
| E44 | T-02-004, T-02-014, T-02-025, T-06-007, T-06-011, T-06-088, T-11-024, T-11-068, T-13-004 |
| E45 | T-01-009, T-02-011, T-03-044, T-03-111, T-03-117, T-03-118, T-03-119, T-04-042, T-05-063, T-06-010, T-07-037, T-07-090, T-09-017, T-09-024, T-12-011, T-13-015, T-LP-013 |
| E46 | T-01-009, T-03-039, T-03-120, T-03-121, T-06-008, T-06-071, T-07-036, T-11-025, T-12-011, T-13-006 |
| E47 | T-06-020, T-06-111, T-07-032 |
| E48 | T-06-015, T-06-110, T-07-053, T-11-026, T-13-007 |
| E49 | T-03-037, T-03-073, T-03-074, T-03-075, T-05-077, T-13-003 |
| E50 | T-03-006, T-03-127, T-13-024 |
| E51 | T-03-099, T-03-100, T-03-135, T-04-004, T-04-005, T-04-008, T-06-022, T-13-025, T-13-028 |
| E52 | T-03-133, T-03-134, T-04-050 |
| E53 | T-05-008, T-07-026, T-07-028, T-07-031, T-07-039, T-12-023, T-13-044 |
| E54 | T-03-007, T-03-042, T-03-105, T-03-106, T-03-107, T-C12-021 |
| E55 | T-07-033, T-08-022 |
| E56 | T-03-110, T-05-007, T-05-020, T-06-019, T-06-054, T-06-055, T-06-058, T-06-059, T-12-014, T-C07-004 |
| E57 | T-01-008, T-01-020, T-03-079, T-03-080, T-03-081, T-03-083, T-03-084, T-06-002, T-06-003, T-06-005, T-06-041, T-06-043, T-06-044, T-06-045, T-06-046, T-06-048, T-06-052, T-06-053, T-06-057, T-06-059, T-06-060, T-06-067, T-09-022, T-13-009, T-13-010 |
| E58 | T-03-089, T-03-090, T-03-139, T-06-009, T-07-072, T-11-013, T-13-005 |
| E59 | T-03-108, T-04-016, T-04-053, T-05-054, T-06-067, T-07-013, T-07-070 |
| E60 | T-03-103, T-06-001, T-06-028, T-06-029, T-06-113, T-07-009, T-12-029, T-C06-009 |
| E61 | T-01-005, T-06-001, T-06-030, T-07-075, T-07-091 |
| E62 | T-01-012, T-02-015, T-06-019, T-06-092, T-07-017, T-07-037, T-07-073 |
| E63 | T-01-016, T-01-037, T-06-011, T-07-018, T-13-032 |
| E64 | T-06-076, T-06-077, T-06-078, T-06-079, T-07-020, T-09-022, T-10-047 |
| E65 | T-01-022, T-02-005, T-02-020, T-02-021, T-05-079, T-06-013, T-06-016, T-06-018, T-06-034, T-06-036, T-06-039, T-06-091, T-08-016, T-08-019, T-08-022, T-08-023, T-08-024, T-08-025, T-08-030, T-08-041, T-08-044, T-08-045, T-08-057, T-08-058, T-08-059, T-09-005, T-09-008, T-12-031, T-C11-003, T-LP-018 |
| E66 | T-01-016, T-02-006, T-05-002, T-05-023, T-05-061, T-05-063, T-05-064, T-08-002, T-08-007, T-08-009, T-08-010, T-08-011, T-08-012, T-08-015, T-08-026, T-08-027, T-08-029, T-08-035, T-08-037, T-08-046, T-08-047, T-08-053, T-08-055, T-08-056, T-08-064, T-10-007, T-10-053, T-11-067 |
| E67 | T-02-006, T-04-009, T-08-003, T-08-017, T-08-033, T-08-039, T-08-049, T-08-050, T-08-051, T-08-052, T-08-054 |
| E68 | T-01-037, T-02-019, T-03-116, T-05-025, T-06-094, T-06-095, T-06-096, T-06-098, T-08-004, T-08-034, T-08-036, T-08-038, T-12-013, T-12-028, T-13-013 |
| E69 | T-02-007, T-05-046, T-09-001, T-09-002, T-09-004, T-09-006, T-09-010, T-09-013, T-09-015, T-09-028, T-09-029, T-10-011, T-13-029, T-13-031, T-C11-009, T-C11-010, T-C11-011, T-C11-012 |
| E70 | T-04-059, T-05-048, T-05-049, T-05-065, T-05-066, T-05-068, T-05-070, T-09-012, T-10-024, T-11-055, T-13-023, T-13-027 |
| E71 | T-03-026 |
| E72 | T-03-016, T-03-130, T-03-131, T-10-050 |
| E73 | T-02-010, T-02-036, T-06-013, T-06-023, T-06-024, T-06-026, T-06-027, T-07-006, T-07-009, T-08-025, T-12-010, T-C06-007, T-C06-014 |
| E74 | T-03-001, T-07-002, T-07-004, T-07-048, T-07-074, T-12-005, T-12-046, T-C12-005 |
| E75 | T-06-074, T-06-108, T-07-016, T-07-040, T-07-043, T-07-055, T-11-031, T-13-014, T-13-034 |
| E76 | T-06-107, T-07-014, T-07-030, T-13-014, T-C11-013 |
| E77 | T-02-043, T-07-069 |
| E78 | T-00-003, T-01-014, T-05-017, T-06-061, T-07-065, T-07-066, T-11-030 |
| E79 | T-05-013, T-06-078, T-08-031, T-10-044, T-10-055, T-10-056, T-10-057, T-C12-006 |
| E80 | T-06-018, T-06-022, T-08-060, T-C12-017, T-AG-012 |
| E81 | T-06-073, T-07-050, T-07-052, T-07-054, T-07-055, T-07-056, T-07-057, T-13-011, T-13-035 |
| E82 | T-03-104, T-06-066, T-07-001, T-10-008, T-10-009, T-10-018, T-10-019, T-10-020, T-10-021, T-10-022, T-10-023, T-10-024, T-10-025, T-10-026, T-10-027, T-10-028, T-10-029, T-10-030, T-10-031, T-10-032, T-10-033, T-12-032, T-13-045 |
| E83 | T-05-040, T-06-014, T-06-017, T-06-102, T-06-106, T-06-114, T-07-007, T-07-008, T-07-021, T-07-022, T-07-076, T-07-081, T-11-033, T-11-065, T-13-014 |
| E84 | T-02-021, T-02-022, T-06-036, T-06-037, T-07-010, T-07-011, T-07-012, T-07-023, T-07-077, T-08-021, T-08-042 |
| E85 | T-03-053, T-06-093, T-06-097, T-07-071, T-07-073, T-09-009, T-09-021, T-09-026, T-12-042 |
| E86 | T-06-112, T-07-038, T-11-035 |
| E87 | T-07-047, T-11-036, T-12-030, T-13-040 |
| E88 | T-11-032 |
| E89 | T-07-079 |
| E90 | T-C06-003 |
| E91 | T-C11-008 |
| CI-01 | T-00-005, T-03-003, T-03-004, T-03-005, T-03-014, T-03-018, T-03-023, T-03-031, T-03-059, T-03-060, T-03-061, T-03-062, T-03-063, T-03-064, T-03-065, T-03-066, T-03-067, T-03-068, T-03-069, T-03-071, T-03-072, T-03-077, T-03-080, T-03-085, T-03-094, T-03-109, T-03-110, T-03-111, T-03-112, T-03-114, T-03-115, T-03-118, T-03-120, T-03-122, T-03-132, T-03-140, T-03-141, T-03-142, T-03-143, T-03-144, T-03-145, T-03-146, T-03-147, T-03-148, T-03-149, T-03-150, T-06-080, T-07-086, T-11-005, T-11-007, T-11-013, T-11-053, T-12-007, T-12-009, T-13-003, T-13-016, T-13-031, T-C01-001, T-C01-008, T-C01-009, T-C01-010, T-C01-011, T-C02-001, T-C03-001, T-C11-007, T-C12-004, T-LP-013, T-LP-017 |
| CI-02 | T-01-032, T-02-033, T-05-001, T-08-032, T-09-003, T-12-024, T-C01-007, T-C10-001, T-AG-002, T-AG-003, T-AG-011, T-AG-012, T-AG-013 |
| CI-03 | T-02-040, T-06-064, T-07-061, T-07-089, T-11-056, T-13-010, T-C01-002, T-C01-005, T-AG-010 |
| CI-04 | T-02-002, T-02-039, T-03-013, T-03-047, T-03-095, T-04-001, T-04-002, T-04-005, T-04-007, T-04-010, T-04-011, T-04-036, T-04-044, T-04-059, T-04-060, T-04-061, T-04-062, T-04-063, T-04-064, T-04-065, T-04-066, T-04-069, T-05-066, T-05-069, T-05-073, T-11-017, T-11-054, T-12-006, T-12-020, T-13-025 |
| CI-05 | T-04-029, T-04-031, T-04-032, T-04-067 |
| CI-06 | T-02-026, T-02-027, T-04-003, T-04-054, T-04-055, T-04-056, T-04-057, T-04-068, T-07-060, T-09-023, T-09-027, T-11-059, T-C13-012, T-AG-005 |
| CI-07 | T-01-004, T-01-033, T-01-035, T-02-035, T-07-024, T-07-082, T-C00-003, T-C12-009, T-AG-004, T-AG-009 |
| CI-08 | T-02-037, T-06-017, T-06-099, T-06-100, T-06-101, T-06-103, T-07-049, T-07-083, T-07-084, T-07-085, T-10-003, T-11-027, T-11-031, T-13-017, T-13-042, T-C12-016, T-AG-006 |
| CI-09 | T-02-034, T-05-003, T-08-001, T-08-005, T-08-006, T-08-008, T-08-050, T-08-061, T-08-062, T-08-063, T-11-028, T-11-060, T-C09-002 |
| CI-10 | T-02-003, T-04-026, T-05-001, T-05-004, T-05-014, T-05-028, T-05-037, T-05-062, T-08-040, T-11-055, T-12-003, T-AG-003 |
| CI-11 | T-09-030, T-09-031 |
| CI-12 | T-06-030, T-07-091 |
| CI-13 | T-06-047, T-06-050, T-06-063, T-07-087, T-11-003, T-11-014, T-11-056, T-13-017 |
| CI-14 | T-06-072, T-11-025, T-11-056, T-13-041 |
| CI-15 | T-07-058, T-07-088 |
| CI-16 | T-02-010, T-02-036, T-06-024, T-07-092, T-11-033, T-11-034, T-11-037 |
| CI-17 | T-04-047, T-05-016, T-05-017, T-05-018, T-05-019, T-05-075, T-06-062, T-07-068, T-11-004, T-11-030, T-12-039 |
| CI-18 | T-00-001, T-11-001, T-12-001, T-13-002, T-C08-001 |
| CI-19 | T-02-045, T-04-013, T-11-039, T-11-059 |
| CI-20 | T-00-003, T-01-001, T-01-010, T-01-026, T-01-027, T-01-030, T-02-044, T-05-050, T-05-051, T-07-019, T-07-040, T-07-041, T-07-042, T-07-043, T-07-044, T-07-045, T-07-046, T-10-002, T-11-003, T-11-006, T-11-007, T-11-008, T-11-009, T-11-010, T-11-011, T-11-019, T-11-020, T-11-037, T-11-055, T-11-058, T-12-038, T-13-043 |
| CI-21 | T-01-017, T-02-028, T-02-029, T-02-030, T-09-032, T-09-033, T-09-034, T-10-005, T-10-016, T-10-017, T-11-040 |
| CI-22 | T-01-024, T-10-013, T-11-018 |
| CI-23 | T-C00-001, T-C00-002, T-C12-010, T-LP-020 |
| CI-24 | T-C11-005 |
| MON-01 | T-05-049, T-10-037, T-10-038, T-10-039, T-10-040, T-10-041, T-10-042, T-12-006 |
| MON-02 | T-01-024, T-01-025, T-01-027, T-02-044, T-10-034, T-10-035, T-10-036, T-11-021 |
| MON-03 | T-02-046, T-03-093, T-03-129, T-04-058, T-06-089, T-06-090, T-06-116, T-07-067, T-08-048, T-09-035, T-10-014, T-10-051, T-11-043, T-11-044, T-11-045, T-11-046, T-11-047, T-11-048, T-11-049, T-11-050, T-11-051, T-11-052, T-12-019, T-12-021, T-12-025, T-12-034, T-13-036, T-C12-008 |
| REV-01 | T-06-114, T-06-115, T-11-002, T-11-007, T-11-042, T-11-062, T-12-037 |
| REV-02 | T-00-002, T-00-004, T-00-007, T-01-004, T-01-017, T-01-018, T-01-019, T-02-028, T-02-038, T-02-041, T-05-040, T-05-055, T-06-021, T-06-075, T-06-104, T-07-001, T-07-078, T-07-080, T-10-006, T-10-043, T-10-044, T-10-045, T-10-046, T-10-047, T-10-048, T-10-049, T-10-050, T-11-001, T-11-041, T-11-064, T-12-002, T-12-027, T-12-030, T-12-033, T-12-035, T-12-036, T-12-041, T-12-044, T-13-038 |
| REV-03 | T-11-038, T-AG-015 |
| REV-04 | T-01-028, T-01-029, T-07-076, T-07-077, T-11-029 |
| REV-05 | T-06-031, T-06-065, T-C13-013, T-AG-001, T-AG-007, T-AG-008 |
| REV-06 | T-01-031, T-10-004, T-10-052, T-10-053, T-11-016, T-11-066, T-11-070, T-12-040, T-12-045 |

737 of 1035 live rows have **no existing E01–E22 coverage** and rely only on the proposed checks above.

---

## C. Contradictions between plan documents

Resolution column = the reading this matrix uses (safer/simpler), pending an integrator decision where marked ⚑.

| # | Contradiction | Where | Resolution used here |
|---|---|---|---|
| C1 | Fixed 10 ms group-commit window vs adaptive group commit | 04 §8.1, §11; 05 §7; 09 §2, §4; 02 §12 vs ADR-34 | ADR-34 wins (adaptive). Rows T-04-036, T-04-057, T-09-023 amended. ⚑ plan text of 04/05/09 still says 10 ms |
| C2 | WebSocket transport still described as current | 01 §6 ("persistent multiplexed WebSocket — Keep"), 02 §3.1 (Edge "WebSocket upgrade"), 02 §2 diagram ("WSS"), 02 §7, 03 §2–§4 and §14, 04 §1/§2 ("frames"), 07 §3/§10 (`tokio-tungstenite`), 10 §2 ("Nodes' WebSockets") vs ADR-33 + 03 update note | ADR-33 wins (gRPC). Rows T-03-002/008/010/011/027/029/030 marked `superseded`; transport rows amended. ⚑ plan body text not yet updated |
| C3 | Two "schedule" concepts: pledge `schedule` with Active→Paused on window close (05 §4.1–4.2) vs device `schedule` + worker `window_open` eligibility flag (07 §6.4, 03 §5.2, 04 §3–4) | 05 vs 03/04/07 | A closing window is an **eligibility** condition (rule 3), never a persisted pledge status change; pledge `Paused` only by explicit donor action. Both pledge and device schedules supported |
| C4 | `over_task_cap` and `quota_exceeded` both "HTTP 400/403" | 03 §10.3 | `over_task_cap` → 400 `invalid_request_error`; `quota_exceeded` → 403 `permission_error` (never 429, which agents retry) |
| C5 | Default Gateway port "chosen at first run" and held by the OS service manager vs a fresh port every start | 07 §4.1; 06 §13 vs CONTRACT §6 `gateway_addr` default `127.0.0.1:0` | Pick a free port at first run, persist it in config, reuse it; `127.0.0.1:0` only when explicitly configured (tests). ⚑ |
| C6 | Relay binary name `moochy-relay` vs `relay` | 02 §8, 06 §12 vs 10 §11, CONTRACT §6 | `relay` (CONTRACT) |
| C7 | `worker.offer.window` vs `window_open` | 03 §5.2 vs CONTRACT §5, link.proto | `window_open` |
| C8 | Inner payload: only `body` zstd-compressed vs whole JSON compressed; `provider_headers` vs `headers` | 03 §6.2, §7.2 vs CONTRACT §4 | CONTRACT §4 |
| C9 | "Max frame 64 KiB including the 23-byte header" vs header gone | 03 §2, §4.2 vs ADR-33 | Ciphertext ≤ 64 KiB, plaintext ≤ 65,497 B, gRPC message cap 128 KiB |
| C10 | Template CSS via Tailwind vs hand-written CSS | 02 §9, 08 §1.6 vs CONTRACT §9, AGENTS §6 | Hand-written, ≤ 12 KB (CONTRACT) |
| C11 | Mock UI shows native ids (`claude-sonnet-5-5`) while public ids are slugs | 08 §3–4 vs 05 §2.1 | Slugs in UI, native alias as secondary text |
| C12 | Live-update cadence: `goal` ≤ 1/30 s, `pool`/`audit` ≤ 1/s, donors every 60 s vs "visible ≤ 500 ms after settle, window 250 ms" | 08 §3, §7 vs CONTRACT §13 | CONTRACT §13 for audit/pool/station (250 ms window); `goal` and donor ranking may stay slower because they are not "a task settled" events. ⚑ confirm |

## D. CONTRACT ↔ plan conflicts (CONTRACT wins for encodings and interfaces; listed for the integrator)

| # | Conflict | CONTRACT | Plan | Note |
|---|---|---|---|---|
| D1 | Client is three crates (`proto`, `worker`, `node`; worker must not depend on proto) | §0 | 02 §10, 07 §12 (one crate with modules) | Plan module table superseded |
| D2 | Ed25519 crate `ed25519-zebra` (ZIP-215) | §1, AGENTS §3 | 02 §9, 07 §10 (`ed25519-dalek`) | dalek's `verify_strict` is not ZIP-215; zebra is the right call |
| D3 | gRPC (`tonic`/`prost`, `grpc-go`) for all machine-to-machine links | §12 | 02 §9 rows for WS, 07 §10 `tokio-tungstenite` | ADR-33 |
| D4 | `lp` integer width: "integers inside `lp` are `u64_be`" yet AADs use `u32(i)` / `u32(seq)` | §1 vs §3 (internal) | 03 §6 (unspecified) | Explicit widths in §3 win; vectors must pin it. ⚑ integrator should reword §1 |
| D5 | `dialed_origin = wss://host:port` but the Node now dials `https://host:GRPCPORT` | §3 vs §6 (internal) | 03 §3 | ⚑ Must be fixed before vectors freeze. Safer reading: the exact origin string the Node dialed (`https://host:port`), scheme included |
| D6 | Stale lines: §3 "transmitted as base64url … field `route_b64`" and §5 last line "Binary frame header: 03 §4.2 (23 bytes)" | §3, §5 (internal) | — | Now `SubmitOpen.route` / `Assign.route` raw bytes; no frame header. ⚑ |
| D7 | Request AAD still contains `kind_byte` though frame kinds are gone | §3 | 03 §6.2 | Keep the constant `0x01` in the request AAD (response AAD has no kind); vectors pin it |
| D8 | Chaos `inject_frame` "on a different connection": with per-connection stream auth such a frame is rejected by the relay itself before reaching the Gateway | §6 | 03 §4.2 | E17 still meaningful only if the chaos relay injects a forged `Chunk` **into the Gateway's own `Submit` stream**. ⚑ request to mo-relay/mo-e2e |
| D9 | `MaxConcurrentStreams` 64 per connection vs Worker `slots_max` up to 64 + Gateway ≤ 16 concurrent tasks + 1 Session on the same connection (= 81) | §12 | 03 §16, 07 §6.4 | ⚑ Either raise the stream cap to ≥ 128 or clamp `slots_max + gateway concurrency ≤ 63` per connection. Until decided: Node clamps (safer) |
| D10 | `user_id` = `u_` + ULID, while 09 says `users.id` is a plain ULID and the **pseudonym** is `u_…` | §1 | 09 §3.1 | Same prefix for the secret-ish internal id and the public pseudonym invites leaks/confusion. ⚑ propose pseudonym prefix `m_` (mock in 08 §4 already shows `m_8Hq…`) |
| D11 | Repository uniqueness case-insensitive (`lower(owner)`, `lower(name)`), device-name uniqueness per user | §11 | 09 §3.2 (case-sensitive), 09 §3.1 (none) | CONTRACT wins; 09 needs an update |
| D12 | Phase scope: E06 failover, E07 429 reroute, E08 cancel, E11 chaos caps, E15–E18, E20 (3 workers), E22 budgets are in the current "definition of working" | §8, §13 | 11 puts multi-worker failover, cancellation, deadlines in Phase 2 and tool gating/progress signatures in Phase 3 | Matrix keeps plan phases but these rows are effectively due now |
| D13 | OpenAI adapter and fake exist now (`keys add openai`) | §6, §7 | 07 §6.2 (Phase 2) | Treated as Phase 1-ready |
| D14 | Phase 1 Worker check 2 (owner-signed `MEMBER_ADDED`) cannot run without the key log; dev API asserts members/pledges | §6 `/dev/member`, `/dev/pledge` | 03 §7.2, 11 Ph1 | Phase 1: Worker trusts relay-asserted membership **only** under `--dev`/design-partner mode; T-11-069 forbids it in beta. ⚑ document the Phase 1 source of truth for membership |
| D15 | Process interface has no metrics address, no TOML config file, no autocert flags, no read-only boot | §6 | 10 §2, §5.1; 09 §7 | Additive flags needed (see requests) |
| D16 | Tessera allowed by plan, not by the Go dependency allowlist | AGENTS §4 | 02 §9, 06 §10.1 | Use `x/mod/sumdb/tlog` + own tiles layer |
| D17 | SSE update cadence | §13 | 08 §3 | See C12 |
| D18 | Served-task set persistence vs "no fsync in the hot path" and Ack ≤ 1 ms | §13 | 03 §7.2 #5, 07 §6.5 (persisted set) | ⚑ Safer and fsync-free: after any unclean restart the Worker refuses tasks whose ULID timestamp is earlier than its boot time (the ±10 min window then covers the gap); the set itself can persist asynchronously |

## E. Other ambiguities resolved while tracing (recorded, not blocking)

1. Route header unknown fields: the Relay ignores unknown control fields, but the route header is signed and AAD-bound; the Worker treats an unknown route-header field as `route_mismatch` (fail closed, AGENTS §5).
2. `est_input_tokens` "text_bytes": counted over the UTF-8 bytes of all text content (system, messages, tool definitions, tool results) after scrubbing; exact definition must be pinned in the route↔body vectors (T-03-146).
3. Proof of zero spend lists `unauthorized_task` and `bad_envelope`, which are also "alert" codes; they still release the reservation (no provider call happened).
4. `KnownTask.state` has only `running`/`outbox`; plan 03 §5.2 says "in progress or in its outbox" — consistent.
5. `Welcome.max_concurrent_tasks` is the per-Gateway-device limit (03 §16 default 16).
6. Phase for "web pledge form" is 1 (11 Ph1 relay scope) even though the full Donor Station is Phase 4.

## Requests to other owners (from tracing)

- **integrator**: resolve D4, D5, D6, D9, D10, D14, D18 and C1/C2/C5/C12 in `spec/CONTRACT.md` and the plan text; adopt the proposed E23–E91 IDs (or renumber them here); add `CI-23` (proto regeneration check) to the build entry points.
- **mo-relay**: add flags for metrics address, TOML config, autocert, read-only boot (D15); chaos `inject_frame` must inject into the victim's own `Submit` stream (D8); expose pledge-freeze for runbook R2.
- **mo-e2e**: E17 harness per D8; scaffolds for proposed scenarios with `t.Skip("pending: …")`.
- **mo-sec**: when `docs/security/attack-catalog.md` lands, add A-ids to the 06 §3 threat rows (T-06-001…T-06-022, T-06-117) and to the E23/E25/E26/E40/E43/E44/E46/E48/E49/E57/E58/E61/E68/E80/E91 proposals.
- **mo-web / mo-relay**: keep the reserved-handle list in sync with the route map (CI-24).
- **Proposed new owners**: `mo-ops*`, `mo-release*`, `mo-docs*`, `human-po*`, `human-counsel*` (see §A).

---

## F. Statistics (generated)

- Rows: **1042** (1035 live, 7 superseded). Status: todo 1035, superseded 7.
- Rows per table: 00: 7, 01: 37, 02: 46, 03: 150, 04: 69, 05: 80, 06: 117, 07: 92, 08: 64, 09: 37, 10: 57, 11: 70, 12: 47, 13: 45, C00: 3, C01: 11, C02: 1, C03: 2, C06: 14, C07: 4, C08: 1, C09: 2, C10: 1, C11: 14, C12: 22, C13: 14, LP: 20, AG: 15.
- Live rows by first phase: D: 16, P0: 32, P1: 567, P2: 139, P3: 93, P4: 86, P5: 25, P6: 40, R: 13, —: 24 (D = deferred, R = research, — = permanent).
- Live rows verified by at least one existing E01–E22 scenario: 298; by proposed checks only: 737; with a proposed owner: 120.
