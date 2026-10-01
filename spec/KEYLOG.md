# Key log formats (proposed by `mo-keylog`, pending integrator review)

Normative once accepted into CONTRACT. Implemented by `relay/internal/tlog` (Go) and
`cli/crates/keylog` (Rust); golden vectors in `spec/vectors/keylog/*.json` (written by the
Go test `TestVectors`, verified by the Rust test `tests/vectors.rs`). Rationale: plan 06 §10,
09 §3.5, D14, D16.

## 1. Tree, checkpoints, tiles

- Tree: RFC 6962 / RFC 9162 (SHA-256; leaf = `H(0x00 || record)`, node = `H(0x01 || l || r)`),
  hashing and proofs from Go `x/mod/sumdb/tlog`.
- Checkpoint (C2SP `tlog-checkpoint` in the C2SP `signed-note` format, Ed25519 alg `0x01`):
  text `<origin>\n<tree size decimal>\n<base64 std root>\n`, no extension lines. Key name = origin
  (e.g. `moochy.dev/keylog`). Nodes pin the verifier key string
  `<origin>+<hash8>+<base64(0x01 || pub32)>`. Verification is ZIP-215 (Rust `ed25519-zebra`).
- A checkpoint is signed only for a tree size ≤ the size reported as replicated (Litestream hook),
  at most once per 60 s while the log grows; empty trees are never signed.
- Tiles (C2SP `tlog-tiles`, height 8) under the relay prefix `/log/`:
  `checkpoint`, `tile/<L>/<N>[.p/<W>]`, `tile/entries/<N>[.p/<W>]`. `N` in 3-digit groups, all but
  the last prefixed with `x` (`1234067` → `x001/x234/067`). Entry bundle = `(u16_be(len) || record)*`.
  Only data covered by the newest signed checkpoint is served, so every tile is immutable
  (`Cache-Control: public, max-age=31536000, immutable`); `checkpoint` is `no-cache`.
- Git anchor: every hour the newest checkpoint note is written to the file `checkpoint` of an
  operator-configured local Git repository and committed (`keylog checkpoint <size>`); the operator
  pushes it publicly. The relay refuses to anchor (and to boot) when the anchored/signed checkpoint
  is not a prefix of its database (fork or stale restore).

## 2. Record (tree leaf data)

```
record = lp("moochy/v1/keylog", u32(kind), u64(logged_at_ms), body, sig)     ≤ 1024 bytes
```

`logged_at_ms` = relay clock at append. `sig` = 64 bytes for kinds 1 and 3–7, empty otherwise.
Ids are the canonical strings of CONTRACT §1; byte strings are raw.

| kind | name | body = lp(…) | sig |
|---|---|---|---|
| 1 | `KEY_ADDED` | `device_id, pseudonym, sign_pub(32), enc_pub(32), suite, roles, repo_scope` | PoP: `Ed25519(sign_key, lp("moochy/v1/key-pop", sign_pub, enc_pub, suite))` |
| 2 | `KEY_REVOKED` | `device_id, pseudonym, reason` | — (relay-asserted; only removes trust) |
| 3 | `REPO_CLAIMED` | `repo_id, provider, provider_repo_id, owner_pseudonym, signer_device, u64(issued_at_ms)` | owner device |
| 4 / 5 | `DONOR_APPROVED` / `DONOR_REVOKED` | `repo_id, donor_pseudonym, signer_device, u64(issued_at_ms)` | owner device |
| 6 / 7 | `MEMBER_ADDED` / `MEMBER_REMOVED` | `repo_id, member_pseudonym, signer_device, u64(issued_at_ms)` | owner device |
| 8 | `CATALOG` | `u64(version), sha256(catalog_json)(32), catalog_sig(1..128, opaque)` | — |
| 9 | `MODERATION` | `subject_pseudonym, action, reason` | — |

Owner-device signature (kinds 3–7): `Ed25519(signer_key, lp("moochy/v1/keylog-sig", u32(kind), body))`.

Field grammar (identical in both languages, fail closed on anything else):
`device_id` = `d_` + ULID, `repo_id` = `r_` + ULID (26 Crockford chars, first ≤ `7`, uppercase);
pseudonym = `ps_` + 16 ASCII alphanumerics; `roles` ∈ {`gateway`, `worker`, `gateway,worker`};
`repo_scope` = `""` or a `repo_id`; `suite`, `reason`, `action` = `[a-z0-9._-]` (suite ≤ 64, others ≤ 32);
`provider` ∈ {`github`, `gitlab`}; `provider_repo_id` = canonical decimal (1–20 digits, no leading 0);
`issued_at_ms` > 0; catalog `version` > 0.
No usernames, emails, device names or repo slugs ever enter the log (06 §10.3).

## 3. Labels (add to CONTRACT §2)

`moochy/v1/keylog`, `moochy/v1/keylog-sig`, `moochy/v1/key-pop`.

## 4. State machine (authority derived from a log prefix)

Entries apply in log order; a rejected entry confers nothing (the relay refuses to append it; a
Node that finds one in the log raises an alert). Codes are shared strings.

| kind | accepted iff | effect |
|---|---|---|
| `KEY_ADDED` | device id new (`dup_device`), `sign_pub` new (`dup_key`), PoP valid (`bad_pop`) | device active |
| `KEY_REVOKED` | device logged for that pseudonym (`unknown_device`), not yet revoked (`revoked`) | device revoked |
| `REPO_CLAIMED` | signer logged (`unknown_device`), unrevoked (`revoked`), belongs to `owner_pseudonym` (`not_owner`), sig (`bad_sig`); repo id keeps its provider binding (`repo_binding`); `issued_at` > previous claim's (`replay`) | owner set; a **new** owner drops every approval and membership |
| `DONOR_*`, `MEMBER_*` | repo claimed (`unclaimed`); signer is an unrevoked device of the **current** owner (`unknown_device`/`revoked`/`not_owner`), sig (`bad_sig`); `issued_at` > previous for (repo, donor\|member, subject) (`replay`) | grant on/off, remembers the entry index |
| `CATALOG` | version > previous (`catalog_version`) | version → sha256 |
| `MODERATION` | well-formed | informational |

Relay append also enforces `|issued_at − relay clock| ≤ 10 min` (`skew`).

Queries:
- **sealable(worker_device, repo)**: device logged (`unknown_device`), unrevoked (`revoked`), role
  `worker` (`role`), scope empty or `repo` (`scope`), repo claimed (`unclaimed`), active
  `DONOR_APPROVED` for the device's pseudonym (`not_approved`) → `enc_pub`, key index, approval index.
- **gateway_allowed(gateway_device, repo)**: same device checks with role `gateway`, then the
  pseudonym is the repo owner or has an active `MEMBER_ADDED` (`not_member`). The Worker then checks
  the task signature with the returned `sign_pub` (03 §7.2).

## 5. Monitor rules (Node)

With `me` = own pseudonym + signing keys the user created or acknowledged:
`UnknownKey` (KEY_ADDED on my pseudonym with an unknown key), `KeyHijack` (my key under another
pseudonym), `NotSignedByMe` (claim/approval/membership on a repo I own — or a claim naming me —
signed by a key I do not know), `RepoClaimedByOther`, `Rejected`/`Invalid` (the relay appended an
entry that is not valid). Forks: a checkpoint whose root does not match the mirrored history, or a
Git-anchor checkpoint that is not a prefix of the mirror (`Fork`), or an anchor ahead of what the
relay serves after a full sync (rollback).
