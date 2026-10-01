# FAQ

## Open source and free

### Is Moochy free?

Yes, completely. No fees, no commission, no paid tier, no "pro" features. Donors pay their own provider (Anthropic, OpenRouter, DeepSeek, OpenAI) directly for the tasks their key actually serves. Moochy never holds, moves, or touches anyone's money. The moochy.dev infrastructure is cheap and funded by sponsors; its monthly cost and sponsors are published on moochy.dev/open.

### What is open source?

**The client is open source (Apache-2.0)**: the `moochy` binary that runs on your machine, the protocol definition (`spec/proto`, test vectors, and the [protocol specification](../../spec/protocol.md)), and these guides. Contributions are welcome with a DCO sign-off (`git commit -s`).

The relay and the moochy.dev web app are **not** open source.

### Why is that enough to trust it?

Because everything that matters to your safety runs in the client you can read:

- your provider API key is stored and used only by the client on the donor's machine;
- prompts, code, and outputs are encrypted and decrypted only by the clients at both ends;
- every check that protects a donor (task authenticity, the request firewall, the device spending cap) and every check that protects a maintainer (tool-call checks, receipt verification) runs in the client.

The relay only ever sees encrypted bytes plus the small amount of routing and accounting data listed below. It cannot read your prompts, forge a task, or overspend your cap on your machine. You do not have to trust what code the server runs; you only need to trust the client, and you can read and rebuild it.

### Can I run my own relay?

No. Moochy runs one relay at moochy.dev and does not offer self-hosting. The client's relay URL is configurable only for development and testing of the client.

### Are private repositories supported?

No. Only public repositories can receive donations: the purpose is open source, and public use is auditable.

## Privacy

### What does the relay see?

| Sees | Never sees |
|---|---|
| Which repository a request is for, the model, effort, `max_tokens`, a size estimate, whether it streams | Your prompts, system prompts, code, files, tools, or outputs |
| Sizes and timing of encrypted chunks | Your provider API key |
| Usage and cost of each task (to keep budgets) | Error details (they are encrypted for the maintainer) |
| Your account, devices' public keys, pledges | The provider's request id (only a salted hash) |

The relay keeps task metadata (model, sizes, cost) for 90 days, then only daily aggregates. Connection logs with IP addresses are kept 7 days.

### What is public?

- The project's goal and totals.
- A short, donor-signed record per task: model, cost, the **day** (never the time), and the donor's name only as the donor chose (`public`, `pseudonymous`, or `anonymous`). No device names, no task ids, no prompts.
- Which donors are online is shown only as an aggregate ("7 nodes online") unless a donor opts in.
- The key log (see below) contains pseudonymous ids (`ps_…`) and public keys, never names or emails.

### What stays on my machine?

The donor's journal (what each task was, model, cost) and, only if you turn it on, the full text of requests and responses. The maintainer's client keeps its own journal. Both are local files, kept 90 days by default.

## Security model, in plain words

### Can a donor see my code?

Yes: the donor's machine decrypts the request in order to send it to their provider, and the provider sees it too, exactly as when you use the provider directly. Maintainers choose which donors to approve. What the design guarantees is that **nobody in between** (the relay, its operator, its hosting company, someone who steals its database) can read it.

Before anything leaves your machine, the client scrubs secret-looking strings (API keys, tokens, private keys) from requests. Files you delegate are read only from inside your repository; `.git`, ignored files, and secret-shaped files are refused.

### Can someone use a donor's key for something else?

The donor's client accepts a task only if it is signed by a device of a member the repository owner approved with their own signature, is fresh (created in the last 10 minutes, and not before the donor's client started), and was never served before. It then checks the request against a strict allowlist: no server-side tools, no remote MCP servers, no file stores, no paid add-ons unless the donor opted in. A malicious relay cannot invent tasks, replay them, or move them to another project.

### Can I lose more than I pledged?

Three independent limits stop spending, and the strictest wins:

1. your pledge budgets (enforced by the relay);
2. your **device monthly cap**, enforced by the client on your machine before every call, even if the relay misbehaves;
3. the **spend limit at your provider**, which does not depend on Moochy at all. Set it.

### Can a donor attack me with the model's output?

Model output is untrusted input. Every tool call in a response is held until complete, checked against the tools and schemas your client actually offered, scanned for dangerous patterns, and released only if a signature from the donor's device covers it. Delegated results are labelled as untrusted content from a named donor. A donor who misbehaves can be identified (every response is signed by their device) and removed.

### How do I know a donor really used the model they claim?

Nobody can prove that cryptographically today. What the system does: the donor signs a receipt for every task; the maintainer's client checks it against what it sent and received (sizes, token counts, reported model) and files a signed dispute when something does not match; disputed receipts are excluded from rankings. Donors are approved by the project owner, and they pay their own provider: there is little to gain by cheating.

### What stops the relay from adding a fake donor or member?

Approvals of donors and members are signed by the repository owner's own device and published in a public, append-only **key log**. Every client keeps a copy and checks it: maintainers' clients encrypt only to donors the owner approved; donors' clients accept tasks only from members the owner approved. Each client also alerts its user if a key appears on their account, or an approval appears for their repository, that they did not create. The log's checkpoints are published hourly to a public Git repository, so a rewritten history would be visible to everyone.

### How do I check the binary I run?

- Release artifacts are signed with Sigstore and carry SLSA build provenance. Verify with `gh attestation verify <file> --repo <moochy-cli repository>` or `cosign verify-blob`.
- Builds are reproducible: build the tagged source yourself and compare.
- Or simply build from source and run your own build.

A binary cannot vouch for itself, so verification always happens outside it.

## Usernames

### Why can't I use capital letters or accented characters in my username?

Usernames are lowercase ASCII (`a-z`, `0-9`, single hyphens, 3–32 characters) so that nobody can register a look-alike of yours using characters from another alphabet. `Alice` and `alice` are the same name. Old names are retired forever after a rename, so nobody can take over links that pointed to you.

## Using it

### Which tools work?

Anything that speaks MCP, and anything that lets you set an Anthropic- or OpenAI-compatible base URL. See [Integrations](integrations.md).

### Why does my agent get a 400 or 403 instead of a retry?

Policy refusals (over the per-task cap: 400; quota used up: 403) are deliberately not 429, which agents retry in a loop. Temporary problems (a busy or rate-limited donor) are retried on another donor automatically, and come back as 429/529 only if every candidate failed.

### What happens if moochy.dev is down?

Tasks fail with normal, retryable provider errors. If the maintainer enabled the **own-key fallback**, their client calls the provider directly with their own key until the relay is back. Donors' receipts wait safely in their local outbox and are delivered after recovery, so nothing is lost or charged twice.
