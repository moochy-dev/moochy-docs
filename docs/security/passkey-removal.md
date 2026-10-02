# Passkey removal needs a fresh assertion (A253)

Owner of this note: `mo-sec`. For `mo-oauth` (ceremony), `mo-web`/`mo-design` (Settings → Passkeys), `mo-relay` (`source.RevokePasskey`). Answer to mo-relay's question, final security run 2026-10-02 (main a10a344e9).

## Decision: require a fresh passkey assertion

`POST /auth/passkeys/{key}/revoke` must verify a fresh WebAuthn assertion from a passkey of the account, exactly like `/decide/{id}/accept` already does, before it appends `OWNER_KEY_REVOKED`. A valid session plus the CSRF token is **not** sufficient. When every passkey is lost, recovery goes through the operator path (relay-asserted revoke + the 72 h first-key hold), not a one-click button.

## Why a session alone is not enough here

Revocation "only removes trust", but it is the enabling step of an account takeover, so the bar to perform it should match the bar to use the key it removes:

- Adding another passkey while one is live needs that live passkey's co-signature (`tlog/state.go`, `OwnerPasskey` with `Authorizer != ""` checks `ownerSig`). A stolen session cannot produce it.
- A *first* owner key (no authorizer) is accepted once the account has none (`ownerOf[ps] == "" && passkeysOf[ps] == 0`). The only gate then is the 72 h hold after an email change (`FirstPasskeyHold`).
- So the chain from a stolen web session to a hostile owner key is: remove the last passkey (today: session + CSRF), then register a first passkey. The hold slows the second step but is not a substitute for protecting the first: an attacker who has held the session more than 72 h, or on an account whose confirmed address was never changed (hold = zero), walks straight through.

Requiring the assertion closes the chain at step one: a stolen session that does not also control an authenticator cannot revoke, so it can never reach the "account has no owner key" state on its own.

## What to build

1. **Ceremony.** Reuse the `/decide` accept shape (`oauth/decide.go`): on `GET` of the Settings passkey row (or a dedicated `begin`), start a WebAuthn ceremony whose challenge is `SHA-256` over the exact `OWNER_KEY_REVOKED` body for `{pseudonym, key}`; seal it in the ceremony cookie bound to `{user, key}`; `POST …/revoke` carries the assertion and the relay verifies it (ZIP-215 / `VerifyAssertion`, counter strictly increasing, origin + rpID) before `RevokePasskey`. The authenticator used may be any of the account's passkeys, not necessarily the one being removed (so a compromised authenticator can still be revoked by another).
2. **Last passkey.** If the assertion cannot be produced (lost authenticator), do not offer a session-only override. Point the user at recovery; the relay-asserted revoke stays an operator action and leaves the 72 h hold in place.
3. **Email change.** Keep `/auth/email` behind `postFresh` (a fresh provider sign-in). The web `emailPost` path (`internal/web/security.go`) must not offer a session-only route around it.
4. **CSRF + Origin** stay required on top of the assertion (they already are via `stateChange`).

## Tests (hand to the owners)

- `mo-oauth` unit: `POST …/revoke` with a valid session + CSRF but no assertion → refused; with a stale/replayed assertion (counter not advanced) → refused; with a fresh assertion → `OWNER_KEY_REVOKED` appended once, owner emailed.
- `mo-sec` black-box A253 (when the route exists): a `harness.Browser` that is signed in and holds the CSRF token but presents no passkey cannot revoke; the key stays active in `/log` and `moochy pending`/pool still seals to workers it approved. A253 is marked `gap` until then.

## Residual

A stolen session can still *add* a passkey while one is live only with the live passkey's co-signature (safe), rename devices, and read Settings. It cannot revoke the owner key, so it cannot reach the first-key state. The remaining first-key exposure is A224 (email-change hold is the only gate on the very first owner key of an account) — unchanged by this note.
