# Donate tokens

You give an open-source project a monthly limit on **your own** LLM API account. The Moochy app on your machine receives encrypted requests from the project's members, checks them, and calls your provider with your key. Nothing is paid in advance and nothing is transferred: your provider bills you only for requests your donation actually serves, and never more than the limits you set.

It takes about 5 minutes.

---

## What runs on your machine

- **Inference only.** For each request, the app opens it, checks it, makes one HTTPS call to your provider with your key, and sends the encrypted response back. That is all a donor's machine ever does.
- **Nothing executes.** The app never runs a command, a tool, a script, or code from a request. Requests that ask the provider to run things on its side (server tools, code execution, remote MCP servers, file storage) are refused by the safety checks before your provider is called. Tool calls in a response go back to the maintainer, who runs them on their own machine.
- **The background app locks itself down.** Once it has loaded its keys and opened its connections, it removes its own ability to start programs, limits itself to its own state folder, and can connect only to your provider and to Moochy (Linux: seccomp and Landlock; macOS: Seatbelt). If it cannot lock itself down, it refuses to donate, and `moochy doctor` tells you why.
- **Each request is checked in a throwaway process** with no files, no network, and no keys, so a malformed request cannot reach anything that matters.
- **Use a separate provider key with a spending limit at the provider** ([how](#4-set-a-spending-limit-at-your-provider-strongly-recommended)). Then even a bug anywhere in Moochy cannot cost you more than that limit.
- **Your own GPU works too.** Instead of a provider key, you can donate tokens from a model running on your own hardware (Ollama, LM Studio, vLLM, llama.cpp): see [Donate from your own GPU](local-gpu.md).

## 1. Install

The Moochy app is open source (Apache-2.0). Each release of the public `moochy-dev/moochy-cli` repository publishes signed archives for macOS, Linux, and Windows, shell and PowerShell installers, a Homebrew formula, and the npm package `moochy`:

```sh
brew install moochy-dev/tap/moochy
```

Or build it yourself (Rust stable):

```sh
# in a checkout of moochy-dev/moochy-cli
cd cli
cargo build --release          # the app: target/release/moochy
```

You can check what you run: release files are signed with Sigstore, carry SLSA provenance, and build reproducibly. See the [FAQ](faq.md#how-do-i-check-the-app-i-run).

## 2. Sign in and add this device

```sh
moochy login --roles worker
```

The command prints a short code such as `WXYZ-1234` and a link. Open the link, sign in with GitHub or GitLab, and enter the code. The first time, you choose your **handle** (see [Your handle](#10-your-handle)). This device then gets its own keys, which never leave it. `--name laptop` gives the device a name you will recognise in your list of devices.

`--roles worker` lets this device serve your donations. Use `--roles gateway,worker` if you also want to use donated tokens from it.

## 3. Add a provider key

Use a **separate API key** for Moochy, with a **spending limit at the provider** (next section). The key is read from standard input, never from the command line, so it stays out of your shell history. It goes to your system keychain (or the encrypted key file) and is never sent to Moochy.

```sh
read -rs KEY                                       # paste the key, press Enter (nothing is shown)
printf '%s' "$KEY" | moochy keys add anthropic --key-stdin && unset KEY
```

Providers: `anthropic`, `openai`, `openrouter`, `deepseek`, `xai`, and `local` for your own GPU ([guide](local-gpu.md)). `moochy keys list` shows your keys; `moochy keys remove <provider>` deletes one. `moochy keys rotate` gives this device new keys of its own (not provider keys); the old ones stop working 24 hours later.

The app checks the key with a free call to the provider's model list, and offers exactly the models the key can use.

| Provider | What you donate | Notes |
|---|---|---|
| **Anthropic** | Claude models | Works with tools that speak the Anthropic format (Claude Code, Claude Agent SDK) and with `moochy_delegate` from any MCP client |
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

## 5. The safety step: this device's monthly limit (required)

Right after you add a key, the app asks two things before this device donates anything: a **monthly limit for this machine** (in dollars, across all your donations), and a checkbox confirming that you set a spending limit at your provider, or accept the risk. The app checks its own limit before every request, before calling your provider, whatever happens elsewhere. Until you finish this step, the device does not donate.

To do it (or change the limit) later, or without a terminal prompt:

```sh
moochy safety                                        # asks again
moochy safety --monthly-limit '$25' --accept-safety  # scripts and servers
moochy config set slots_max 4                        # requests served at the same time (1–64)
moochy config show                                   # check your settings
```

If you use several devices, each has its own limit, and they add up.

The most you can spend is the **smallest** of three separate limits:

1. the monthly limit of each donation, kept by Moochy;
2. this device's monthly limit, checked by the app on your machine;
3. your spending limit at the provider, kept by your provider.

## 6. Start the app

```sh
moochy up                      # start in the background
moochy status                  # connection, slots in use, donations
moochy doctor                  # keychain, connection, clock, provider keys, lockdown
moochy service install         # start it at login (systemd user unit or launchd agent); --print shows the unit first
```

On a server, see [Run Moochy on a server or in CI](headless-node.md#13-run-it-as-a-service).

## 7. Donate tokens

Open a project on moochy.dev and press **Donate tokens**, or from the terminal:

```sh
moochy donate --repo owner/name --cap '$20'     # up to $20 a month; asks you to confirm
```

Write the amount with a dollar sign, in single quotes so your shell keeps the `$`. From the terminal, the limit per request is the default ($5) and every model your key offers is allowed; change those on the website. A donation has:

| Setting | Meaning |
|---|---|
| Monthly limit | The most this project can use per month, in dollars, shown with an approximate token count. Not a payment: nothing leaves your account until a request is served |
| Limit per request | The most one request may cost. Default $5. A request that could cost more is refused |
| Models | Which models the project may use with your key (whole families allowed, for example all Claude Sonnet models) |
| Maximum reasoning effort | `low` … `max` |
| Extras | Opt-ins such as images, documents, long context, fast mode |
| Schedule | Optional: only serve at certain times, for example nights and weekends. Outside those times your device simply gets no requests |
| On public pages | **Show my handle**, **Show a pseudonym**, or **Hide me** |

The donation shows **waiting for the maintainer** until the project's owner accepts you, with a signature made on their own machine. Then your device starts serving.

## 8. Pause or stop donating

| You want to | Do | What happens |
|---|---|---|
| Stop serving from this device now | `moochy pause` (`moochy resume` to undo) | Immediate, works offline, no sign-in needed. This device takes no new requests |
| See your donations | `moochy donations` (or the Dashboard) | What each project used this month, and each donation's id |
| Pause one donation | `moochy donations pause <id>` (`resume` to undo), or Dashboard → the donation → **Pause** | No new requests for that project until you resume |
| Give less | Lower the donation's monthly limit | Takes effect within milliseconds |
| Stop donating to a project | `moochy donations stop <id>`, or Dashboard → **Stop donating** | The donation ends. No new requests; requests in progress finish and are recorded |
| Remove this device | `moochy logout` | Its keys are revoked, then deleted from the device |
| Remove another device | `moochy keys revoke <device id>`, or the Devices page on moochy.dev | Its keys stop working immediately |

Stopping is immediate because nothing was ever transferred. Your money stays in your provider account until a request is actually served.

### Emails you get

You confirm an email address when you first sign in; Moochy uses it only for these notifications.

| Kind | Examples | Can you turn it off? |
|---|---|---|
| Account and security | Confirm your email; sign-in from a new device; a device or an owner key was added or revoked; account deletion | No |
| Donations | Accepted, refused (with the maintainer's reason), expired after 30 days without an answer, or stopped by the maintainer; 80% and 100% of a monthly limit; a device offline for more than a day while a donation is active; a disputed receipt; your provider key is failing; monthly summary | Yes, per kind in Settings, or with the one-click unsubscribe link in each email |

Emails never contain prompts, responses, keys, or tokens, and have no tracking pixels.

## 9. See what your key was used for

```sh
moochy journal                 # recent requests: project, model, tokens, cost, status
moochy journal --follow        # live
```

The journal stays on your machine. By default it keeps details only, never the text of prompts or responses. To also keep the text on your machine: `moochy config set journal_full_text true`.

Each served request gets a receipt signed by your device. The project's page shows a short public receipt: model, cost, the day, and your name as you chose. It never shows prompts, times finer than a day, or device names. If a response looks wrong, `moochy report <task> --reason "…"` saves signed evidence you can send.

## 10. Your handle

Every account has one handle on moochy.dev, and no two accounts share one:

- 3–32 characters: lowercase letters `a–z`, digits, and single hyphens, starting and ending with a letter or digit. Letters from other alphabets are not allowed, so nobody can copy your handle with a look-alike such as a Cyrillic "а".
- Case does not matter: `Alice` and `alice` are the same handle.
- At first sign-in it is your GitHub or GitLab login, if that is valid and free; otherwise you choose one. Moochy never adds a number for you.
- Some words are reserved (`admin`, `support`, `moochy`, `security`, page names, …).
- You can change it once every 30 days. Your old handle is retired for good (nobody else can take it) and points to the new one for 90 days. Your profile is at `moochy.dev/u/<handle>`.

## 11. Troubleshooting

| What you see | Check |
|---|---|
| **Waiting for the maintainer** for a long time | The owner has not accepted you yet. The project page shows whether the owner is active |
| Nothing is served | `moochy status`: device limit reached? outside your schedule? paused? key invalid? |
| The app refuses to donate | `moochy doctor`: usually the lockdown could not be applied on this system; it says why. (`moochy up --unsafe-no-lockdown` exists only for debugging the app; do not donate with it) |
| Provider errors | `moochy doctor` checks the keychain, connection, clock, and provider keys |
| Unexpected costs | `moochy pause`, then `moochy journal`. Export your usage from the provider's usage page as a CSV and run `moochy audit --provider --from-file usage.csv`: it compares what this device served over 90 days with what your provider billed. Save evidence with `moochy report <task>` |

Exit codes: 0 ok, 2 wrong usage, 3 sign-in or acceptance refused, 4 network, 10 internal error.
