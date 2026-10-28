# 15 — Gift links, QR codes and credits

> Product owner, 2026-10-28: "at the end of the day it should be extremely easy to give away some tokens just by generating a link or a QR code and that can be scanned; carefully plan all that." "For people that don't have the compute but still want to donate real money that will actually be used in AI tokens compute; plan the best way to handle that and review carefully." Clarification: "it should be possible to add credits in the platform dashboard and/or give away an amount of AI tokens from a QR code, one-time scan of course."
>
> Nothing in the trust model changes. The relay still sees only ciphertext. Every donation still needs the maintainer's `DONOR_APPROVED` (owner key or passkey). Donors' device caps still apply, and the key-log format is unchanged. Credits add one new actor: **Moochy Credits**, a donor account run by Moochy, with Moochy's own provider key, on its own hosts.

## 1. Decisions

| # | Decision |
|---|---|
| D1 | **Ship first: a QR code for every donate link** (`…/qr.svg`, a QR tab in the showcase studio, a QR item in the share menu). It is a pure function of the URL: no data, no money, no new trust. Then gift links paid from the giver's key. Credits (§5) are built next behind a flag that is off by default and use a fake Stripe server and Stripe test mode. Go-live waits for §5.10. |
| D2 | **A gift is one object.** It is single-use and has a fixed one-off amount. Its `source` is `tokens` (the giver's own key, served by their devices) or `credits` (the giver's balance, served by Moochy Credits). No monthly or multi-use gifts. |
| D3 | **A claimed gift is an ordinary donation with a total instead of a monthly limit.** A `pledges` row with `total=1`, `ends_at` and `gift_id`, accepted with the usual `/decide` passkey. A credits gift to a project that already accepted Moochy Credits is active at once. |
| D4 | **Credits are spent through Moochy Credits.** Payments go through Stripe Checkout (no card data on Moochy). Each payment buys credits worth the payment minus the Stripe fee and the provider's fee, at cost. Credits are spent by donating or gifting them. One Moochy Credits donation per target is served by Moochy's own worker on an operator host with Moochy's OpenRouter key. Every cent is visible in public receipts and on a public ledger page. Moochy takes nothing. |
| D5 | **QR rendering:** `rsc.io/qr` (BSD-3, no dependencies), allowed only in `relay/internal/web/qr` (AGENTS §4 amendment). Desktop app: the Rust `qrcode` crate with `default-features = false`. The `moochy` CLI prints URLs only and draws no terminal QR. |

## 2. A QR code for every donate link

### 2.1 URL and output

- **Routes:** `…/qr.svg` everywhere `button.svg` exists: projects (`/p/github/o/r/qr.svg`, legacy `/p/o/r/qr.svg`, `/p/gitlab/g/sub/r/-/qr.svg`), orgs (`/org/…/qr.svg`), people (`/people/…/qr.svg`).
- **What it encodes:** the canonical `…/donate` URL on the configured `BaseURL`, never the Host header (A234). No database read, so there is no existence oracle. Unclaimed and unknown targets get a valid QR too; the donate page says "not on Moochy yet".
- **SVG:** one `<path>` of dark modules, ink on paper, a 4-module quiet zone, `shape-rendering="crispEdges"`, `viewBox` in modules, `<title>Scan to donate tokens to {name}</title>`. Always dark on light (scanners struggle with inverted codes), so there is no theme option. ECC level M.
- **Query:** only `size=s|m|l` (128, 256 or 512 px). Anything else is refused with 400, like `chart.svg`.
- **Headers:** as the badge (`web.go:1277-1280`): `Content-Security-Policy: default-src 'none'`, `nosniff`, `Cache-Control: public, max-age=86400`. Per-IP rate limit like the button.

### 2.2 Code changes

| File | Change |
|---|---|
| `relay/internal/project/project.go:28` | `Actions` += `"qr.svg"` |
| `relay/internal/web/web.go:685` | `projectGET["qr.svg"] = (*Handler).qrSVG` |
| `relay/internal/web/orgs.go:122`, `:339` | `orgActions` += `qr.svg`, a case next to `button.svg`; the same in the people switch |
| `relay/internal/web/qr/qr.go` (new, ~60 lines) | `SVG(text string, px int) []byte` over `rsc.io/qr.Encode(text, qr.M)`; unit test with an ISO 18004 vector and the 2,953-byte bound |
| `relay/internal/web/button.go:266` (`studioData.Tab`) | A third studio tab, `qr`: preview, "Download SVG", a printable card (`@media print`: QR, "Scan to donate tokens to {name}", moochy.dev), Markdown/HTML snippet |
| `relay/internal/web/share.go:216` (`shareFor`) | A "QR code" share item linking to `qr.svg` (no JS) |
| `cli/crates/node/src/button.rs` | `moochy button --qr [--repo|--org|--person]` prints the `qr.svg` URL and a Markdown snippet; offline from the git remote |
| `relay/AGENTS.md` §4 | "`rsc.io/qr` (only in `relay/internal/web/qr`)" |
| `docs/guides/donate-button.md`, `moochy-donate-button` skill | A "QR code" section |
| Desktop app (plan 14 §2.3, Projects tab) | "QR code" per project, rendered locally with `qrcode` (svg), "Save SVG" |

### 2.3 Encoder choice

`rsc.io/qr` is small, has no dependencies and is pure computation over our own URL. It beats about 400 lines of Reed–Solomon, masking and version tables we would own. The in-tree encoder is the fallback if the amendment is refused. A terminal QR in `moochy` is rarely scanned and grows the binary: not now.

## 3. Gift links and QR codes

### 3.1 Shape

- Link `https://moochy.dev/g/{t}`, `t` = 22 characters of base64url (128 random bits): short enough for a version 3–4 QR at ECC M (stickers), enough for an online-only bearer token behind a rate limit. Box-token pattern (`edge/box.go:137`, `sched/box.go:201`): shown once, only `SHA-256(t)` stored.
- **Single-use:** the first account to complete a claim gets it.
- **Fixed amount:** $1–$1,000 for `tokens`; up to the available balance for `credits`.
- **Expiry:** 30 days by default, 90 at most. Revocable until claimed.
- **Optional policy:** models and maximum reasoning effort (validated like `pledgeForm`, `forms.go:394`), visibility (default public), a note ≤ 140 characters (`CleanReason`, `edge/donations.go:353`).
- **Spend window:** a claimed token gift is a total donation that ends 12 months after the claim (`ends_at`). A credits gift is an allocation that returns to the giver's balance when unused after 12 months (§5.6).
- **The giver keeps control:** they can stop a claimed gift like any donation; unused tokens never left their account; unused credits return to their balance.
- **Lost link:** "Replace link" rotates the token; the old link dies.

### 3.2 Flows

**Giver, web.** Donations → "Gift tokens" (`GET /gifts`): amount; "Pay with: my API key / my credits" (credits only when on); note; expiry. `POST /gifts` shows a once-only page: the link with Copy, an inline server-rendered QR (the token never appears in a second URL), "Download SVG" (`data:` link), a printable gift card, and "Anyone who scans this first can claim it. Treat it like cash." `/gifts` lists gifts (open, claimed by {handle} for {target}, revoked, expired) with Revoke and Replace link.

**Giver, CLI.** `moochy gift create 20 [--credits] [--note …] [--models …] [--expires 30]` prints the link ("Shown once. Anyone with this link can claim it."); `moochy gift list`; `moochy gift revoke gf_…`.

**Giver, desktop.** Donations → "+ Gift tokens": the same form, then a big QR (`qrcode`), Copy, Save SVG.

**Claimer, web (one tap plus a passkey when signed in).**
1. Scan → `GET /g/{t}`. Signed out: "{giver or Someone} gives $20 of AI tokens to an open-source project. Claim it for yours.", the note, the models, sign-in with `next=/g/{t}`. A GET never changes state (unfurlers and link scanners are harmless).
2. Signed in: the claimer's eligible targets (claimed repos, claimed orgs, own person profile; preselected when only one) and **Accept the gift** (`POST /g/claim`: csrf, t, target). No eligible target: "Add your project first" → `/claim?next=/g/{t}` (the gift is not reserved meanwhile).
3. **tokens:** a pending total donation from the giver (`via=gift`), then 303 to `/decide/{p}?a=accept` (`oauth/decide.go:139`); one passkey touch appends `DONOR_APPROVED`. Without a passkey the page shows `moochy approve …`. **credits:** active at once when the target already accepted Moochy Credits; otherwise the Moochy Credits donation is pending, accepted once per target forever.

**Claimer, CLI.** `moochy gift claim <link|token> --repo o/r | --org … | --person …` (RPC `ClaimGift`); when pending and an owner key is present, it runs the existing approve path (decoded body and Lookup, A217/A218), one passphrase prompt.

**Claimer, desktop.** Paste the link: the app opens `/g/…` in the browser (owner-key actions stay on the web, plan 14 §2.2).

**Undo.** A claim whose donation is declined or expires unanswered (30 days, §16.6) is undone: the link works again until its own expiry; credits return to the hold.

### 3.3 Abuse

| Threat | Counter |
|---|---|
| Link leaked publicly | Single-use; the giver sees who claimed it for what and can stop; device caps and the provider's limit still bound `tokens` |
| Private or junk repo (farming) | Only claimed Moochy targets (public repos, ADR-31); the repo (for org/person: at least one covered repo) is not a fork, not archived and ≥ 30 days old, read with the claimer's fresh sign-in token (§19.2a). ≤ 3 claims per account per day, ≤ 10 live gift donations per account |
| Self-claim or sybil | `self_gift` when giver and claimer are the same account or share a linked identity, a confirmed email or a device (A297, `source.selfSponsor`, extended to repo and org targets) |
| Giver already donates to the target | Token gift: that target is refused ("alice already donates to this project; pick another"). Credits: one more allocation |
| Double claim | Claim runs in the scheduler actor with the guard `claimed_at IS NULL` |
| Token guessing | 128 bits; 30/min per IP on `/g/`; unknown, used, expired and revoked tokens get the identical 404 |
| Token in logs or Referer | `logPath(r)` redacts `/g/…` at `web/web.go:1448` and `oauth/oauth.go:546,550,720`; the claim POST carries `t` in the body; `/g/` pages use `pinHeaders` (`Referrer-Policy: same-origin`, `no-store`); only the hash is stored; `gf_` ids in logs and exports |
| Pending flood | `maxPendingPerRepo` (`sched/admin.go:483`) |

### 3.4 Unfurl preview

`/g/{t}`: `og:title` "A gift of AI tokens on Moochy"; `og:description` "{giver or Someone} gives ${N} of AI tokens to an open-source project. 100% free."; `og:url` the gift URL; `og:image` a static `/static/og-gift.png` (no token in any image URL).

### 3.5 Records and notifications

No new key-log kind (acceptance is `DONOR_APPROVED`). Decisions trail: `requested` with `via=gift`; new `completed` at `ends_at`. Emails: `GiftClaimed` to the giver; `DonationEnded` reused for `completed`; the maintainer's "new donor waiting" email is skipped for `via=gift` (the claimer is on the decide page).

### 3.6 `gifts` table (migration 0022)

`id` (`gf_`+ULID), `giver_id`, `token_hash` (UNIQUE), `source` (`tokens|credits`), `amount_uusd` (1,000,000–1,000,000,000), `per_task_cap_uusd`, `policy`, `visibility`, `note`, `expires_at`, `revoked_at`, `created_at`, `claimed_at`, `claimer_id`, `target_id`, `pledge_id`, `allocation_id`. Index `(giver_id, created_at)`. At most 20 open gifts per giver.

### 3.7 RPCs (link.proto, additive)

`CreateGift{request_id, source, amount_uusd, per_task_cap_uusd, models, max_effort, visibility, note, expires_days}` → `{gift_id, url}` (the only time the URL is returned); `ListGifts`; `RevokeGift{gift_id, replace}` → `{url?}`; `ClaimGift{token, repo_slug|org|person}` → `Donation`. Edge handlers beside `Donate` (`edge/donations.go:194`) on `donationSession`; scheduler events `EvGiftCreate`, `EvGiftRevoke`, `EvGiftClaim` in `sched/gift.go`. Web: `GET/POST /gifts`, `POST /gifts/{id}/revoke`, `GET /g/{t}`, `POST /g/claim`.

## 4. Total donations (gifts and credits)

| File | Change |
|---|---|
| `relay/internal/store/migrations/0022_gifts.sql` | `pledges` += `total INTEGER NOT NULL DEFAULT 0 CHECK (total IN (0,1))`, `ends_at INTEGER`, `gift_id TEXT`; the `gifts` table |
| `relay/internal/sched/state.go:153` | `Pledge` += `Total`, `EndsAt`, `Gift` |
| `relay/internal/sched/money.go:38` | `rollPledge`: a total donation never rolls; `Budget` is the lifetime total |
| `relay/internal/sched/core.go:1180` | the sweep ends a live donation at `ends_at` (trail `completed`, `DonationEnded`) |
| `relay/internal/sched/admin.go:504` | `newPledge` options `Total`, `EndsAt`, `Gift`; per-donor limits skip the Moochy Credits user |
| `spec/proto/moochy/v1/link.proto:564` `Donation` | `bool total = 24; int64 ends_at_ms = 25; string gift_id = 26; bool credits = 27;` |
| Worker (`worker.rs:381`) | No change |
| Displays (web, `/decide`, TUI, desktop) | "Total $20 · ends 2027-10-28" instead of "monthly limit" |

## 5. Credits: money that becomes tokens

### 5.1 Options

| Option | Money really buys tokens? | Verdict |
|---|---|---|
| The project's own rails (GitHub Sponsors, Open Collective) | No | A link on project pages ("Fund {project} directly"), not the answer |
| Provider-native gifting | Not offered by any supported provider | — |
| **Moochy Credits** (Stripe Checkout → balance → Moochy-run donor node) | **Yes, provably** (public signed receipts, public ledger, monthly reconciliation) | **Recommended**; keeps "100% free" (at cost, fees disclosed) and "keys stay on your machine" (users' keys untouched) |
| A fiscal host (Open Collective) for the same fund | Yes | Fallback without a legal entity; ~10% host fee |
| Paying token donors (marketplace) | Yes | Rejected: a payments business, breaks "free" |
| Crypto | — | Rejected |

### 5.2 How it works

1. **Add credits** (`/credits`): $10 / $25 / $50 / $100 or $5–$500 custom; balance ≤ $1,000. `POST /credits/checkout` creates `credit_purchases` (`cp_…`) and a Stripe Checkout Session; 303 to its URL (host must be `checkout.stripe.com`).
2. **Webhook** `checkout.session.completed` (`payment_status=paid`): read the real fee, then `credits_uusd = floor((amount_cents − stripe_fee_cents) × 10_000 × 1e6 / (1e6 + provider_fee_ppm))` (OpenRouter 5.5% → 55,000 ppm). Available after a **72 h hold**.
3. **Spend:** "Pay with: my credits" on donate forms, `moochy donate --credits 20 --repo o/r`, or a credits gift. Each spend is a `credit_allocations` row that raises the target's single Moochy Credits donation (`total=1`). The first allocation needs the owner's acceptance once; later ones are instant.
4. **Serving:** Moochy Credits' worker devices serve like any donor.
5. **Per-payer accounting is computed:** the donation's `Spent` is split over allocations oldest-first (`relay/internal/credits/fifo.go`, pure, table-tested), each linked to its receipts.
6. **Stop:** the payer stops an allocation; the rest returns to their balance.

### 5.3 Fraud

- Credits never go to a target the payer owns or maintains (A297, extended).
- Card testing: sign-in with a confirmed email, card-only Checkout with Radar, $5 minimum, ≤ 3 purchases a day.
- Disputes and early-fraud warnings debit the unconsumed part (stopping the newest allocations when needed) and freeze the account's credits; an early-fraud warning also refunds the unconsumed part. The 72 h hold bounds stolen-card spend.
- Exposure capped three times: the node's `safety --monthly-limit`, OpenRouter's per-key limit, a provider balance of about two weeks of spend.

### 5.4 Data model (migration 0023)

`credit_purchases` (`cp_`, amounts, fees, `credits_uusd`, status, unique Stripe session and payment intent, `paid_at`, `available_at`, `expires_at`, `refunded_cents`, `visibility` default anonymous); `credit_entries` (append-only; balance = SUM; kinds purchase, hold, release, allocate, return, refund, chargeback); `credit_allocations` (`ca_`, target, pledge, amount, gift, `ends_at`, `ended_at`); `stripe_events` (dedupe); `credit_treasury` (operator top-ups and reconciliations, public); `users.credits_frozen_at`. The scheduler actor owns balances so an allocation and the donation's budget commit together.

### 5.5 Stripe (`relay/internal/credits/`, closed)

No SDK: `net/http`, 10 s timeout, pinned `Stripe-Version`, `Idempotency-Key` on every POST. Calls: create Checkout Session, read the payment intent's balance transaction, refunds, balance. Webhook `POST /hooks/stripe`: 64 KiB limit, `Stripe-Signature` HMAC-SHA256 over `t.body` with 300 s tolerance and constant-time compare, dedupe by event id, the session must match a known `cp_` with the same amount and currency. Events: `checkout.session.completed`, `checkout.session.expired`, `charge.refunded`, `charge.dispute.created`, `radar.early_fraud_warning.created`. Secrets are systemd credentials (`stripe-key`, `stripe-webhook-secret`). Flags: `--credits` (off: routes 404, no Stripe calls), `--credits-user`, `--credits-provider-fee-ppm`, `--credits-hold`, `--stripe-api-base` (dev); an `sk_live_` key is refused without `--credits-live`. A fake Stripe in `relay/internal/credits/stripefake/` serves dev and E2E.

### 5.6 Refunds and unspent money

| Case | What happens |
|---|---|
| Target declines or never answers (30 days) | Allocations return to the givers' balances; gifts are undone |
| Allocation unused 12 months, or the target's claim released | The rest returns to the balance |
| "Refund my unused credits" | Oldest purchases first, at the net ratio; Stripe keeps its fee (stated before payment) |
| A purchase turns 12 months old | Its unconsumed part is refunded automatically, with an email |
| Refund fails | Listed on the public ledger as pending; settled by hand (runbook) |

### 5.7 Moochy Credits node and key custody

A normal Moochy account (handle `credits`, reserved) owned by the product owner, owner key on a hardware token. Two operator VMs, **not the relay host**, run the released `moochy` client with lockdown as its worker devices; the OpenRouter key is entered with `moochy keys add openrouter --key-stdin` into the host's secret store, with an OpenRouter per-key limit and `safety --monthly-limit`. The relay holds the Stripe keys and never the provider key; the node hosts hold the provider key and never Stripe. Disclosure on the accept page and `/credits`: "Moochy Credits is served by Moochy's own computers with Moochy's own provider key. Like any donor's computer, they see the requests they serve; Moochy's relay still sees only ciphertext." ADR-51: Moochy Credits is a donor run by Moochy with its own key; ADR-30 (never host donor keys) is unchanged. Operator commands: `relay admin credits topup` and `relay admin credits reconcile`.

### 5.8 Transparency

Public `/credits/ledger`: money in, Stripe fees, provider fees, credits issued, used (Moochy Credits receipts, each linked), refunded, held; cash at Stripe and the provider balance; top-ups with invoice hashes; the monthly reconciliation. Payers are anonymous unless they chose "Show my handle". Private `/credits`: balance, holds, purchases with fees, allocations with used/left/receipts, Stop, Refund unused, Add credits, Gift credits. CLI: `moochy credits [--json]`, `moochy credits add [20]` (opens the browser; cards only ever there), `moochy donate --credits 20 …`. Desktop: a balance card; "Add credits" opens `/credits`.

### 5.9 Copy

- "Add credits to give AI tokens without your own API key. Moochy keeps nothing. The card fee (Stripe, 2.9% + 30¢) and the provider's fee for buying tokens (OpenRouter, 5.5%) come out of your payment, and the rest becomes credits: $20 → $18.12 of tokens. Every request your credits pay for has a public receipt. Unused credits are refunded after 12 months, or any time you ask."
- "Moochy is 100% free. Credits are optional and at cost." "This is not a tax-deductible donation."
- "Your API keys stay on your machine. Credits are spent by Moochy's own computers with Moochy's own provider key, never stored on the servers that route requests."
- Gift: "Anyone who scans this first can claim it. Treat it like cash."

### 5.10 Before go-live (product owner)

1. A legal entity in a Stripe-supported country, bank account, terms, privacy and refund policy.
2. Counsel on purchase-at-cost vs donation framing, VAT/sales tax, stored-value and unclaimed-property rules.
3. An activated Stripe account and its webhook secret, configured by the owner.
4. An OpenRouter account in the entity's name, written confirmation that serving free third-party requests is within their terms, a card for top-ups.
5. Two operator hosts for the Moochy Credits node and a hardware owner key.

Built and tested now: everything in §5 behind `--credits` (off), fake Stripe in E2E, Stripe test mode by hand, a dev Moochy Credits node against the fake OpenRouter provider.

## 6. Scenarios (E130–E138 are taken)

| E | Proves |
|---|---|
| E139 | `qr.svg` for every target kind decodes to the canonical donate URL on `BaseURL` whatever the Host header; unknown targets still give a QR; unknown params 400; badge headers; no script or external reference |
| E140 | Studio QR tab, printable card, share-menu item (no JS); `moochy button --qr`; desktop smoke renders the QR |
| E141 | Gift create (web, CLI, both sources): link shown once; no token in the DB or any log; list, revoke, Replace link; 21st open gift refused |
| E142 | Token gift on the web: unfurler GETs change nothing; sign-in → pick → `/decide` passkey → `DONOR_APPROVED`; serving stops at the total; `completed` at `ends_at`; `GiftClaimed` once |
| E143 | `moochy gift claim` with an owner key: pending → approved in one command (A218); org and person targets |
| E144 | Abuse: second claim, expired, revoked, tampered → identical 404; self-claim refused; fork/archived/young repos refused; rate limits; existing donation conflict; undo on decline; giver stops a claimed gift |
| E145 | Credits off by default: routes 404, RPCs unimplemented, no Stripe calls; `sk_live_` without `--credits-live` refuses to start |
| E146 | Add credits end to end with fake Stripe: fee-exact credits, hold, donate credits, owner accept, Moochy Credits node serves, FIFO split matches receipts |
| E147 | Webhook security: unsigned, stale, wrong secret, replay, mismatch, unknown session → no effect; 64 KiB limit |
| E148 | Credits gift: hold, release, instant activation for an accepted target, undo on decline |
| E149 | Refunds: decline, stop, refund unused, 12-month auto-refund, failed refund on the ledger |
| E150 | Fraud: dispute and early-fraud clawback, freeze, self-donation refused, purchase limits |
| E151 | `/credits/ledger` totals equal the sums from `/dev/state`; anonymous payers never named |
| E152 | CLI `credits`, `donate --credits`, `gift` and the desktop gift screen end to end against fake Stripe |

## 7. Rollout

1. QR for donate links.
2. Total donations and token gifts (0022, sched, `/g`, CLI, emails, E139–E144).
3. Credits behind the flag (0023, `credits`, fake Stripe, credits gifts, ledger, E145–E152); security pass over `/g`, `/hooks/stripe` and the Moochy Credits node.
4. Owner prerequisites (§5.10), then `--credits-live` with a $100 balance cap.
5. Desktop screens in the next client release.

## 8. Open questions (defaults apply until answered)

| # | Question | Default |
|---|---|---|
| OQ1 | Gift link expiry | 30 days, max 90 |
| OQ2 | Spend window | 12 months |
| OQ3 | Eligibility | Public, not a fork, not archived, ≥ 30 days old; no license check |
| OQ4 | What a claimer may pick | Own repos, orgs, own person profile |
| OQ5 | QR module | `rsc.io/qr` with the AGENTS amendment |
| OQ6 | Terminal QR | No |
| OQ7 | Credits provider | OpenRouter (one key, all models, exact cost) |
| OQ8 | Who pays fees | The payer, disclosed with an example |
| OQ9 | Hold | 72 h |
| OQ10 | Purchase limits | $5–$500, $1,000 balance, 3 a day |
| OQ11 | Unused credits | Refund on request; auto-refund at 12 months |
| OQ12 | Payer visibility | Anonymous by default |
| OQ13 | Leaderboard credit | No; Moochy Credits is one donor |
| OQ14 | Legal front | Own entity with Stripe; fallback a fiscal host |
| OQ15 | Recurring credits or gifts | No |
| OQ16 | Self-donation or self-claim | Refused |
