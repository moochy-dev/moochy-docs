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
moochy service install         # optional: start at login
```

Confirm the printed code in your browser (GitHub or GitLab sign-in). The first time, you choose your handle (rules in the [donor guide](donor.md#10-your-handle)). `--roles gateway` lets this device use donated tokens.

## 2. Register your repository

1. On moochy.dev, open **Claim** and pick the repository. Moochy asks your code host, once, whether you are an **admin** of it. The sign-in token is used for that check and not stored.
2. Confirm with your own device:

   ```sh
   moochy claim owner/repo
   ```

   Your device signs an entry in the public key log. From then on, every donor or member accepted for this repository needs a signature from one of your devices.
3. In **Project settings**, set the **monthly goal**, a short public note on what you use the tokens for (donors read it before donating), and the **default model**.

Add a **Donate tokens** button to your README so donors find you: see [Add a "Donate tokens" button](donate-button.md).

## 3. Accept donors

New donations show **waiting for the maintainer**. Project settings list each donor with useful signals: account age, other projects they donate to, past disputes. Accept them with your device, so the decision is yours and cannot be faked by anyone else:

```sh
moochy status                  # donors and members waiting for you
moochy approve <donor-handle>  # accept this donor
```

Decline in Project settings. Before any member's app sends a single encrypted byte to a donor, it checks your signature for that donor in the public key log. Moochy's servers can show you a request, but cannot accept a donor on your behalf.

Your own app warns you if the public key log ever shows a donor, member, or claim for your repository that you did not sign.

## 4. Members

Members are the people (and CI machines) allowed to use your project's donations.

```sh
moochy members add <handle>
moochy members add --device <device_id>     # a CI or server agent
moochy members remove <handle>
```

Set each member's and each device's monthly limit in Project settings. By default a member may use 20% of what donors give each month; the owner has no limit. Each change is signed by your device and recorded in the public key log. A donor's device serves a request only from a member you signed, or from you.

Give a CI or container agent its **own device** with its own monthly limit, so an agent running on its own can never use up the project's donations. See [Run Moochy on a server or in CI](headless-node.md#2-an-agent-in-ci-or-a-container).

## 5. Connect your tools

In the repository directory:

```sh
moochy connect <tool>          # print the settings for that tool
moochy connect <tool> --write  # add them to the tool's user-level config, after showing the change
```

Tools: `claude-code`, `opencode`, `cursor`, `cline`, `continue`, `zed`, `goose`, `windsurf`, `vscode`, `claude-desktop`, `aider`, `generic-mcp`, `generic-openai`, `generic-anthropic`. Tokens are never written into files tracked by git.

Two ways in, both on `127.0.0.1` only:

| Way in | What you get | Use it when |
|---|---|---|
| **MCP** (`moochy mcp` over stdio, or `http://127.0.0.1:PORT/mcp`) | The tools `moochy_delegate` and `moochy_pool_status`. Your agent hands self-contained tasks (read and summarize files, review a diff, draft tests) to donated tokens. The Moochy app reads the files, not your agent, so they never fill your agent's own paid context | Your agent has its own model and you want to hand off work |
| **API** (Anthropic Messages and OpenAI Chat Completions on `http://127.0.0.1:PORT`) | Donated tokens as your tool's **main** model | The tool lets you set a base URL |

The raw values, for anything not listed:

```sh
moochy env --repo owner/repo --json
# {"anthropic_base_url":"http://127.0.0.1:PORT","openai_base_url":"http://127.0.0.1:PORT/v1","token":"…"}
```

The token works for one repository and only on this machine. The port is chosen once and stays the same, so your settings keep working after a restart. Exact settings for every tool are in [Connect your tools](integrations.md).

Model ids look like `anthropic/claude-sonnet-5`, `deepseek/deepseek-chat`, or `x-ai/grok-4`. `GET /v1/models` (and `moochy_pool_status`) list exactly what donors offer your project right now.

## 6. What protects you

Donors' devices produce your model output, so treat it like any input you did not write:

- **Tool calls are checked before your tool sees them.** Each tool call is held until complete, checked against the tool list and schema your tool sent, scanned for dangerous patterns (for example `curl … | sh`), and released only with a signature from the donor's device. Anything that fails is replaced by an error result.
- **Results from `moochy_delegate` are marked as untrusted content** from a named donor.
- **Secrets are removed** from requests before they are encrypted.
- **Receipts are checked for you.** If a donor's signed usage does not match what your app actually sent and received, your app files a signed dispute. When everything matches, you do nothing.
- **Your own key as a fallback** (optional, off by default): when no donation is available or your monthly limit is used, the app can call the provider directly with your own key instead of failing.

## 7. Errors your tools may see

Errors come back in the provider's own format, so agents react sensibly:

| Situation | Response | Your agent retries? |
|---|---|---|
| A donor is busy or rate-limited | Sent to another donor automatically; if all fail, 429 or 529 | yes |
| The request could cost more than the donors' limit per request | 400 `invalid_request_error` | no |
| Your monthly limit or the project's donations are used up | 403 `permission_error` | no |
| No donor offers that model | 404 | no |
| Something donors' safety checks do not allow (for example server-side tools, file ids, remote MCP servers inside the request) | 400 with the reason | no |

## 8. Day to day

```sh
moochy status                  # donations available, your limit, who is waiting for you, requests in progress
moochy journal --follow        # requests you made: model, donor pseudonym, cost
```

Project settings show how much donors gave this month and how much was used, usage per member and per model, the cache hit rate, and models your members asked for that no donor offers.
