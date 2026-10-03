# Key log formats (normative, CONTRACT R8)

Implemented by `relay/internal/tlog` (Go, relay) and `cli/crates/keylog` (Rust, Node); golden
vectors in `spec/vectors/keylog/*.json` (written by the Go tests `TestVectors`,
`TestWebAuthnVectors`, `TestBoxVectors`, `TestOwnerKeyProofVectors` and `TestOrgVectors`, verified by the
Rust tests `tests/vectors.rs`, `tests/monitor.rs`, `tests/webauthn.rs`, `tests/boxes.rs`,
`tests/owner_proof.rs` and `tests/orgs.rs`). Rationale: plan 06 §10, 09 §3.5, D14, D16,
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
- **Size bound.** A record is ≤ 480 bytes (the largest plain record, a `KEY_ADDED` with every
  field at its maximum, is 397), except records carrying a WebAuthn assertion (§4a: kinds 3–7
  and 13–15 signed by a passkey, passkey `OWNER_KEY_ADDED`), ≤ 2048 bytes. An entry bundle is always
  ≤ 256 × 482 = 123,392 bytes and fits one 128 KiB gRPC message: before appending a record of
  `L` bytes at bundle slot `c` (0–255) when the bundle already holds `S` bytes (`Σ 2 + len`), the
  relay first appends `PAD` entries (kind 12, empty body and sig) while `S + 2 + L > 482 × (c + 1)`.
  Plain records never need one; an assertion record needs at most 4. Verifiers refuse an entry
  over its bound and a bundle over 123,392 bytes. `GetLogTile` answers are ≤ that bound.
- **Git anchor.** Every hour the newest checkpoint note is written to the file `checkpoint` of the
  anchor repository, committed (`keylog checkpoint <size>`) and pushed to the public remote. The
  relay refuses to anchor, and to boot, when the anchored or signed checkpoint is not a prefix of
  its database. Anyone can verify the whole public history: every commit's note is signed by the
  log key, sizes never decrease, and each is a prefix of the current log (`VerifyAnchorHistory`).

## 2. Record (tree leaf data)

```
record = lp("moochy/v1/keylog", u32(kind), u64(logged_at_ms), body, sig)     ≤ 480 bytes (§1)
```

`logged_at_ms` = relay clock at append. Ids are the canonical strings of CONTRACT §1; byte strings
are raw. `owner_key_id(pub) = "ok_" + lowercase hex(SHA-256(pub)[0..16])`.

| kind | name | body = lp(…) | sig |
|---|---|---|---|
| 1 | `KEY_ADDED` | `device_id, pseudonym, sign_pub(32), enc_pub(32), suite, roles, repo_scope`; box device (9 fields, §2b): `…, repo_scope, box_token_id, u64(expires_at_ms)` | PoP: `Ed25519(sign_key, lp("moochy/v1/key-pop", sign_pub, enc_pub, suite))` (`DeviceStartRequest.pop_sig`) |
| 2 | `KEY_REVOKED` | `device_id, pseudonym, reason` | — (relay-asserted; only removes trust) |
| 3 | `REPO_CLAIMED` | `repo_id, provider, provider_repo_id, owner_pseudonym, signer = owner_key_id, u64(issued_at_ms)` | owner key |
| 4 / 5 | `DONOR_APPROVED` / `DONOR_REVOKED` | `repo_id` or `org_id` (§2c), `donor_pseudonym, signer = owner_key_id, u64(issued_at_ms)` | owner key |
| 6 / 7 | `MEMBER_ADDED` / `MEMBER_REMOVED` | `repo_id, member_pseudonym, signer = owner_key_id, u64(issued_at_ms)` | owner key |
| 8 | `CATALOG` | `u64(version), sha256(catalog_json)(32), catalog_sig(1..128, opaque)` | — |
| 9 | `MODERATION` | `subject_pseudonym, action, reason` | — |
| 10 | `OWNER_KEY_ADDED` | Ed25519 (4 fields): `pseudonym, owner_pub(32), prev_owner_pub (empty or 32), u64(issued_at_ms)`; Ed25519 authorized by a passkey (5 fields, §4b): `…, u64(issued_at_ms), authorizer`; passkey (9 fields, §4a) | `new_sig` (64, a first key only before the §4c cutover), `lp(new_sig, email_proof)` (104, first key with the email proof, §4c), or `new_sig ‖ prev_sig` (128) when `prev` is set; 5 fields: `lp(new_sig, authorizer_sig)`; passkey: §4a |
| 11 | `OWNER_KEY_REVOKED` | `pseudonym, owner_pub(32) or passkey cose_key(77), reason` | — (relay-asserted; only removes trust) |
| 12 | `PAD` | empty | — (relay filler for the bundle budget, §1; no effect) |
| 13 | `ORG_CLAIMED` | `org_id, provider, provider_org_id, owner_pseudonym, signer = owner_key_id, u64(issued_at_ms)` (§2c) | owner key |
| 14 / 15 | `ORG_REPO_ADDED` / `ORG_REPO_REMOVED` | `org_id, repo_id, signer = owner_key_id, u64(issued_at_ms)` (§2c) | owner key |

Owner signature (kinds 3–7 and 13–15, "owner-signed kinds") and both signatures of kind 10, for an
Ed25519 owner key: `Ed25519(key, lp("moochy/v1/keylog-sig", u32(kind), body))`; for a passkey owner
key, the owner-signed kinds carry a WebAuthn assertion over the same message instead (§4a). The state decides which form a
signature has from the `signer`'s key type, never from its length.

Field grammar (identical in both languages; anything else is refused):
`device_id` = `d_` + ULID, `repo_id` = `r_` + ULID, `org_id` = `o_` + ULID (26 Crockford chars,
uppercase, first ≤ `7`); the target of `DONOR_*` is a `repo_id` or an `org_id`, of `MEMBER_*` a
`repo_id` only;
pseudonym = `ps_` + 16 lowercase Crockford base32 chars (`0-9a-hjkmnp-tv-z`); `roles` ∈
{`gateway`, `worker`, `gateway,worker`}; `repo_scope` = `""` or a `repo_id`; `suite`, `reason`,
`action` = `[a-z0-9._-]` (suite ≤ 64, others ≤ 32); `provider` ∈ {`github`, `gitlab`};
`provider_repo_id`, `provider_org_id` = canonical decimal (1–20 digits, no leading 0); `signer` = `ok_` + 32 lowercase
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

### 2b. Box devices (CONTRACT §17.1)

An agent box (boat.dev, E2B, Codespaces, …) never holds the maintainer's device key: it enrolls
with a single-purpose token and generates its own keys, and the relay logs a **box** `KEY_ADDED`,
the 7 fields followed by `box_token_id` (`bt_` + ULID, the enrollment token's id) and
`u64(expires_at_ms)`. Grammar: `roles` = `gateway` only (no donor role), `repo_scope` set (one
repo), `expires_at_ms` > 0; anything else is refused. The PoP is the ordinary one (§2): the box
signs its keys, the relay asserts the token, scope and expiry, which only narrow the device.

- **State.** Accepted iff `logged_at_ms < expires_at_ms ≤ logged_at_ms + 30 days` (`box_expiry`,
  enrollment tokens live 10 min – 30 days), plus the `KEY_ADDED` rules (§5). Its pseudonym is the
  enrolling owner's or member's.
- **Inactive once expired.** `gateway_allowed` / `sealable` refuse a box device at or after
  `expires_at_ms` (`expired`), judged by the asking party's clock (the Worker's, the relay's);
  the relay also logs the usual `KEY_REVOKED` when a box expires or is revoked. A box never
  satisfies `sealable` (no worker role) and has no owner powers: owner keys are separate keys
  (§4) and the relay refuses §2a requests from a box except revoking itself.
- **Monitors.** A user's box devices are listed apart from their devices (`State::boxes`); a box
  on my account raises `BoxEnrolled` (never `UnknownKey`: its keys are made in the box), and
  `BoxOutsideRepo` (security) when its repo is one I neither own nor am an active member of at
  that point of the log.

Vectors: `spec/vectors/keylog/boxes.json`.

### 2c. Organisations (CONTRACT §19)

An org owner's approvals serve every repo the org **covers**, and coverage is verifiable from the
log alone:

- **`ORG_CLAIMED`** binds `org_id` (`o_` + ULID; a GitHub organisation or a GitLab group, the
  numeric provider id in `provider_org_id`) to `owner_pseudonym`, signed by that user's owner key.
  Same rules as `REPO_CLAIMED` (§5): the org keeps its provider binding (`repo_binding`),
  `issued_at` grows (`replay`), and a claim by a **new** owner drops every org approval and every
  covered repo (they must be re-signed). The relay appends it only after the provider confirms the
  user owns the org (§19.2); the log cannot check that, Nodes alert on it (§9).
- **`ORG_REPO_ADDED(org, repo)`** is signed by an owner key of the org's current owner, and is
  accepted only when `repo` is claimed by **that same** pseudonym (`not_owner` otherwise: a repo
  claimed by another account is never covered, whatever its path). **`ORG_REPO_REMOVED`** needs only
  the org owner's signature. Replay is per (org, repo).
- **`DONOR_APPROVED` / `DONOR_REVOKED` with an `org_id`** use the unchanged repo rules against the
  org's claim: the org owner approves a donor once per org.
- **Sealing** (§5 `sealable`): the donor's approval for the repo, else for an org O with
  `ORG_CLAIMED(O)` and `REPO_CLAIMED(repo)` active under the **same** owner and
  `ORG_REPO_ADDED(O, repo)` active. A later change of either owner ends the coverage without any new
  entry. An org id is never a repo: queries naming one answer `unclaimed`.

Vectors: `spec/vectors/keylog/orgs.json` (siphoning through a foreign-claimed repo, a forged
`ORG_REPO_ADDED`, replays, an org takeover, a repo changing owner, two orgs covering one repo).

## 3. Labels

`moochy/v1/keylog`, `moochy/v1/keylog-sig`, `moochy/v1/key-pop`, `moochy/v1/receipt-log`; device
requests (§2a): `moochy/v1/key-revoke`, `moochy/v1/key-rotate`; passkeys (§4a):
`moochy/v1/email-proof`.

Owner-key requests (authenticate a request, never a log signature): `moochy/v1/lookup`. For
`POST /api/lookup` (A218: the owner's independent handle → pseudonym check) the owner CLI signs
`lp("moochy/v1/lookup", handle, repo_slug, owner_pseudonym, decimal(issued_at_ms))` with its
Ed25519 owner key; `decimal` = canonical ASCII decimal (no sign, no leading zero). The relay
checks it against the user's active owner key; it is never accepted as a log signature and the
reverse (distinct label).

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
  session's pseudonym **only with a proof** (§4c): the confirmed-email proof, or the co-signature
  of an active passkey (§4b). Every Node of that user alerts (`unknown_owner_key`) on an owner key
  it did not create or acknowledge, exactly like a rogue device key.
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

### 4a. Passkey owner keys (`webauthn-es256`, CONTRACT §16.6)

A user may also hold **passkeys** as owner keys, so that the Accept button of an email or the web
signs `DONOR_APPROVED` (and every other kind 3–7) with the human's authenticator: a WebAuthn
assertion with user verification, whose challenge is the hash of the exact entry. A passkey is an
additional active owner key of its user (any number; the Ed25519 CLI key, if any, stays the single
rotated one). Vectors: `spec/vectors/keylog/webauthn.json`.

**Key.** `cose_key` = the canonical CTAP2 encoding of the EC2 P-256 credential public key, exactly
77 bytes: `A5 01 02 03 26 20 01 21 58 20 ‖ x(32) ‖ 22 58 20 ‖ y(32)` (`{1:2, 3:-7, -1:1, -2:x, -3:y}`),
with `(x, y)` a point of P-256. Nothing else is accepted: verifiers parse only this subset, the
relay re-encodes the authenticator's COSE key into it at registration. `owner_key_id(cose_key)` =
`ok_` + hex(SHA-256(cose_key)[0..16]); monitors name a passkey by `SHA-256(cose_key)`.

**`OWNER_KEY_ADDED` (passkey)** = 9 fields (the Ed25519 form has 4):

```
body = lp(pseudonym, cose_key(77), authorizer, u64(issued_at_ms), "webauthn-es256",
          credential_id(1..255), rp_id, origins, email_proof)
sig  = lp(pop_assertion, authorizer_sig)
```

- `authorizer` = `""` (the account's **first** owner key: then `email_proof` is 32 bytes and
  `authorizer_sig` is empty) or the `owner_key_id` of an active owner key of the same user (then
  `email_proof` is empty and `authorizer_sig` is that key's signature over the same message:
  64-byte Ed25519 or an assertion).
- `rp_id` = lowercase DNS name (or IPv4 literal for dev), ≤ 253 chars. `origins` = 1–4
  comma-separated origins, ≤ 256 bytes: `https://host[:port]` (dev: `http://localhost[:port]`,
  `http://127.0.0.1[:port]`), each `host` equal to `rp_id` or a subdomain of it; no path, no
  trailing slash. The assertion's `origin` must equal one of them byte for byte.
- `pop_assertion`: an assertion by the new credential itself over the entry (proof of possession;
  the web runs `navigator.credentials.create()` then immediately `get()` with that challenge).

**Assertion** (wire form, wherever a passkey signs) = `lp(authenticatorData(37..256),
clientDataJSON(1..768), signature(DER, 8..72))`; a record carrying one is ≤ 2048 bytes (§1).

**Signed message and challenge.** The message is the same as for Ed25519 owner keys,
`m = lp("moochy/v1/keylog-sig", u32(kind), body)` over the **exact** body bytes that are logged
(the relay never re-encodes a body after it was signed). The WebAuthn challenge is
`SHA-256(m)` (32 bytes); `clientDataJSON.challenge` is its base64url encoding without padding (43
chars), compared as a string.

**Verification** of an assertion `a` by passkey `k` over `m`, given the last sign counter `prev`
seen for that credential, in this order (first failure wins, codes are shared):

1. `clientDataJSON` is UTF-8 and one JSON object (RFC 8259), with no duplicate member name at any
   level (after unescaping), nesting ≤ 4, no lone surrogate or U+FFFD, nothing after it, else
   `webauthn_format`. Then `type` is the string `"webauthn.get"` (`webauthn_type`); `challenge` is
   the string above (`webauthn_challenge`); `origin` is a string in `k.origins`, `crossOrigin` is
   absent or `false`, `topOrigin` is absent (`webauthn_origin`). Other members are ignored.
2. `authenticatorData[0..32] = SHA-256(k.rp_id)` (`webauthn_rp`).
3. Flags `authenticatorData[32]`: UP (0x01) and UV (0x04) set, AT (0x40) clear, ED (0x80) set iff
   the data is longer than 37 bytes (`webauthn_flags`). Extensions are covered by the signature
   and otherwise ignored.
4. Sign counter `c = u32_be(authenticatorData[33..37])`: `c > prev`, or `c = prev = 0`
   (authenticators without a counter) (`counter`). A counter that does not move although it once
   did is a cloned authenticator or a replay; the first assertion of a credential is checked with
   `prev = 0`.
5. `signature` is strict DER `SEQUENCE {INTEGER r, INTEGER s}`: definite short-form lengths,
   minimal positive integers, `1 ≤ r, s ≤ n − 1`, nothing trailing (`webauthn_format`); and
   **low-S**: `s ≤ n / 2` (`high_s`), `n` the P-256 order. Signatures are not malleable in the log:
   the relay rewrites a high-S signature to `(r, n − s)` (which verifies identically) before
   appending, and verifiers refuse high-S.
6. ECDSA P-256 / SHA-256 over `authenticatorData ‖ SHA-256(clientDataJSON)` with `(x, y)` of
   `cose_key` (`bad_sig`).

A rejected assertion consumes nothing; an accepted entry sets the credential's counter to `c`.

**First passkey: the confirmed-email proof (A224).** An account with **no** active owner key of
any kind may bind its first passkey without a co-signature, on the relay's attestation that the
user just proved control of the account's confirmed email (a one-time token mailed to it and
redeemed in the same browser session as the ceremony):

```
email_proof = SHA-256(lp("moochy/v1/email-proof", SHA-256(token), owner_key_id(cose_key), pseudonym))
```

The proof binds the token to this key and account; it is **relay-attested**, not verifiable by
third parties (the token stays secret). Its presence in the log is the flag: every Node of the
user raises `UnknownPasskey{email_proof: true}` for an email-proof passkey it did not create,
naming it as the takeover path of a compromised mailbox or relay; public monitors can count such
registrations. With an active owner key, a new passkey needs that key's co-signature
(`owner_key_exists` otherwise), and an Ed25519 `OWNER_KEY_ADDED` without `prev` is refused while a
passkey is active (`owner_key_exists`): bind the CLI key with a passkey's co-signature (§4b).

**Revocation.** `OWNER_KEY_REVOKED` with the 77-byte `cose_key` (relay-asserted, as for Ed25519).

### 4b. A CLI owner key authorized by a passkey

An account whose owner keys are passkeys binds its first CLI (Ed25519) owner key with a 5-field
`OWNER_KEY_ADDED`: `body = lp(pseudonym, owner_pub(32), "" (no prev), u64(issued_at_ms),
authorizer)`, `sig = lp(new_sig(64), authorizer_sig)`, both over
`m = lp("moochy/v1/keylog-sig", u32(10), body)`: `new_sig = Ed25519(new key, m)` (proof of
possession, `bad_pop`), `authorizer_sig` = an assertion of the active passkey `authorizer` (§4a,
its counter moves) or 64 bytes if the authorizer is an Ed25519 key. Accepted iff the user has no
active CLI key (else `owner_key_exists`: rotate it with `prev` instead), `authorizer` is an
unrevoked owner key of the same user (`unknown_owner_key` / `revoked` / `not_owner`), and both
signatures verify. Effect: the key becomes the user's active CLI owner key (later rotations use
`prev` as usual). The CLI signs `m`; the web adds the assertion (WIRING §9).

### 4c. A first CLI owner key needs a proof (A224)

Before this rule an account's first Ed25519 owner key was bound on the session's word alone: a
compromised background process (or relay) could bind its own key, then claim and approve. Now a
first CLI key (no active CLI key, no `prev`) is accepted only with one of:

- **The confirmed-email proof**, carried next to the signature: the body is the ordinary 4-field
  one (the CLI signs it once, unchanged), and `sig = lp(new_sig(64), email_proof(32))` (104 bytes),
  `email_proof = SHA-256(lp("moochy/v1/email-proof", SHA-256(token), owner_key_id(owner_pub),
  pseudonym))` as for passkeys (§4a): `token` is the single-use secret of a link mailed to the
  account's confirmed address and opened by the user for **this** key (the mail names `ok_…`). The
  relay never issues it within 72 h of a change of the confirmed address (the old address is told
  of the change), nor while the account has any active owner key: then `owner_key_exists` (rotate
  with `prev`, or §4b with a passkey). Relay-attested like the passkey proof: third parties cannot
  check the token, its presence is what monitors and the user's Nodes read.
- **An authorizer** (§4b): an active owner key of the same user co-signs (a passkey).

A first CLI key with neither is refused with `owner_key_proof`.

**Cutover, existing logs.** The rule applies to an entry when the **running maximum of
`logged_at_ms` over the accepted entries**, the entry included, is ≥ `2026-10-05T00:00:00Z`
(`1791158400000`, the same constant in Go `OwnerKeyProofFromMs` and Rust
`OWNER_KEY_PROOF_FROM_MS`). Proofless first keys logged before it stay valid, and so do the
approvals they signed: no verified history changes, mirrors and the relay rebuild the same state.
The running maximum (not the entry's own time) means a relay cannot back-date one entry under the
cutover once anything later was accepted; a relay that stamps every entry before the cutover forever
shows a frozen log clock, visible against the hourly Git anchor commits. Monitors flag every first
CLI key without proof on my account, mine included (`UnprovenOwnerKey{known}`: a reminder when I
created it, an intrusion otherwise), and owner keys expose how they were bound
(`OwnerKeyInfo.Proof` / `OwnerKeyProof`: `none`, `email`, `authorizer`, `rotation`). Tests and dev
logs may move the cutover (`Config.OwnerKeyProofFromMs`, `State::with_owner_key_proof_from`; 0 =
always); Nodes verify production logs with the constant. Vectors: `owner-proof.json`.

## 5. State machine (authority derived from a log prefix)

Entries apply in log order; a rejected entry confers nothing (the relay refuses to append it; a
Node that finds one in the log raises an alert). Codes are shared strings.

| kind | accepted iff | effect |
|---|---|---|
| `KEY_ADDED` | device id new (`dup_device`), `sign_pub` new among all keys (`dup_key`), box expiry in `(logged_at, logged_at + 30 d]` (`box_expiry`, §2b), PoP valid (`bad_pop`) | device active (a box until its expiry) |
| `KEY_REVOKED` | device logged for that pseudonym (`unknown_device`), not yet revoked (`revoked`) | device revoked |
| `OWNER_KEY_ADDED` | `owner_pub` new among all keys (`dup_key`); no active key and no `prev` (and no active passkey unless authorized, §4b), or `prev` = the active key (`unknown_owner_key` / `owner_key_exists`); a first key carries the email proof or an authorizer past the cutover (`owner_key_proof`, §4c; the email proof and the authorizer only for a first key: `owner_key_exists`); new-key signature (`bad_pop`); `prev` signature (`bad_sig`); authorizer (§4b) | key active; `prev` revoked |
| `OWNER_KEY_ADDED` (passkey, §4a) | `cose_key` and `credential_id` new (`dup_key`); PoP assertion (§4a codes, `prev` = 0); first key: no active owner key of any kind (`owner_key_exists`); else `authorizer` an unrevoked owner key of the same user (`unknown_owner_key`/`revoked`/`not_owner`) whose signature verifies (`bad_sig` / §4a codes) | passkey active, counter = PoP counter; authorizer's counter moves |
| `OWNER_KEY_REVOKED` | key logged for that pseudonym (`unknown_owner_key`), not revoked (`revoked`) | key revoked (an Ed25519 revocation leaves the user with no active CLI key) |
| `REPO_CLAIMED` | `signer` is a logged owner key (`unknown_owner_key`), unrevoked (`revoked`), of `owner_pseudonym` (`not_owner`), signature (`bad_sig`); repo id keeps its provider binding (`repo_binding`); `issued_at` > previous claim's (`replay`) | owner set; a **new** owner drops every approval and membership |
| `DONOR_*`, `MEMBER_*` | repo (or org, `DONOR_*` only) claimed (`unclaimed`); `signer` is an unrevoked owner key of the **current** owner (`unknown_owner_key`/`revoked`/`not_owner`), signature (`bad_sig`); `issued_at` > previous for (repo, donor\|member, subject) (`replay`) | grant on/off, remembers the entry index |
| `ORG_CLAIMED` | as `REPO_CLAIMED`, for the org id (codes included) | owner set; a **new** owner drops every org approval and covered repo |
| `ORG_REPO_ADDED` / `_REMOVED` | org claimed (`unclaimed`); `signer` is an unrevoked owner key of the org's current owner (`unknown_owner_key`/`revoked`/`not_owner`), signature (`bad_sig`); ADDED only: repo claimed (`unclaimed`) by the org's owner (`not_owner`); `issued_at` > previous for (org, repo) (`replay`) | coverage on/off |
| `CATALOG` | version > previous (`catalog_version`) | version → sha256 |
| `MODERATION` | well-formed | informational |
| `PAD` | empty body and sig | none |

For a passkey `signer`, "signature" in the owner-signed kinds means the §4a verification with the credential's
last counter; the counter moves only when the entry is accepted.

Relay append also enforces `|issued_at − relay clock| ≤ 10 min` for kinds 3–7, 10 and 13–15 (`skew`),
and takes org kinds 13–15 only after its own provider check (§19.2–19.3): a Node's
`SignedLogEntry` of those kinds is refused with `ungated` unless the relay's gate admitted it. The
owner's Node rebuilds a relay-proposed `ApprovalRequest.body_to_sign` with its own owner key id
and current time before signing, after showing the user what it means.

Queries:
- **sealable(worker_device, repo)**: device logged (`unknown_device`), unrevoked (`revoked`), not an
  expired box (`expired`, at the caller's clock), role
  `worker` (`role`), scope empty or `repo` (`scope`), repo claimed (`unclaimed`; an org id is
  `unclaimed`), active `DONOR_APPROVED` for the device's pseudonym on the repo, or on an org that
  covers it (§2c) (`not_approved`) → `enc_pub`, key index, approval index: the repo's own approval
  when active, else the **smallest** index among the covering orgs' active approvals (deterministic,
  so the relay's `PoolWorker.approval_log_index` and the Gateway's mirror agree).
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
`UnknownKey` (device key on my pseudonym I don't know), `BoxEnrolled` / `BoxOutsideRepo` (§2b),
`UnprovenOwnerKey` (a first CLI key of mine bound without any proof, §4c), `UnknownOwnerKey`, `UnknownPasskey` (a
passkey on my pseudonym whose `SHA-256(cose_key)` I don't know; `email_proof` says it was bound as
the first owner key on the relay's email attestation, §4a), `PasskeyCounter` (an entry signed by one
of my passkeys refused with `counter`: cloned authenticator or replay), `OwnerKeyRevoked`,
`KeyHijack` (my key under another pseudonym), `NotSignedByMe` (claim/approval/membership on a repo I
own, an org claim, covered-repo change or approval on an org I own, or a repo/org claim naming me,
signed by an owner key I do not know; `repo_id` is then the `o_` id for org entries),
`RepoClaimedByOther` (a repo or org I owned claimed by another account),
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
