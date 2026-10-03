# Moochy guides

Moochy lets you donate tokens to open-source projects from your own LLM API account, with a monthly limit you choose. Maintainers use those tokens from the AI tools they already have. Your key never leaves your machine, and every request is end-to-end encrypted.

Open-source client (Apache-2.0) · 100% free. No fees, no commission, no paid tier. You pay your own provider for what your donations actually use; Moochy never touches money.

| Guide | For |
|---|---|
| [Donate tokens](donor.md) | Install the app, add a provider key, set your limits, donate, pause, stop donating, see what your key was used for |
| [Use donated tokens in your project](maintainer.md) | Register a project, accept donors, add members, connect your tools |
| [Donations for your organisation](organisations.md) | Claim a GitHub organisation or GitLab group, choose the projects it funds, share caps, accept donors once, owner changes |
| [Sponsor a person](sponsor-a-person.md) | Sponsor a maintainer's own requests on the repos they maintain; claim your profile and choose the repos |
| [Donate to an organisation](donate-to-an-organisation.md) | `moochy donate --org`, the organisation page, one limit across its projects, what each project used |
| [Donate from your own GPU](local-gpu.md) | Ollama, LM Studio, vLLM, or llama.cpp instead of an API key |
| [The dashboard in your terminal: `moochy tui`](tui.md) | Tabs, keys, command palette and filter, themes, `NO_COLOR`, `--ascii`, demo and snapshot mode |
| [Run your agent safely with `moochy run`](run.md) | The sandbox your coding agent runs in: what it can reach, Linux and macOS notes |
| [Add a "Donate tokens" button](donate-button.md) | The exact recipe, for people and AI agents: find the project, check it, pick the snippet, put it in the README; organisation and person buttons; live showcase charts |
| [For AI agents](for-ai-agents.md) | How agents read these docs (`/llms.txt`, `.md` pages), rules for agents, a snippet for your `AGENTS.md` |
| [Connect your tools](integrations.md) | Exact settings for 22 coding agents (Claude Code, Codex, GitHub Copilot CLI, Gemini CLI, Cursor, OpenCode, Amp, Droid, Kiro CLI, …), Claude Desktop, agent frameworks, and SDKs |
| [Use Moochy in cloud boxes](boxes.md) | Agents in boat.dev, E2B, Daytona, Modal, Morph, Fly, Codespaces; donating from cloud machines and rented GPUs |
| [Run Moochy on a server or in CI](headless-node.md) | An always-on donation from a machine you control; agents in CI |
| [How Moochy protects you](threat-model.md) | The attacks Moochy is designed against, and where each defence lives |
| [FAQ](faq.md) | Open source and free, privacy, how your key and code are protected |

The network protocol the app speaks is specified in [`spec/protocol.md`](../../spec/protocol.md). To report a vulnerability, see [`cli/SECURITY.md`](../../cli/SECURITY.md).
