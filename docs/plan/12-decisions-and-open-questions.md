# 12 — Decisions, Rejected Ideas, and Open Questions

> The decision record (ADR-style, one line of context each), the ideas deliberately not built or deferred, and the questions that still need an owner's answer. Revisit a decision only when its "revisit when" condition is met.

> **Updated 2026-10-01:** the record now covers the decisions taken while writing `spec/CONTRACT.md` and in the 2026-10-01 traceability review, and agrees with the revised ADR-01 source boundary. Changes: ADR-35 to ADR-42 appended (unique handles, three crates, served-task boot floor, key log now, tlog + note without Tessera, `ps_` pseudonyms, window = eligibility, policy errors never 429); ADR-02, ADR-30, ADR-31, Q2, and the rejected-ideas table no longer rely on self-hosted relays; ADR-21 no longer mentions frame kinds (ADR-33).

---

## 1. Decision record

| ID | Decision | Alternatives considered | Why | Revisit when |
|---|---|---|---|---|
| ADR-01 | **Open-source client, closed-source core** (product owner, 2026-10-01): the `moochy` client, the protocol definition (`.proto`, vectors, public protocol spec) and user guides are **Apache-2.0** with DCO; the relay + web monorepo (backend and frontend) is proprietary. Open code never depends on closed code; all key handling and cryptography live in the open client | Everything open source (earlier revision of this plan); dual Apache-2.0/MIT; AGPL relay | Users only need to trust what they can read and verify (the client); the relay sees only ciphertext; the product owner keeps the core proprietary | — |
| ADR-02 | **Free forever**: no fees, no commission, no paid tier, no paid "verified" mode; Moochy never holds anyone's money | Take rate, premium tiers | Project requirement ("100% free"); public wording everywhere is "Open-source client (Apache-2.0) · 100% free"; avoids payment/escrow/tax regimes; infrastructure is cheap and sponsor-funded with public accounts | Never for fees. Funding model only |
| ADR-03 | Unit of account = **µ$ (int64 micro-USD)** | Raw tokens (draft); floats | Tokens are not comparable across models or token types; integers avoid drift | — |
| ADR-04 | **Two doors, one pipeline**: an MCP server (stdio + Streamable HTTP) **and** a provider-compatible API (Anthropic + OpenAI) on loopback | MCP only (draft); API only | MCP reaches every MCP client and agent framework; the API door makes donated compute the *primary* model for any tool with a base URL; one pipeline = the same guarantees | — |
| ADR-05 | **One Node process per machine** with roles and thin front-ends | Separate `moochy-mcp` and `moochy-daemon` binaries (draft) | Zero cold start, one connection, one key unlock, one place for caps | — |
| ADR-06 | **Scheduler = single-owner goroutine (actor)** with a sheddable submit queue and a never-blocking lifecycle queue; `sync.Map` only for the data-plane forwarding table | Lock-free `sync.Map` registry (draft); global mutex; Redis | Matching + reserving is a multi-entity transaction; actor = no races, deterministic replay, simulation testing | Scheduler p99 > 200 µs or > 50k events/s → shard by repo |
| ADR-07 | **End-to-end sealed envelopes**: recipient-independent body under a **fresh content key per body**, per-recipient HPKE wraps, **per-attempt response keys salted by the Worker** | Relay sees plaintext; one key per task | The operator learns nothing; zero-RTT failover still works; no key/nonce reuse is possible whatever the Relay does | — |
| ADR-08 | **Gateway-signed tasks**; Workers accept only owner-approved members, fresh and never-seen task ids | Trusting the Relay to assign only real tasks | HPKE base mode lets anyone with a public key build an envelope; signatures stop relay-originated inference, replays, and cross-repo charging | — |
| ADR-09 | **Ed25519 (signing, ZIP-215 verification in both languages: Rust `ed25519-zebra`, Go `ed25519consensus`) + X25519 (encryption)** per device; no GPG; length-prefixed domain-separated labels | GPG/OpenPGP (draft); converting Ed25519 → X25519 | One small, standard toolset; no cross-implementation verification gaps | — |
| ADR-10 | Keys in the **OS keychain**; encrypted-file / systemd-creds fallback | Passphrase AES-256-GCM store (draft) | An always-on daemon cannot prompt for a passphrase on every start | — |
| ADR-11 | Signatures mean **accountability**: donor-signed receipts and **signed progress checkpoints on every tool call**, plus maintainer **signed disputes** (silence = acceptance) | Single signature as "verification" (draft); full countersigning of every receipt | Signatures cannot prove which model generated output; they can prove who sent which bytes. Disputes give most of the value of countersigning with one message instead of one per task | Leaderboard fraud appears → add countersigning |
| ADR-12 | **Owner-signed approvals** of donors and members, recorded in a public **key log** (Merkle tree, signed checkpoints, hourly public Git anchor), mirrored by every Node; in scope now (ADR-38) | Trust tiers and relay-asserted approvals; receipt log + witnesses in v1 | Closes the "relay invents an approved donor" attack with a small log that every Node can mirror; tiers and a receipt log add surface without protecting a v1 promise | Demand for third-party audit of omissions → receipt log + witnesses |
| ADR-13 | **Public receipt projections** (donor-signed, day granularity, no device ids or task ids) | Publishing full receipts | Full receipts would publish donors' online times and maintainers' work timelines forever | — |
| ADR-14 | **Worker request firewall = strict recursive allowlist** per adapter, including provider headers; only safe mutations (attribution id, model-id mapping, stream usage, `store: false`) | Trusting "text-only" (draft); denylist | Modern APIs include server-side execution, file stores, connectors, and paid add-ons; only an allowlist stays safe as APIs grow | — |
| ADR-15 | **Money durability**: `synchronous=FULL`, ack after commit, commit before assign, per-attempt reservations released only on proof of zero spend, Worker outboxes kept 7 days, start-period attribution | `synchronous=NORMAL`; in-memory reservations; per-task receipts | The review found real double-spend, lost-receipt, and period-drift windows; each rule closes one at negligible cost | — |
| ADR-16 | **Three-layer caps**, layer 2 = Worker local reservations per device | Relay-only enforcement | The donor's worst case must not depend on trusting the Relay | — |
| ADR-17 | **Session affinity aligned with the provider cache TTL** (5 min / 1 h), affinity key = HMAC under a per-device secret | Latency or random routing; unsalted hash | ~10× cheaper input on agent sessions; key unguessable by the Relay | — |
| ADR-18 | **Public model ids = OpenRouter-style slugs**, native ids accepted, mapping through the signed catalog | Exact provider strings; separate alias feature later | One pool per model across native providers and OpenRouter from day one | — |
| ADR-19 | **No cross-dialect translation**; OpenRouter and DeepSeek serve **both** dialects | Translate Anthropic ↔ OpenAI formats | Translation is lossy; both providers already expose both API shapes | Dialect mismatch leaves > 10% of requests unserved |
| ADR-20 | **No hedged requests and no failover after the provider started** | Duplicate to 2 donors; retry mid-stream | Doubles spend of donated money | — |
| ADR-21 | **Prefix-delta transfer deferred** (designed in [03 §9](03-wire-protocol.md); nothing is reserved in `link.proto` yet, and when built it is added as new `oneof` members on the `Submit`/`Serve` streams, which protobuf accepts without breaking old peers) | Ship in v1 | After zstd the saving is ~65–100 ms per turn; complexity and risk are not justified yet | Upload p50 > 150 ms or egress in the top 3 costs |
| ADR-22 | **Drain-and-restart deploys** in v1 | Blue/green with make-before-break | One cheap VM; ~10 s of retryable errors per weekly deploy is acceptable; outboxes make it safe | Deploy-caused failures visible in metrics |
| ADR-23 | `count_tokens` answered **locally** by the Gateway | Route through the pool | It is free at the provider but would cost a relay round trip, envelopes, and a donor slot | — |
| ADR-24 | Go stdlib `ServeMux`; Rust `serde_json` | `chi`; `simd-json` (draft) | Not needed; fewer dependencies | — |
| ADR-25 | **Single-node relay**, partition by repo when needed | Multi-node from day one | Fits the design point; tasks never cross repos, so sharding is clean later | Metrics in [10 §9](10-operations.md) |
| ADR-26 | The relay is blind → **no content moderation at the relay** | Relay-side scanning | Incompatible with E2E; providers run safety systems; owners approve donors | — |
| ADR-27 | **No direct peer-to-peer transport** in v1 | NAT traversal | Saves ~50–150 ms at best vs seconds of model time | Egress or latency data justify it |
| ADR-28 | **Presence aggregated by default**; per-donor display opt-in | Public per-node presence with RTT (draft) | Per-person presence leaks when someone's machine is on | — |
| ADR-29 | **API keys only**; subscription/consumer credentials refused | Any credential | Provider terms; donor account safety | — |
| ADR-30 | **Never host donor keys; no relay-hosted MCP endpoint**; remote-only MCP clients get an opt-in **self-tunnel** mode (Phase 5): the user exposes their **own Node's** `/mcp` through their own tunnel (this is not a self-hosted relay) | Custodial "cloud workers"; hosted MCP URL | Both would require trusting the operator with keys or plaintext | — |
| ADR-31 | **Public repositories only** on the public instance | Allow private repos | Purpose is supporting open-source projects; public use is auditable; private repositories are not offered, and there is no self-hosted relay alternative (ADR-01) | Q2 |
| ADR-32 | Durations, deadlines, and weights are **configuration values with documented defaults** | Hard-coded constants | They will be tuned from telemetry | — |
| ADR-33 | **gRPC (HTTP/2, protobuf) for every machine-to-machine link**: Node ↔ Relay (`NodeLink`: Session + one stream per task/attempt + device login), CLI/MCP shim ↔ Node (`LocalControl` over a 0600 Unix socket), operator ↔ Relay (`RelayAdmin` over a Unix socket). HTTP/JSON/SSE kept only where external compatibility requires it (provider API door, MCP transports, browser, OAuth, badges). Signed artifacts stay exact JSON bytes inside protobuf `bytes` | Custom WebSocket framing (earlier draft of this plan) | Product owner requirement; one typed schema for Go and Rust; per-task HTTP/2 flow control, cancellation and deadlines for free; supersedes the 23-byte frame header (plan 03 §4.2) | — |
| ADR-34 | **Responsiveness budgets** are release blockers (`spec/CONTRACT.md` §13, measured by E22); **adaptive group commit** (commit at once when idle, batch only while a commit is in flight) replaces the fixed 10 ms window of plans 04/05/09 | Throughput-first batching | Product owner requirement ("drastic responsiveness"); idle-first commits remove up to 10 ms from every assignment at no durability cost | — |
| ADR-35 | **One unique handle per user**: ASCII lowercase `^[a-z0-9](?:[a-z0-9-]{1,30}[a-z0-9])$`, no `--`, unique case-insensitively (stored lowercase + `COLLATE NOCASE`); default = provider login if valid and free, else the user picks (no auto-suffix); reserved route, staff, and system words; rename at most every 30 days; old handles become **permanent tombstones** that redirect for 90 days (CONTRACT §11, E21) | Provider login as-is; Unicode handles; recycling freed handles; auto-suffix `alice-2` | Handles appear on public pages, badges, and the log: ASCII-only removes homoglyph impersonation, tombstones stop recycling takeovers of links and reputation, no auto-suffix avoids look-alikes. Shared Go/Rust vectors keep both sides identical | Users from non-Latin scripts ask for display names (add a separate, non-unique display name, never a Unicode handle) |
| ADR-36 | **Three Rust crates**: `moochy-proto` (wire types, crypto, receipts, vectors), `moochy-worker` (firewall, adapters, parsers, outbox, served-task set) with **no dependency on `moochy-proto`**, and `moochy` (CLI, keystore, relay link, doors, wiring); plus `moochy-keylog` (decision D1) | One crate with modules (earlier revision of 02 and 07) | The provider-facing code that guards the donor's account can be reviewed, fuzzed, and owned on its own; it cannot reach sealing code by accident; parallel ownership by separate agents | Compile times or duplication show the split costs more than it protects |
| ADR-37 | **Served-task set in memory plus a boot-time floor**: the Worker keeps task ids for the ±10 min freshness window and refuses any task whose ULID timestamp is earlier than its own process start (decision D18) | Persisting the set with fsync per task | Replay across restarts becomes impossible without any fsync on the hot path, which keeps Assign → Ack ≤ 1 ms (CONTRACT §13). Cost: tasks submitted just before a Worker restart are refused by that Worker and fail over | Restarts during load cause measurable failovers |
| ADR-38 | **Key log in scope now**; until it ships, a Worker accepts relay-asserted membership and approvals **only** when started with `MOOCHY_INSECURE_DEV=1` (tests, design partners); with the key log it requires owner-signed `REPO_CLAIMED`, `DONOR_APPROVED`, and `MEMBER_*` entries (decision D14) | Defer the key log to a later phase; trust relay-asserted membership in Phase 1 by default | Without the log the relay can invent members and donors; an explicit, loud dev switch keeps tests and design partners moving without letting that mode reach production | — |
| ADR-39 | **Key log built on `golang.org/x/mod/sumdb/tlog`** (hashing, proofs) and **`x/mod/sumdb/note`** (signed checkpoints), with our own thin C2SP tlog-tiles path layer; Rust verifier in `moochy-keylog` (decision D16) | transparency-dev Tessera | Stays inside the Go dependency allowlist (AGENTS §4); the `x/mod` code is battle-tested in the Go checksum database; the tile layer is small | Log size or write rate outgrows the simple layer (Tessera or a sharded log becomes worth its dependency weight) |
| ADR-40 | **Public pseudonym `ps_` + 16 random base32 characters**, stored in `users.pseudonym`, **never derived from** the internal `user_id` (`u_` + ULID, never public) (decision D10) | Pseudonym = `u_…` id; hash of `user_id` | Distinct prefixes stop internal ids leaking through copy-paste; a random value cannot be linked back to the account or brute-forced from a known id | — |
| ADR-41 | **A closing schedule window is an eligibility condition**, sent as `WorkerOffer.window_open`; it never changes pledge status. A pledge is `paused` only by explicit donor action. Pledge schedules and device schedules both exist and both only gate eligibility (C3) | Pledge goes Active → Paused when its window closes | One meaning per state: status changes are donor decisions recorded in the ledger, while availability changes many times a day and belongs in scheduler memory; no write per window edge | — |
| ADR-42 | **Policy errors are never HTTP 429**: `over_task_cap` → 400 `invalid_request_error`, `quota_exceeded` → 403 `permission_error`, both non-retryable (C4) | 429 for quota errors | Agents retry 429 automatically, so a hopeless request would loop and burn time; 400/403 make them stop | A major client mishandles 403 for quota |

---

## 2. Rejected or deferred ideas (and why)

| Idea | Status | Reason |
|---|---|---|
| Crypto tokens / on-chain ledger | Rejected | No value over a transparency log; adds speculation, fees, and regulation to a free project |
| Moochy-run "cloud workers" holding donor keys | Rejected | Breaks the core invariant (keys never leave the donor's control) |
| Relay-hosted MCP / API endpoint | Rejected | Would expose plaintext to the operator; headless Nodes and self-tunnels cover the need |
| Content moderation by the relay | Rejected | Incompatible with E2E |
| Hedged requests; failover after start; stream splicing | Rejected | Waste donations; two samples cannot be joined |
| GPG keys | Rejected | Complexity without benefit |
| Lock-free multi-index registry | Rejected | Wrong tool for transactional matching |
| `moochy self-verify` | Rejected | A binary vouching for itself proves nothing; verify externally |
| Trust tiers, auto-approval, tier headers | Deferred | Owner-signed approvals cover v1; add when owners ask for scale |
| Countersigning every receipt | Deferred | Disputes cover v1 |
| Public receipt log, witnesses, in-browser verifier | Deferred | Key log + Git anchor + projections + CLI verification cover v1 |
| Prefix-delta transfer | Deferred | ADR-21 |
| Blue/green deploys | Deferred | ADR-22 |
| Stream resume after Gateway reconnect | Deferred | Add if mid-stream disconnects exceed 0.5% |
| Federation between relays | Rejected | Self-hosting the relay is not offered (ADR-01); one operated relay, sharded by repo when needed (ADR-25) |
| Self-hosted relays and private pools on your own relay | Rejected | ADR-01: users stay safe without running a relay, because keys, code, and cryptography live in the open-source client and the relay only sees ciphertext |
| Custom WebSocket framing with binary frame headers | Superseded | ADR-33 (gRPC streams) |
| Fixed 10 ms group-commit window | Superseded | ADR-34 (adaptive group commit) |
| Persisted served-task set (fsync per task) | Rejected | ADR-37 (boot-time floor) |
| Tessera for the key log | Rejected | ADR-39 |
| Tailwind or another CSS framework | Rejected | Hand-written CSS within the CONTRACT §9 budgets; no build toolchain |
| Cross-dialect translation | Deferred | ADR-19 |
| Verified compute (TLS notarization, TEEs) | Research track, opt-in and free | [06 §15](06-security-and-trust.md) |
| Local GPU donors | Research track | Needs token-denominated goals |
| Email notifications | Deferred | No v1 need |

---

## 3. Open questions

| # | Question | Recommendation | Needed by |
|---|---|---|---|
| Q1 | License and contributions | **Decided:** Apache-2.0 for the open-source parts, DCO sign-off | — |
| Q2 | Private repositories on the public instance in a later phase? | No for v1 (ADR-31); there is no self-hosted relay alternative, so revisit only with design-partner demand | Phase 5 |
| Q3 | Which providers get a counsel "go"? | Start with those that clearly allow API-based service to third-party end users with attribution | Phase 0 |
| Q4 | Which IDEs can reach a loopback base URL? Which MCP clients send roots, honor progress, and allow longer tool timeouts? | Validate in Phase 0; the matrix and `moochy connect` encode the answers | Phase 0 |
| Q5 | Exact Anthropic-compatible endpoints and usage fields for OpenRouter and DeepSeek | Confirm in Phase 0; adapters are data tables | Phase 0 |
| Q6 | Public instance region | Nearest to early design partners; revisit with latency data | Phase 1 |
| Q7 | Governance: who holds the log and catalog signing keys? Fiscal host? | Two maintainers with hardware tokens; Open Collective as fiscal host; documented in `GOVERNANCE.md` | Phase 6 |
| Q8 | Task metadata retention (90 days proposed) | 90 days raw, aggregates forever | Phase 1 |
| Q9 | Default per-member quota (20% of committed) and per-task cap ($5) | Keep, editable by owners and donors | Phase 2 |
| Q10 | Should donors be able to restrict *which members* use their pledge? | Not in v1; revisit with feedback | Phase 4 |
| Q11 | Project name: does "mooch" (to freeload) send the right message? | Check with design partners | Phase 0 |
