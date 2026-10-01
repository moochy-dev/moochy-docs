# Donor guide

You give an open-source project a monthly budget on **your own** LLM API account. Your machine runs the `moochy` client, which receives encrypted tasks from the project's maintainers, checks them, and calls your provider with your key. Nothing is pre-paid and nothing is transferred: your provider bills you only for tasks actually served, never above the limits you set.

Target: first served task in under 5 minutes.

---

## 1. Install

The `moochy` client is open source (Apache-2.0). Prebuilt, signed binaries for macOS, Linux, and Windows are published with each release, along with a Homebrew tap, an npm wrapper, and a container image. To build from source (Rust stable):

```sh
# in a checkout of the public moochy-cli repository
cd cli
cargo build --release          # binary: target/release/moochy
```

Check what you run: release artifacts carry Sigstore signatures and SLSA provenance, and builds are reproducible. See the [FAQ](faq.md#how-do-i-check-the-binary-i-run).

## 2. Sign in and register this machine

```sh
moochy login --roles worker
```

The command prints a short code such as `WXYZ-1234` and a URL. Open the URL, sign in with GitHub or GitLab, and enter the code. The first time, you choose your **Moochy username** (see [§10](#10-your-username)). The machine then gets its own keys; they never leave it.

Use `--roles gateway,worker` if you also want to use pooled compute from this machine.

## 3. Add a provider key

Use a **dedicated API key** for Moochy, with a **spending limit set at the provider** (next section). The prompt keeps the key out of your shell history; it goes to your OS keychain and is never sent to Moochy.

```sh
moochy keys add anthropic      # or: openrouter, deepseek, openai
```

For scripts: `printf '%s' "$KEY" | moochy keys add anthropic --key-stdin`.

The client validates the key with a free call to the provider's models endpoint and offers exactly the models the key can use.

| Provider | What you donate | Notes |
|---|---|---|
| **Anthropic** | Claude models | Serves Anthropic-format clients (Claude Code, Claude Agent SDK) and MCP delegation |
| **OpenRouter** | Hundreds of models from many vendors with one key | Serves both API formats. Paid add-ons such as web search and "online" variants are blocked unless your pledge opts in |
| **DeepSeek** | DeepSeek models | Very low prices: a small pledge goes a long way. Serves both API formats |
| **OpenAI** | OpenAI models | Requests are sent with `store: false` |

Only API keys are accepted. Consumer subscription credentials (chat-app plans) are refused: provider terms do not allow sharing them, and your account would be at risk.

## 4. Set a spending limit at your provider (strongly recommended)

This is the most important safety step, and it does not depend on Moochy at all. Even if every piece of Moochy failed, your provider stops at this limit.

| Provider | How |
|---|---|
| **Anthropic** | In the Anthropic Console, create a separate **workspace** (for example `moochy`), set its **monthly spend limit**, and create the API key inside that workspace |
| **OpenRouter** | In OpenRouter's key settings, create a key with a **credit limit** |
| **DeepSeek** | DeepSeek bills a prepaid balance. Use a separate account, or top up only what you want to donate: the balance is your hard limit |
| **OpenAI** | Create a dedicated **project**, set its monthly **budget** in the project's limits, and create the key in that project. With prepaid billing, the credit balance is a hard stop as well |

## 5. Set this machine's monthly cap (required)

The client enforces its own cap on every task, before calling your provider, even if the Moochy relay misbehaved. There is no default: you choose it. Amounts are in micro-dollars (1 USD = 1,000,000).

```sh
moochy config set device_monthly_cap_uusd 25000000   # $25 per month, across all pledges
moochy config set slots_max 4                        # concurrent tasks (1–64)
```

If you run several machines, each has its own cap; they add up.

Your worst case is the **smallest** of three independent limits:

1. your pledge budgets, enforced by the relay;
2. this device cap, enforced by the client on your machine;
3. your provider spend limit, enforced by your provider.

## 6. Start the node

```sh
moochy up                      # start in the background
moochy service install         # start at login/boot (launchd, systemd user unit, Windows)
moochy status                  # connection, slots, budgets, pending approvals
```

## 7. Donate

Pick a project on moochy.dev and press **Donate compute**, or:

```sh
moochy donate
```

A pledge has:

| Setting | Meaning |
|---|---|
| Monthly budget | The ceiling for this project per month, in dollars. Not a payment: nothing leaves your account until a task is served |
| Per-task cap | Maximum one request may cost. Default $5. A request whose worst case is above it is refused |
| Models | Which models the project may use on your key (wildcards per family) |
| Maximum effort | `low` … `max` |
| Features | Opt-ins such as `images`, `documents`, `long_context`, `fast` |
| Schedule | Optional: only serve at certain times (for example nights and weekends). Outside the window your machine simply isn't offered work |
| Visibility | `public`, `pseudonymous`, or `anonymous` on the project's public pages |

The pledge stays **pending** until the repository owner approves you with a signature from their own device. `moochy status` then shows "serving".

## 8. Pause and reclaim

| You want to | Do | Effect |
|---|---|---|
| Stop all serving from this machine now | `moochy pause` (`moochy resume` to undo) | Instant, works offline, no web login needed. Running tasks are aborted |
| Pause one pledge | Donor Station (`/station`) → pause | No new tasks for that project; reversible |
| Give less | Lower the pledge budget | Effective within milliseconds |
| Stop donating to a project | Station → reclaim (ends the pledge) | No new tasks; running ones finish and are recorded |
| Revoke a machine | `moochy keys revoke <device>` or the devices page | Its keys stop working immediately |

Reclaiming is instant because nothing was ever transferred. "Donated" money never leaves your account until a task is served.

## 9. See what your key was used for

```sh
moochy journal                 # tasks served: project, member pseudonym, model, usage, cost, status
moochy journal --follow        # live
moochy journal --full          # with prompt and output text, if you enabled full-text journaling
moochy audit --provider        # compare the journal with your provider's own usage report
moochy verify <receipt_ref>    # verify a public receipt against your logged key
```

The journal is local to your machine and kept 90 days. By default it stores metadata only. To also keep the text of requests and responses on your machine: `moochy config set journal_full_text true`.

Every served task produces a receipt signed by your device. The project's public page shows a short version (model, cost, day, your name per your visibility setting), never prompts, timestamps finer than a day, or device names.

## 10. Your username

Every account has one unique username on moochy.dev:

- 3–32 characters: lowercase ASCII letters, digits, and single hyphens, starting and ending with a letter or digit. No look-alike characters from other alphabets, so nobody can impersonate you with a Cyrillic "а".
- Unique regardless of case: `Alice` and `alice` are the same name.
- At first sign-in it defaults to your GitHub/GitLab login if that is valid and free; otherwise you pick one. Moochy never silently adds a suffix.
- Some words are reserved (`admin`, `support`, `moochy`, `security`, route names, …).
- You can rename at most once every 30 days. Your old name is retired forever (nobody else can take it) and redirects to the new one for 90 days.

## 11. Troubleshooting

| Symptom | Check |
|---|---|
| `waiting for approval` for a long time | The owner has not signed your approval yet. The project page shows whether the owner is active |
| Nothing is served | `moochy status`: device cap reached? schedule closed? paused? key invalid? |
| Provider errors | `moochy doctor` checks the keychain, connectivity, clock, provider key health, and the service |
| Unexpected spend | `moochy pause`, then `moochy journal` and `moochy audit --provider`. Report anything suspicious with `moochy report <task_id>` |

Exit codes: 0 ok, 2 usage error, 3 authentication or approval refused, 4 network, 10 internal error.
