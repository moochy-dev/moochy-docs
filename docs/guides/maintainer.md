# Use donated tokens in your project

Donors give your project a monthly token limit on their own LLM API accounts. You and your members use those tokens from the tools you already have: any MCP client or agent, and any tool that lets you set a provider base URL. Prompts and code are encrypted on your machine and decrypted only on the donor's device that serves the request.

Once a first donor is accepted, getting an agent running on donated tokens takes about 3 minutes.

Only **public** repositories can be registered.

---

## 1. Install and sign in

Install the Moochy app as in the [donor guide](donor.md#1-install), then:

```sh
moochy login --roles gateway
moochy up
```

Confirm the printed code in your browser (GitHub or GitLab sign-in). The first time, you choose your handle (rules in the [donor guide](donor.md#10-your-handle)). `--roles gateway` lets this device use donated tokens.

## 2. Register your repository

1. Create your **owner key**, once per account:

   ```sh
   moochy owner init
   ```

   It is a separate key that signs only your decisions as an owner (claims, accepted donors, members). It is encrypted with its own passphrase, which you type in the terminal, and it is used only by the commands below, never by the app running in the background. Keep the passphrase somewhere safe. `moochy owner rotate` replaces a key you still have; if you lose the key or its passphrase, it can be revoked after you sign in again on moochy.dev, and you create a new one with `moochy owner init`. Your other devices warn you if an owner key appears on your account that you did not create.
2. On moochy.dev, open **Claim** and pick the repository. Moochy asks your code host, once, whether you are an **admin** of it. The sign-in token is used for that check and not stored.
3. Confirm on your own machine, in the repository folder:

   ```sh
   moochy claim --repo owner/repo
   ```

   The app shows what it is about to sign, asks you to confirm, and asks for your owner key's passphrase. Your signature goes into the public key log. From then on, every donor or member accepted for this repository needs your signature.
4. In **Project settings**, set the **monthly goal**, a short public note on what you use the tokens for (donors read it before donating), and the **default model**.

Add a **Donate tokens** button to your README so donors find you: see [Add a "Donate tokens" button](donate-button.md).

**Own a GitHub organisation or a GitLab group?** Claim it too, and one donation to the organisation funds every project you choose in it, with donors accepted once: see [Donations for your organisation](organisations.md).

## 3. Accept or refuse donations

New donations show **waiting for the maintainer**. Each request shows the donor's handle or pseudonym, the models, the monthly limit, and the limit per request, with useful signals: account age, other projects they donate to, past disputes. You decide in one of three places; every decision is recorded.

**From the terminal**, on your own machine:

```sh
moochy pending                                       # donors and members waiting for you
moochy accept ps_7hc2qz… --repo owner/repo           # or the donor's handle; `moochy approve` is the same command
moochy accept ps_7hc2qz… --repo owner/repo --revoke  # remove a donor you accepted
```

The app shows exactly what it will sign (the project, the donor, your owner key), asks you to confirm, and asks for the owner key's passphrase. In scripts and CI, `--yes` skips the question and the passphrase comes from `MOOCHY_OWNER_PASSPHRASE`; it is never read from standard input, so a tool piping into `moochy` cannot answer for you.

**From an email.** When a donor is waiting, Moochy emails you the request with **Accept**, **Refuse**, and **Review** buttons. A button never decides anything by itself (mail scanners open links): it opens the request on moochy.dev, where you must be signed in (within the last 2 hours) and press the button again. The link works once and for 7 days.

**From the website**, Repositories → the project → the request: the same page.

- **Refuse** is one click on that page, with an optional short reason the donor sees. A refusal grants nothing, so it needs no signature.
- **Accept** on the website or from an email needs a **passkey**: Touch ID, Windows Hello, or a security key registered as one of your owner keys. Your device signs the exact acceptance, and every member's app checks that signature in the public key log, as with the terminal. Moochy's servers cannot forge or replay it. To register your first passkey, you confirm with a link sent to your confirmed email address (or sign with an owner key you already have).
- A request nobody answers **expires after 30 days**, and the donor is told.

**Approvals are always signed by you, never by Moochy.** Whether from the terminal (owner key) or the website (passkey), the signature is made on your own device after you confirm. The background app cannot accept anyone, and a donor you did not accept never receives your project's requests.

**Every decision is traced.** Activity → Decisions shows each request and what happened to it (requested, accepted, refused, expired, stopped, lowered, resumed, revoked), who decided, when, and how (terminal, website, email link, passkey). The donor sees the same history for their donation. Both are in your data export, and acceptances are verifiable in the public key log.

Your own app warns you if the public key log ever shows a donor, member, or claim for your repository that you did not sign. If you get an email confirming a decision you did not make, treat it as a security problem: revoke the key or passkey it names.

### Emails you get

You confirm an email address when you first sign in; Moochy uses it only for these notifications.

| Kind | Examples | Can you turn it off? |
|---|---|---|
| Account and security | Confirm your email; sign-in from a new device; a device, an owner key, or a passkey was added or revoked; account deletion | No |
| Maintainer | A donor is waiting for you; a member request; a donation stopped or lowered; your project's donations are running low; claim confirmed; monthly summary | Yes, per kind in Settings, or with the one-click unsubscribe link in each email |

Bursts are grouped (at most one email of a kind per hour). Emails never contain prompts, responses, keys, or tokens, and have no tracking pixels.

## 4. Members

Members are the people (and CI machines) allowed to use your project's donations.

```sh
moochy members add alice --repo owner/repo --cap '$20'          # up to $20 a month
moochy members add --device d_01J… --repo owner/repo --cap '$5'  # a CI or server agent
moochy members remove alice --repo owner/repo
```

Write the amount with a dollar sign, in single quotes so your shell keeps the `$`. Each change is signed on your machine after you confirm, like an acceptance. Without `--cap`, a member may use 20% of what donors give each month by default; the owner has no limit. You can change limits later in Project settings. A donor's device serves a request only from a member you signed, or from you.

Give a CI or container agent its **own device** with its own monthly limit, so an agent running on its own can never use up the project's donations. See [Run Moochy on a server or in CI](headless-node.md#2-an-agent-in-ci-or-a-container).

## 5. Run your agent in the sandbox

```sh
moochy run -- claude          # or opencode, aider, goose, …
```

**Tool calls from donated tokens only reach agents inside `moochy run`.** The sandbox lets your agent work on this repository and nothing else: no access to your other files or keys, and no network except Moochy. A tool started without `moochy run` still gets text answers, but each tool call is replaced by a `[moochy]` notice, unless you allow it for this project (`moochy config set allow_unsandboxed_tools owner/repo`, with a warning at every start). Details: [Run your agent safely with `moochy run`](run.md).

## 6. Connect your tools

`moochy run` sets everything up for the agent it starts. To configure a tool yourself, in the repository folder:

```sh
moochy connect list              # the tools it knows
moochy connect <tool>            # print the settings for that tool
moochy connect <tool> --write    # add them to the tool's user-level config, after showing the change
```

Tokens are never written into files tracked by git: `--write` refuses such files.

Two ways in, both on `127.0.0.1` only:

| Way in | What you get | Use it when |
|---|---|---|
| **MCP** (`moochy mcp` over stdio, or `http://127.0.0.1:PORT/mcp`) | The tools `moochy_delegate` and `moochy_pool_status`. Your agent hands self-contained tasks (read and summarize files, review a diff, draft tests) to donated tokens. Over stdio, `moochy mcp` reads the files you name on your machine and sends their contents, so they never fill your agent's own paid context | Your agent has its own model and you want to hand off work |
| **API** (Anthropic Messages and OpenAI Chat Completions on `http://127.0.0.1:PORT`) | Donated tokens as your tool's **main** model | The tool lets you set a base URL |

The raw values, for anything not listed:

```sh
moochy env --repo owner/repo            # shell exports: ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN, OPENAI_BASE_URL, OPENAI_API_KEY, MOOCHY_MCP_URL
moochy env --repo owner/repo --json     # {"anthropic_base_url", "openai_base_url", "token"}
moochy env --repo owner/repo --rotate   # replace the project token
```

The token works for one repository and only on this machine. The port is chosen once and stays the same, so your settings keep working after a restart. Exact settings for every tool are in [Connect your tools](integrations.md).

Model ids look like `anthropic/claude-sonnet-5`, `deepseek/deepseek-chat`, or `x-ai/grok-4`. `GET /v1/models` (and `moochy_pool_status`) list exactly what donors offer your project right now.

## 7. What protects you

Donors' devices produce your model output, so treat it like any input you did not write:

- **The sandbox** (`moochy run`, above) keeps a bad command from reaching anything outside your project.
- **Tool calls are checked before your agent sees them.** Each tool call is held until complete, checked against the tool list and schema your tool sent, scanned for dangerous patterns (for example `curl … | sh`), and released only with a signature from the donor's device. Anything that fails is replaced by an error result.
- **Responses are rebuilt, not copied.** Your app re-creates every streamed event from checked, typed data, so no byte a donor chose reaches your tool's parser as-is. Terminal control characters are removed.
- **Results from `moochy_delegate` are marked as untrusted content** from a named donor.
- **Secrets are removed** from requests before they are encrypted, and secret files are hidden inside `moochy run`.
- **Receipts are checked for you.** If a donor's signed usage does not match what your app actually sent and received, your app files a signed dispute. When everything matches, you do nothing.
- **Providers you exclude** in Project settings (for example for data retention reasons) never receive your project's requests.

## 8. Errors your tools may see

Errors come back in the provider's own format, so agents react sensibly:

| Situation | Response | Your agent retries? |
|---|---|---|
| A donor is busy or rate-limited | Sent to another donor automatically; if all fail, 429 or 529 | yes |
| The request could cost more than the donors' limit per request | 400 `invalid_request_error` | no |
| Your monthly limit or the project's donations are used up | 403 `permission_error` | no |
| No donor offers that model | 404 | no |
| Something donors' safety checks do not allow (for example server-side tools, file ids, remote MCP servers inside the request) | 400 with the reason | no |

## 9. Day to day

```sh
moochy status                  # donations available to your projects, requests in progress
moochy pending                 # anything waiting for your signature
moochy journal --follow        # requests you made: model, cost, status
moochy verify <receipt_ref>    # check a public receipt of one of your requests: donor signature, link to the signed receipt, public key log
```

Project settings show how much donors gave this month and how much was used, usage per member and per model, the cache hit rate, and models your members asked for that no donor offers.
