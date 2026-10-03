# Moochy — Architecture Plan (master index)

> **User-facing wording:** these plan docs keep internal terms (pledge, budget, Node, Worker, station, …). Every word a user sees follows [`docs/brand/VOICE.md`](../brand/VOICE.md) ("Donate tokens", donation, monthly limit, Dashboard, Project settings, …).

> **Moochy lets developers donate a capped slice of their own LLM API budget to open-source projects, and lets maintainers use it from any AI client or agent. The donor's key never leaves their machine, and every request is end-to-end encrypted and accountable.**
>
> **Open-source client (Apache-2.0) · 100% free** (no fees, no commission, no paid tier; Moochy never holds anyone's money) · **works with anything** (any MCP client or agent, any tool with a base URL; Anthropic, OpenAI, OpenRouter, DeepSeek, xAI (Grok), and OpenAI-compatible donors).

> **Updated 2026-10-01:** the index and summary now match `spec/CONTRACT.md`, revised ADR-01, and ADR-33 to ADR-42. Changes: open-source client (Apache-2.0, DCO) with a closed-source relay and web, no relay self-hosting (ADR-01, CONTRACT §0a); gRPC streams replace the WebSocket link and binary frames (ADR-33); adaptive group commit and responsiveness budgets (ADR-34, CONTRACT §13); unique ASCII usernames with tombstones (ADR-35, CONTRACT §11); key log in scope now, not deferred (ADR-38, ADR-39); three Rust crates (ADR-36); the CONTRACT §8 E2E table (E01–E22) is the definition of "working".
>
> **Updated again 2026-10-01 (main `b65289e7`):** sandboxing (ADR-43, CONTRACT §15), owner keys (ADR-44), receipt transparency log (ADR-45), VOICE.md vocabulary and monochrome visual direction (ADR-46), xAI (ADR-47), profiles at `/u/{handle}` (ADR-48); doc map updated.

Status: architecture plan; implementation is under way against `spec/CONTRACT.md` (normative for encodings and interfaces; it wins when it and this plan disagree) and `spec/proto/moochy/v1/link.proto`. Date: 2026-10-01. Input: `draft-spec.md`, which this plan **supersedes**. Its split between a closed-source core and an open-source client is the design again (ADR-01): the client and protocol definition are open source, the relay and web are proprietary. The draft is kept unchanged for reference.

---

## 1. Executive summary

The draft had the right instincts: a Go + HTMX + SQLite monolith, a Rust client, one persistent connection per Node (a WebSocket in the draft; gRPC over HTTP/2 in this plan, ADR-33), a fast in-memory router, signed results, and a public audit page. Taking it to production-grade depth, and through three independent adversarial reviews, changed the design in seven ways:

1. **What is donated is money, not tokens.** Budgets are integer micro-dollars (µ$), because a token of one model can cost 200× a token of another.
2. **The relay is blind, and cannot cheat with keys.** Requests are sealed end-to-end to donor devices with a fresh key per body and a Worker-salted key per attempt. Every task is signed by the maintainer's device. The relay is closed source, and nobody could verify what a server runs anyway, so confidentiality is enforced cryptographically by the open-source client that users can read and verify.
3. **Two universal doors.** An MCP server (stdio + Streamable HTTP) for every MCP client and agent, and a local Anthropic/OpenAI-compatible API so donated compute can be any tool's *primary* model. OpenRouter and DeepSeek serve both API shapes, so even Anthropic-format clients like Claude Code can run on them.
4. **Routing optimizes the money, not microseconds.** Session affinity keeps agent sessions on one donor key so provider prompt caches hit (input up to ~10× cheaper). The scheduler is a single-owner actor: correct by construction and replayable in tests.
5. **Approvals and accountability are signed, not asserted.** Repo owners sign donor approvals and memberships into a public key log that every Node mirrors. Workers sign every streamed tool call and every receipt. Maintainers sign disputes. This addresses the biggest real risk, which the draft missed: **a malicious donor feeding poisoned tool calls to a maintainer's agent**.
6. **Donor safety is layered.** A strict recursive allowlist firewall (modern provider APIs can execute code, read account files, and bill add-ons) plus caps enforced in three independent places, the strongest being the provider's own spend limit.
7. **Build a vertical slice first, then thicken it.** A real Claude Code and OpenCode session running on real donor keys through every component by the end of Phase 1. About 6 months to public beta with 2 engineers.

Decisions taken after the review passes, while the implementation contract was written (ADR-01 revised, ADR-33 to ADR-42, [12](12-decisions-and-open-questions.md)):

> **Repositories since 2026-10-03:** the project lives in four repositories under `moochy-dev`: `moochy-cli` (public, the client), `moochy-docs` (public, `docs/` and `spec/`), `moochy-skills` (public) and `moochy-relay` (private, relay + e2e + relay deployment). The layout below is the plan as written; [CONTRACT §0a](../../spec/CONTRACT.md#0a-source-boundary-product-owner-decisions-2026-10-01-repositories-since-2026-10-03) is current.

- **Open-source client, closed-source core.** The `moochy` client, `spec/proto`, `spec/vectors`, the public protocol spec, and user guides are Apache-2.0 (DCO sign-off), published as `moochy-cli`. The relay and web are proprietary (`moochy-core`). Everything that touches keys, code, and cryptography runs in the open client, so nobody has to trust the closed relay: it only ever sees ciphertext plus the route header and accounting metadata. Self-hosting the relay is not offered.

- **gRPC for every machine-to-machine link.** Node ↔ Relay is the `moochy.v1.NodeLink` service over HTTP/2 + TLS 1.3: one long-lived `Session` stream per connection, one `Submit` stream per task, one `Serve` stream per attempt. Cancellation, deadlines, and per-task flow control come from HTTP/2. The CLI and MCP shim reach the running Node through `LocalControl`, and operators reach the Relay through `RelayAdmin`, both over 0600 Unix sockets. Signed artifacts stay exact JSON bytes inside protobuf `bytes`.
- **Responsiveness has numbers.** CONTRACT §13 budgets are release blockers, measured by E22. The ledger writer uses **adaptive group commit**: it commits at once when idle and batches only while a commit is in flight.
- **One unique handle per user.** ASCII lowercase, case-insensitive unique, reserved words, renamed handles become permanent tombstones (CONTRACT §11, E21). Public log entries use a random `ps_` pseudonym, never derived from the internal `user_id`.
- **The key log is in scope now.** Until it ships, Workers accept relay-asserted membership only under `MOOCHY_INSECURE_DEV=1`.
- **"Working" means the E2E table.** CONTRACT §8 (E01–E22) runs real binaries against fake providers; failover, cancel, tamper/replay/injection defenses, usernames, and budgets are all due now.

---

## 2. Ideas that make the design work

| # | Idea | Payoff | Where |
|---|---|---|---|
| 1 | **µ$ unit of account** + one public model-id scheme (slugs) | Fair, comparable pledges; one pool per model across native providers and OpenRouter | [05 §1–2](05-ledger-and-accounting.md) |
| 2 | **Recipient-independent sealed body + 80-byte HPKE wraps** | End-to-end encryption *and* zero-RTT failover | [03 §6](03-wire-protocol.md) |
| 3 | **Worker-salted per-attempt response keys** | Failover can never reuse a key, whatever the relay does | [03 §6.1](03-wire-protocol.md) |
| 4 | **Route header bound as HPKE AAD + Worker recomputation + Gateway task signature** | Neither a relay nor a maintainer can swap models, inflate budgets, replay, or forge tasks | [03 §7](03-wire-protocol.md) |
| 5 | **Cache-aligned session affinity** (HMAC key) | ~10× cheaper input for agent sessions | [04 §5](04-routing-engine.md) |
| 6 | **Budget-weighted power-of-two-choices** | O(1) routing, no herding, proportional drain across donors | [04 §6](04-routing-engine.md) |
| 7 | **Actor scheduler, commit-before-assign, per-attempt accounting** | No double-spend, no lost receipts, deterministic simulation testing | [04 §1, §8](04-routing-engine.md) |
| 8 | **Worker outbox as the source of truth for spend** (kept 7 days) | Relay crashes and even disaster recovery lose no spend | [05 §7](05-ledger-and-accounting.md) |
| 9 | **Owner-signed approvals in a key log every Node mirrors**, anchored in public Git | The relay cannot invent a donor, a member, or a key without published evidence | [06 §10](06-security-and-trust.md) |
| 10 | **Signed progress checkpoints gate every tool call** | Every tool call an agent executes is attributable to a donor device | [03 §12.3](03-wire-protocol.md) |
| 11 | **Signed disputes, silence = acceptance** | Leaderboard integrity at one message per anomaly, not one per task | [03 §12.2](03-wire-protocol.md) |
| 12 | **Privacy-preserving receipt projections** | A public, verifiable audit feed that never reveals anyone's working hours | [03 §12.1](03-wire-protocol.md) |
| 13 | **Recursive allowlist firewall incl. provider headers** | The donor's account can't be turned into a remote execution, exfiltration, or billing-amplification platform | [06 §7](06-security-and-trust.md) |
| 14 | **MCP `files` read by the Node** under strict path rules | Delegated big reads never enter the calling agent's own paid context | [07 §5.2](07-client-cli.md) |
| 15 | **Three-layer caps, incl. the provider's own spend limit** | Worst case bounded even if Moochy itself is buggy | [05 §6](05-ledger-and-accounting.md) |
| 16 | **Provider-native errors, policy errors non-retryable** | Existing agents' retry logic handles failover; they stop retrying hopeless requests | [03 §10.3](03-wire-protocol.md) |
| 17 | **README badge** | Organic growth loop at near-zero cost | [08 §8](08-web-dashboard.md) |
| 18 | **One gRPC stream per task and per attempt** (ADR-33) | Cancellation = stream cancel (provider call aborted); per-task flow control and deadlines without a custom framing layer | [03](03-wire-protocol.md), CONTRACT §12 |
| 19 | **Adaptive group commit + measured budgets** (ADR-34) | Durable commit-before-assign without a timer on the idle path; Relay Submit → Assign ≤ 2 ms p50 | [04 §8](04-routing-engine.md), CONTRACT §13 |
| 20 | **Unique ASCII handles with permanent tombstones** (ADR-35) | No homoglyph impersonation, no username-recycling takeover of links and badges | [09](09-data-model.md), CONTRACT §11 |

---

## 3. Document map

| # | Document | Read it for |
|---|---|---|
| 01 | [Vision, scope, and draft review](01-vision-scope-and-draft-review.md) | Principles, invariants, metrics, verdict on every draft item |
| 02 | [Architecture overview](02-architecture-overview.md) | Components, trust boundaries, main flows, stack, repositories (open `moochy-cli`, closed `moochy-core`; three Rust crates + key log), latency budget, scale envelope |
| 03 | [Wire protocol](03-wire-protocol.md) | gRPC `NodeLink` (ADR-33), handshake with channel binding, messages, envelopes, task authenticity, failover, receipts, disputes, vectors |
| 04 | [Routing engine](04-routing-engine.md) | Scheduler actor, backpressure, eligibility, affinity, P2C, commit-before-assign with adaptive group commit, deadlines, fairness |
| 05 | [Ledger and accounting](05-ledger-and-accounting.md) | µ$, model ids and catalog, cost function, per-attempt reservations, caps, durability, reconciliation |
| 06 | [Security and trust](06-security-and-trust.md) | Threat model, keys, owner-signed approvals (owner keys), firewall, output-injection defense, key log and receipt log, privacy, terms, sandboxing (§18) |
| 07 | [Client (`moochy`)](07-client-cli.md) | Node, MCP door, API door, integration matrix, Worker, adapters (Anthropic, OpenAI, OpenRouter, DeepSeek, xAI, …), setup flows, `moochy run` sandbox and donor lockdown (§15), crate owners (mo-node / mo-donor split) |
| 08 | [Web and dashboards](08-web-dashboard.md) | Routes, public pages, Dashboard (`/station`), Project settings (`/console`), SSE fan-out, public receipts, Donate tokens button studio, organisation pages, mint visual direction |
| 09 | [Data model](09-data-model.md) | Tables, uniqueness constraints (handles, tombstones), write and read paths, migrations, backups, sizes |
| 10 | [Operations](10-operations.md) | Deploys, observability, SLOs, runbooks, costs, staying free |
| 11 | [Roadmap and testing](11-roadmap-and-testing.md) | Phases with checkable exit criteria mapped to the CONTRACT §8 E2E scenarios, verification strategy, launch checklist |
| 12 | [Decisions and open questions](12-decisions-and-open-questions.md) | ADRs, rejected or deferred ideas, questions needing an owner |
| 13 | [Review log](13-review-log.md) | What each of the five review passes and the 2026-10-01 traceability review found and changed |

**Reading order by role**: *Everyone*: 00 → 01 → 02, then `spec/CONTRACT.md` before writing code. *Relay engineer*: 03, 04, 05, 09, 10. *Client engineer*: 03, 07, 06 §7–8 and §13, 05 §3. *Security reviewer*: 06, 03 §3 and §6–7 and §12. *Product/design*: 01, 07 §4.4 and §8, 08, 11.

---

## 4. Glossary

| Term | Meaning |
|---|---|
| **Node** | The local `moochy` background process (one per machine), with roles |
| **NodeLink** | The gRPC service between Node and Relay (`spec/proto/moochy/v1/link.proto`): `Session`, `Submit`, `Serve`, `DeviceStart`, `DevicePoll` |
| **Gateway** | Node role that consumes pooled compute; serves the MCP door and the API door on loopback |
| **Worker** | Node role that serves tasks with the donor's provider key |
| **Relay** | The closed-source Go server (operated by Moochy) that routes sealed tasks, keeps the ledger, runs the key log and the web app; it only sees ciphertext plus routing and accounting metadata |
| **Door** | A consumer entry point: the **MCP door** (stdio / Streamable HTTP) or the **API door** (Anthropic / OpenAI-compatible HTTP) |
| **Dialect** | The API shape of a request: `anthropic.messages` or `openai.chat` |
| **Model id** | Public OpenRouter-style slug (`vendor/model`); native ids are accepted and mapped |
| **Handle** | A user's unique Moochy username (ASCII lowercase, case-insensitive unique, tombstoned on rename; CONTRACT §11) |
| **Pseudonym** | The random public `ps_…` id used in the key log and projections; never derived from the internal `user_id` |
| **Pledge** | A donor's standing commitment to one repo: µ$ budget per period + policy |
| **Approval** | The repo owner's device signature admitting a donor (or a member) to the repo, recorded in the key log |
| **Pool** | The active, approved pledges of one repo |
| **Task / attempt** | One model request; each assignment to a Worker is an attempt (at most 3) |
| **Route header** | The small plaintext metadata the relay schedules on, bound to the sealed body |
| **Envelope** | The sealed request: body under a fresh content key, plus per-recipient wraps |
| **Receipt / projection** | The donor-signed usage record of an attempt / its privacy-preserving public summary |
| **Dispute** | The maintainer's signed objection to a receipt that does not match what its Gateway saw |
| **Progress checkpoint** | A Worker signature over the response so far, required before a tool call is released |
| **Reservation** | The µ$ upper bound held against a pledge, member, and device while an attempt is open |
| **Affinity** | Keeping one agent session on one donor key to reuse the provider's prompt cache |
| **Firewall** | The Worker's recursive allowlist of request fields, headers, and features |
| **Tripwire** | The Gateway's pattern scan of tool calls (a speed bump, not a guarantee) |
| **Key log** | The public append-only Merkle log of device keys, owner-signed approvals, and catalog versions |
| **µ$** | Micro-US-dollar, the integer unit of all money values |

---

## 5. What is deliberately not here

No code, no SQL, no configuration files. Everything is specified at the level of components, protocols, data shapes, algorithms, and checkable criteria. Exact encodings, process interfaces, and the E2E scenario table live in `spec/CONTRACT.md`; the wire schema lives in `spec/proto/`; cross-language test vectors live in `spec/vectors/`, because they are the contract between the two languages and every future implementation. The phases are in [11](11-roadmap-and-testing.md).
