# 12 — Decisions, Rejected Ideas, and Open Questions

> The decision record (ADR-style, one line of context each), the ideas deliberately not built or deferred, and the questions that still need an owner's answer. Revisit a decision only when its "revisit when" condition is met.

---

## 1. Decision record

| ID | Decision | Alternatives considered | Why | Revisit when |
|---|---|---|---|---|
| ADR-01 | **Open-source client, closed-source core** (product owner, 2026-10-01): the `moochy` client, the protocol definition (`.proto`, vectors, public protocol spec) and user guides are **Apache-2.0** with DCO; the relay + web monorepo (backend and frontend) is proprietary. Open code never depends on closed code; all key handling and cryptography live in the open client | Everything open source (earlier revision of this plan); dual Apache-2.0/MIT; AGPL relay | Users only need to trust what they can read and verify (the client); the relay sees only ciphertext; the product owner keeps the core proprietary | — |
| ADR-02 | **Free forever**: no fees, no commission, no paid tier, no paid "verified" mode; Moochy never holds anyone's money | Take rate, premium tiers | Project requirement ("100% free"); avoids payment/escrow/tax regimes; infrastructure is cheap and sponsor-funded with public accounts | Never for fees. Funding model only |
| ADR-03 | Unit of account = **µ$ (int64 micro-USD)** | Raw tokens (draft); floats | Tokens are not comparable across models or token types; integers avoid drift | — |
| ADR-04 | **Two doors, one pipeline**: an MCP server (stdio + Streamable HTTP) **and** a provider-compatible API (Anthropic + OpenAI) on loopback | MCP only (draft); API only | MCP reaches every MCP client and agent framework; the API door makes donated compute the *primary* model for any tool with a base URL; one pipeline = the same guarantees | — |
| ADR-05 | **One Node process per machine** with roles and thin front-ends | Separate `moochy-mcp` and `moochy-daemon` binaries (draft) | Zero cold start, one connection, one key unlock, one place for caps | — |
| ADR-06 | **Scheduler = single-owner goroutine (actor)** with a sheddable submit queue and a never-blocking lifecycle queue; `sync.Map` only for the data-plane forwarding table | Lock-free `sync.Map` registry (draft); global mutex; Redis | Matching + reserving is a multi-entity transaction; actor = no races, deterministic replay, simulation testing | Scheduler p99 > 200 µs or > 50k events/s → shard by repo |
| ADR-07 | **End-to-end sealed envelopes**: recipient-independent body under a **fresh content key per body**, per-recipient HPKE wraps, **per-attempt response keys salted by the Worker** | Relay sees plaintext; one key per task | The operator learns nothing; zero-RTT failover still works; no key/nonce reuse is possible whatever the Relay does | — |
| ADR-08 | **Gateway-signed tasks**; Workers accept only owner-approved members, fresh and never-seen task ids | Trusting the Relay to assign only real tasks | HPKE base mode lets anyone with a public key build an envelope; signatures stop relay-originated inference, replays, and cross-repo charging | — |
| ADR-09 | **Ed25519 (signing, ZIP-215 verification in both languages) + X25519 (encryption)** per device; no GPG; length-prefixed domain-separated labels | GPG/OpenPGP (draft); converting Ed25519 → X25519 | One small, standard toolset; no cross-implementation verification gaps | — |
| ADR-10 | Keys in the **OS keychain**; encrypted-file / systemd-creds fallback | Passphrase AES-256-GCM store (draft) | An always-on daemon cannot prompt for a passphrase on every start | — |
| ADR-11 | Signatures mean **accountability**: donor-signed receipts and **signed progress checkpoints on every tool call**, plus maintainer **signed disputes** (silence = acceptance) | Single signature as "verification" (draft); full countersigning of every receipt | Signatures cannot prove which model generated output; they can prove who sent which bytes. Disputes give most of the value of countersigning with one message instead of one per task | Leaderboard fraud appears → add countersigning |
| ADR-12 | **Owner-signed approvals** of donors and members, recorded in a public **key log** (Merkle tree, signed checkpoints, hourly public Git anchor), mirrored by every Node | Trust tiers and relay-asserted approvals; receipt log + witnesses in v1 | Closes the "relay invents an approved donor" attack with a small log that every Node can mirror; tiers and a receipt log add surface without protecting a v1 promise | Demand for third-party audit of omissions → receipt log + witnesses |
| ADR-13 | **Public receipt projections** (donor-signed, day granularity, no device ids or task ids) | Publishing full receipts | Full receipts would publish donors' online times and maintainers' work timelines forever | — |
| ADR-14 | **Worker request firewall = strict recursive allowlist** per adapter, including provider headers; only safe mutations (attribution id, model-id mapping, stream usage, `store: false`) | Trusting "text-only" (draft); denylist | Modern APIs include server-side execution, file stores, connectors, and paid add-ons; only an allowlist stays safe as APIs grow | — |
| ADR-15 | **Money durability**: `synchronous=FULL`, ack after commit, commit before assign, per-attempt reservations released only on proof of zero spend, Worker outboxes kept 7 days, start-period attribution | `synchronous=NORMAL`; in-memory reservations; per-task receipts | The review found real double-spend, lost-receipt, and period-drift windows; each rule closes one at negligible cost | — |
| ADR-16 | **Three-layer caps**, layer 2 = Worker local reservations per device | Relay-only enforcement | The donor's worst case must not depend on trusting the Relay | — |
| ADR-17 | **Session affinity aligned with the provider cache TTL** (5 min / 1 h), affinity key = HMAC under a per-device secret | Latency or random routing; unsalted hash | ~10× cheaper input on agent sessions; key unguessable by the Relay | — |
| ADR-18 | **Public model ids = OpenRouter-style slugs**, native ids accepted, mapping through the signed catalog | Exact provider strings; separate alias feature later | One pool per model across native providers and OpenRouter from day one | — |
| ADR-19 | **No cross-dialect translation**; OpenRouter and DeepSeek serve **both** dialects | Translate Anthropic ↔ OpenAI formats | Translation is lossy; both providers already expose both API shapes | Dialect mismatch leaves > 10% of requests unserved |
| ADR-20 | **No hedged requests and no failover after the provider started** | Duplicate to 2 donors; retry mid-stream | Doubles spend of donated money | — |
| ADR-21 | **Prefix-delta transfer deferred** (designed, frame kind reserved) | Ship in v1 | After zstd the saving is ~65–100 ms per turn; complexity and risk are not justified yet | Upload p50 > 150 ms or egress in the top 3 costs |
| ADR-22 | **Drain-and-restart deploys** in v1 | Blue/green with make-before-break | One cheap VM; ~10 s of retryable errors per weekly deploy is acceptable; outboxes make it safe | Deploy-caused failures visible in metrics |
| ADR-23 | `count_tokens` answered **locally** by the Gateway | Route through the pool | It is free at the provider but would cost a relay round trip, envelopes, and a donor slot | — |
| ADR-24 | Go stdlib `ServeMux`; Rust `serde_json` | `chi`; `simd-json` (draft) | Not needed; fewer dependencies | — |
| ADR-25 | **Single-node relay**, partition by repo when needed | Multi-node from day one | Fits the design point; tasks never cross repos, so sharding is clean later | Metrics in [10 §9](10-operations.md) |
| ADR-26 | The relay is blind → **no content moderation at the relay** | Relay-side scanning | Incompatible with E2E; providers run safety systems; owners approve donors | — |
| ADR-27 | **No direct peer-to-peer transport** in v1 | NAT traversal | Saves ~50–150 ms at best vs seconds of model time | Egress or latency data justify it |
| ADR-28 | **Presence aggregated by default**; per-donor display opt-in | Public per-node presence with RTT (draft) | Per-person presence leaks when someone's machine is on | — |
| ADR-29 | **API keys only**; subscription/consumer credentials refused | Any credential | Provider terms; donor account safety | — |
| ADR-30 | **Never host donor keys; no relay-hosted MCP endpoint**; remote-only MCP clients get an opt-in **self-tunnel** mode (Phase 5) | Custodial "cloud workers"; hosted MCP URL | Both would require trusting the operator with keys or plaintext | — |
| ADR-31 | **Public repositories only** on the public instance | Allow private repos | Purpose is open source; public use is auditable; private pools fit self-hosted relays | Q3 |
| ADR-32 | Durations, deadlines, and weights are **configuration values with documented defaults** | Hard-coded constants | They will be tuned from telemetry | — |
| ADR-33 | **gRPC (HTTP/2, protobuf) for every machine-to-machine link**: Node ↔ Relay (`NodeLink`: Session + one stream per task/attempt + device login), CLI/MCP shim ↔ Node (`LocalControl` over a 0600 Unix socket), operator ↔ Relay (`RelayAdmin` over a Unix socket). HTTP/JSON/SSE kept only where external compatibility requires it (provider API door, MCP transports, browser, OAuth, badges). Signed artifacts stay exact JSON bytes inside protobuf `bytes` | Custom WebSocket framing (earlier draft of this plan) | Product owner requirement; one typed schema for Go and Rust; per-task HTTP/2 flow control, cancellation and deadlines for free; supersedes the 23-byte frame header (plan 03 §4.2) | — |
| ADR-34 | **Responsiveness budgets** are release blockers (`spec/CONTRACT.md` §13, measured by E22); **adaptive group commit** (commit at once when idle, batch only while a commit is in flight) replaces the fixed 10 ms window of plans 04/05/09 | Throughput-first batching | Product owner requirement ("drastic responsiveness"); idle-first commits remove up to 10 ms from every assignment at no durability cost | — |

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
| Federation between relays | Deferred | Self-hosting covers private pools |
| Cross-dialect translation | Deferred | ADR-19 |
| Verified compute (TLS notarization, TEEs) | Research track, opt-in and free | [06 §15](06-security-and-trust.md) |
| Local GPU donors | Research track | Needs token-denominated goals |
| Email notifications | Deferred | No v1 need |

---

## 3. Open questions

| # | Question | Recommendation | Needed by |
|---|---|---|---|
| Q1 | License and contributions | **Decided:** Apache-2.0 for the open-source parts, DCO sign-off | — |
| Q2 | Private repositories on the public instance in a later phase? | No; private pools are better served by self-hosted relays | Phase 5 |
| Q3 | Which providers get a counsel "go"? | Start with those that clearly allow API-based service to third-party end users with attribution | Phase 0 |
| Q4 | Which IDEs can reach a loopback base URL? Which MCP clients send roots, honor progress, and allow longer tool timeouts? | Validate in Phase 0; the matrix and `moochy connect` encode the answers | Phase 0 |
| Q5 | Exact Anthropic-compatible endpoints and usage fields for OpenRouter and DeepSeek | Confirm in Phase 0; adapters are data tables | Phase 0 |
| Q6 | Public instance region | Nearest to early design partners; revisit with latency data | Phase 1 |
| Q7 | Governance: who holds the log and catalog signing keys? Fiscal host? | Two maintainers with hardware tokens; Open Collective as fiscal host; documented in `GOVERNANCE.md` | Phase 6 |
| Q8 | Task metadata retention (90 days proposed) | 90 days raw, aggregates forever | Phase 1 |
| Q9 | Default per-member quota (20% of committed) and per-task cap ($5) | Keep, editable by owners and donors | Phase 2 |
| Q10 | Should donors be able to restrict *which members* use their pledge? | Not in v1; revisit with feedback | Phase 4 |
| Q11 | Project name: does "mooch" (to freeload) send the right message? | Check with design partners | Phase 0 |
