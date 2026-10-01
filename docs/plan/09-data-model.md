# 09 — Data Model (SQLite)

> Tables described as column tables, with keys, constraints, indexes, write paths, retention, migrations, backups, and size estimates. SQL is written out only for the uniqueness constraints (§9), because those are part of the contract. Replaces the draft's `schema.sql`.

> **Updated 2026-10-01:** aligned with `spec/CONTRACT.md` §1, §11, §13 and ADR-33/34. Changes: adaptive group commit replaces the 10 ms window (ADR-34, C1); `users.id` = `u_`+ULID (internal) and pseudonym = `ps_`+16 random base32, never derived from the id (D10); usernames, tombstones, rename tracking and every CONTRACT §11 uniqueness rule enforced by the database with SQL in §9 (D11, ADR-35); a closing schedule window never changes pledge status (C3); key-log tables built on `x/mod/sumdb/tlog` (D16); restore drills boot with `relay serve --read-only` (D15); message names follow the gRPC `NodeLink` (ADR-33).

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
| `synchronous` | **`FULL`** | `ReceiptAck` and `Assign` promise durability. Adaptive group commit (§4) keeps the fsync rate proportional to load: one fsync per commit, one commit in flight at a time, so a busy relay amortizes many ops per fsync and an idle one commits at once. Cheap on NVMe |
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
| `id` | TEXT | PK, `u_` + ULID. **Internal only**: never shown on a page, in the log, in a projection, or in a URL |
| `username` | TEXT | **Unique handle**, stored lowercase, `UNIQUE COLLATE NOCASE`, ASCII `^[a-z0-9](?:[a-z0-9-]{1,30}[a-z0-9])$` (3–32 chars, no `--`), reserved words and tombstoned handles refused (rules: `spec/CONTRACT.md` §11; SQL in §9) |
| `username_changed_at` | INTEGER | ms of the last rename (NULL = never renamed). A trigger refuses a second rename within 30 days (§9) |
| `pseudonym` | TEXT | UNIQUE, `ps_` + 16 random base32 chars, generated independently of `id` (never derived from it); the **only** user identifier in the public log and projections |
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
| | | PK (`provider`, `provider_user_id`); UNIQUE (`user_id`, `provider`): at most one identity per provider per user |

**`devices`**
| Column | Type | Constraints / notes |
|---|---|---|
| `id` | TEXT | PK (`d_…`) |
| `user_id` | TEXT | FK users |
| `name` | TEXT | User-chosen; UNIQUE per user, case-insensitive: (`user_id`, lower(`name`)) |
| `sign_pub` | BLOB | 32 bytes, UNIQUE |
| `enc_pub` | BLOB | 32 bytes |
| `suite` | TEXT | Envelope suite id (bound into HPKE info) |
| `roles` | TEXT | `gateway`, `worker`, or both |
| `repo_scope` | TEXT | NULL = any repo the user may use; else one repo id (CI / headless agent devices) |
| `cap_uusd_month` | INTEGER | Optional consumption cap (headless agents); NULL = none |
| `key_log_index` | INTEGER | Index of its `KEY_ADDED` entry |
| `created_at`, `revoked_at` | INTEGER | `revoked_at` NULL = active |

**`device_usage`** (only for capped devices): `device_id`, `month` (PK together), `spent_uusd`, `reserved_uusd`, with `CHECK (spent_uusd >= 0 AND reserved_uusd >= 0)`.

**`username_tombstones`**: `username` (PK, `COLLATE NOCASE`), `user_id`, `retired_at`, `redirect_until` (`retired_at` + 90 days). Written by a trigger whenever a username changes or an account is deleted (§9), so no code path can free a handle without tombstoning it. A handle that was ever used is never assigned again, to anyone (blocks username-recycling takeovers of links, badges and reputation). Until `redirect_until`, any page or link that resolves the old handle redirects to the user's current handle; after that they 404 but the handle stays retired.

**`web_sessions`**: `id_hash` (PK, SHA-256 of the cookie value), `user_id`, `created_at`, `expires_at`.

**`device_codes`** (short-lived): `user_code` (PK), `device_code_hash`, `sign_pub`, `enc_pub`, `requested_roles`, `requested_scope`, `approved_by`, `expires_at`.

### 3.2 Repositories, approvals, and membership

**`repos`**
| Column | Type | Constraints / notes |
|---|---|---|
| `id` | TEXT | PK (`r_…`) |
| `provider`, `provider_repo_id` | TEXT | UNIQUE together (stable across renames) |
| `owner`, `name` | TEXT | Current slug; UNIQUE (`provider`, lower(`owner`), lower(`name`)). Case-insensitive because GitHub and GitLab slugs are: `Foo/Bar` and `foo/bar` are the same repo and must not become two pools |
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
| `status` | TEXT | `pending`, `active`, `paused`, `ended`, `declined`. `paused` only by explicit donor action; a closed `schedule` window is an eligibility check at match time and never writes this column ([05 §4.2](05-ledger-and-accounting.md)) |
| `approval_log_index` | INTEGER | Owner-signed `DONOR_APPROVED` entry (NULL while pending) |
| `budget_uusd` | INTEGER | Per period, ≥ 0 |
| `per_task_cap_uusd` | INTEGER | > 0, default 5,000,000 |
| `policy` | TEXT (JSON) | `{models[], max_effort, dialects[], flags[], max_slots?, schedule?}`; `models` are public slugs |
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

The key log uses `golang.org/x/mod/sumdb/tlog` for hashing, inclusion and consistency proofs, `golang.org/x/mod/sumdb/note` for signed checkpoints, and our own C2SP tile path layer on top (D16; no Tessera). The tables below are just its storage: `tlog.StoredHashes` produces the `log_hashes` rows, and `tlog.TileHashReader` reads them back.

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
| Scheduler | Task and attempt rows, reservations, releases, settlements (pledge, member, device, period rows) | **Adaptive group commit** (ADR-34): when the writer is idle, an op is committed immediately; ops that arrive while a commit is in flight are batched (up to 256) into the next commit, which starts as soon as the previous one finishes. No timer ever delays an idle commit. Each op runs in its own SAVEPOINT; the Scheduler is notified on the completion channel. **`Assign` and `ReceiptAck` are sent only after the commit returns.** Budget: Submit→Assign ≤ 2 ms p50 / ≤ 8 ms p99 (CONTRACT §13, E22) |
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
- **Spend has an effective RPO of 0.** Workers keep acknowledged receipts 7 days and replay them on `ReceiptReplaySince` after a restore ([05 §7](05-ledger-and-accounting.md)).
- **Checkpoints never get ahead of the replica**, so a restore never contradicts a published checkpoint.
- **Restore drill** monthly (automated): restore to a scratch VM, boot with `relay serve --read-only` (opens the database `mode=ro`, runs no migrations, starts no writer, Scheduler, sweeps or NodeLink listener; web and audit reads only), run the audit job, compare the key-log root with the published anchor. Read-only boot guarantees the drill can never "repair" or append to a restored copy and hide a gap. The drill script lives with the ops artifacts (`deploy/`, `docs/ops/`, owned by mo-ops).
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

---

## 9. Uniqueness constraints (CONTRACT §11)

Every uniqueness rule of `spec/CONTRACT.md` §11 is **enforced by the database, not only by code**. Code validates first so users get a clear error; the constraint is the second guard that holds when code has a bug, two requests race, or someone edits the database by hand. A constraint violation inside the writer is a fatal bug (§4), so a race can never leave two rows behind.

| Thing | Unique key (CONTRACT §11) | Where it is enforced |
|---|---|---|
| User handle | `users.username` (case-insensitive) + `username_tombstones.username` | `users.username` `UNIQUE COLLATE NOCASE` + format `CHECK`; tombstone PK; triggers refuse tombstoned handles and write tombstones on rename/delete |
| User pseudonym (public log) | `users.pseudonym` | `UNIQUE` + format `CHECK` |
| Provider identity | (`provider`, `provider_user_id`); at most one identity per provider per user | `identities` PK + `UNIQUE (user_id, provider)` |
| Device signing key | `devices.sign_pub` | `UNIQUE` |
| Device name | (`user_id`, lower(`name`)) | Unique expression index |
| Repository | (`provider`, `provider_repo_id`) and (`provider`, lower(`owner`), lower(`name`)) | `UNIQUE` + unique expression index |
| Live pledge | (`donor_id`, `repo_id`) where status ∈ {pending, active, paused} | Partial unique index |
| Membership | (`repo_id`, `user_id`) | `members` PK |
| Local token | the random token itself (≥ 256-bit), stored hashed | **Node-side**, not in the relay database: the Node stores only SHA-256 of each `mooch_local_…` token, keyed by the hash, and compares with `subtle` ([06 §13](06-security-and-trust.md), [07 §4](07-client-cli.md)) |
| Task | (`gateway_device`, `task_id`) | `tasks` PK (`gateway_device`, `id`) |
| Receipt | (`task_id`, `attempt`); `receipt_ref` unique | `receipts` PK + `UNIQUE (receipt_ref)` |
| Web session | `id_hash` | `web_sessions` PK |

Reserved words (route segments, staff and system words) are checked in code with the shared vectors `spec/vectors/usernames.json`, identically in Go and Rust; they are not in a table because the list ships with the binary and changes with the route map. E21 exercises the duplicate, case-variant, reserved, confusable and tombstone cases end to end.

### 9.1 Identity

```sql
CREATE TABLE users (
  id                  TEXT PRIMARY KEY CHECK (id GLOB 'u_*' AND length(id) = 28),   -- 'u_' + ULID, internal
  username            TEXT NOT NULL UNIQUE COLLATE NOCASE
                      CHECK (username = lower(username)
                             AND length(username) BETWEEN 3 AND 32
                             AND username NOT GLOB '*[^a-z0-9-]*'
                             AND username NOT GLOB '-*' AND username NOT GLOB '*-'
                             AND instr(username, '--') = 0),
  username_changed_at INTEGER,                                                      -- ms, NULL = never renamed
  pseudonym           TEXT NOT NULL UNIQUE
                      CHECK (pseudonym GLOB 'ps_*' AND length(pseudonym) = 19),     -- 'ps_' + 16 random base32
  display_name        TEXT,
  status              TEXT NOT NULL CHECK (status IN ('active','suspended','deleted')),
  created_at          INTEGER NOT NULL
);

CREATE TABLE username_tombstones (
  username       TEXT PRIMARY KEY COLLATE NOCASE,
  user_id        TEXT NOT NULL REFERENCES users(id),
  retired_at     INTEGER NOT NULL,
  redirect_until INTEGER                                                            -- NULL = no redirect (deleted account)
);

-- A tombstoned handle is never assigned again, to anyone.
CREATE TRIGGER users_username_not_tombstoned_ins BEFORE INSERT ON users
WHEN EXISTS (SELECT 1 FROM username_tombstones t WHERE t.username = NEW.username)
BEGIN SELECT RAISE(ABORT, 'username_tombstoned'); END;

CREATE TRIGGER users_username_not_tombstoned_upd BEFORE UPDATE OF username ON users
WHEN NEW.username <> OLD.username
 AND EXISTS (SELECT 1 FROM username_tombstones t WHERE t.username = NEW.username)
BEGIN SELECT RAISE(ABORT, 'username_tombstoned'); END;

-- Rename at most once per 30 days; the caller sets username_changed_at = now.
CREATE TRIGGER users_rename_rate BEFORE UPDATE OF username ON users
WHEN NEW.username <> OLD.username
 AND (NEW.username_changed_at IS NULL
      OR (OLD.username_changed_at IS NOT NULL
          AND NEW.username_changed_at - OLD.username_changed_at < 30 * 86400000))
BEGIN SELECT RAISE(ABORT, 'rename_too_soon'); END;

-- The old handle becomes a permanent tombstone that redirects for 90 days.
CREATE TRIGGER users_rename_tombstone AFTER UPDATE OF username ON users
WHEN NEW.username <> OLD.username
BEGIN
  INSERT INTO username_tombstones (username, user_id, retired_at, redirect_until)
  VALUES (OLD.username, OLD.id, NEW.username_changed_at, NEW.username_changed_at + 90 * 86400000);
END;

-- Account deletion retires the handle too (no redirect).
CREATE TRIGGER users_delete_tombstone AFTER UPDATE OF status ON users
WHEN NEW.status = 'deleted' AND OLD.status <> 'deleted'
BEGIN
  INSERT OR IGNORE INTO username_tombstones (username, user_id, retired_at, redirect_until)
  VALUES (OLD.username, OLD.id, CAST(unixepoch('subsec') * 1000 AS INTEGER), NULL);
END;

CREATE TABLE identities (
  user_id            TEXT NOT NULL REFERENCES users(id),
  provider           TEXT NOT NULL CHECK (provider IN ('github','gitlab')),
  provider_user_id   TEXT NOT NULL,
  -- username, avatar_url, account_created_at …
  PRIMARY KEY (provider, provider_user_id),
  UNIQUE (user_id, provider)                                                        -- one identity per provider per user
);

-- devices: sign_pub BLOB NOT NULL UNIQUE CHECK (length(sign_pub) = 32)
CREATE UNIQUE INDEX devices_user_name ON devices (user_id, lower(name));

-- web_sessions: id_hash BLOB PRIMARY KEY  (SHA-256 of the cookie value; the cookie itself is never stored)
```

`lower()` is ASCII-only in SQLite, which is exactly right here: handles are ASCII by rule, and repo/device names compare case-insensitively the way GitHub and GitLab do for ASCII slugs.

### 9.2 Repositories, membership, pledges

```sql
-- repos
--   UNIQUE (provider, provider_repo_id)                                stable across renames
CREATE UNIQUE INDEX repos_slug ON repos (provider, lower(owner), lower(name));

-- members: PRIMARY KEY (repo_id, user_id)

CREATE UNIQUE INDEX pledges_live ON pledges (donor_id, repo_id)
  WHERE status IN ('pending','active','paused');                      -- one live pledge per donor per repo
```

### 9.3 Tasks and receipts

```sql
-- tasks:    PRIMARY KEY (gateway_device, id)                          dedupe scope of the Gateway's ULID
-- receipts: PRIMARY KEY (task_id, attempt)                            settlement idempotency key
--           receipt_ref TEXT NOT NULL UNIQUE                          random public id of the projection
```
