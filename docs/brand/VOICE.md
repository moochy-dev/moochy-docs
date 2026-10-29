# Moochy voice and vocabulary (product owner review, 2026-10-01; gifts, 2026-10-28)

Normative for every user-facing word: web app, landing page, CLI output and help, errors, toasts, guides, README. Internal identifiers in code and protocol (`pledge_id`, `PoolSync`, …) do not change.

## Positioning (product owner decision, 2026-10-28)
Moochy lets people give AI tokens from their own provider account (Anthropic, OpenAI, OpenRouter, DeepSeek, xAI) or their own GPU. The tokens go to open-source projects, organisations and maintainers, or to anyone with a link or a QR code.

- Open source comes first: in examples, in the order of options, and in images. Personal gifts are the second path.
- Tagline: "Share your AI tokens without sharing your API key."
- One-liner: "Give AI tokens from your own API key or GPU to open-source projects or to anyone. Your key never leaves your machine, and every request has a signed public receipt. Free."
- Do not say that tokens can go only to open source. "Donate tokens to the open-source projects you use" is fine as one use.

## Key phrases
**Donate tokens.** Primary call to action, button label, headline language for a project, an organisation or a maintainer. Never "donate AI compute" or "donate compute".

**Gift tokens.** The call to action for a single-use gift link or QR code of a fixed amount. The person who gets it presses **Claim the gift**.

## Vocabulary

| Internal / old | User-facing |
|---|---|
| pledge | donation (a monthly token donation to a project) |
| create a pledge / pledge to | Donate tokens / donate tokens to |
| pledges | your donations |
| budget, budget_per_period | monthly limit |
| per-task cap | limit per request |
| spent | used |
| reserved | in progress |
| headroom | left this month |
| reclaim | stop donating (ends the donation) |
| pause / resume | pause / resume |
| pending approval | waiting for the maintainer |
| approve a donor | accept a donor |
| decline | decline |
| pool | donations available to the project (avoid "pool" in headlines) |
| station | Dashboard |
| maintainer console | Project settings |
| Node, worker, gateway | the Moochy app on your machine; "your device" in lists |
| firewall | safety checks |
| max effort | maximum reasoning effort |
| visibility public / pseudonymous / anonymous | Show my handle / Show a pseudonym / Hide me |
| goal | monthly goal |
| receipt / projection | receipt / public receipt |
| key log | public key log |
| relay | do not mention to newcomers; "relay" only on technical pages |
| µ$ | never shown; show dollars and an approximate token count |
| gift | Gift tokens (button); "a gift" in text |
| gift URL, `/g/{t}` | gift link; its picture is the QR code |
| claim a gift | claim; button **Claim the gift** |
| personal target, `personal` | For my own use |
| total donation (`total = 1`) | Total, for example "Total $20 · ends 2027-10-28" (in place of a monthly limit) |
| `ends_at` | ends on, for example "The gift ends on 28 October 2027" |
| Moochy Credits, credits balance | credits. Paying money is built but off: do not name credits on public pages, the landing page or the docs front pages until they are on |

## Tone
- Plain, short, concrete sentences. Sentence case for headings and buttons.
- Say what happens and what it costs. Prefer verbs: "Donate tokens", "Stop donating", "Add a device".
- Warm, not cute. The mascot speaks rarely, if ever.
- Banned: seamless, unlock, empower, supercharge, revolutionize, effortless, leverage, cutting-edge, AI-powered, next-gen, magic, game-changer; exclamation marks; emoji.
- Numbers: "$20 a month", "about 2.4M tokens", "3 of 4 slots in use".
- Security claims stay precise and honest: "Your key never leaves your machine." "The relay only sees encrypted bytes." No "military-grade", no "100% secure", no "zero-knowledge".
