# Maintainer guide

Your project receives compute budgets from donors. You and your members use it from the tools you already have: any MCP client or agent, and any tool that lets you set a provider base URL. Prompts and code are encrypted on your machine and decrypted only on the donor's machine that serves the request; the Moochy relay never sees them.

Target: an agent running on donated compute in under 3 minutes after the first donor is approved.

Only **public** repositories can be registered.

---

## 1. Install and sign in

Install the `moochy` client as in the [donor guide](donor.md#1-install), then:

```sh
moochy login --roles gateway
moochy up
moochy service install         # optional: start at login
```

Approve the printed code in your browser (GitHub or GitLab sign-in). The first time, you pick your Moochy username (rules in the [donor guide](donor.md#10-your-username)).

## 2. Claim your repository

1. On moochy.dev, open **Claim** and pick the repository. Moochy asks your code host, once, whether you are an **admin** of it (the OAuth token is used for that check and not stored).
2. Confirm the claim with your own machine:

   ```sh
   moochy claim owner/repo
   ```

   Your device signs a `REPO_CLAIMED` entry in the public key log. From now on, every approval for this repository must carry a signature from one of your devices.
3. On the maintainer console (`/console/owner/repo`), set the **monthly goal** and a short public description of what you use AI compute for (donors read it before pledging), and the **default model**.

Add the README badge so donors find you:

```markdown
[![Moochy](https://moochy.dev/p/owner/repo/badge.svg)](https://moochy.dev/p/owner/repo)
```

## 3. Approve donors

New pledges arrive as **pending**. The console shows each donor with useful signals (account age, other projects they support, past disputes). Approve with your device, so the approval is yours and not the relay's:

```sh
moochy status                  # lists pending donors and members
moochy approve <donor-username>
```

Decline on the console. Your device signs `DONOR_APPROVED`; every member's client checks that signature in the key log before sending a single encrypted byte to that donor. The relay can show you a request but cannot forge an approval.

Your own client alerts you if the key log ever shows an approval, member, or claim for your repository that you did not sign.

## 4. Members

Members are the people (and CI machines) allowed to use the pool.

```sh
moochy members add <username>
moochy members add --device <device_id>     # a CI or headless agent device
moochy members remove <username>
```

Set each member's and device's monthly cap on the console. The default member cap is 20% of the monthly amount committed by donors; the owner is unlimited. Each change is signed by your device and logged. Donors' machines serve a task only if its sender is a member you signed (or you).

A CI or container agent should have its **own device** with its own cap, so an autonomous agent can never drain the pool. See [Running a headless node](headless-node.md#2-an-agent-in-ci-or-a-container-uses-the-pool).

## 5. Connect any client

In the repository directory:

```sh
moochy connect <client>          # print the configuration for that client
moochy connect <client> --write  # merge it into the client's user-level config after showing a diff
```

Clients: `claude-code`, `opencode`, `cursor`, `cline`, `continue`, `zed`, `goose`, `windsurf`, `vscode`, `claude-desktop`, `aider`, `generic-mcp`, `generic-openai`, `generic-anthropic`. Tokens are never written into git-tracked files.

Two ways in, both on `127.0.0.1` only:

| Door | What it gives you | Use when |
|---|---|---|
| **MCP** (`moochy mcp` over stdio, or `http://127.0.0.1:PORT/mcp`) | Tools `moochy_delegate` and `moochy_pool_status`. Your agent hands self-contained sub-tasks (read and summarize files, review a diff, draft tests) to donated compute. Files are read by the client, not by your agent, so they never fill your agent's own paid context | Your agent has its own model and you want to offload work |
| **API** (Anthropic Messages and OpenAI Chat Completions on `http://127.0.0.1:PORT`) | Donated compute as your tool's **main** model | The tool lets you set a base URL |

The raw values, for anything not listed:

```sh
moochy env --repo owner/repo --json
# {"anthropic_base_url":"http://127.0.0.1:PORT","openai_base_url":"http://127.0.0.1:PORT/v1","token":"…"}
```

The token is scoped to one repository and works only on this machine. The port is picked once and stays the same, so configurations keep working across restarts. Exact snippets for every client are in [Integrations](integrations.md).

Model ids are public slugs such as `anthropic/claude-sonnet-5` or `deepseek/deepseek-chat`. `GET /v1/models` (and `moochy_pool_status`) list exactly what donors currently offer your repository.

## 6. What protects you

Donor machines produce your model output, so treat it like any untrusted input:

- **Tool calls are checked before your client sees them.** Each tool call is held until it is complete, checked against the tool list and schema your client sent, scanned for dangerous patterns (for example `curl … | sh`), and released only with a signature from the donor's device. Anything that fails is replaced by an error tool result.
- **Delegated results are framed as untrusted content** from a named donor.
- **Secrets are scrubbed** from requests before they are encrypted.
- **Receipts are checked automatically.** If a donor's signed usage does not match what your client actually sent and received, the client files a signed dispute; you do nothing when everything matches.
- **Own-key fallback** (optional, off by default): when the pool is empty or your quota is used up, the client can call the provider directly with your own key instead of failing.

## 7. Errors your tools may see

Errors come back in the provider's own format, so agents behave sensibly:

| Situation | Response | Your agent retries? |
|---|---|---|
| A donor is busy or rate-limited | Rerouted to another donor automatically; if all fail, 429/529 | yes |
| The request's worst-case cost is above the donors' per-task cap | 400 `invalid_request_error` | no |
| Your member quota or the pool is used up | 403 `permission_error` | no |
| The model is not offered by any donor | 404 | no |
| A feature the donor pool does not allow (for example server-side tools, file ids, remote MCP servers in the request) | 400 with the reason | no |

## 8. Day to day

```sh
moochy status                  # pool, quotas, pending approvals, tasks flowing
moochy journal --follow        # tasks you consumed: model, donor pseudonym, cost
```

The console shows committed vs used budget, per-member and per-model usage, cache hit rate, and models requested but missing from the pool.
