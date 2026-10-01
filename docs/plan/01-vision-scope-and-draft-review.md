# 01 — Vision, Scope, and Review of the Draft

> Why Moochy exists, the non-negotiable principles and invariants, what is in and out of scope, how success is measured, and a line-by-line verdict on the original `draft-spec.md`.

> **Updated 2026-10-01:** principles, draft verdicts, and metrics now match `spec/CONTRACT.md`, revised ADR-01, and ADR-33 to ADR-42. Changes: open-source client (Apache-2.0, DCO) with a closed-source relay and web, no relay self-hosting (ADR-01, CONTRACT §0a); the draft's persistent WebSocket is replaced by gRPC streams (ADR-33); Tailwind replaced by hand-written CSS (CONTRACT §9); group commit is adaptive (ADR-34); responsiveness budgets added as a beta metric (CONTRACT §13, E22); unique usernames added as a missing draft item (ADR-35, CONTRACT §11).

---

## 1. Problem

Open-source maintainers increasingly do their work with AI coding agents, and those agents cost real money per month in API usage. Meanwhile, many developers and companies have API budget they would gladly direct to projects they depend on. Today the options are clumsy:

- **Send money** (sponsorships): the maintainer still has to buy API credits, manage keys, and pay taxes on income. Money is also an awkward ask for many communities.
- **Share an API key**: unsafe (unbounded spend, no revocation granularity, no audit), and against most provider terms.

**Moochy lets a donor route a capped slice of their own API capacity to the projects they choose, without the key ever leaving their machine, and lets maintainers use it from any AI client or agent with zero tooling changes.** Every unit of compute is attributable, auditable, and publicly verifiable.

---

## 2. Actors

| Actor | One-line need |
|---|---|
| Donor | "Give $X/month of my API budget to project Y, safely, with a hard cap, and see exactly what it was used for." |
| Maintainer (owner/admin) | "Run my agents on donated compute without changing tools, and control who can use it." |
| Member | "Use my project's pool within my quota." |
| Visitor | "See who supports this project, and check that it is real." |
| Operator (Moochy) | "Run a cheap, blind, reliable relay." |

---

## 3. Principles (non-negotiable)

1. **Open-source client (Apache-2.0).** The `moochy` client, the protocol definition (`.proto`, test vectors, public protocol spec), and the user guides are Apache-2.0 with DCO sign-off, published as the public `moochy-cli` repository. Everything that touches a donor's key, a maintainer's code, or the cryptography is in that client, so anyone can audit it, verify the release, or write a compatible client. The relay and web are closed source and operated by Moochy; self-hosting the relay is not offered.
2. **100% free.** Public wording: "Open-source client (Apache-2.0) · 100% free". No fees, no commission on compute, no paid tier, no feature gating. Donors pay their own provider directly; Moochy never holds anyone's money. The public instance's small hosting bill is covered by open sponsorship, with public accounts.
3. **Works with anything.** Any MCP client or AI agent (MCP door), any tool or SDK with a configurable base URL (API door), and any major provider on the donor side (Anthropic, OpenAI, OpenRouter, DeepSeek, xAI (Grok), OpenAI-compatible hosts).
4. **Trust no operator.** Nobody can verify what a server runs, open source or not, so confidentiality and integrity are enforced cryptographically by the open-source client on the user's own machine. The relay only ever sees encrypted bytes plus the plaintext route header and accounting metadata; owner-signed approvals, the key log, Worker local caps, and the provider's own spend limit cover the rest.
5. **Donated money is sacred.** Every design choice that can make a donated dollar go further (cache affinity, cancellation propagation, no hedging, budget-proportional routing) is taken.
6. **Boring infrastructure.** One Go relay binary + one SQLite file + one Rust client binary. No queue, no cache cluster, no microservices.

---

## 4. Invariants (the system's promises)

| # | Invariant | Mechanism (document) |
|---|---|---|
| I1 | A provider API key never leaves the donor's machine | Keystore + Worker-only use ([06 §4](06-security-and-trust.md)) |
| I2 | The relay cannot read prompts or outputs | E2E envelopes ([03 §6](03-wire-protocol.md)) |
| I3 | A donor never spends more than their caps (within one task's overage) | Three-layer caps ([05 §6](05-ledger-and-accounting.md)) |
| I4 | A donor's account never executes anything server-side or touches account data on behalf of a maintainer | Request firewall ([06 §7](06-security-and-trust.md)) |
| I5 | Every unit of spend has a donor-signed receipt, checked by the maintainer's Gateway (signed dispute on mismatch), with a donor-signed public projection; every executed tool call carries a donor signature | Receipts, disputes, progress checkpoints ([03 §12](03-wire-protocol.md)) |
| I9 | The relay can neither invent a donor, a member, or a key, nor originate or replay a task, without published evidence | Owner-signed approvals in the key log, Gateway task signatures ([06 §10](06-security-and-trust.md), [03 §7.2](03-wire-protocol.md)) |
| I6 | Maintainers' tools work unmodified | Two doors ([07 §1](07-client-cli.md)) |
| I7 | No personal data in the append-only log | Pseudonyms + salted commitments ([06 §10.3](06-security-and-trust.md)) |
| I8 | No silent spend: every cent is in the donor's local journal | Journal ([07 §6.5](07-client-cli.md)) |

---

## 5. Goals, non-goals, and success metrics

### 5.1 Goals (v1 / public beta)

- Donors pledge µ$ budgets to public repos using Anthropic, OpenAI, OpenRouter, DeepSeek, or xAI keys.
- Maintainers and members consume through MCP or provider-compatible APIs from any client.
- Real-time public pages, README badges, verifiable receipts.
- Open-source client with reproducible, signed releases that users can verify.

### 5.2 Non-goals

- Payments, escrow, crypto tokens, or any money flow.
- Hosting donor keys or running inference on Moochy servers.
- Arbitrary compute (shell, containers, binaries).
- Content moderation by the relay.
- Private repositories (not offered on the public instance).
- Self-hosted relays (the Node's relay URL is configurable for development and tests only).
- Cross-dialect request translation (v1).

### 5.3 Success metrics

| Metric | Target at beta |
|---|---|
| Task success rate (excl. provider errors and cancels) | ≥ 99.5% |
| Relay-added latency p50 (same continent) | ≤ 60 ms |
| Ledger drift vs provider bills | ≤ 0.5% |
| Cache-read share of input tokens in agent sessions | ≥ 80% |
| Donor onboarding → first served task | < 5 min |
| Maintainer onboarding → agent running on donated compute | < 3 min |
| Clients verified working (either door) | ≥ 10 |
| Monthly infra cost of the public instance | ≤ $200 at 1M tasks/month |
| Responsiveness budgets (Moochy-added time per hop, loopback, instant fake provider) | Every CONTRACT §13 row met at p50 and p99, measured by E22 (release blocker) |

---

## 6. Review of `draft-spec.md`

Verdicts: **Keep** (as is), **Change** (keep the intent, change the design), **Drop**.

| Draft item | Verdict | Why | Replacement |
|---|---|---|---|
| Closed-source monorepo `moochy-core` | Keep | An earlier revision of this plan opened everything; the product owner restored the split (ADR-01). Users never need to trust the relay for confidentiality or caps, because those are enforced in the open client | Private `moochy-core` (relay + web, e2e, deploy, internal docs) and public `moochy-cli` (client, `spec/proto`, vectors, protocol spec, guides), Apache-2.0 + DCO for the open side ([02 §10](02-architecture-overview.md)) |
| Open-source Rust client with MCP + daemon | Keep / Change | Keep Rust and open source (Apache-2.0); merge into one binary and one Node process | `moochy` Node with roles + two doors ([07](07-client-cli.md)) |
| Go monolith, HTMX, SSE, Tailwind | Keep / Change | Go + HTMX + SSE are boring and effective; Tailwind adds a build tool for a few pages | Hand-written CSS with custom properties, no framework; motion built on native CSS features plus a small vanilla JS layer; budgets CSS ≤ 48 KB raw (≤ 12 KB gzip), motion JS ≤ 12 KB gzip, LCP ≤ 1.0 s on 4G, CLS 0 (CONTRACT §9) |
| `chi` router | Drop | Go ≥ 1.22 `ServeMux` covers it | stdlib |
| SQLite WAL + `modernc.org/sqlite` | Keep | Right size; CGO-free | + single writer, adaptive group commit (ADR-34), Litestream ([09](09-data-model.md)) |
| "In-memory zero-latency routing table (<1 ms dispatch)" | Change | Sub-ms is real but irrelevant next to upload and model latency | Honest latency budget; compression, warm pools, affinity ([02 §11](02-architecture-overview.md)) |
| Lock-free `sync.Map` registry | Change | Can't make match + reserve atomic → double-spend | Single-owner Scheduler actor; `sync.Map` for chunk forwarding only ([04 §1](04-routing-engine.md)) |
| `simd-json` / "<2 ms" serialization | Drop | No measurable benefit; payloads are opaque to the relay | `serde_json` |
| Persistent multiplexed WebSocket | Change | Keep the idea (one long-lived, multiplexed connection per Node, shared by all local clients); replace the transport. A custom WebSocket framing would have to rebuild per-task flow control, cancellation, and deadlines that HTTP/2 already provides | gRPC over HTTP/2 + TLS 1.3 (`moochy.v1.NodeLink`): one `Session` stream per connection, one stream per task and per attempt (ADR-33, [03 §2](03-wire-protocol.md)) |
| 500 ms ACK + auto-redirect | Keep / Change | Keep the ACK; add slot grants so ACKs rarely fail, NACK codes, per-attempt keys and accounting, no failover after the provider started | [03 §10](03-wire-protocol.md), [04 §8](04-routing-engine.md) |
| HMAC-signed payloads with a per-repo `mcp_secret` | Drop | Redundant with TLS; plaintext shared secret in the DB | Device-key handshake ([03 §3](03-wire-protocol.md)) |
| GPG / Ed25519 signatures as "verification" | Change | Signatures can't prove which model produced output; GPG adds complexity | Ed25519 only; donor-signed receipts, signed tool calls, and maintainer disputes for **accountability** ([06 §8–9](06-security-and-trust.md)) |
| AES-256-GCM passphrase keystore | Change | Background daemon cannot prompt on every start | OS keychain + encrypted-file fallback |
| "Text-only JSON-RPC, zero arbitrary execution" | Change | No longer automatically true: providers offer server tools, file stores, MCP connectors | Strict allowlist firewall ([06 §7](06-security-and-trust.md)) |
| Routing index by models, effort, balance, RTT | Keep / Change | Keep the dimensions; add affinity, rate-limit headroom, budget-weighted P2C | [04 §4–6](04-routing-engine.md) |
| Token pledges (LOCKED → RESERVED → SPENT → RECLAIMED) | Change | Tokens aren't comparable; states mix pledge and task concerns | µ$ budgets; pledge lifecycle + per-task reserve/settle ([05](05-ledger-and-accounting.md)) |
| Leftovers return to LOCKED; reclaim releases unreserved | Keep | — | Same semantics, made explicit |
| Public page with goal, live pool, audit log | Keep / Change | Keep; add verify links, privacy-preserving presence, badges | [08 §3](08-web-dashboard.md) |
| Per-node "RTT / GPG Verified" public display | Change | Leaks individual donors' online times; "verified" overclaims | Aggregated presence; privacy-preserving projections; honest verification via `moochy verify` |
| `users.public_key` | Change | One key per user, no rotation | `devices` table |
| `audit_logs` table | Change | One signature, one token number, no attempt or privacy model | Attempts + receipts + public projections ([09 §3](09-data-model.md)) |
| Models `claude-3-7-sonnet`, `gpt-4o`, `deepseek-r1` hard-coded | Change | Out of date; models change monthly | Signed, versioned catalog fed from provider model lists |
| MCP as the only maintainer integration | Change | Many tools can use a base URL directly as their main model | MCP door **and** API door ([07 §1](07-client-cli.md)) |
| Roadmap: backend → routing → web → CLI | Change | Nothing works end-to-end until the last phase | Vertical slice first ([11](11-roadmap-and-testing.md)) |
| (missing) Maintainer safety vs malicious donor output | **Add** | Highest real risk | [06 §8](06-security-and-trust.md) |
| (missing) Provider terms | **Add** | Existential risk | [06 §14](06-security-and-trust.md), Phase 0 |
| (missing) Prompt-cache economics | **Add** | ~10× cost lever | [04 §5](04-routing-engine.md) |
| (missing) Crash-safe accounting | **Add** | Money correctness | Outbox ([05 §7](05-ledger-and-accounting.md)) |
| (missing) Username uniqueness and impersonation | **Add** | Handles appear on public pages, badges, and the log; confusable or recycled names enable impersonation | One unique ASCII handle per user, case-insensitive, reserved words, permanent tombstones on rename (ADR-35, CONTRACT §11) |
