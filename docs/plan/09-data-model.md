# 09 — Data Model (SQLite)

> Tables described as column tables (no SQL yet), with keys, constraints, indexes, write paths, retention, migrations, backups, and size estimates. Replaces the draft's `schema.sql`.

---

## 1. Changes from the draft schema

| Draft | Problem | New design |
|---|---|---|
| `users.public_key` | One key per user; no devices, rotation, or revocation | `devices` table (many per user, revocable, logged) |
| `users.provider`, `provider_id` on the user row | One identity provider per user | `identities` table (GitHub and GitLab can link to one user) |
| `repositories.mcp_secret` (plaintext, UNIQUE) | Database leak = every repo's credential leaked | Removed. Nodes authenticate with device signatures; no shared secrets stored |
| `target_token_goal` in tokens | Tokens are not comparable across models | `goal_uusd_month` in µ$ |
| `token_pledges.amount_*` updated in place, no history | No per-period history, no audit trail | `pledges` (current period) + `pledge_periods` (history) + receipts as the source of truth |
| `audit_logs` with one `signature` and `tokens_used` | One token number; no attempt, no projection, no dispute | `attempts` + `receipts` (exact signed bytes, usage breakdown, public projection, dispute) |
| No tasks table | No failover, latency, or utilization analytics | `tasks` + `attempts` (metadata only, 90-day retention) |
| `DATETIME DEFAULT CURRENT_TIMESTAMP` strings | Timezone and parsing ambiguity | `INTEGER` Unix milliseconds everywhere |

---

## 2. Connection settings

| Pragma | Value | Why |
|---|---|---|
| `journal_mode` | `WAL` | Concurrent readers with one writer |
| `synchronous` | **`FULL`** | `receipt.ack` promises durability. With 10 ms group commit this is ≤ 100 fsyncs/s, which is cheap on NVMe |
| `foreign_keys` | `ON` | Integrity |
| `busy_timeout` | 5000 ms | Readers vs checkpoints |
| `temp_store` | `MEMORY` | — |
| `mmap_size` | 1 GiB | Read performance |
| `wal_autocheckpoint` | `0` | Litestream controls checkpoints (its recommended setting) |

**One writer connection**, owned by the Store writer goroutine. **A pool of read-only connections** (`mode=ro`) for web pages, the audit job, and log tile serving.

---

## 3. Tables

### 3.1 Identity

**`users`**
| Column | Type | Constraints / notes |
|---|---|---|
| `id` | TEXT | PK, ULID |
| `pseudonym` | TEXT | UNIQUE, random (`u_…`); the **only** user identifier in the public log and projections |
| `display_name` | TEXT | Nullable |
| `status` | TEXT | `active`, `suspended`, `deleted` |
| `created_at` | INTEGER | ms |

**`identities`**
| Column | Type | Constraints / notes |
|---|---|---|
| `user_id` | TEXT | FK users |
| `provider` | TEXT | `github` or `gitlab` |
| `provider_user_id` | TEXT | Stable numeric id from the provider |
| `username`, `avatar_url` | TEXT | Refreshed at login |
| `account_created_at` | INTEGER | From the provider (shown to owners when approving donors) |
| | | PK (`provider`, `provider_user_id`) |

**`devices`**
| Column | Type | Constraints / notes |
|---|---|---|
| `id` | TEXT | PK (`d_…`) |
| `user_id` | TEXT | FK users |
| `name` | TEXT | User-chosen |
| `sign_pub` | BLOB | 32 bytes, UNIQUE |
| `enc_pub` | BLOB | 32 bytes |
| `suite` | TEXT | Envelope suite id (bound into HPKE info) |
| `roles` | TEXT | `gateway`, `worker`, or both |
| `repo_scope` | TEXT | NULL = any repo the user may use; else one repo id (CI / headless agent devices) |
| `cap_uusd_month` | INTEGER | Optional consumption cap (headless agents); NULL = none |
| `key_log_index` | INTEGER | Index of its `KEY_ADDED` entry |
| `created_at`, `revoked_at` | INTEGER | `revoked_at` NULL = active |

**`device_usage`** (only for capped devices): `device_id`, `month` (PK together), `spent_uusd`, `reserved_uusd`, with `CHECK (spent_uusd >= 0 AND reserved_uusd >= 0)`.

**`web_sessions`**: `id_hash` (PK, SHA-256 of the cookie value), `user_id`, `created_at`, `expires_at`.

**`device_codes`** (short-lived): `user_code` (PK), `device_code_hash`, `sign_pub`, `enc_pub`, `requested_roles`, `requested_scope`, `approved_by`, `expires_at`.

### 3.2 Repositories, approvals, and membership

**`repos`**
| Column | Type | Constraints / notes |
|---|---|---|
| `id` | TEXT | PK (`r_…`) |
| `provider`, `provider_repo_id` | TEXT | UNIQUE together (stable across renames) |
| `owner`, `name` | TEXT | Current slug; UNIQUE (`provider`, `owner`, `name`) |
| `claimed_by` | TEXT | FK users |
| `claim_log_index` | INTEGER | Owner-signed `REPO_CLAIMED` entry |
| `goal_uusd_month` | INTEGER | ≥ 0 |
| `default_model` | TEXT | Public model id used when a delegate call names none |
| `description` | TEXT | "What we use compute for" |
| `settings` | TEXT (JSON) | Auto-caching, tripwire mode, member default cap, pinned donors |
| `status` | TEXT | `active`, `archived` |

**`members`**
| Column | Type | Constraints / notes |
|---|---|---|
| `repo_id`, `user_id` | TEXT | PK together |
| `role` | TEXT | `owner`, `member` |
| `log_index` | INTEGER | Owner-signed `MEMBER_ADDED` entry (NULL for the owner) |
| `cap_uusd_month` | INTEGER | NULL = unlimited |
| `spent_uusd`, `reserved_uusd`, `month` | INTEGER | Current calendar month; `CHECK (spent_uusd >= 0 AND reserved_uusd >= 0)` |
| `removed_at` | INTEGER | Set by an owner-signed `MEMBER_REMOVED` |

**`member_months`**: `repo_id`, `user_id`, `month` (PK together), `spent_uusd`. History used for start-period attribution and the audit.

### 3.3 Pledges

**`pledges`**
| Column | Type | Constraints / notes |
|---|---|---|
| `id` | TEXT | PK (`p_…`) |
| `donor_id`, `repo_id` | TEXT | FKs |
| `status` | TEXT | `pending`, `active`, `paused`, `ended`, `declined` |
| `approval_log_index` | INTEGER | Owner-signed `DONOR_APPROVED` entry (NULL while pending) |
| `budget_uusd` | INTEGER | Per period, ≥ 0 |
| `per_task_cap_uusd` | INTEGER | > 0, default 5,000,000 |
| `policy` | TEXT (JSON) | `{models[], max_effort, dialects[], flags[], max_slots?, schedule?}` |
| `visibility` | TEXT | `public`, `pseudonymous`, `anonymous` |
| `rollover` | INTEGER | 0/1 |
| `period_anchor_day` | INTEGER | 1–28 |
| `period_start` | INTEGER | ms; current period |
| `spent_uusd`, `reserved_uusd` | INTEGER | Current period; `CHECK (spent_uusd >= 0 AND reserved_uusd >= 0)` |
| `created_at`, `ended_at` | INTEGER | — |
| | | Partial UNIQUE (`donor_id`, `repo_id`) WHERE `status IN ('pending','active','paused')` |

**`pledge_periods`**: `pledge_id`, `period_start` (PK together), `budget_uusd`, `spent_uusd`, `tasks`, `closed_at`. Closed periods still receive settlements of attempts that **started** in them ([05 §9](05-ledger-and-accounting.md)).

### 3.4 Tasks, attempts, and receipts

**`tasks`** (metadata only; never content)
| Column | Type | Notes |
|---|---|---|
| `gateway_device`, `id` | TEXT | PK together (dedupe scope); `id` is the Gateway's ULID |
| `repo_id`, `member_id` | TEXT | — |
| `dialect`, `model`, `effort`, `max_tokens`, `est_input`, `body_bytes` | — | Route facts |
| `status` | TEXT | `routing`, `started`, `ended`, `failed`, `cancelled` |
| `fail_code` | TEXT | Final failure or policy code |
| `t_submit`, `t_end` | INTEGER | Relay clock |
| Index | | (`repo_id`, `t_submit`) |

**`attempts`**
| Column | Type | Notes |
|---|---|---|
| `task_id`, `attempt` | — | PK together |
| `gateway_device` | TEXT | — |
| `worker_device`, `pledge_id` | TEXT | — |
| `reserved_uusd`, `cost_uusd` | INTEGER | — |
| `catalog_version` | INTEGER | In effect at attempt start |
| `period_start` | INTEGER | Pledge period the attempt **started** in |
| `status` | TEXT | `committed`, `assigned`, `acked`, `started`, `superseded`, `awaiting_receipt`, `settled`, `released`, `orphaned`, `pessimistic` |
| `nack_code` | TEXT | — |
| `t_assign`, `t_ack`, `t_started`, `t_end` | INTEGER | Relay clock |
| Index | | (`pledge_id`, `period_start`); partial on `status IN ('awaiting_receipt','orphaned')` for the sweeps |

**`receipts`**
| Column | Type | Notes |
|---|---|---|
| `task_id`, `attempt` | — | PK together (idempotency key) |
| `body`, `donor_sig` | BLOB | Exact signed bytes + 64-byte signature |
| `projection`, `projection_sig` | BLOB | Public projection + signature |
| `receipt_ref` | TEXT | Random public id of the projection; UNIQUE |
| `dispute_code`, `dispute_sig` | — | NULL unless the Gateway disputed |
| `pledge_id`, `period_start` | — | For aggregation |
| `cost_uusd`, `input`, `output`, `cache_write_5m`, `cache_write_1h`, `cache_read`, `provider_cost_uusd` | INTEGER | Denormalized from `body` |
| `estimated` | INTEGER | 0/1 |
| `received_at` | INTEGER | — |
| Index | | (`pledge_id`, `period_start`); (`received_at`) for the public feed |

### 3.5 Key log

**`log_entries`**: `log` (`keys`; reserved: `receipts` for the post-beta receipt log), `idx` (PK together), `kind`, `body` (exact bytes), `sigs` (BLOB: one or more signatures), `created_at`.

**`log_hashes`**: `log`, `idx` (PK together), `hash` (32 bytes). Stored hashes for tiles and proofs.

**`checkpoints`**: `log`, `tree_size` (PK together), `root_hash`, `note` (signed note bytes), `anchored_at` (when committed to the public Git anchor), `created_at`.

Full tiles are immutable. They are computed on demand from `log_hashes` and cached in memory or on the CDN, never stored twice.

### 3.6 Catalog, aggregates, moderation

**`catalog`**: `version`, `model` (public slug), `provider` (PK together), `provider_model_id`, `dialects`, `in`, `out`, `cache_write_5m`, `cache_write_1h`, `cache_read`, `max_image_tokens`, `max_page_tokens`, `fast_multiplier`, `default_effort`, `max_output`, `native_aliases` (JSON), `source` (`curated` or `openrouter_import`), `effective_at`, `log_index`.

**`usage_daily`**: `day`, `repo_id`, `pledge_id`, `model` (PK together), `tasks`, `input`, `output`, `cache_read`, `cache_write`, `cost_uusd`, `cost_uncached_uusd` (for "saved by caching"), `failovers`, `p50_added_ms`, `p95_added_ms`. Rolled up hourly from `attempts` + `receipts`; kept forever (small).

**`reports`**: `id`, `task_id`, `reporter_id`, `kind`, `evidence` (BLOB, encrypted to the operator's moderation key), `status`, `decision`, timestamps.

**`strikes`**: `user_id`, `kind` (`route_mismatch`, `firewall`, `dispute_upheld`, …), `task_id`, `created_at`.

---

## 4. Write paths

| Producer | Operations | Batching |
|---|---|---|
| Scheduler | Task and attempt rows, reservations, releases, settlements (pledge, member, device, period rows) | **Group commit**: one transaction every 10 ms or 256 ops, each op in its own SAVEPOINT; the Scheduler is notified on the completion channel. **`task.assign` and `receipt.ack` are sent only after the commit returns** |
| Receipt intake | Insert receipt (+ projection), settle the attempt | Same group commit, atomic with the balance update |
| Disputes | Update `dispute_code` / `dispute_sig` | Group commit |
| Key-log appends | Device events, owner-signed approvals and memberships, repo claims, catalog versions, moderation | Group commit; checkpoint signed only after Litestream has replicated the tree size |
| Web handlers | Pledge drafts, repo settings, pending approval requests | Through the writer goroutine (request → reply), typically < 15 ms |
| Sweeps (every minute) | Pessimistic settlement of attempts awaiting a receipt > 24 h with an absent Worker; leaderboard finalization | Small transactions |
| Rollups | `usage_daily` | Hourly |
| Retention | Delete `tasks`/`attempts` older than 90 days (after rollup), expired sessions and device codes | Nightly, in small batches |

A constraint violation inside a SAVEPOINT is treated as a **fatal bug**: the process exits and restarts from the database, and the Worker outboxes replay. Memory and disk never silently diverge.

---

## 5. Read paths

| Reader | Query shape | Index used |
|---|---|---|
| Repo page | Aggregates for the current month; newest projections for the repo | `usage_daily` PK; `receipts(received_at)` filtered by the repo's pledges |
| Donor Station | Pledges by donor; balances | `pledges(donor_id)` |
| Console | Members, pending approvals, usage by member and model | `members` PK; `pledges(repo_id, status)`; `usage_daily` |
| Tile server | Hash ranges | `log_hashes` PK |
| Audit job | Σ receipts per pledge-period, member-month, device-month | `receipts(pledge_id, period_start)`, `attempts` |
| Boot | Active pledges, members, capped devices, open attempts | `pledges(status)`, partial index on open attempt statuses |

---

## 6. Migrations

- Embedded, numbered, **forward-only** migrations, each in its own transaction, run at boot **before the Relay accepts connections**. With drain-and-restart deploys ([10 §3](10-operations.md)) the previous process has already exited, so there is never a second writer during a migration.
- Each migration declares a `min_compatible_version`. A binary refuses to start only if the database requires a newer binary than itself, so rolling back to the previous release keeps working.
- Expand → migrate → contract across two releases. Long index builds run as a background step after boot, never inside the boot transaction.
- The test suite applies all migrations on an empty DB and on a snapshot from the previous release.

---

## 7. Backups and restore

- **Litestream** replicates the WAL continuously to S3-compatible storage (≈ 1 s RPO for the database). Snapshots daily, retention 30 days.
- **Spend has an effective RPO of 0.** Workers keep acknowledged receipts 7 days and replay them on `receipt.replay_since` after a restore ([05 §7](05-ledger-and-accounting.md)).
- **Checkpoints never get ahead of the replica**, so a restore never contradicts a published checkpoint.
- **Restore drill** monthly (automated): restore to a scratch VM, boot read-only, run the audit job, compare the key-log root with the published anchor.
- The **key log is mirrored by every Node** and anchored in a public Git repository. Losing the operator's copy would not lose the history.

---

## 8. Size estimates (per year, at 1M tasks/month)

| Table | Row size | Rows/year | Size |
|---|---|---|---|
| `tasks` + `attempts` (90-day window) | ~400 B | ~3.3M live | ~1.3 GB |
| `receipts` (incl. projection) | ~900 B | 12M | ~11 GB |
| Key log (`log_entries` + `log_hashes`) | ~400 B | ~100k | < 0.1 GB |
| `usage_daily` | ~150 B | ~2M | ~0.3 GB |
| Everything else | — | — | < 1 GB |

About 14 GB per year at that volume. One NVMe volume covers years.

> **Ceiling note:** past ~100M receipts, archive receipts older than 13 months to compressed files in object storage (the projections stay in the DB) before considering anything else.
