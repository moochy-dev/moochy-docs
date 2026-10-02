# For AI agents

This page is for coding agents (and the people who instruct them). Everything here is public and needs no sign-in.

## Start here

- **Index:** `https://moochy.dev/llms.txt` lists every page as raw Markdown, following the llms.txt convention. The donate-button recipe comes first.
- **Everything at once:** `https://moochy.dev/llms-full.txt` is all pages in one text file.
- **One page:** add `.md` to any docs address for its raw Markdown, for example `https://moochy.dev/docs/donate-button.md`. The same page as HTML is `https://moochy.dev/docs/donate-button`.

Prefer the `.md` pages: they are the source of the HTML pages, with the same text.

## Install the Moochy skills

Three skills give your agent the exact steps, so it does not have to read the whole docs each time:

```sh
npx skills add moochy-dev/moochy-cli
```

| Skill | For |
|---|---|
| `moochy-donate-button` | Add, fix, or check the "Donate tokens" button in a README |
| `moochy-use-donated-tokens` | Use a project's donated tokens: `moochy connect`, `moochy run`, `moochy_delegate` |
| `moochy-donate` | Help a donor install the app, keep keys local, set limits, donate, pause, stop |

They work with Claude Code, Codex, GitHub Copilot, Gemini CLI, Cursor, Windsurf, Cline, Amp, Antigravity, OpenClaw, Droid, Goose, Kilo Code, Kiro CLI, Hermes Agent, OpenCode, Roo Code, Trae, Zed, and Continue; per-agent notes and the skills themselves are on [Agent skills](https://moochy.dev/docs/skills) (source: [`skills/`](../../skills/README.md)). Each `SKILL.md` is also raw Markdown at `https://moochy.dev/docs/skills/<name>.md`.

## Common tasks

| Task | Read |
|---|---|
| Add a "Donate tokens" button to a repository's README | [`donate-button.md`](donate-button.md) (or the `moochy-donate-button` skill): follow the recipe exactly, top to bottom |
| Use donated tokens from a coding tool or agent framework | [`integrations.md`](integrations.md) (MCP server and provider-compatible base URLs, one section per agent) or the `moochy-use-donated-tokens` skill |
| Run inside the Moochy sandbox | [`run.md`](run.md) |
| Set yourself up inside a cloud box (boat.dev, E2B, Daytona, Modal, Morph, Fly, Codespaces) | [`boxes.md`](boxes.md#1-use-donated-tokens-from-a-cloud-box): install, enroll with the token the maintainer gives you, then `moochy run` |
| Explain Moochy to a maintainer or donor | [`maintainer.md`](maintainer.md), [`donor.md`](donor.md), [`faq.md`](faq.md) |

## Rules for agents

- **Never handle secrets.** No Moochy task an agent does needs a provider API key, a Moochy token, or a passphrase. Do not ask for them, print them, or write them to files. The project token a maintainer's tools use comes from `moochy env` on their machine and stays there.
- **Never sign for a person.** Claiming a project, accepting a donor, and adding a member are signed with the maintainer's owner key after they confirm. Tell the maintainer the command; do not run it for them.
- **Do not create donations.** Donating is the donor's decision and spends their money.
- **In a cloud box, enroll; never copy keys.** Use the enrollment token the maintainer gives you (`MOOCHY_ENROLL`), enroll when the box starts (never in a template or snapshot), and if Moochy says the box is a copy, delete its Moochy home folder and enroll again.
- **Inside `moochy run`**, the standard variables (`ANTHROPIC_BASE_URL`, `ANTHROPIC_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_API_KEY`) already point to Moochy and hold a token for that run only. Use them as they are; there is nothing to configure.
- **Tool calls from donated tokens** reach an agent only inside `moochy run`. If you see a `[moochy]` notice instead of a tool call, ask the maintainer to start you with `moochy run -- <your command>`.

## Using Moochy as a model or a tool

- **MCP:** `moochy mcp --repo owner/name` (stdio) or `http://127.0.0.1:PORT/mcp` with a bearer token. Tools: `moochy_delegate` (hand a self-contained task to donated tokens) and `moochy_pool_status` (what is available). See [integrations](integrations.md#1-the-values-you-need).
- **Provider-compatible API:** Anthropic Messages at `http://127.0.0.1:PORT` and OpenAI Chat Completions at `http://127.0.0.1:PORT/v1`, on the maintainer's machine only. `moochy env --repo owner/name` prints the values.
- **Protocol** (for implementers): `spec/protocol.md` in the public `moochy-dev/moochy-cli` repository.

## For maintainers: a snippet for your agents

Paste this into your repository's `AGENTS.md`, `CLAUDE.md`, or similar file:

```markdown
## Moochy

This project uses Moochy (https://moochy.dev) for donated LLM tokens.
- Docs for agents: https://moochy.dev/llms.txt (raw Markdown pages end in .md).
- The README "Donate tokens" button links to the project's Moochy page (https://moochy.dev/p/…/donate).
  Keep it; to add or change it, follow https://moochy.dev/docs/donate-button.md exactly.
- Never put API keys or tokens in files or commits; never run `moochy claim`, `moochy accept`,
  `moochy members`, or `moochy donate` for me: tell me the command instead.
```
