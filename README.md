# moochy-docs

Guides, protocol specification and design documents for [Moochy](https://moochy.dev).

Moochy lets you donate tokens to open-source projects from your own LLM API account, with a monthly limit you choose. Maintainers use those tokens from the AI tools they already have. Your key never leaves your machine, and every request is end-to-end encrypted.

Open-source client (Apache-2.0) · 100% free.

## Start here

| You want to | Read |
|---|---|
| Donate tokens, or use donated tokens in your project | [`docs/guides/`](docs/guides/README.md), also on [moochy.dev/docs](https://moochy.dev/docs) |
| Let an AI agent set Moochy up | [`docs/guides/for-ai-agents.md`](docs/guides/for-ai-agents.md) |
| Implement the protocol | [`spec/protocol.md`](spec/protocol.md), [`spec/KEYLOG.md`](spec/KEYLOG.md), [`spec/proto/`](spec/proto/), [`spec/vectors/`](spec/vectors/) |
| Know how Moochy defends you | [`docs/guides/threat-model.md`](docs/guides/threat-model.md), [`docs/security/`](docs/security/README.md) |
| Understand the design | [`docs/plan/00-PLAN.md`](docs/plan/00-PLAN.md), then the implementation contract [`spec/CONTRACT.md`](spec/CONTRACT.md) |

## Layout

| Path | What |
|---|---|
| `docs/guides/` | User guides (donors, maintainers, organisations, integrations, donate button, cloud boxes) |
| `docs/brand/` | Voice and vocabulary for every user-facing word |
| `docs/plan/` | Design plan: architecture, wire protocol, routing, ledger, security, client, web, data model, operations, roadmap, decisions |
| `docs/security/` | Attack catalog and per-component hardening checklists |
| `docs/ops/` | Runbooks and service-level objectives |
| `docs/TRACEABILITY.md` | Requirement-to-test traceability |
| `spec/CONTRACT.md` | Implementation contract (normative for encodings and interfaces) |
| `spec/protocol.md`, `spec/KEYLOG.md` | Public protocol and key log specifications |
| `spec/proto/`, `spec/vectors/` | Protocol buffers and golden test vectors |

## Files shared with other repositories

- `spec/proto/` and `spec/vectors/` are produced in [moochy-cli](https://github.com/moochy-dev/moochy-cli), which keeps identical copies. Update them there first, then copy them here.
- `docs/guides/integrations.md` and `docs/guides/donate-button.md` are written here and copied to `cli/crates/node/assets/` in moochy-cli: the app prints sections of the first (`moochy connect`) and its tests check the second.
- moochy.dev serves `docs/guides/` as its `/docs` pages and `/llms.txt`.

## Check

```sh
python3 scripts/check-links.py   # every relative Markdown link resolves
```

## License

`docs/guides/`, `spec/proto/`, `spec/vectors/`, `spec/protocol.md` and `spec/KEYLOG.md` are Apache-2.0 ([`spec/LICENSE`](spec/LICENSE)). The other documents are published to read; all rights reserved.

## Related repositories

- [moochy-cli](https://github.com/moochy-dev/moochy-cli): the open-source `moochy` app.
- [moochy-skills](https://github.com/moochy-dev/moochy-skills): agent skills for donating tokens and using donated tokens.
