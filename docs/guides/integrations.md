# Connect your tools

**If a tool speaks MCP, it can hand work to your project's donated tokens. If it lets you set a base URL, donated tokens can power its main model.** Most current tools do both.

**The safest path is `moochy run`.** For any command-line agent (Claude Code, OpenCode, Aider, Goose, …), `moochy run -- <agent>` starts it in a sandbox already pointed at Moochy, with nothing to configure: inside, the standard variables (`ANTHROPIC_BASE_URL`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `OPENAI_BASE_URL`, `OPENAI_API_KEY`) point to Moochy and carry a token made for that run only. **Tool calls from donated tokens only reach agents inside `moochy run`**: a tool connected with the settings on this page gets text answers, and each tool call is replaced by a visible `[moochy]` notice, unless the project allows it (`moochy config set allow_unsandboxed_tools owner/repo`, with a warning at every start). See [Run your agent safely with `moochy run`](run.md). The settings below are for editors and apps that cannot run inside `moochy run`, for `moochy_delegate`, and for scripts that need no tool calls.

The quickest path is `moochy connect <tool>` in your repository: it prints the settings below with your real port, repository, and available models filled in, and `--write` adds them to the tool's user-level config after showing the change. This page is the same information written out, for review and for tools `moochy connect` does not know.

Tools change their configuration formats between versions. When a snippet here and `moochy connect` disagree, trust `moochy connect` (it is updated with each release of the app) and tell us.

---

## 1. The values you need

```sh
moochy up
moochy env --repo owner/repo --json
# {"anthropic_base_url":"http://127.0.0.1:PORT","openai_base_url":"http://127.0.0.1:PORT/v1","token":"…"}
export MOOCHY_TOKEN="$(moochy env --repo owner/repo --json | jq -r .token)"
# or simply: eval "$(moochy env --repo owner/repo)"   # ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN, OPENAI_BASE_URL, OPENAI_API_KEY, MOOCHY_MCP_URL
```

| Way in | Endpoint | Authentication |
|---|---|---|
| API, Anthropic Messages | `http://127.0.0.1:PORT` (SDKs append `/v1/messages`) | `x-api-key: TOKEN` or `Authorization: Bearer TOKEN` |
| API, OpenAI Chat Completions | `http://127.0.0.1:PORT/v1` | `Authorization: Bearer TOKEN` |
| Models | `GET /v1/models` (both dialects) | same |
| MCP, stdio | command `moochy mcp --repo owner/repo` | none (it talks to the running Moochy app over a private local socket) |
| MCP, Streamable HTTP | `http://127.0.0.1:PORT/mcp` | `Authorization: Bearer TOKEN` |

- `PORT` is chosen once at the first `moochy up` and then stays fixed, so configs keep working.
- The token is scoped to one repository and only works on this machine. Keep it out of git: use environment variables or the tool's secret storage, never a file tracked by git.
- Both ways in listen on `127.0.0.1` only, refuse requests with a foreign `Host` header, and send no CORS headers, so web pages cannot reach them.
- **Models** are public slugs such as `anthropic/claude-sonnet-5`, `deepseek/deepseek-chat`, `x-ai/grok-4`, or any OpenRouter model id; providers' own ids are accepted too. Use only ids listed by `GET /v1/models` or `moochy_pool_status`: they are what donors offer your project right now. The examples below use `anthropic/claude-sonnet-5`; use your project's models.
- **Formats.** Anthropic donors serve the Anthropic format; OpenAI and xAI (Grok) donors serve the OpenAI format; OpenRouter and DeepSeek donors serve both. A Claude Code session therefore needs Anthropic, OpenRouter, or DeepSeek donors, and a Grok model is reached through the OpenAI-compatible endpoint. `moochy_delegate` picks the right format for you.
- GUI applications often do not inherit your shell's `PATH`. If an MCP server fails to start, use the absolute path from `command -v moochy` as the command.

### MCP tools

| Tool | What it does |
|---|---|
| `moochy_delegate` | Runs a self-contained task on donated tokens: `prompt`, optional `system`, `files` (paths; over stdio, `moochy mcp` reads them on your machine under the rules below and sends their contents, so they never fill your agent's context; over HTTP, send `file_contents` as `[{"path", "text"}]` instead), `model` (one of the models donors offer), `effort`, `max_tokens`, `output` (`text` or `json`). Returns the result marked as untrusted content from the donor, plus a cost line |
| `moochy_pool_status` | Donations left this month, your monthly limit, models available, number of donors |

Files shared with `moochy_delegate` come only from inside the repository, at most 2 MiB in total; `.git`, `.env` and key files, secret-looking files, and files ignored by git are refused, and secrets are removed from the text before it is encrypted.

Long tasks send MCP progress notifications. Some tools stop waiting for a tool call after about a minute; raise the tool timeout where the tool allows it (shown below).

### What is verified by our end-to-end tests

Our internal end-to-end suite runs the real `moochy` and relay binaries against fake providers. It tests the **ways in** with plain HTTP and MCP clients, not the third-party tools themselves:

| Way in | Scenario |
|---|---|
| Anthropic Messages API, byte-identical streaming, receipts, cost | E01; through DeepSeek and OpenRouter donors: E03 |
| OpenAI Chat Completions API through an OpenRouter donor | E02 |
| xAI donors | pending (scenario not written yet) |
| MCP over stdio: `initialize`, `tools/list`, `moochy_delegate` | E04 |
| MCP over Streamable HTTP, bearer token required (401 otherwise) | E05 |
| Local hardening: wrong token 401, bad `Host` 403, no CORS, loopback only | E14 |

In the tables below, **E2E** names the scenario that covers the way in a snippet uses. **Tool** says how the tool's own settings were checked: `manual` = checked by hand against the tool's documentation and release, not in automated tests.

---

## 2. Coding agents and IDEs

### Claude Code

| Way in | E2E | Tool |
|---|---|---|
| MCP stdio / HTTP | E04 / E05 | manual |
| API (Anthropic) | E01, E03 | manual |

Recommended: `moochy run -- claude` in your repository. It needs no setup and is the only way Claude Code receives tool calls from donated tokens. To configure Claude Code yourself instead:

MCP, user scope (available in every project):

```sh
claude mcp add --scope user moochy -- moochy mcp --repo owner/repo
# or over HTTP:
claude mcp add --scope user --transport http moochy http://127.0.0.1:PORT/mcp \
  --header "Authorization: Bearer $MOOCHY_TOKEN"
```

Raise the tool timeout for long tasks: `export MCP_TOOL_TIMEOUT=300000` (milliseconds).

API (donated tokens as Claude Code's model). Works with Anthropic, OpenRouter, and DeepSeek donors, which all serve the Anthropic format:

```sh
export ANTHROPIC_BASE_URL=http://127.0.0.1:PORT
export ANTHROPIC_AUTH_TOKEN="$MOOCHY_TOKEN"
export ANTHROPIC_MODEL=anthropic/claude-sonnet-5
export ANTHROPIC_DEFAULT_HAIKU_MODEL=anthropic/claude-haiku-4.5   # small/fast model: pick one donors offer
claude
```

Or put the same keys in the `env` block of `~/.claude/settings.json` (user-level, never the project's `.claude/settings.json` if it is committed).

### OpenCode

| Way in | E2E | Tool |
|---|---|---|
| MCP stdio / HTTP | E04 / E05 | manual |
| API (OpenAI-compatible or Anthropic) | E02 / E01 | manual |

`~/.config/opencode/opencode.json`. You can use both ways in at once: a donated model as the main model **and** `moochy_delegate` for sub-tasks.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "moochy": {
      "type": "local",
      "command": ["moochy", "mcp", "--repo", "owner/repo"],
      "enabled": true
    }
  },
  "provider": {
    "moochy": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Moochy",
      "options": {
        "baseURL": "http://127.0.0.1:PORT/v1",
        "apiKey": "{env:MOOCHY_TOKEN}"
      },
      "models": {
        "anthropic/claude-sonnet-5": {},
        "deepseek/deepseek-chat": {}
      }
    }
  },
  "model": "moochy/anthropic/claude-sonnet-5",
  "small_model": "moochy/deepseek/deepseek-chat"
}
```

MCP over HTTP instead of stdio:

```json
"moochy": {
  "type": "remote",
  "url": "http://127.0.0.1:PORT/mcp",
  "headers": { "Authorization": "Bearer {env:MOOCHY_TOKEN}" }
}
```

For Claude models served by Anthropic donors, `"npm": "@ai-sdk/anthropic"` with the same `baseURL` keeps Anthropic prompt caching, which makes donations go further.

### Cursor

| Way in | E2E | Tool |
|---|---|---|
| MCP stdio / HTTP | E04 / E05 | manual |
| API | — | **not supported**: Cursor sends custom-model traffic through its own servers, which cannot reach `127.0.0.1`. Use MCP |

`~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "moochy": { "command": "moochy", "args": ["mcp", "--repo", "owner/repo"] }
  }
}
```

Over HTTP:

```json
{
  "mcpServers": {
    "moochy": {
      "url": "http://127.0.0.1:PORT/mcp",
      "headers": { "Authorization": "Bearer TOKEN" }
    }
  }
}
```

### Cline

| Way in | E2E | Tool |
|---|---|---|
| MCP stdio / HTTP | E04 / E05 | manual |
| API (OpenAI-compatible or Anthropic) | E02 / E01 | manual |

MCP: Cline → MCP Servers → Configure (`cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "moochy": {
      "command": "moochy",
      "args": ["mcp", "--repo", "owner/repo"],
      "timeout": 300
    }
  }
}
```

Over HTTP: `{"type": "streamableHttp", "url": "http://127.0.0.1:PORT/mcp", "headers": {"Authorization": "Bearer TOKEN"}}`.

API: Settings → API Provider **OpenAI Compatible**: Base URL `http://127.0.0.1:PORT/v1`, API Key = token, Model ID = a model donors offer. Or provider **Anthropic** with "Use custom base URL" = `http://127.0.0.1:PORT`.

### Continue

| Way in | E2E | Tool |
|---|---|---|
| MCP stdio | E04 | manual |
| API (OpenAI-compatible) | E02 | manual |

`~/.continue/config.yaml`, with the token stored as a Continue secret named `MOOCHY_TOKEN`:

```yaml
name: moochy
version: 0.0.1
schema: v1
models:
  - name: Claude Sonnet (Moochy)
    provider: openai
    model: anthropic/claude-sonnet-5
    apiBase: http://127.0.0.1:PORT/v1
    apiKey: ${{ secrets.MOOCHY_TOKEN }}
    roles: [chat, edit, apply]
mcpServers:
  - name: moochy
    command: moochy
    args: [mcp, --repo, owner/repo]
```

### Zed

| Way in | E2E | Tool |
|---|---|---|
| MCP stdio | E04 | manual |
| API (OpenAI-compatible) | E02 | manual |

`settings.json`:

```json
{
  "context_servers": {
    "moochy": {
      "command": "moochy",
      "args": ["mcp", "--repo", "owner/repo"]
    }
  },
  "language_models": {
    "openai_compatible": {
      "Moochy": {
        "api_url": "http://127.0.0.1:PORT/v1",
        "available_models": [
          { "name": "anthropic/claude-sonnet-5", "display_name": "Claude Sonnet (Moochy)", "max_tokens": 200000 }
        ]
      }
    }
  }
}
```

Enter the token as the provider's API key in the Agent panel settings.

### Goose

| Way in | E2E | Tool |
|---|---|---|
| MCP stdio / HTTP | E04 / E05 | manual |
| API (Anthropic or OpenAI) | E01 / E02 | manual |

`~/.config/goose/config.yaml`:

```yaml
extensions:
  moochy:
    name: moochy
    type: stdio
    cmd: moochy
    args: [mcp, --repo, owner/repo]
    enabled: true
    timeout: 300
```

Over HTTP: `type: streamable_http`, `uri: http://127.0.0.1:PORT/mcp`, `headers: {Authorization: "Bearer TOKEN"}`.

API:

```sh
export GOOSE_PROVIDER=anthropic
export ANTHROPIC_HOST=http://127.0.0.1:PORT
export ANTHROPIC_API_KEY="$MOOCHY_TOKEN"
export GOOSE_MODEL=anthropic/claude-sonnet-5
```

### Windsurf

| Way in | E2E | Tool |
|---|---|---|
| MCP stdio / HTTP | E04 / E05 | manual |
| API | — | not supported (no custom base URL for the agent's model) |

`~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "moochy": { "command": "moochy", "args": ["mcp", "--repo", "owner/repo"] }
  }
}
```

Over HTTP: `{"serverUrl": "http://127.0.0.1:PORT/mcp", "headers": {"Authorization": "Bearer TOKEN"}}`.

### VS Code (agent mode)

| Way in | E2E | Tool |
|---|---|---|
| MCP stdio / HTTP | E04 / E05 | manual |
| API | — | depends on your VS Code and Copilot version's support for custom OpenAI-compatible models; use MCP otherwise |

Command palette → **MCP: Open User Configuration** (`mcp.json`). The `inputs` entry makes VS Code prompt for the token once and store it securely, so no token lands in a file:

```json
{
  "inputs": [
    { "type": "promptString", "id": "moochy-token", "description": "Moochy token (moochy env --json)", "password": true }
  ],
  "servers": {
    "moochy": {
      "type": "stdio",
      "command": "moochy",
      "args": ["mcp", "--repo", "owner/repo"]
    },
    "moochy-http": {
      "type": "http",
      "url": "http://127.0.0.1:PORT/mcp",
      "headers": { "Authorization": "Bearer ${input:moochy-token}" }
    }
  }
}
```

Use one of the two entries, not both.

### Aider

| Way in | E2E | Tool |
|---|---|---|
| API (OpenAI-compatible) | E02 | manual |

```sh
export OPENAI_API_BASE=http://127.0.0.1:PORT/v1
export OPENAI_API_KEY="$MOOCHY_TOKEN"
aider --model openai/anthropic/claude-sonnet-5
```

The `openai/` prefix tells Aider to use the OpenAI-compatible endpoint; the rest is the model id.

---

## 3. Chat applications

### Claude Desktop

| Way in | E2E | Tool |
|---|---|---|
| MCP stdio | E04 | manual |

`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`; Windows: `%APPDATA%\Claude\`). Use the absolute path to `moochy`:

```json
{
  "mcpServers": {
    "moochy": {
      "command": "/usr/local/bin/moochy",
      "args": ["mcp", "--repo", "owner/repo"]
    }
  }
}
```

Good for handing long reads and reviews to donated tokens from a chat.

### Web chat apps and remote-only connectors

Tools that can only reach a **remote HTTPS** MCP server (connectors in web chat apps, cloud agents that cannot run a local binary) are **not supported**: both ways in listen only on your own machine by design, and Moochy never runs a hosted endpoint, because that endpoint would have to see your prompts.

---

## 4. Agent frameworks

Any framework with an MCP client can use the Moochy tools; any framework whose model client takes a base URL can run on donated tokens. In CI or containers, run [Moochy next to the agent](headless-node.md).

| Framework | MCP | Model via base URL | E2E | Tool |
|---|---|---|---|---|
| OpenAI Agents SDK | yes | yes | E05 / E02 | manual |
| Claude Agent SDK | yes | yes | E04 / E01 | manual |
| LangChain / LangGraph | yes (`langchain-mcp-adapters`) | yes | E05 / E01, E02 | manual |
| Pydantic AI | yes | yes | E05 / E02 | manual |
| CrewAI, Mastra, others | yes (stdio command or Streamable HTTP URL + header) | yes | E04, E05 / E02 | manual |

**OpenAI Agents SDK** (Python):

```python
import os
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

async with MCPServerStreamableHttp(params={
    "url": "http://127.0.0.1:PORT/mcp",
    "headers": {"Authorization": f"Bearer {os.environ['MOOCHY_TOKEN']}"},
}) as moochy:
    agent = Agent(name="reviewer", instructions="…", mcp_servers=[moochy])
    result = await Runner.run(agent, "Review the diff in src/")
```

**Claude Agent SDK** (Python): set `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` as for Claude Code to run on donated tokens, and/or add the Moochy tools:

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    mcp_servers={"moochy": {"type": "stdio", "command": "moochy", "args": ["mcp", "--repo", "owner/repo"]}},
)
async for message in query(prompt="Summarize docs/ with moochy_delegate", options=options):
    print(message)
```

**LangGraph / LangChain** (Python):

```python
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

client = MultiServerMCPClient({"moochy": {
    "transport": "streamable_http",
    "url": "http://127.0.0.1:PORT/mcp",
    "headers": {"Authorization": f"Bearer {os.environ['MOOCHY_TOKEN']}"},
}})
tools = await client.get_tools()
llm = ChatOpenAI(base_url="http://127.0.0.1:PORT/v1", api_key=os.environ["MOOCHY_TOKEN"],
                 model="anthropic/claude-sonnet-5")
```

**Pydantic AI**:

```python
import os
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

moochy = MCPServerStdio("moochy", args=["mcp", "--repo", "owner/repo"])
agent = Agent("openai:gpt-5", toolsets=[moochy])   # your agent's own model; moochy_delegate uses donated tokens
```

---

## 5. SDKs and libraries

| SDK | E2E | Client |
|---|---|---|
| Anthropic SDKs | E01, E03 | manual |
| OpenAI SDKs | E02 | manual |
| Vercel AI SDK, LiteLLM | E02 | manual |

**Anthropic** (Python; TypeScript takes the same `baseURL`/`apiKey`):

```python
import os, anthropic
client = anthropic.Anthropic(base_url="http://127.0.0.1:PORT", api_key=os.environ["MOOCHY_TOKEN"])
msg = client.messages.create(model="anthropic/claude-sonnet-5", max_tokens=1024,
                             messages=[{"role": "user", "content": "Hello"}])
```

**OpenAI** (Python; TypeScript is the same):

```python
import os
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:PORT/v1", api_key=os.environ["MOOCHY_TOKEN"])
resp = client.chat.completions.create(model="deepseek/deepseek-chat",
                                      messages=[{"role": "user", "content": "Hello"}])
```

**Vercel AI SDK** (TypeScript):

```ts
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';
const moochy = createOpenAICompatible({
  name: 'moochy',
  baseURL: 'http://127.0.0.1:PORT/v1',
  apiKey: process.env.MOOCHY_TOKEN,
});
const model = moochy('anthropic/claude-sonnet-5');
```

**LiteLLM**:

```python
import os, litellm
litellm.completion(model="openai/anthropic/claude-sonnet-5", api_base="http://127.0.0.1:PORT/v1",
                   api_key=os.environ["MOOCHY_TOKEN"], messages=[{"role": "user", "content": "Hello"}])
```

---

## 6. Request rules worth knowing

- Send `max_tokens` (the Moochy app adds the model's default if your tool leaves it out, and tells you once).
- The donor's app runs safety checks against a strict list of what is allowed. Server-side tools, remote MCP servers inside the request, provider file ids, URL images, and `n > 1` are refused with a 400 that says why.
- Refusals that a retry cannot fix are never 429, so agents do not retry them in a loop: over the donors' limit per request → 400, monthly limit used → 403.
- `POST /v1/messages/count_tokens` is answered locally (no donor involved) with a deliberately pessimistic estimate.
- Responses carry `x-moochy-task`, `x-moochy-donor` (pseudonym), and `x-moochy-cost-uusd` (cost in millionths of a dollar) headers.
