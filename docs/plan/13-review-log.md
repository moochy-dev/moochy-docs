# 13 — Review Log

> The plan went through five review passes before being saved. Each pass used a different lens. This file records what was challenged, what changed, and what was deliberately *not* changed, so readers can see why the documents look the way they do. A later traceability review against `spec/CONTRACT.md` is recorded at the end.

> **Updated 2026-10-01:** added the traceability review (C1–C12, D1–D18) and the product-owner decisions of the same day. Changes: new final section and summary row; past entries kept as history, with short "superseded by" notes where an entry states something that is no longer the current design (source boundary ADR-01, gRPC ADR-33, OpenAI adapter phase D13, key-log library ADR-39, Gateway port C5).

| Pass | Lens | Reviewer | Findings | Accepted | Adapted | Declined |
|---|---|---|---|---|---|---|
| 0 | Requirement change mid-drafting | Product owner | 3 | 3 | — | — |
| 1 | Mechanical consistency (references, shared numbers, terms) | Author (scripted checks) | 11 | 11 | — | — |
| 2 | Adversarial security and applied cryptography | Independent reviewer | 15 | 13 | 2 | — |
| 3 | Distributed systems, money correctness, operations | Independent reviewer | 15 | 12 | 3 | — |
| 4 | Simplicity, requirement fit, factual risk | Independent reviewer | 15 | 13 | 1 | 1 |
| 5 | Final consistency after all changes | Author (scripted checks + read-through) | 9 | 9 | — | — |
| 6 | Traceability against `spec/CONTRACT.md` (2026-10-01) | Traceability matrix + integrator | 30 | 30 | — | — |

Passes 2–4 ran in parallel without seeing each other's output. Their overlap is itself a signal: **all three independently found the same critical key/nonce-reuse flaw.**

---

## Pass 0: requirement change while drafting

> "Any client, AI agents, OpenRouter, DeepSeek, OpenCode, anything should be able to integrate the MCP workflow, and it should be 100% clear it's open source and 100% free."

| Change | Documents |
|---|---|
| **Everything open source**: the draft's closed `moochy-core` becomes part of one public monorepo (`relay/`, `cli/`, `spec/`), Apache-2.0 OR MIT; self-hosting first-class; confidentiality still never depends on trusting the operator (superseded by revised ADR-01, 2026-10-01: open-source client under Apache-2.0, closed-source relay and web, no relay self-hosting) | 00, 01, 02, 03, 06, 10, 11, 12 |
| **Free forever**: no fees, commission, or paid tier; sponsor-funded public instance with a public cost page (`/open`); statement on every web page | 00, 01, 06, 08, 10, 12 |
| **MCP as a first-class universal door** (stdio + Streamable HTTP, `moochy connect <client>`, `npx -y moochy mcp`, headless agents), next to the provider-compatible API door; integration matrix covering OpenCode, Claude Code, Cursor, Cline, Zed, Goose, agent frameworks, SDKs | 00, 01, 02, 07, 08, 11 |
| **OpenRouter and DeepSeek first-class** in Phase 1: adapters, usage mappings, firewall rules, catalog import | 05, 06, 07, 09, 11 |

---

## Pass 1: mechanical consistency

Method: a script resolved every `[NN §X]` reference to an existing heading, and every shared parameter (deadlines, windows, limits, retention, defaults) was compared across all documents.

| # | Finding | Fix |
|---|---|---|
| 1.1 | Receipt/log ordering contradicted itself across 02, 03, 09 | One model everywhere (later simplified further in pass 4) |
| 1.2 | Zero-downtime deploy design could cut streams and run two writers | Redesigned (later simplified to drain-and-restart in pass 4, with the safe design kept for later) |
| 1.3 | Cache-read discount stated as "5–10%" | 2.5–10% depending on the model |
| 1.4 | Auto-caching injection not marked Anthropic-only | Clarified |
| 1.5 | Body-size limit phrased two ways | One rule |
| 1.6 | CI devices had scope and caps in 07 but nothing in 04/09 | Device scope, caps, and eligibility rule |
| 1.7 | Model aliases missing from the catalog schema | Added (later replaced by public slugs in pass 4) |
| 1.8 | OpenAI adapter phase ambiguous | Phase 2 (superseded by D13: Phase 1) |
| 1.9 | MCP delegate dialect selection unspecified; `files` could leak `.env` | Dialect chosen by the Node; file rules (hardened further in pass 2) |
| 1.10 | Token-equivalent display had no formula | One documented formula; mock number corrected |
| 1.11 | "Up to 400×" price-ratio claim | Corrected to 200× |

---

## Pass 2: adversarial security and cryptography

| # | Sev. | Finding | Disposition |
|---|---|---|---|
| 2.1 | **Critical** | Response key depended only on the content key, so two attempts (failover or a relay assigning twice) could share key and nonces, letting the relay recover plaintext and forge chunks. Request side had the same issue on full-body resends | **Accepted.** Fresh CK per sealed body; `K_req` derived; **Worker-salted per-attempt `RK`**; attempt and `R` bound in AAD; Gateway decrypts only the accepted attempt and aborts on a second started stream; test vectors prove distinct keys ([03 §6](03-wire-protocol.md)) |
| 2.2 | **Critical** | Key transparency only proved keys were logged for *some* user; the relay could invent an "approved donor" and receive plaintext | **Accepted.** Owner-signed `REPO_CLAIMED`, `DONOR_APPROVED`, `MEMBER_ADDED` in the key log; Gateways seal only to owner-approved keys; owner's Node alerts on unsigned approvals; public Git anchoring from the start ([06 §10](06-security-and-trust.md)) |
| 2.3 | High | Nothing proved who created a task (HPKE base mode); the relay could run its own inference, replay tasks, or charge another repo's pledge | **Accepted.** Gateway task signature; `repo_id` in the route header; Worker checks membership, pledge↔repo, ULID freshness, served-task set ([03 §7.2](03-wire-protocol.md)) |
| 2.4 | High | A malicious Worker could stream a poisoned tool call and disconnect before signing anything | **Accepted.** Signed progress checkpoints; tool calls released only after verification ([03 §12.3](03-wire-protocol.md)) |
| 2.5 | High | MCP `files`: client-declared roots, symlinks, `..`, `.git/config`, injected paths | **Accepted.** Recorded git root ∩ client roots, realpath containment, no symlinks, deny lists, `git check-ignore` ([06 §13](06-security-and-trust.md)) |
| 2.6 | High | OpenAI-style streams without usage, and cancellations, made receipts under-count (hidden reasoning) | **Accepted.** Force stream usage reporting; `estimated` receipts settle pessimistically at the reservation ([05 §5](05-ledger-and-accounting.md)) |
| 2.7 | Medium | Input-estimate band allowed under-reservation; images/PDFs priced by pixels/pages; concurrency made "one task overage" false; layer 2 per device | **Accepted.** Deterministic estimate recomputed exactly by the Worker; PDFs behind a flag; overage bound restated; Worker local reservations; per-device caveat documented |
| 2.8 | Medium | Beta headers passed through; OpenAI `n`, predictions, service tier, audio, web-search options; OpenRouter routing, plugins, variants; nesting | **Accepted.** Headers sealed and allowlisted; explicit denies; OpenRouter max-price; recursive validation and fuzzing ([06 §7](06-security-and-trust.md)) |
| 2.9 | Medium | Tripwire covered only Anthropic `tool_use`; MCP delegate results unprotected | **Accepted.** OpenAI `tool_calls` per index; name-in-`tools[]` and schema checks; denied block types; model match; untrusted-content framing for MCP results |
| 2.10 | Medium | Auth signed a relay-supplied origin; no channel binding; unprefixed fields | **Accepted.** Dialed origin + TLS exporter channel binding + `lp()` everywhere ([03 §3](03-wire-protocol.md)) |
| 2.11 | Medium | Public receipts leaked device ids and millisecond timestamps forever; affinity key was guessable | **Accepted.** Public **projections** (day granularity, no device or task ids); affinity key is an HMAC under a per-device secret |
| 2.12 | Medium | `connect --write` could commit tokens; another local user could squat the port | **Accepted.** User-scoped configs only, refuse git-tracked files, token rotation, port held by the service manager (superseded by C5: port picked at first run, persisted, and reused), `doctor` uid check |
| 2.13 | Low | Countersign plausibility checks failed on hidden reasoning and ignored input/cache inflation | **Adapted.** Same checks moved into the dispute rules (countersigning itself deferred per 4.2) |
| 2.14 | Low | Labels not prefix-free; one salt for three commitments; CK dual use; Ed25519 verification differences; no version binding; catalog rollback | **Accepted.** `lp()` labels, HKDF-derived salts and keys, ZIP-215 in both languages with vectors, suite id in HPKE info and `KEY_ADDED`, monotonic catalog |
| 2.15 | Low | `x/mod/sumdb/tlog` does not provide C2SP paths or witnesses; `hpke` not independently audited; computer use is client-executed; header claim false | **Adapted.** Library wording hedged (own path layer or Tessera; superseded by ADR-39: own layer, no Tessera); `hpke` under `cargo-vet`; firewall table corrected |

---

## Pass 3: distributed systems, money correctness, operations

| # | Sev. | Finding | Disposition |
|---|---|---|---|
| 3.1 | **Critical** | Same key/nonce reuse as 2.1 | **Accepted** (same fix) |
| 3.2 | **Critical** | Receipts keyed by `task_id` alone: a failover's second receipt froze honest donors; released reservations underflowed | **Accepted.** Receipts and reservations **per attempt**; release only on proof of zero spend; "started" (provider headers) replaces "first byte"; no failover after start ([04 §8](04-routing-engine.md)) |
| 3.3 | High | `synchronous=NORMAL` broke the "durably stored" promise of `receipt.ack`; checkpoints could be un-published | **Accepted.** `synchronous=FULL`; ack after commit; checkpoints only for replicated sizes; Workers keep acked receipts 7 days; `receipt.replay_since` after disaster recovery |
| 3.4 | High | Crash lost recent reservations; receipts for unknown tasks; orphan over-charging; Worker link-loss behavior unspecified | **Accepted.** Commit-before-assign; Workers abort and receipt on link loss; `worker.known_tasks` releases orphans at zero cost; pessimistic settlement only for long-absent Workers |
| 3.5 | High | Deploy handoff lost releases and receipts | **Adapted.** v1 uses drain-and-restart (pass 4.9), which removes the overlap entirely; the fixes are recorded as requirements for a future blue/green design ([10 §3](10-operations.md)) |
| 3.6 | High | Worker device cap checked only settled spend | **Accepted.** Worker local reservations before ack; Relay decrements `local_cap_left` |
| 3.7 | High | Period rollover attribution made the audit drift monthly; CHECK failures aborted whole batches | **Accepted.** Settle into the start period's row; boot applies missed rollovers; SAVEPOINT per op; constraint violations are fatal and recover by replay |
| 3.8 | Medium | Gateway disconnect didn't cancel; dedupe was global; frames forwarded from any connection | **Accepted.** Cancel on Gateway disconnect; dedupe per `(gateway_device, task_id)`; resubmission rules; forwarding checks the expected source connection (with gRPC, ADR-33: each task has its own stream, and streams must arrive on the authenticated connection) |
| 3.9 | Medium | Inbox backpressure could stall readers or deadlock with the writer | **Accepted.** Sheddable submit queue, never-blocking lifecycle queue, slice-swap writer handoff, separate completion channel |
| 3.10 | Medium | Stale session's offline event could remove a live worker | **Accepted.** Presence keyed by `(device, session)` |
| 3.11 | Medium | Device caps had no counters | **Accepted.** `device_usage` table, state, invariants, audit |
| 3.12 | Medium | 24 h timers in memory; unbounded buffered bodies; contradictory log-append text | **Accepted.** SQL sweeps; Edge byte budgets; text fixed |
| 3.13 | Medium | Migrations ran beside the live writer; rollback impossible | **Adapted.** Drain-and-restart runs migrations with no second writer; `min_compatible_version` enables rollback; long index builds run after boot |
| 3.14 | Low | Policy failures reported as retryable "overloaded"; $2 default per-task cap too low for large contexts on top models | **Accepted.** Non-retryable `over_task_cap`, `quota_exceeded`, `model_not_in_pool`; default cap $5 with console visibility |
| 3.15 | Low | Little's-law inconsistency; frame size overflow; band too loose; need_full vs tried[]; late messages; routing deadline vs slow uploads; WAL checkpoint setting | **Accepted.** ≈ 200 starts/s at 5k concurrent; 65,497-byte plaintext chunks; exact estimate; delta deferred (need_full gone); late-message rule; deadline from the last body frame; `wal_autocheckpoint=0` |

---

## Pass 4: simplicity, requirement fit, factual risk

| # | Impact | Finding | Disposition |
|---|---|---|---|
| 4.1 | High | Same key/nonce reuse as 2.1 | **Accepted** (same fix) |
| 4.2 | High | Trust layer oversized for v1 (key log + receipt log + witnesses + Git anchor + countersign + browser verifier) | **Accepted, merged with 2.2.** v1 keeps one key log (now carrying owner-signed approvals) + Git anchor + projections + CLI verification + signed disputes. Deferred: receipt log, witnesses, countersigning, in-browser verifier |
| 4.3 | High | OpenRouter and DeepSeek served only the OpenAI dialect, so Claude Code could not use them | **Accepted.** Both adapters serve both dialects (exact endpoints confirmed in Phase 0) |
| 4.4 | High | Model ids fragmented pools across providers; small/fast models could fail | **Accepted.** OpenRouter-style slugs as the public scheme from Phase 1; native ids accepted; `moochy connect` sets main and small models |
| 4.5 | High | MCP door relied on optional features (roots, progress, parallel calls, long timeouts) | **Accepted.** Roots fallback; timeout budget + client config; model enum in the schema; server `instructions`; "where supported" wording |
| 4.6 | Medium | Prefix-delta transfer not worth its complexity after compression | **Accepted.** Deferred with a metric trigger; latency table corrected to compressed sizes |
| 4.7 | Medium | OpenRouter cost varies by upstream; OpenAI-style streams lack usage by default | **Accepted.** Settle on OpenRouter's reported cost with a reservation bound; stream usage forced |
| 4.8 | Medium | "Open source and free" still had holes (draft file, open question, "premium tier", money wording) | **Accepted**, with one adaptation: `draft-spec.md` is the user's file and was **not modified**. 00 states that it is superseded instead |
| 4.9 | Medium | Zero-downtime deploys over-built for one cheap VM | **Accepted.** Drain-and-restart in v1; blue/green kept as a designed, metric-triggered upgrade |
| 4.10 | Medium | Remote-HTTPS-only MCP clients silently excluded | **Accepted.** Stated in the matrix; opt-in self-tunnel mode in Phase 5 |
| 4.11 | Medium | Trust tiers, auto-approve, tier header, and a "100%" tripwire criterion over-built | **Accepted.** Replaced by owner-signed approvals + pinned donors; tripwire documented as a speed bump; criterion rewritten |
| 4.12 | Low | `self-verify` proves nothing; cross-platform reproducibility too ambitious for beta | **Accepted.** External verification; reproducible Linux musl builds for beta |
| 4.13 | Low | Reconciliation against provider bills differs per provider | **Accepted.** Method per provider ([05 §7.1](05-ledger-and-accounting.md)) |
| 4.14 | Low | `count_tokens` took the full relay path | **Accepted.** Answered locally |
| 4.15 | Low | Library naming, browser-verifier trust claim, telemetry and NACK-detail consistency | **Accepted** (library wording hedged; browser verifier deferred; telemetry opt-in everywhere; NACK details sealed). **Declined:** dropping the pure-JS Ed25519 fallback became moot once the in-browser verifier was deferred |

---

## Pass 5: final consistency after all changes

Method: the reference resolver re-run, **plus a semantic check of every link into 03** (its sections were renumbered), a sweep for retired terms (countersign, dual-signed, tiers, witnesses, delta, first byte, closed source), shared-parameter re-comparison, Markdown table and Mermaid sanity checks.

| # | Finding | Fix |
|---|---|---|
| 5.1 | Three links pointed to renumbered protocol sections (errors, vectors) | Re-targeted |
| 5.2 | Overview still described failover "before the first byte" | "Before the provider started", linked to 03 §10 |
| 5.3 | Latency table still credited delta transfer for the relay→worker hop | Compression instead |
| 5.4 | Runbook R7 referenced a receipt log that is now deferred | Archive old receipts instead |
| 5.5 | Fake-provider tests said "slow first byte" | "Slow response start" |
| 5.6 | `moochy verify` described inclusion proofs for receipts | Projection + key-log + Git-anchor verification |
| 5.7 | Console still offered "anyone with push access" membership | Owner-signed membership only |
| 5.8 | Two table cells contained unescaped `\|` inside code spans (breaks GitHub tables) | Escaped |
| 5.9 | Mermaid labels contained `;` and `->`, which some renderers misparse | Normalized in 11 labels |

**Result:** 0 broken references, 0 retired terms outside deliberate "deferred" contexts, consistent parameters (ACK 500 ms, start 30 s, routing 5 s after the last body frame, ≤ 8 wraps, ≤ 3 attempts, ±10 min freshness, 7-day outbox retention, `synchronous=FULL`, $5 default per-task cap, 90-day metadata retention).

---

## Traceability review (2026-10-01)

Method: after `spec/CONTRACT.md`, `link.proto`, and the first components existed, every normative statement in plans 00–13, the CONTRACT (including §11–§13), and AGENTS was traced to an owner and a test (`docs/TRACEABILITY.md`). The trace found 12 contradictions between plan documents (C1–C12) and 18 conflicts between the CONTRACT and the plan (D1–D18). The integrator resolved all of them in CONTRACT §14 and ADR-35 to ADR-42; the plan text was then rewritten to match (this pass).

| Group | What was stale | Resolution |
|---|---|---|
| Transport (C2, C7, C9, D3, D5, D6, D7, D8, D9) | WebSocket, "WSS", text/binary frames, the 23-byte header, `route_b64`, `wss://` dialed origin, `worker.offer.window`, 64 streams per connection | gRPC `NodeLink` (ADR-33); `https://host:port` dialed origin; route bytes raw in `SubmitOpen.route` / `Assign.route`; constant `kind_byte` 0x01 kept in the request AAD; ciphertext ≤ 64 KiB, gRPC message cap 128 KiB, 128 streams per connection; `window_open`; E17 injects into the Gateway's own `Submit` stream |
| Durability and speed (C1, D18) | Fixed 10 ms group-commit window; persisted served-task set | Adaptive group commit (ADR-34); in-memory set with a boot-time floor (ADR-37); CONTRACT §13 budgets measured by E22 |
| Money and errors (C3, C4) | Window close paused the pledge; `over_task_cap` / `quota_exceeded` mapping unclear | Window = eligibility only (ADR-41); 400 / 403, never 429 (ADR-42) |
| Identity (D10, D11) | Pseudonym shared the `u_` prefix; case-sensitive repo uniqueness | `ps_` random pseudonyms (ADR-40); CONTRACT §11 uniqueness table, unique handles (ADR-35, E21) |
| Client shape (D1, D2, D4, D13, C5, C8) | One crate; `ed25519-dalek`; `lp` widths implicit; OpenAI adapter in Phase 2; fresh Gateway port per start; inner payload field names | Three crates + `moochy-keylog` (ADR-36); `ed25519-zebra`; explicit widths; OpenAI in Phase 1; port persisted at first run; CONTRACT §4 payload, whole JSON zstd-compressed |
| Relay and ops (C6, D15, D16) | `moochy-relay` binary; no metrics/config/autocert/read-only flags; Tessera | `relay`; optional `--config`, `--metrics-addr`, `--autocert-domain`, `--read-only`; `x/mod` tlog + note with own tiles (ADR-39) |
| Web (C10, C11, C12, D17) | Tailwind; native model ids in the UI; mixed SSE cadences | Hand-written CSS within the CONTRACT §9 budgets; public slugs first; 250 ms coalescing for audit, pool, and station, goal ≤ 1/30 s, rankings ≤ 1/60 s |
| Scope (D12, D14) | Failover, cancel, chaos, tamper/replay/injection, tool gating, throughput, budgets in later phases; key log deferred | E01–E22 due now ([11 §6](11-roadmap-and-testing.md)); key log in scope now, relay-asserted membership only under `MOOCHY_INSECURE_DEV=1` (ADR-38) |

The same day the product owner also changed the source boundary (revised ADR-01, CONTRACT §0a): the client, `spec/proto`, vectors, the public protocol spec, and guides are Apache-2.0 with DCO (`moochy-cli`); the relay, web, e2e, and internal docs are proprietary (`moochy-core`); self-hosting the relay is not offered. The plan's trust argument no longer relies on self-hosting: everything that touches keys, code, and cryptography runs in the open client, and the relay only sees ciphertext plus routing and accounting metadata.

**Result:** plans 00–13 rewritten in place with an "Updated 2026-10-01" banner each; no section renumbered; past review entries kept as history with "superseded by" notes.
