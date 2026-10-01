# Donate tokens

You give an open-source project a monthly limit on **your own** LLM API account. The Moochy app on your machine receives encrypted requests from the project's members, checks them, and calls your provider with your key. Nothing is paid in advance and nothing is transferred: your provider bills you only for requests your donation actually serves, and never more than the limits you set.

It takes about 5 minutes.

---

## 1. Install

The Moochy app is open source (Apache-2.0). Each release publishes signed builds for macOS, Linux, and Windows, a Homebrew tap, an npm package, and a container image. To build it yourself (Rust stable):

```sh
# in a checkout of the public moochy-cli repository
cd cli
cargo build --release          # the app: target/release/moochy
```

You can check what you run: release files are signed with Sigstore, carry SLSA provenance, and build reproducibly. See the [FAQ](faq.md#how-do-i-check-the-app-i-run).

## 2. Sign in and add this device

```sh
moochy login --roles worker
```

The command prints a short code such as `WXYZ-1234` and a link. Open the link, sign in with GitHub or GitLab, and enter the code. The first time, you choose your **handle** (see [Your handle](#10-your-handle)). This device then gets its own keys, which never leave it.

`--roles worker` lets this device serve your donations. Add `gateway` (`--roles gateway,worker`) if you also want to use donated tokens from it.

## 3. Add a provider key

Use a **separate API key** for Moochy, with a **spending limit at the provider** (next section). The prompt keeps the key out of your shell history. The key goes to your system keychain and is never sent to Moochy.

```sh
moochy keys add anthropic      # or: openai, openrouter, deepseek, xai
```

In scripts: `printf '%s' "$KEY" | moochy keys add anthropic --key-stdin`.

The app checks the key with a free call to the provider's model list, and offers exactly the models the key can use.

| Provider | What you donate | Notes |
|---|---|---|
| **Anthropic** | Claude models | Works with tools that speak the Anthropic format (Claude Code, Claude Agent SDK) and with delegation from any MCP client |
| **OpenAI** | OpenAI models | Requests are sent with `store: false` |
| **OpenRouter** | Hundreds of models from many companies, with one key | Works with both API formats. Paid extras such as web search and "online" models are refused unless you allow them in your donation |
| **DeepSeek** | DeepSeek models | Low prices, so a small monthly limit goes a long way. Works with both API formats |
| **xAI** | Grok models | Works with tools that speak the OpenAI format |

Only API keys are accepted. Logins from chat subscriptions are refused: providers do not allow sharing them, and your account would be at risk.

## 4. Set a spending limit at your provider (strongly recommended)

This is the most important safety step, and it does not depend on Moochy at all. Even if everything in Moochy failed, your provider stops at this limit.

| Provider | How |
|---|---|
| **Anthropic** | In the Anthropic Console, create a separate **workspace** (for example `moochy`), set its **monthly spend limit**, and create the API key inside that workspace |
| **OpenAI** | Create a separate **project**, set its monthly **budget** in the project's limits, and create the key in that project. With prepaid billing, your credit balance is also a hard stop |
| **OpenRouter** | In OpenRouter's key settings, create a key with a **credit limit** |
| **DeepSeek** | DeepSeek uses a prepaid balance. Use a separate account, or top up only what you want to donate: the balance is your hard limit |
| **xAI** | In the xAI Console, use a separate **team** for Moochy and create the key there. Buy prepaid credits only for what you want to donate (the balance is a hard stop), and set a monthly spending limit in the team's billing settings if your account offers one |

## 5. Set this device's monthly limit (required)

The app checks its own limit before every request, before calling your provider, whatever happens elsewhere. There is no default: you choose it.

```sh
moochy config set device_monthly_cap_uusd 25000000   # $25 a month, across all your donations
moochy config set slots_max 4                        # requests served at the same time (1–64)
```

The setting is written in millionths of a dollar: `25000000` is $25. If you use several devices, each has its own limit, and they add up.

The most you can spend is the **smallest** of three separate limits:

1. the monthly limit of each donation, kept by Moochy;
2. this device's monthly limit, checked by the app on your machine;
3. your spending limit at the provider, kept by your provider.

## 6. Start the app

```sh
moochy up                      # start in the background
moochy service install         # start at login (launchd, systemd user unit, Windows)
moochy status                  # connection, slots in use, limits, donations waiting for the maintainer
```

## 7. Donate tokens

Pick a project on moochy.dev and press **Donate tokens**, or:

```sh
moochy donate
```

A donation has:

| Setting | Meaning |
|---|---|
| Monthly limit | The most this project can use per month, in dollars, shown with an approximate token count. Not a payment: nothing leaves your account until a request is served |
| Limit per request | The most one request may cost. Default $5. A request that could cost more is refused |
| Models | Which models the project may use with your key (whole families allowed, for example all Claude Sonnet models) |
| Maximum reasoning effort | `low` … `max` |
| Extras | Opt-ins such as images, documents, long context, fast mode |
| Schedule | Optional: only serve at certain times, for example nights and weekends. Outside those times your device simply gets no requests |
| On public pages | **Show my handle**, **Show a pseudonym**, or **Hide me** |

The donation shows **waiting for the maintainer** until the project's owner accepts you, with a signature from their own device. `moochy status` then shows "serving".

## 8. Pause or stop donating

| You want to | Do | What happens |
|---|---|---|
| Stop serving from this device now | `moochy pause` (`moochy resume` to undo) | Immediate, works offline, no sign-in needed. Requests in progress are stopped |
| Pause one donation | Dashboard → the donation → **Pause** | No new requests for that project until you resume |
| Give less | Lower the monthly limit | Takes effect within milliseconds |
| Stop donating to a project | Dashboard → **Stop donating** | The donation ends. No new requests; requests in progress finish and are recorded |
| Remove a device | `moochy keys revoke <device>` or the Devices page | Its keys stop working immediately |

Stopping is immediate because nothing was ever transferred. Your money stays in your provider account until a request is actually served.

## 9. See what your key was used for

```sh
moochy journal                 # requests served: project, member pseudonym, model, tokens, cost, status
moochy journal --follow        # live
moochy journal --full          # with the text of requests and responses, if you turned it on
moochy audit --provider        # compare the journal with your provider's own usage report
moochy verify <receipt_ref>    # check a public receipt against your device's key in the public key log
```

The journal stays on your machine for 90 days. By default it keeps details only, not text. To also keep the text of requests and responses on your machine: `moochy config set journal_full_text true`.

Each served request gets a receipt signed by your device. The project's page shows a short public receipt: model, cost, the day, and your name as you chose. It never shows prompts, times finer than a day, or device names.

## 10. Your handle

Every account has one handle on moochy.dev, and no two accounts share one:

- 3–32 characters: lowercase letters `a–z`, digits, and single hyphens, starting and ending with a letter or digit. Letters from other alphabets are not allowed, so nobody can copy your handle with a look-alike such as a Cyrillic "а".
- Case does not matter: `Alice` and `alice` are the same handle.
- At first sign-in it is your GitHub or GitLab login, if that is valid and free; otherwise you choose one. Moochy never adds a number for you.
- Some words are reserved (`admin`, `support`, `moochy`, `security`, page names, …).
- You can change it once every 30 days. Your old handle is retired for good (nobody else can take it) and points to the new one for 90 days.

## 11. Troubleshooting

| What you see | Check |
|---|---|
| **Waiting for the maintainer** for a long time | The owner has not accepted you yet. The project page shows whether the owner is active |
| Nothing is served | `moochy status`: device limit reached? outside your schedule? paused? key invalid? |
| Provider errors | `moochy doctor` checks the keychain, connection, clock, provider key, and the service |
| Unexpected costs | `moochy pause`, then `moochy journal` and `moochy audit --provider`. Report anything suspicious with `moochy report <task_id>` |

Exit codes: 0 ok, 2 wrong usage, 3 sign-in or acceptance refused, 4 network, 10 internal error.
