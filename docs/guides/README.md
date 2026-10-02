# Moochy guides

Moochy lets you donate tokens to open-source projects from your own LLM API account, with a monthly limit you choose. Maintainers use those tokens from the AI tools they already have. Your key never leaves your machine, and every request is end-to-end encrypted.

Open-source client (Apache-2.0) · 100% free. No fees, no commission, no paid tier. You pay your own provider for what your donations actually use; Moochy never touches money.

| Guide | For |
|---|---|
| [Donate tokens](donor.md) | Install the app, add a provider key, set your limits, donate, pause, stop donating, see what your key was used for |
| [Use donated tokens in your project](maintainer.md) | Register a project, accept donors, add members, connect your tools |
| [Donate from your own GPU](local-gpu.md) | Ollama, LM Studio, vLLM, or llama.cpp instead of an API key |
| [Run your agent safely with `moochy run`](run.md) | The sandbox your coding agent runs in: what it can reach, Linux and macOS notes |
| [Add a "Donate tokens" button](donate-button.md) | Put the button in your GitHub README |
| [Connect your tools](integrations.md) | Exact settings for OpenCode, Claude Code, Cursor, Cline, Continue, Zed, Goose, Windsurf, VS Code, Claude Desktop, Aider, agent frameworks, and SDKs |
| [Run Moochy on a server or in CI](headless-node.md) | An always-on donation from a machine you control; agents in CI |
| [How Moochy protects you](threat-model.md) | The attacks Moochy is designed against, and where each defence lives |
| [FAQ](faq.md) | Open source and free, privacy, how your key and code are protected |

The network protocol the app speaks is specified in [`spec/protocol.md`](../../spec/protocol.md). To report a vulnerability, see [`cli/SECURITY.md`](../../cli/SECURITY.md).
