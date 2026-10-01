# Hardening checklist — `relay/internal/web` (`mo-web`)

Owner: `mo-web`. Server-rendered HTMX pages, SSE hub, badges, the OAuth-backed console. Go stdlib only. The web attacker (A5) can make victims visit pages and controls repo/owner strings via GitHub. Attack ids → [attack-catalog.md](attack-catalog.md).

Rows WB7–WB10 and WB12 (sessions, OAuth, redirects, device approval) are owned by `mo-oauth` (`relay/internal/oauth/**`, CONTRACT §0); the rest by `mo-web`.

| # | Control | Attack | Proof |
|---|---|---|---|
| WB1 | `html/template` for every page and fragment; never `template.HTML`/`template.JS`/`template.URL` built from data (repo names, usernames, donor pseudonyms, goal text) | A50 | A50 |
| WB2 | Repo/owner/usernames validated at the source against `^[A-Za-z0-9._-]{1,100}$`; reject at claim/display otherwise | A50 | A50 |
| WB3 | Badge from a `text/template` that emits only digits and fixed strings with XML-escaping of every value; serve with `Content-Type: image/svg+xml`, `Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'`, `X-Content-Type-Options: nosniff`; no `<script>`/`<foreignObject>`/external refs | A51 | A50 |
| WB4 | State-changing requests require `HX-Request: true` **and** an exact `Origin` match; non-HTMX form fallback uses a per-session token | A52 | A52 |
| WB5 | CSP on pages: `default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'; img-src 'self' https://avatars.githubusercontent.com https://gitlab.com`; scripts only from self (htmx vendored); no `'unsafe-inline'` for scripts | A53, A57 | A53 |
| WB6 | Also send `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin` or `strict-origin-when-cross-origin`; never `Access-Control-Allow-Origin: *` | A53 | A53 |
| WB7 | Session cookie `__Host-`-prefixed: `Secure; HttpOnly; SameSite=Lax; Path=/`; 256-bit random id, store only its hash | A55 | U |
| WB8 | **Rotate the session id on login/privilege change** (session-fixation defense) | A55 | U |
| WB9 | OAuth: PKCE S256 + one-time `state` bound to a pre-login cookie; exact `redirect_uri`; reject a reused/mismatched `state` (RFC 9700) | A54 | U |
| WB10 | Redirect targets (`next=`) accepted only when they start with a single `/` (not `//`, not `/\`); else `/` | A56 | U |
| WB11 | Avatars via CSP `img-src` allowlist; if proxied, fixed host list, no redirects, size cap, `Content-Type` forced to `image/*` | A57 | U |
| WB12 | Device-approval page shows device name, requested roles, requester IP country and the code's age, with "only approve a code shown in your own terminal"; codes expire 10 min; poll route rate-limited (`slow_down`) | A59 | U |
| WB13 | Per-IP and per-session rate limits on POST routes and SSE; per-IP SSE cap (proposed 6) + global cap; SSE writes have a deadline and slow subscribers are dropped | A58 | U |
| WB14 | The exported `Source` interface is read-only; `mo-web` never writes the ledger and never sees content | A28 | E19 |
