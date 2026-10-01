# 10 — Operations

> How the Relay is deployed, upgraded without dropping streams, observed, backed up, scaled, and recovered. Includes SLOs, alerts, runbooks, and a cost estimate.

---

## 1. Environments

| Env | Purpose | Shape |
|---|---|---|
| `dev` | Local development | Relay + fake providers + N simulated Nodes in one test harness command |
| `staging` | Pre-release, real providers with test keys and tiny budgets | Same binary and topology as prod, smaller VM |
| `prod` | Production | One VM, one binary, one SQLite file, Litestream sidecar |

The **same artifact** is promoted from staging to prod; there are no environment-specific builds.

---

## 2. Production deployment

- **Host**: one VM with NVMe storage (start: 4 vCPU / 8 GB RAM; that already covers the design point in [02 §12](02-architecture-overview.md)). Choose the region nearest the largest group of early donors and maintainers (likely EU-central or US-east); revisit using the latency telemetry in §5.
- **Process supervision**: one systemd unit; restarts use the drain-and-restart procedure (§3).
- **Self-hosting uses the same recipe.** The public instance runs exactly the open-source binary and the `deploy/` files from the monorepo. A community or company relay is the same binary with its own domain, OAuth app, and signing keys.
- **TLS**: ACME autocert inside the process (certificates cached on disk). No reverse proxy.
- **Optional CDN** in front of `/log/tile/*`, `/static/*`, and `/p/*/badge.svg` only. Those paths are immutable or short-TTL. Nodes' WebSockets and SSE go straight to the origin.
- **Secrets**: log and catalog signing keys loaded at boot from an encrypted file (passphrase via systemd credentials) or a cloud KMS; OAuth client secrets via systemd credentials. Never in the environment of child processes, never in logs.
- **Configuration**: one TOML file plus flags; every value has a documented default; the effective configuration is printed at boot (secrets redacted).

---

## 3. Upgrades: drain and restart (v1)

A single cheap VM does not justify blue/green machinery yet. The v1 procedure is short, has one writer at all times, and relies on mechanisms that already exist (outboxes, provider-native retryable errors):

1. **Drain** (≤ 30 s): send `relay.draining`; the Scheduler stops assigning; new submits get a retryable error; tasks that have not started are failed (retryable) and their Workers cancelled; started streams get up to 30 s to finish.
2. **Restart**: flush the writer, exit, start the new binary, run migrations ([09 §6](09-data-model.md)), load state, apply missed period rollovers, accept connections.
3. **Recover**: Gateways reconnect immediately and Workers with jitter (0–10 s). Workers send `worker.known_tasks` and replay outboxes. Streams cut at the restart reached clients as native retryable errors, so agents retry on their own.

**Exit criterion for this procedure:** at most ~10 s of retryable errors per upgrade, and zero ledger drift. Deploys are infrequent (scheduled, typically weekly).

**When to build zero-downtime blue/green:** when `tasks_total{status="failed", cause="deploy"}` becomes a visible share of failures. The design is already worked out: `SO_REUSEPORT` instances, make-before-break Node connections, the old process failing all non-started tasks at handoff and then forwarding only, settlement in the new process via outbox replay, and Gateways reconnecting at once while Workers are jittered.

---

## 4. Backups and disaster recovery

| Scenario | RPO | RTO | Procedure |
|---|---|---|---|
| Process crash | 0 (`synchronous=FULL`; receipts acked only after commit) | < 10 s (systemd restart) | Automatic |
| VM loss | ~1 s of DB; 0 for spend (Workers keep acked receipts 7 days and answer `receipt.replay_since`) | < 30 min | Provision VM → Litestream restore → boot → `replay_since` to all Workers → Nodes reconnect |
| Disk corruption | ~1 s | < 30 min | Same as VM loss |
| Region outage | ~1 s | < 1 h | Restore into another region; update DNS (low TTL on the relay hostname) |
| Log signing key compromise | — | hours | Runbook R6 |

**Monthly restore drill**, automated ([09 §7](09-data-model.md)).

---

## 5. Observability

### 5.1 Metrics (Prometheus format on a private port)

| Area | Metric | Why it matters |
|---|---|---|
| Latency | `relay_added_latency_ms` (histogram): last body frame received → first response byte forwarded, **minus** the Worker-reported provider time-to-first-token | The latency the Relay path adds, measured honestly |
| | `gateway_overhead_ms` (opt-in Node telemetry): end-to-end Moochy overhead seen by the Gateway, including upload | What maintainers feel |
| | `scheduler_apply_us` by event type | Ceiling watch ([04 §11](04-routing-engine.md)) |
| | `ack_latency_ms`, `start_latency_ms` | Worker health |
| Reliability | `tasks_total` by final status; `failovers_total` by NACK code; `routing_deadline_exceeded_total` | Pool health |
| Capacity | `workers_online` by model; `slots_free_total`; `pool_headroom_uusd` by repo | Supply |
| Money | `reserved_uusd_total`, `settled_uusd_total`, `pessimistic_settlements_total`, `audit_drift_uusd` (must be 0) | Ledger correctness |
| Cache | `cache_read_ratio` (cache-read tokens ÷ total input) by repo; `affinity_hit_ratio` | The biggest cost lever ([04 §5](04-routing-engine.md)) |
| Upload | `request_bytes_sealed` (histogram) | Trigger for building delta transfer ([03 §9](03-wire-protocol.md)) |
| Log | `key_log_size`, `checkpoint_age_s`, `anchor_lag_s` (checkpoint → public Git anchor) | Transparency health |
| Edge | `ws_connections`, `ws_writer_queue_overflow_total`, `sse_subscribers`, `sse_dropped_total` | Backpressure |
| Store | `commit_latency_ms`, `group_commit_batch_size`, `wal_size_bytes`, `litestream_lag_s` | Durability |
| Security | `firewall_rejections_total` by field name (from Worker telemetry), `route_mismatch_total`, `bad_envelope_total`, `unknown_key_alerts_total` | Abuse and tampering signals |

### 5.2 Logs and traces

- Structured logs (`log/slog`, JSON) with `task_id`, `repo_id`, and `device_id` on every task-scoped line. **Never** content, never secrets (enforced by type: content is opaque bytes and has no string formatter).
- Optional OpenTelemetry traces for task lifecycles (sampled 1%) in staging and prod.
- Nodes send **opt-in** anonymous telemetry: version, OS, firewall rejection field names, latency histograms. Never content.

---

## 6. SLOs

| SLO | Target | Measured by |
|---|---|---|
| Relay availability (WS handshake + task acceptance) | 99.9% monthly | Synthetic probes from 3 regions every 30 s |
| Task success (excluding provider errors and maintainer cancels) | ≥ 99.5% | `tasks_total` |
| Relay-added latency p50 / p95 (same continent) | ≤ 60 ms / ≤ 150 ms | `relay_added_latency_ms` |
| Scheduler apply p99 | ≤ 50 µs | `scheduler_apply_us` |
| Receipt durability | 100% of donor-signed receipts settled within 24 h | Audit job + `pessimistic_settlements_total` |
| Ledger drift | 0 µ$ | Nightly audit |
| Checkpoint freshness | ≤ 2 min when the log grew | `checkpoint_age_s` |

---

## 7. Alerts (page vs ticket)

| Alert | Severity |
|---|---|
| `audit_drift_uusd != 0` | **Page** |
| Availability probe failing for 2 min | **Page** |
| `bad_envelope_total` spike or `unknown_key_alerts_total > 0` | **Page** (possible tampering or compromise) |
| `litestream_lag_s > 60` | Page |
| `checkpoint_age_s > 600` while the log grows | Ticket → page after 30 min |
| Failover rate > 5% for 15 min | Ticket |
| `scheduler_apply_us` p99 > 200 µs | Ticket |
| `ws_writer_queue_overflow_total` rising | Ticket |
| `firewall_rejections_total` for a new field name from > 50 distinct Workers | Ticket (a harness changed; review the allowlist) |

---

## 8. Runbooks (outline)

| ID | Situation | First actions |
|---|---|---|
| R1 | Relay down | Check systemd status / disk / certificates → restart → if the VM is gone: DR restore (§4) → post status update |
| R2 | Ledger drift detected | Freeze affected pledges (pause new reservations) → diff receipts vs balances → identify cause (bug, partial migration, duplicate settle) → correction entries → postmortem |
| R3 | Mass Worker disconnect | Check egress and network → check `relay.draining` misfire → check a provider-wide outage (Workers NACK `provider_error`) → status page |
| R4 | Provider outage | Pools for that provider go empty → Gateways return native overloaded errors → nothing to fix on our side; communicate |
| R5 | Abuse report (malicious output) | Verify the evidence bundle ([06 §9](06-security-and-trust.md)) → suspend the donor's devices → log the `MODERATION` entry → notify the affected repo |
| R6 | Log key compromise | Rotate: generate a new key offline → publish a transition checkpoint co-signed by the old and new keys (if still possible), anchored in the public Git repository → announce → Nodes pin the new key via a signed release |
| R7 | Database grows fast | Check retention job → check for task-row floods (abuse) → archive receipts older than 13 months to object storage ([09 §8](09-data-model.md)) |
| R8 | Firewall bypass reported | Ship a client release with a tighter allowlist → raise `min_client_version` → notify donors |

---

## 9. Scaling path (only when metrics demand it)

1. **Vertical**: a bigger VM. Covers far more than the first year's realistic load.
2. **Split web from relay**: run the web/SSE handlers as a second process reading the same SQLite (WAL readers) and receiving Scheduler events over a local socket.
3. **Regional edges**: thin Edge processes in other regions terminate Node connections near users and forward frames to the central Scheduler over a persistent link. This cuts the network part of the added latency for far-away users without splitting state.
4. **Shard by repo** ([02 §12](02-architecture-overview.md)): multiple Scheduler+SQLite shards; global users/devices/key log replicated; Workers connect to the shards their pledges live on.

Each step is triggered by a specific metric crossing a threshold. None is built ahead of need.

---

## 10. Cost estimate (infrastructure only)

| Item | Early stage (≤ 100k tasks/month) | Growth (≈ 1M tasks/month) |
|---|---|---|
| VM | ~$20–40/month | ~$60–120/month |
| Object storage (Litestream) | < $5 | ~$10 |
| Egress (zstd-compressed request ~75 KB + response ~10 KB per task) | negligible | ~85 GB/month → within typical VPS transfer allowances |
| CDN (tiles, badges) | free tier | free tier or a few dollars |
| Domain, email, monitoring probes | ~$10 | ~$20 |
| **Total** | **≈ $40–60/month** | **≈ $100–180/month** |

Compression before sealing cuts egress 3–5×. Prefix-delta transfer ([03 §9](03-wire-protocol.md)) would cut it by roughly another order of magnitude and stays designed but deferred until egress or upload latency justifies it.

### 10.1 Keeping it 100% free

The design keeps the public instance cheap enough to run on sponsorship alone:

- **No fees, ever**: no commission on donated compute, no paid tier, no feature gating. This is a project principle ([01 §3](01-vision-scope-and-draft-review.md)), not a launch promotion.
- **Funding**: open sponsorship (GitHub Sponsors / Open Collective) with a **public monthly cost page** (`/open`) listing every line item above and who covers it. The expected total (≈ $40–180/month) is within reach of a handful of sponsors.
- **The expensive part is decentralized**: the costly resource (LLM compute) is never paid by Moochy. Donors pay their providers directly. Moochy only pays for a small relay.
- **If the public instance ever disappeared**, anyone could self-host the same binary. Pools are portable: Nodes switch relay with one config value, and every receipt history is in the public log mirrors.

---

## 11. Admin tooling (minimal)

- `/admin` (operator devices only): user / device / pledge lookup by id or pseudonym, suspend/unsuspend, moderation queue, catalog publishing (two-person approval), feature flags.
- `relay admin …` subcommands for the same operations from the VM shell (for when the web is down).
- Every admin action produces an internal audit-log row, and publicly visible actions (catalog, moderation) also produce a transparency-log entry.
