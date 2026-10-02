# SLOs (internal)

Plan 10 §6 targets with their exact measurement. Recording rules and alerts: `deploy/relay/prometheus/alerts.yml` (tested by `alerts_test.yml`); dashboard: `deploy/relay/grafana/moochy-relay.json`; metric definitions: `relay/internal/metrics/defs.go`.

| SLO | Target | Measured by (PromQL / source) | Window | Alert |
|---|---|---|---|---|
| Relay availability (TLS 1.3 + h2 handshake and `grpc.health.v1` on NodeLink) | 99.9% | `avg_over_time(moochy:availability:probe_avg[30d])`; blackbox `moochy_grpc_health` from 3 regions every 30 s | calendar month (43 min budget) | `RelayUnavailable` (majority of regions down 2 min) |
| Task success, excluding provider errors and maintainer cancels | ≥ 99.5% | `moochy:task_success:ratio_rate1h` = settled ÷ (settled + failed with `cause` ∉ {provider, client}) | 30 days | ticket on the dashboard; deploy share via `tasks_total{cause="deploy"}` |
| Relay-added latency, same continent | p50 ≤ 60 ms, p95 ≤ 150 ms | `moochy:relay_added_latency_ms:p50_5m` / `p95_5m` (last request chunk → first response byte forwarded, minus Worker-reported provider TTFT) | 30 days | dashboard |
| Scheduler apply | p99 ≤ 50 µs | `moochy:scheduler_apply_us:p99_5m` | 7 days | `SchedulerApplySlow` (> 200 µs, 10 min) |
| Receipt durability | 100% of donor-signed receipts settled within 24 h | `receipts_unsettled_oldest_age_s` ≤ 86 400; `pessimistic_settlements_total` reviewed weekly | continuous | `ReceiptsUnsettled` |
| Ledger drift | 0 µ$ | `audit_drift_uusd` from the nightly audit (read-only connection); `audit_last_success_timestamp_s` fresh | every run | `LedgerDrift` (page), `AuditNotRunning` |
| Cache-read share of input tokens (cost lever, 01 §5.3) | ≥ 80% | `moochy:cache_read:ratio_rate1h` from `input_tokens_total{kind}`; affinity `moochy:affinity_hit:ratio_rate1h` | 7 days | `CacheReadRatioLow` (< 50% for 6 h) |
| Checkpoint freshness | ≤ 2 min when the log grew | `checkpoint_age_s` while `changes(key_log_size[30m]) > 0` | continuous | `CheckpointStale` (> 10 min, ticket), `CheckpointStalePage` (40 min) |

## Responsiveness budgets (CONTRACT §13)

E22 is the release gate (dev box, instant fake provider). In production the relay-side rows are tracked continuously:

| Path | Budget p50 / p99 | Production metric | Alert |
|---|---|---|---|
| Relay: Submit → Assign (incl. durable reservation) | 2 ms / 8 ms | `submit_to_assign_us` | `SubmitToAssignSlow` (p99 > 8 ms, 15 min) |
| Relay share of per-chunk forwarding | part of 300 µs / 1 ms | `chunk_forward_us` | dashboard |
| Group commit | sub-ms when idle (ADR-34) | `commit_latency_ms`, `group_commit_batch_size` | dashboard |
| Web TTFB `/`, `/p/{owner}/{repo}` | 30 ms / 80 ms | `web_ttfb_ms{route}` | dashboard |
| Live update after a task settles | ≤ 500 ms | `web_update_delay_ms` | dashboard |

Gateway and Worker rows are measured by E22 and by opt-in Node telemetry (`gateway_overhead_ms`).

## Durability objectives (plan 10 §4)

| Scenario | RPO | RTO | Proven by |
|---|---|---|---|
| Process crash | 0 | < 10 s (`Restart=always`, `RestartSec=1`) | E12 |
| VM loss / disk corruption | ≈ 1 s DB, 0 spend (`receipt.replay_since`) | < 30 min | monthly restore drill (`moochy_restore_drill_restore_seconds`), Phase 6 DR drill |
| Region outage | ≈ 1 s | < 1 h | DR drill into another region |

Worker health: `ack_latency_ms` / `start_latency_ms` (Assign → Ack / Started, Scheduler clock); `WorkerAckSlow` tickets at p95 > 250 ms (ack deadline 500 ms). Availability: the probe calls `grpc.health.v1.Health/Check` (server-wide status, service `""`), which the relay reports `NOT_SERVING` from the moment it drains; validated with blackbox_exporter 0.28 against a real relay (TLS 1.3, `SERVING`).

Replication health: `litestream_lag_s` is the time since Litestream last confirmed that every database synced (its heartbeat, every 60 s); alert at 150 s.

## Error budget policy

- Availability budget spent > 50% before day 15 → freeze non-security deploys for the rest of the month.
- Any ledger drift or unsettled receipt older than 24 h → incident and postmortem, regardless of budget.
- Deploy-caused failures (`tasks_total{status="failed",cause="deploy"}`) above 1% of monthly failures → build the blue/green path designed in plan 10 §3.
