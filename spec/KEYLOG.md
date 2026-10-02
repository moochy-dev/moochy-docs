# Key log formats (normative, CONTRACT R8)

Implemented by `relay/internal/tlog` (Go, relay) and `cli/crates/keylog` (Rust, Node); golden
vectors in `spec/vectors/keylog/*.json` (written by the Go test `TestVectors`, verified by the
Rust tests `tests/vectors.rs` and `tests/monitor.rs`). Rationale: plan 06 §10, 09 §3.5, D14, D16,
CONTRACT §15.4.

## 1. Tree, checkpoints, tiles, transport

- Tree: RFC 6962 / RFC 9162 (SHA-256; leaf = `H(0x00 || record)`, node = `H(0x01 || l || r)`),
  hashing and proofs from Go `x/mod/sumdb/tlog`.
- Checkpoint (C2SP `tlog-checkpoint` in the C2SP `signed-note` format, Ed25519 alg `0x01`):
  text `<origin>\n<tree size decimal>\n<base64 std root>\n`, no extension lines. Key name = origin
  (`moochy.dev/keylog`; receipt log `moochy.dev/receipts`). Nodes pin the verifier key
  `<origin>+<hash8>+<base64(0x01 || pub32)>`. Verification is ZIP-215. Signature lines from other
  keys (witnesses, §7) are ignored by the log-signature check.
- A checkpoint is signed only for a tree size ≤ the size reported as replicated (Litestream hook),
  at most once per 60 s while the log grows; empty trees are never signed.
- Tiles (C2SP `tlog-tiles`, height 8), paths relative to the log prefix: `checkpoint`,
  `tile/<L>/<N>[.p/<W>]`, `tile/entries/<N>[.p/<W>]`; `N` in 3-digit groups, all but the last
  prefixed with `x` (`1234067` → `x001/x234/067`). Entry bundle = `(u16_be(len) || record)*`.
  Only data covered by the served checkpoint is served, so every tile is immutable.
- **Transport.** Over the relay link: `NodeLink.GetLogTile{path}` returns exactly those bytes
  (key log; the receipt log under the prefix `receipts/`); `Hello.log_checkpoint` carries the
  current note at connect and every new note is pushed as `RelayMsg.log_checkpoint`. Over HTTP the
  same paths are served under `/log/` (receipts: `/log/receipts/`), `checkpoint` with
  `Cache-Control: no-cache`, tiles `public, max-age=31536000, immutable`.
- **Projections** (for `moochy verify <receipt_ref>`, E63): `GetLogTile{path: "projection/<receipt_ref>"}`
  (ref = 1–64 chars of `[A-Za-z0-9_-]`) returns JSON `{"projection_b64","sig_b64","worker_device",
  "key_log_index"}` — base64url without padding of the exact signed projection bytes and
  `projection_sig`, the worker device named by the signed receipt, and the index of that device's
  `KEY_ADDED` (omitted when the device is not logged). `NOT_FOUND` for an unknown or malformed ref.
  Nothing in it is trusted: the Node verifies `Ed25519(sign_pub, lp("moochy/v1/projection",
  projection))` with the `sign_pub` of the `KEY_ADDED` at `key_log_index` in its **own** mirror, and
  checks the projection names the requested `receipt_ref`.
- **Size bound.** A record is ≤ 480 bytes (the largest real record, a `KEY_ADDED` with every field
  at its maximum, is 397), so a full entry bundle is ≤ 256 × 482 = 123,392 bytes and fits one
  128 KiB gRPC message. `GetLogTile` answers are ≤ that bound.
- **Git anchor.** Every hour the newest checkpoint note is written to the file `checkpoint` of the
  anchor repository, committed (`keylog checkpoint <size>`) and pushed to the public remote. The
  relay refuses to anchor, and to boot, when the anchored or signed checkpoint is not a prefix of
  its database. Anyone can verify the whole public history: every commit's note is signed by the
  log key, sizes never decrease, and each is a prefix of the current log (`VerifyAnchorHistory`).

## 2. Record (tree leaf data)

```
record = lp("moochy/v1/keylog", u32(kind), u64(logged_at_ms), body, sig)     ≤ 480 bytes
```

`logged_at_ms` = relay clock at append. Ids are the canonical strings of CONTRACT §1; byte strings
are raw. `owner_key_id(pub) = "ok_" + lowercase hex(SHA-256(pub)[0..16])`.

| kind | name | body = lp(…) | sig |
|---|---|---|---|
| 1 | `KEY_ADDED` | `device_id, pseudonym, sign_pub(32), enc_pub(32), suite, roles, repo_scope` | PoP: `Ed25519(sign_key, lp("moochy/v1/key-pop", sign_pub, enc_pub, suite))` (`DeviceStartRequest.pop_sig`) |
| 2 | `KEY_REVOKED` | `device_id, pseudonym, reason` | — (relay-asserted; only removes trust) |
| 3 | `REPO_CLAIMED` | `repo_id, provider, provider_repo_id, owner_pseudonym, signer = owner_key_id, u64(issued_at_ms)` | owner key |
| 4 / 5 | `DONOR_APPROVED` / `DONOR_REVOKED` | `repo_id, donor_pseudonym, signer = owner_key_id, u64(issued_at_ms)` | owner key |
| 6 / 7 | `MEMBER_ADDED` / `MEMBER_REMOVED` | `repo_id, member_pseudonym, signer = owner_key_id, u64(issued_at_ms)` | owner key |
| 8 | `CATALOG` | `u64(version), sha256(catalog_json)(32), catalog_sig(1..128, opaque)` | — |
| 9 | `MODERATION` | `subject_pseudonym, action, reason` | — |
| 10 | `OWNER_KEY_ADDED` | `pseudonym, owner_pub(32), prev_owner_pub (empty or 32), u64(issued_at_ms)` | `new_sig` (64), or `new_sig ‖ prev_sig` (128) when `prev` is set |
| 11 | `OWNER_KEY_REVOKED` | `pseudonym, owner_pub(32), reason` | — (relay-asserted; only removes trust) |

Owner signature (kinds 3–7) and both signatures of kind 10:
`Ed25519(key, lp("moochy/v1/keylog-sig", u32(kind), body))`.

Field grammar (identical in both languages; anything else is refused):
`device_id` = `d_` + ULID, `repo_id` = `r_` + ULID (26 Crockford chars, uppercase, first ≤ `7`);
pseudonym = `ps_` + 16 lowercase Crockford base32 chars (`0-9a-hjkmnp-tv-z`); `roles` ∈
{`gateway`, `worker`, `gateway,worker`}; `repo_scope` = `""` or a `repo_id`; `suite`, `reason`,
`action` = `[a-z0-9._-]` (suite ≤ 64, others ≤ 32); `provider` ∈ {`github`, `gitlab`};
`provider_repo_id` = canonical decimal (1–20 digits, no leading 0); `signer` = `ok_` + 32 lowercase
hex; `issued_at_ms` > 0; catalog `version` > 0; `owner_pub ≠ prev`.
No usernames, emails, device names or repo slugs ever enter the log (06 §10.3).

### 2a. Device-signed requests (authenticate a request, never logged as signatures)

A device asks the relay over its authenticated session; the relay checks the signature against
the session's device key before acting. These signatures are **not** key-log signatures: the
resulting log entry keeps its own format (§2).

| Request | `SignedLogEntry` | Signature(s) |
|---|---|---|
| Revoke itself or another device of its own user (`moochy logout`, `moochy keys revoke`) | `kind: "KEY_REVOKED"`, `body` = the KEY_REVOKED body, one sig | `Ed25519(device, lp("moochy/v1/key-revoke", body))`. The logged `KEY_REVOKED` stays relay-asserted (empty sig). |
| Rotate to a successor device (`moochy keys rotate`) | `kind: "KEY_ADDED"`, `body` = the successor's KEY_ADDED body, two sigs | `[PoP by the successor key (§2), Ed25519(current device, lp("moochy/v1/key-rotate", body))]` |

Signing `lp("moochy/v1/keylog-sig", …)` instead is refused (`bad_signature`): the labels keep a
request from ever being replayable as a log signature, and the reverse. Because revoking a
session's own device closes that session, the acknowledgement may never arrive; the
`KEY_REVOKED` entry in the served log is the confirmation. Vectors: `spec/vectors/keylog/requests.json`.

## 3. Labels

`moochy/v1/keylog`, `moochy/v1/keylog-sig`, `moochy/v1/key-pop`, `moochy/v1/receipt-log`; device
requests (§2a): `moochy/v1/key-revoke`, `moochy/v1/key-rotate`.

## 4. Owner keys (CONTRACT §15.4)

Approvals need the human. Every user who owns a repo has exactly one **active owner key**, an
Ed25519 key distinct from all of their device keys:

- **Generated and held by the foreground CLI only** (`moochy owner init`), encrypted at rest with a
  passphrase, loaded into memory only for one explicit approval/claim/membership command after the
  user confirmed what they sign, and wiped right after. The background Node never reads it, so even
  a fully compromised background process cannot approve a donor.
- **Binding.** The first owner key of a user is bound by an `OWNER_KEY_ADDED` without `prev`,
  signed by the new key (proof of possession), submitted over the user's authenticated link
  session (`SignedLogEntry{kind: "OWNER_KEY_ADDED", sigs: [new_sig]}`); the relay binds it to the
  session's pseudonym. Every Node of that user alerts (`unknown_owner_key`) on an owner key it did
  not create or acknowledge, exactly like a rogue device key.
- **Rotation** (`moochy owner rotate`): `OWNER_KEY_ADDED` with `prev` = the current owner key and
  both signatures (`sigs: [new_sig, prev_sig]`). The previous key is revoked by the same entry.
- **Revocation / loss.** `OWNER_KEY_REVOKED` is relay-asserted (lost key after a web
  re-authentication, ban): it only removes trust. After it, a new first key (no `prev`) may be
  bound. The user's Nodes alert on every revocation of their owner key (`your owner key … was
  revoked`): it is the first step of an account takeover, and the window until the user reacts is
  the residual risk (the same as for device keys).
- **Uniqueness.** An owner key can never equal any logged device key or other owner key (one key,
  one role: `dup_key`). Approvals signed by a device key are refused (`unknown_owner_key`).
- **Past approvals stay valid** after rotation or revocation: authority is evaluated at the entry's
  position in the log.

## 5. State machine (authority derived from a log prefix)

Entries apply in log order; a rejected entry confers nothing (the relay refuses to append it; a
Node that finds one in the log raises an alert). Codes are shared strings.

| kind | accepted iff | effect |
|---|---|---|
| `KEY_ADDED` | device id new (`dup_device`), `sign_pub` new among all keys (`dup_key`), PoP valid (`bad_pop`) | device active |
| `KEY_REVOKED` | device logged for that pseudonym (`unknown_device`), not yet revoked (`revoked`) | device revoked |
| `OWNER_KEY_ADDED` | `owner_pub` new among all keys (`dup_key`); no active key and no `prev`, or `prev` = the active key (`unknown_owner_key` / `owner_key_exists`); new-key signature (`bad_pop`); `prev` signature (`bad_sig`) | key active; `prev` revoked |
| `OWNER_KEY_REVOKED` | key logged for that pseudonym (`unknown_owner_key`), not revoked (`revoked`) | key revoked, user has no active key |
| `REPO_CLAIMED` | `signer` is a logged owner key (`unknown_owner_key`), unrevoked (`revoked`), of `owner_pseudonym` (`not_owner`), signature (`bad_sig`); repo id keeps its provider binding (`repo_binding`); `issued_at` > previous claim's (`replay`) | owner set; a **new** owner drops every approval and membership |
| `DONOR_*`, `MEMBER_*` | repo claimed (`unclaimed`); `signer` is an unrevoked owner key of the **current** owner (`unknown_owner_key`/`revoked`/`not_owner`), signature (`bad_sig`); `issued_at` > previous for (repo, donor\|member, subject) (`replay`) | grant on/off, remembers the entry index |
| `CATALOG` | version > previous (`catalog_version`) | version → sha256 |
| `MODERATION` | well-formed | informational |

Relay append also enforces `|issued_at − relay clock| ≤ 10 min` for kinds 3–7 and 10 (`skew`). The
owner's Node rebuilds a relay-proposed `ApprovalRequest.body_to_sign` with its own owner key id
and current time before signing, after showing the user what it means.

Queries:
- **sealable(worker_device, repo)**: device logged (`unknown_device`), unrevoked (`revoked`), role
  `worker` (`role`), scope empty or `repo` (`scope`), repo claimed (`unclaimed`), active
  `DONOR_APPROVED` for the device's pseudonym (`not_approved`) → `enc_pub`, key index, approval index.
- **gateway_allowed(gateway_device, repo)**: same device checks with role `gateway`, then the
  pseudonym is the repo owner or has an active `MEMBER_ADDED` (`not_member`). The Worker then checks
  the task signature with the returned `sign_pub` (03 §7.2).

## 6. Sealing gate (Gateway, CONTRACT §15.4)

The Gateway's key-log view is in one of four states:

| State | Meaning | Sealing |
|---|---|---|
| `NoCheckpoint` | no relay checkpoint verified yet | refused (`no_checkpoint`); only `--dev` may fall back to the relay's pool (D14) |
| `Verified{size}` | the relay's current checkpoint verified against the mirror within the last 10 min | only to workers with `sealable(worker, repo)` **and** `PoolWorker.key_log_index` / `approval_log_index` equal to the mirrored indexes (else `index_mismatch`) |
| `Stale{size}` | no confirmation for > 10 min, or the relay served an older checkpoint | refused (`stale_log`) until a fresh consistent checkpoint |
| `Forked` | a fork was seen (mirror or Git anchor) | refused (`log_forked`), persisted across restarts until the user resolves it |

"Confirmed" = a checkpoint (pushed, or polled with `GetLogTile("checkpoint")` every 60 s when
nothing was pushed) that is consistent with the mirror. The check is one read lock and three hash
lookups, no allocation (≈ 1.5 µs in a debug build).

## 7. Witnesses (C2SP tlog-witness, tlog-cosignature)

The relay submits each new checkpoint to its witnesses (`POST <prefix>/add-checkpoint`: `old <size>`,
consistency proof lines, empty line, signed note; 409 returns the witness's size) and appends the
returned cosignature lines to the served note. Cosignature = `cosignature/v1`, Ed25519, key id
`SHA-256(name || "\n" || 0x04 || pub)[:4]`, payload `id(4) ‖ u64_be(timestamp) ‖ sig(64)` over
`"cosignature/v1\ntime <ts>\n" + checkpoint text`. Nodes pin `(name, key)` of each witness and may
require k valid distinct cosignatures before applying a checkpoint (`Unwitnessed` otherwise). A
witness only cosigns checkpoints consistent with the last one it cosigned, so a split view needs
k witnesses to sign both sides.

## 8. Receipt transparency log

A second log (origin `moochy.dev/receipts`, its own key) whose leaf is
`lp("moochy/v1/receipt-log", sha256(receipt bytes))` (kind 0 in storage). The relay appends every
settled receipt (idempotent per receipt). Receipts themselves never enter the log. A donor or
maintainer holding a receipt proves it was logged with `(index, inclusion proof)` against a signed
receipt-log checkpoint — the relay returns all three in `ReceiptAck` fields 3–5 (a few ms after
settlement: receipts are logged in batches, one transaction and one checkpoint per batch); the relay can no longer silently omit a settled receipt from what it
publishes once the parties check inclusion.

## 9. Monitor rules (Node)

With `me` = own pseudonym + device keys + owner keys the user created or acknowledged:
`UnknownKey` (device key on my pseudonym I don't know), `UnknownOwnerKey`, `OwnerKeyRevoked`,
`KeyHijack` (my key under another pseudonym), `NotSignedByMe` (claim/approval/membership on a repo I
own, or a claim naming me, signed by an owner key I do not know), `RepoClaimedByOther`,
`Rejected`/`Invalid` (an entry no valid signer made). Forks: a checkpoint whose root does not match
the mirrored history, or a Git-anchor checkpoint that is not a prefix of it (`Fork`); an anchor
ahead of what the relay serves (`Rollback`); an older checkpoint than one already served (`Stale`).

## 10. Attacks and counters (research summary)

| Attack | Counter here | As in |
|---|---|---|
| Fork / history rewrite | Nodes keep the whole mirror; a new checkpoint must reproduce the root over the mirrored history; fork evidence (two signed notes) is persisted | Go sumdb client (`SECURITY ERROR` with both trees), Rekor consistency proofs |
| Split view (different logs to different users) | public Git anchor every hour + witness cosignatures (k-of-n); Nodes compare relay checkpoints with both | sumdb "gossip" via proxies and witnesses; Sigstore/Rekor with witnesses (omniwitness) |
| Rollback / freeze (serve an old tree) | no going back (`Stale`), anchor ahead of the relay (`Rollback`), 10-min freshness for sealing | sumdb `latest` cache; witness cosignature timestamps |
| Tile substitution / truncation | every record hashed into the verified root before use; bounded parsing | C2SP tlog-tiles clients |
| Unsigned / forged approvals | owner-key signature checked by every Node and the relay; device keys cannot approve | — |
| Rogue keys on a user's account | own-account monitors (`unknown_key`, `unknown_owner_key`, `OwnerKeyRevoked`) | CT monitors for own domains |
| Omitted receipts | receipt transparency log + inclusion proofs | CT SCT/inclusion |
| Log key compromise | yearly rotation; transition checkpoint co-signed and anchored (runbook R6); witnesses refuse an inconsistent history even under the stolen key | Rekor shard rotation |

## 11. Browser verifier (design note; the page is mo-design's)

A static page can verify a checkpoint without trusting the relay's web server: it embeds the pinned
log vkey and witness keys, fetches `/log/checkpoint` and the anchor's raw `checkpoint` file from the
public Git host, verifies the Ed25519 note signatures with WebCrypto (`Ed25519`, available in
current browsers; strict RFC 8032 there vs ZIP-215 in clients, which only differs on non-canonical
encodings a valid relay never produces), checks the witness cosignatures, and checks consistency
between the anchor and the relay checkpoint with a proof built from `/log/tile/...` hash tiles (the
RFC 9162 algorithm is ~60 lines of JS). For a projection or receipt, it shows the inclusion proof
result. It must say clearly that the page itself is served by the relay, so the real guarantee comes
from the open-source client (`moochy verify`), not the browser.
