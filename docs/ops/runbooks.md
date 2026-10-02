# Runbooks (internal)

Plan 10 §8, made executable. Closed source (CONTRACT §0a). Every alert in `deploy/relay/prometheus/alerts.yml` carries a `runbook` label pointing here.

Conventions: run on the relay VM as root unless stated. `A="/opt/moochy/bin/relay admin --socket /run/moochy/admin.sock"`. `M() { curl -fsS 127.0.0.1:9100/metrics | grep -E "^$1"; }`. Never paste prompts, outputs, keys or tokens into tickets or chat: the relay never has plaintext and the operators never ask for it. Every admin action is audit-logged by the relay; public ones (catalog, moderation) also go to the key log.

Always: open an incident note (time, alert, who), post a status update within 15 min for anything user-visible, write a postmortem for every page.

---

## R1 — Relay down

Alerts: `RelayUnavailable`, `RelayScrapeDown`, `LitestreamLag`, `LitestreamDown`, `LitestreamReplicaErrors`, `RestoreDrillStale`.

1. **Is the process up?**
   ```sh
   systemctl status moochy-relay moochy-litestream --no-pager
   journalctl -u moochy-relay -n 200 --no-pager -o cat | tail -50
   ```
2. **Disk** (SQLite + WAL must fit; Litestream needs room for its LTX files):
   ```sh
   df -h /var/lib/moochy; ls -l /var/lib/moochy/
   ```
   Full disk → delete only `/var/lib/moochy/*.litestream-tmp*` or old journal files, never `relay.db*`. Then R7.
3. **Certificates** (ACME autocert, cached in the state dir):
   ```sh
   echo | openssl s_client -connect "$RELAY_DOMAIN:443" -servername "$RELAY_DOMAIN" 2>/dev/null | openssl x509 -noout -dates
   echo | openssl s_client -connect "$RELAY_DOMAIN:8443" -alpn h2 -tls1_3 2>/dev/null | grep -E 'ALPN|Verify'
   ```
   Expired → check port 443 reachable from the internet (TLS-ALPN challenge) and the rate limits in the log.
4. **Restart** (process wedged but VM healthy):
   ```sh
   deploy/relay/scripts/drain-restart.sh --restart-only        # drains first if the admin socket answers
   systemctl restart moochy-relay                               # only if the socket is dead
   ```
   Crash loops: `journalctl -u moochy-relay -b | grep -m1 -i -E 'panic|fatal|migrat'`. Migration refused because the DB needs a newer binary → install that binary; never edit the schema by hand.
5. **Replication unhealthy** (`LitestreamLag`/`LitestreamDown`): `systemctl restart moochy-litestream`; check bucket credentials and endpoint with `journalctl -u moochy-litestream -n 100`. Do not upgrade the relay while replication lags (the drain script refuses).
6. **VM lost / disk corrupt** (RTO < 30 min, RPO ≈ 1 s DB, 0 spend):
   1. Provision a VM from the recipe (`deploy/relay/README.md`), same region or the next one (region outage, RTO < 1 h).
   2. Copy `/etc/moochy/` (env files, `litestream.yml`, `tls/`) from the operators' vault, then **re-encrypt every credential on the new host** from the vault's offline copies (`enc …` in `deploy/relay/README.md`): a `.cred` only decrypts on the host (and TPM) that made it.
   3. Restore and check:
      ```sh
      sudo -u moochy litestream restore -config /etc/moochy/litestream.yml -o /var/lib/moochy/relay.db /var/lib/moochy/relay.db
      ```
   4. `systemctl enable --now moochy-litestream moochy-relay`; the relay sends `receipt.replay_since` to every Worker on reconnect (spend RPO 0).
   5. Point DNS at the new VM (TTL 60 s). Gateways reconnect at once, Workers with 0–10 s jitter.
   6. Verify: `M relay_build_info`, `M link_connections`, the probes recover, then run the audit (`$A audit` → `drift 0 uusd`, exit 0).
7. Post the status update; postmortem.

## R2 — Ledger drift detected

Alerts: `LedgerDrift` (page), `AuditNotRunning`, `ReceiptsUnsettled`.

1. **Freeze** new reservations on the affected pledges (running streams finish; nothing new is reserved):
   ```sh
   $A audit | tee /root/drift-$(date +%F).txt   # "drift N uusd", then one line per mismatching pledge-period / member-month / device-month
   $A pledge freeze <pledge_id>                   # for each pledge named in the mismatches
   ```
2. **Diff** receipts against balances for each drifting scope, on a restored copy (never the live DB): `restore-drill.sh --keep --skip-anchor --workdir /root/drill`, then `relay serve --read-only --db /root/drill/relay.db` prints the mismatches as JSON; compare with `sqlite3 -readonly` queries on `receipts` and the balance tables.
3. **Classify the cause**: code bug (duplicate settle, rounding), partial migration (check `schema_migrations` vs the release notes), replay after restore (receipt settled twice → idempotency bug). Never "fix" by editing balances directly.
4. **Correct** with correction entries through the relay (requested from mo-relay: `relay admin ledger correct`; until it exists, escalate to the relay maintainers, never write SQL on the live DB), re-run `$A audit` until drift is 0, then `$A pledge unfreeze <id>`.
5. Postmortem with the exact receipts involved (ids only, never content).

## R3 — Mass Worker disconnect

Alerts: `FailoverRateHigh`, `WorkerAckSlow`, `LinkQueueOverflow`, `RelayStuckDraining`; dashboard "Workers online" falls.

1. **Draining misfire?** `M relay_draining` = 1 outside a deploy → `$A state`, then restart without drain: `systemctl restart moochy-relay` (a stuck drain cannot be "undrained" safely).
2. **Our network**: `ss -s`; `M 'link_connections'`; packet loss from the probes' regions; provider-side egress limits on the VM.
3. **Provider outage** (Workers NACK `provider_error`): `M 'failovers_total'` by `code`. Mostly `provider_error`/`rate_limited` for one provider → R4.
4. **Backpressure**: `LinkQueueOverflow` rising with normal CPU → a slow Gateway or a flood; check `M tasks_inflight` and per-IP connection counts in the log (IPs kept 7 days).
5. Status page if more than 25% of Workers are gone for 10 min.

## R4 — Provider outage

1. Confirm on the provider's status page; `M 'failovers_total{code="provider_error"'`.
2. Pools for that provider drain naturally: Gateways get native overloaded/retryable errors and agents back off. **Nothing to change on the relay.**
3. Communicate (status page: "provider X degraded; tasks for X models will retry"). Close when the failover rate returns under 5%.

## R5 — Abuse report (malicious output) / bad envelopes

Alerts: `BadEnvelopeSpike`.

1. **Verify the evidence bundle** (06 §9): the reporter's bundle holds the donor-signed receipt and progress checkpoints. Verify every signature against the key log with the client: `moochy verify` on the bundle (open-source, runs on the operator's laptop). Unsigned or failing bundle → close as unverifiable.
2. **Suspend** the donor's devices (stops new assignments at once): `$A suspend <device_id|username> --reason "<ticket>"`.
3. **Record** the `MODERATION` entry (public, key log): `$A moderation add <username> --reason "<ticket>"`.
4. **Notify** the affected repository owners (contact from the repo claim).
5. Bad-envelope spike without a report: group by device (`journalctl -u moochy-relay | grep bad_envelope`, device ids only). One device → suspend and contact; many → suspect a broken client release (R8) or relay tampering (escalate to security, preserve logs).

## R6 — Log key compromise / unknown key / stale checkpoints

Alerts: `UnknownKeyAlert` (page), `CheckpointStale`, `CheckpointStalePage`.

Stale checkpoint: `M 'checkpoint_age_s|anchor_lag_s|key_log_size'`; check that Litestream is current (checkpoints never get ahead of the replica, so replication lag blocks them: R1 step 5) and that the anchor push credentials work.

Unknown key or suspected key compromise:
1. Treat as compromise until proven otherwise. Page the two key holders (hardware tokens, plan 12 Q7).
2. **Generate the new key offline** on an air-gapped machine with both holders present; record the public key fingerprint on paper.
3. **Transition checkpoint**: sign the current tree head with the old key (if still trusted) **and** the new key; anchor it in the public Git repository (signed commit).
4. Load the new key on the relay: `enc keylog-key < new-keylog-key.txt` (README; the key-log key also signs the catalog), shred the input, `drain-restart.sh --restart-only`.
5. **Announce** (blog, status page, security advisory) with both fingerprints.
6. **Ship a signed client release** pinning the new key (R8 steps 1–3); raise `min_client_version` only if the old key is known to be abused.

## R7 — Database grows fast / performance tickets

Alerts: `SchedulerApplySlow`, `SubmitToAssignSlow`, `MetricsCardinalityCap`, `CacheReadRatioLow`.

1. `ls -l /var/lib/moochy/ && M 'wal_size_bytes'`; WAL above 1 GiB → the checkpointer is starved (long read transactions: web/audit).
2. Retention job ran? `$A state` (retention fields) (task metadata 90 days, plan 12 Q8).
3. Task-row flood (abuse): top Gateways by task count in the last hour from `$A state`; suspend offenders (R5 step 2).
4. Receipts beyond ~100M: archive receipts older than 13 months to object storage (plan 09 §8); projections stay.
5. `CacheReadRatioLow`: per repo `moochy:cache_read_by_repo:ratio_rate1h` and `moochy:affinity_hit:ratio_rate1h`. Low affinity hits → Workers churn or the affinity margin is too tight (sched `AffinityMargin`); low cache reads with good affinity → a harness stopped sending cache markers (client-side, not a relay fault).
6. `SchedulerApplySlow` sustained after cleanup (per event: `scheduler_apply_us` by `event`): the shard-by-repo trigger of ADR-06 (open an engineering ticket with the dashboard screenshot). `MetricsCardinalityCap`: find the family in `M '_overflow'` and the label source.

## R8 — Firewall bypass reported

Alerts: `FirewallNewFieldWidespread` (a harness changed; review the allowlist).

1. Reproduce privately with the reporter; confirm which provider field or path bypasses the Worker firewall.
2. **Client release** with the tighter allowlist (two-person review for allowlist changes, 06 §7.3): tag `vX.Y.Z` in `moochy-cli`; the release is signed, attested and reproducibly rebuilt (deploy/client).
3. **Raise `min_client_version`** to that release (`RELAY_MIN_CLIENT_VERSION` in `/etc/moochy/relay.env` → `--min-client-version`), `drain-restart.sh --restart-only`. Old Workers are refused at `hello`.
4. **Notify donors** (email + dashboard banner): what was exposed, what they must update.
5. For `FirewallNewFieldWidespread` alone (no bypass): a client harness started sending a new field; decide allowlist or keep refusing, and ship accordingly.
