# 10 — Operations

> How the Relay is deployed, upgraded without dropping streams, observed, backed up, scaled, and recovered. Includes SLOs, alerts, runbooks, and a cost estimate.

> **Updated 2026-10-01:** aligned with `spec/CONTRACT.md` §0, §0a, §6, §12–§14 and ADR-33/34. Changes: Nodes connect over gRPC `NodeLink` on a separate `--grpc-addr` listener (TLS 1.3, h2, keepalive 15 s; drain = `Draining` + HTTP/2 GOAWAY) instead of WebSockets (ADR-33, C2); relay binary is `relay` (C6); optional flags `--config`, `--metrics-addr`, `--autocert-domain`, `--read-only` (D15); operator commands are `relay admin …` over `RelayAdmin` on the 0600 `--admin-socket`, never the network; self-hosting the relay is not offered and the relay/web are closed source while the client is open source (CONTRACT §0a); responsiveness budgets (CONTRACT §13, E22) and adaptive group commit (ADR-34) enter the SLOs; ops artifacts (`deploy/`, `docs/ops/`, `relay/internal/metrics/`) belong to mo-ops (§12).

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
- **Process supervision**: one systemd unit running the `relay` binary (`relay serve --config /etc/moochy/relay.toml …`); restarts use the drain-and-restart procedure (§3). The unit file and the rest of the deploy recipe live in `deploy/` (mo-ops, §12).
- **Two listeners** (CONTRACT §6): `--addr` serves HTTP (web pages, SSE, OAuth callbacks, badges, log tiles); `--grpc-addr` serves the gRPC `moochy.v1.NodeLink` service that every Node connects to. NodeLink is TLS 1.3 only, ALPN `h2`, with server keepalive pings every 15 s (2 missed = dead) and the HTTP/2 hardening of CONTRACT §12 (stream caps, Rapid-Reset and CONTINUATION limits, per-IP connection caps). A separate listener keeps grpc-go's native HTTP/2 server and its hardening instead of multiplexing gRPC through `net/http`.
- **Admin socket**: `--admin-socket` is a 0600 Unix socket serving `moochy.v1.RelayAdmin`. It is never bound to a network address (§11).
- **One operator.** moochy.dev runs the only relay. Self-hosting the relay is **not offered**: the relay and web are closed source (CONTRACT §0a) and the deploy recipe is internal. The Node's relay URL (`moochy login --relay …`) stays configurable for development and tests only (local `relay serve --dev`, staging). Users do not need to trust the relay for confidentiality or caps: everything that touches keys, code and cryptography runs in the open-source client, the relay only sees ciphertext plus the route header and accounting metadata, and owner-signed approvals, the key log, Worker local caps and provider spend limits bound the rest ([06](06-security-and-trust.md)).
- **TLS**: ACME autocert inside the process (`--autocert-domain`, certificates cached on disk), used by both listeners. No reverse proxy.
- **Optional CDN** in front of `/log/tile/*`, `/static/*`, and `/p/*/badge.svg` only. Those paths are immutable or short-TTL. NodeLink gRPC connections (the `--grpc-addr` listener) and SSE go straight to the origin: both are long-lived and latency-sensitive, and a CDN in the NodeLink path would terminate TLS and break channel binding.
- **Secrets**: log and catalog signing keys loaded at boot from an encrypted file (passphrase via systemd credentials) or a cloud KMS; OAuth client secrets via systemd credentials. Never in the environment of child processes, never in logs.
- **Configuration**: one TOML file (`--config <toml>`) plus flags, flags winning; every value has a documented default; the effective configuration is printed at boot (secrets redacted). Readiness is the one JSON line `{"event":"ready","addr":…,"grpc_addr":…}` on stdout (CONTRACT §6), which the unit and the restore drill wait for.

---

## 3. Upgrades: drain and restart (v1)

A single cheap VM does not justify blue/green machinery yet. The v1 procedure is short, has one writer at all times, and relies on mechanisms that already exist (outboxes, provider-native retryable errors):

1. **Drain** (≤ 30 s, started with `relay admin drain`): send `Draining{reconnect_after_ms}` on every `Session` stream and an HTTP/2 GOAWAY on every NodeLink connection, so no new streams open while in-flight ones continue; the Scheduler stops assigning; new submits get a retryable error; tasks that have not started are failed (retryable) and their Workers cancelled; started streams get up to 30 s to finish.
2. **Restart**: flush the writer, exit, start the new binary, run migrations ([09 §6](09-data-model.md)), load state, apply missed period rollovers, accept connections.
3. **Recover**: Gateways reconnect immediately and Workers with jitter (0–10 s). Workers send `KnownTasks` and replay outboxes. Streams cut at the restart reached clients as native retryable errors, so agents retry on their own.

**Exit criterion for this procedure:** at most ~10 s of retryable errors per upgrade, and zero ledger drift. Deploys are infrequent (scheduled, typically weekly).

**When to build zero-downtime blue/green:** when `tasks_total{status="failed", cause="deploy"}` becomes a visible share of failures. The design is already worked out: `SO_REUSEPORT` instances, make-before-break Node connections, the old process failing all non-started tasks at handoff and then forwarding only, settlement in the new process via outbox replay, and Gateways reconnecting at once while Workers are jittered.

---

## 4. Backups and disaster recovery

| Scenario | RPO | RTO | Procedure |
|---|---|---|---|
| Process crash | 0 (`synchronous=FULL`; receipts acked only after commit) | < 10 s (systemd restart) | Automatic |
| VM loss | ~1 s of DB; 0 for spend (Workers keep acked receipts 7 days and answer `ReceiptReplaySince`) | < 30 min | Provision VM → Litestream restore → boot → `ReceiptReplaySince` to all Workers → Nodes reconnect |
| Disk corruption | ~1 s | < 30 min | Same as VM loss |
| Region outage | ~1 s | < 1 h | Restore into another region; update DNS (low TTL on the relay hostname) |
| Log signing key compromise | — | hours | Runbook R6 |

**Monthly restore drill**, automated ([09 §7](09-data-model.md)): restore into a scratch VM and boot with `relay serve --read-only`, so the drill only reads (audit job, key-log root vs public anchor) and can never write to the restored copy. The drill script is in `deploy/` (mo-ops).

---

## 5. Observability

### 5.1 Metrics (Prometheus format on a private port)

Served on `--metrics-addr` (loopback by default; never on the public listeners). The registry and the authoritative metric names live in `relay/internal/metrics/` (mo-ops); the table below is the design intent.

| Area | Metric | Why it matters |
|---|---|---|
| Latency | `relay_added_latency_ms` (histogram): last body chunk received → first response byte forwarded, **minus** the Worker-reported provider time-to-first-token | The latency the Relay path adds, measured honestly |
| | `gateway_overhead_ms` (opt-in Node telemetry): end-to-end Moochy overhead seen by the Gateway, including upload | What maintainers feel |
| | `scheduler_apply_us` by event type | Ceiling watch ([04 §11](04-routing-engine.md)) |
| | `submit_to_assign_ms` (Submit received → `Assign` sent, includes the durable reservation) | CONTRACT §13 budget ≤ 2 ms p50 / ≤ 8 ms p99 |
| | `chunk_forward_us` (Relay part of provider byte → client byte) | CONTRACT §13 per-chunk budget |
| | `ack_latency_ms`, `start_latency_ms` | Worker health |
| Reliability | `tasks_total` by final status; `failovers_total` by NACK code; `routing_deadline_exceeded_total` | Pool health |
| Capacity | `workers_online` by model; `slots_free_total`; `pool_headroom_uusd` by repo | Supply |
| Money | `reserved_uusd_total`, `settled_uusd_total`, `pessimistic_settlements_total`, `audit_drift_uusd` (must be 0) | Ledger correctness |
| Cache | `cache_read_ratio` (cache-read tokens ÷ total input) by repo; `affinity_hit_ratio` | The biggest cost lever ([04 §5](04-routing-engine.md)) |
| Upload | `request_bytes_sealed` (histogram) | Trigger for building delta transfer ([03 §9](03-wire-protocol.md)) |
| Log | `key_log_size`, `checkpoint_age_s`, `anchor_lag_s` (checkpoint → public Git anchor) | Transparency health |
| Edge | `grpc_connections`, `grpc_streams_open` by method, `grpc_stream_send_queue_overflow_total`, `grpc_rapid_reset_rejections_total`, `sse_subscribers`, `sse_dropped_total` | Backpressure and HTTP/2 abuse |
| Store | `commit_latency_ms`, `group_commit_batch_size`, `wal_size_bytes`, `litestream_lag_s` | Durability. With adaptive group commit (ADR-34) the batch size is 1 when idle and grows only while a commit is in flight; a rising batch size with flat commit latency is healthy, rising commit latency is not |
| Security | `firewall_rejections_total` by field name (from Worker telemetry), `route_mismatch_total`, `bad_envelope_total`, `unknown_key_alerts_total` | Abuse and tampering signals |

### 5.2 Logs and traces

- Structured logs (`log/slog`, JSON) with `task_id`, `repo_id`, and `device_id` on every task-scoped line. **Never** content, never secrets (enforced by type: content is opaque bytes and has no string formatter).
- Optional OpenTelemetry traces for task lifecycles (sampled 1%) in staging and prod.
- Nodes send **opt-in** anonymous telemetry: version, OS, firewall rejection field names, latency histograms. Never content.

---

## 6. SLOs

| SLO | Target | Measured by |
|---|---|---|
| Relay availability (NodeLink `Session` handshake Hello→Welcome + task acceptance) | 99.9% monthly | Synthetic probes from 3 regions every 30 s |
| Responsiveness budgets (CONTRACT §13) | Every p50/p99 row met | E22 on the dev box gates every release; in prod, `submit_to_assign_ms`, `chunk_forward_us` and web TTFB are tracked against the same numbers |
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
| `grpc_stream_send_queue_overflow_total` rising | Ticket |
| `submit_to_assign_ms` p99 > 8 ms for 15 min | Ticket (CONTRACT §13 budget) |
| `firewall_rejections_total` for a new field name from > 50 distinct Workers | Ticket (a harness changed; review the allowlist) |

---

## 8. Runbooks (outline)

| ID | Situation | First actions |
|---|---|---|
| R1 | Relay down | Check systemd status / disk / certificates → restart → if the VM is gone: DR restore (§4) → post status update |
| R2 | Ledger drift detected | Freeze affected pledges (pause new reservations) → diff receipts vs balances → identify cause (bug, partial migration, duplicate settle) → correction entries → postmortem |
| R3 | Mass Worker disconnect | Check egress and network → check a `Draining` misfire → check a provider-wide outage (Workers NACK `provider_error`) → status page |
| R4 | Provider outage | Pools for that provider go empty → Gateways return native overloaded errors → nothing to fix on our side; communicate |
| R5 | Abuse report (malicious output) | Verify the evidence bundle ([06 §9](06-security-and-trust.md)) → suspend the donor's devices → log the `MODERATION` entry → notify the affected repo |
| R6 | Log key compromise | Rotate: generate a new key offline → publish a transition checkpoint co-signed by the old and new keys (if still possible), anchored in the public Git repository → announce → Nodes pin the new key via a signed release |
| R7 | Database grows fast | Check retention job → check for task-row floods (abuse) → archive receipts older than 13 months to object storage ([09 §8](09-data-model.md)) |
| R8 | Firewall bypass reported | Ship a client release with a tighter allowlist → raise `min_client_version` → notify donors |

---

## 9. Scaling path (only when metrics demand it)

1. **Vertical**: a bigger VM. Covers far more than the first year's realistic load.
2. **Split web from relay**: run the web/SSE handlers as a second process reading the same SQLite (WAL readers) and receiving Scheduler events over a local socket.
3. **Regional edges**: thin Edge processes in other regions terminate NodeLink connections near users (TLS, channel binding, auth) and forward stream messages to the central Scheduler over a gRPC link that reuses the `NodeLink` messages (CONTRACT §12), so an Edge adds no new protocol. This cuts the network part of the added latency for far-away users without splitting state.
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
- **Funding**: sponsorship (GitHub Sponsors / Open Collective) with a **public monthly cost page** (`/open`) listing every line item above and who covers it. The expected total (≈ $40–180/month) is within reach of a handful of sponsors.
- **Public wording**: "Open-source client (Apache-2.0) · 100% free". The client is open source; the relay and web are not (CONTRACT §0a), and nothing should call them open source.
- **The expensive part is decentralized**: the costly resource (LLM compute) is never paid by Moochy. Donors pay their providers directly. Moochy only pays for a small relay.
- **If the public instance ever went away**, nothing donors own would be exposed or lost: their provider keys never left their machines, their spend was bounded by their own provider limits, and the key log is mirrored by every Node and anchored in a public Git repository. Self-hosted relays are not offered as a fallback.

---

## 11. Admin tooling (minimal)

- `/admin` (operator devices only): user / device / pledge lookup by id or pseudonym, suspend/unsuspend, moderation queue, catalog publishing (two-person approval), feature flags.
- `relay admin …` subcommands for the same operations from the VM shell (for when the web is down): suspend, catalog publish, drain, state. They talk gRPC `moochy.v1.RelayAdmin` over the 0600 Unix socket given by `--admin-socket`; access is local file permission on the VM, and the service is **never** exposed on a network listener.
- Every admin action produces an internal audit-log row, and publicly visible actions (catalog, moderation) also produce a transparency-log entry.

---

## 12. Operational artifacts and ownership

This plan explains why; the artifacts that implement it are owned by mo-ops (CONTRACT §0) and are internal (closed source, CONTRACT §0a):

| Artifact | Path |
|---|---|
| Prometheus registry, metric names, SLO and alert rules | `relay/internal/metrics/` |
| systemd units, Litestream config, deploy recipe, backup/restore drill script | `deploy/` |
| Runbooks (R1–R8 in full), drain-and-restart procedure | `docs/ops/` |

Client release tooling (`deploy/client/`) is the exception: it ships with the open-source client.
