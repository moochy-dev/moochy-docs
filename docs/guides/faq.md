# FAQ

## Open source and free

### Is Moochy free?

Yes. No fees, no commission, no paid tier, no paid features. Donors pay their own provider (Anthropic, OpenAI, OpenRouter, DeepSeek, or xAI) directly, and only for the requests their donation actually serves. Moochy never holds, moves, or touches anyone's money. Running moochy.dev costs little and is paid for by sponsors; the monthly cost and the sponsors are published on moochy.dev/open.

### What is open source?

**The Moochy app is open source (Apache-2.0)**: the `moochy` app that runs on your machine, the protocol definition (`spec/proto`, test vectors, and the [protocol specification](../../spec/protocol.md)), and these guides. Contributions are welcome with a DCO sign-off (`git commit -s`).

Moochy's servers and the moochy.dev website are **not** open source.

### Why is that enough to trust it?

Because everything that matters for your safety runs in the app you can read:

- your provider API key is stored and used only by the app on the donor's machine;
- prompts, code, and responses are encrypted and decrypted only by the apps at both ends;
- every check that protects a donor (is this request genuine, the safety checks on each request, the device's monthly limit) and every check that protects a maintainer (tool-call checks, receipt checks) runs in the app.

Moochy's servers (the relay) only see encrypted bytes, plus the small amount of routing and accounting data listed below. The relay cannot read your prompts, invent requests, or go past the monthly limit your own device enforces. You do not need to trust the code running on the server, only the app, which you can read and build yourself.

### Can I run my own server?

No. Moochy runs one service, at moochy.dev, and does not offer self-hosting. The app's server address can be changed only for developing and testing the app.

### Are private repositories supported?

No. Only public repositories can receive donations: Moochy exists for open source, and public use can be checked by anyone.

## Privacy

### What does Moochy's server see?

| Sees | Never sees |
|---|---|
| Which repository a request is for, the model, reasoning effort, the maximum output length, a size estimate, whether it streams | Your prompts, system prompts, code, files, tools, or responses |
| Sizes and timing of encrypted pieces | Your provider API key |
| Tokens used and cost of each request (to keep monthly limits) | Error details (they are encrypted for the maintainer) |
| Your account, your devices' public keys, your donations | The provider's request id (only a salted hash) |

Request details (model, sizes, cost) are kept 90 days, then only daily totals. Connection logs with IP addresses are kept 7 days.

### What is public?

- The project's monthly goal and totals.
- A public receipt per request, signed by the donor: model, cost, the **day** (never the time), and the donor's name only as the donor chose (**Show my handle**, **Show a pseudonym**, or **Hide me**). No device names, no request ids, no prompts.
- Who is online is shown only as a total ("7 devices online"), unless a donor chooses to show it.
- The public key log contains pseudonyms (`ps_…`) and public keys, never names or emails.

### What stays on my machine?

Your journal (each request, its model and cost) and, only if you turn it on, the full text of requests and responses. Both donors and maintainers have one. It is a local file, kept 90 days by default.

## How your key and code are protected

### Can a donor see my code?

Yes. The donor's device decrypts the request to send it to their provider, and the provider sees it too, just as when you use the provider directly. You choose which donors to accept. What the design guarantees is that **nobody in between** (Moochy's servers, the people who run them, their hosting company, someone who steals their database) can read it.

Before anything leaves your machine, the app removes text that looks like a secret (API keys, tokens, private keys). Files you hand to `moochy_delegate` are read only from inside your repository; `.git`, files ignored by git, and secret-looking files are refused.

### What runs on a donor's machine?

Only inference: open the encrypted request, check it, make one HTTPS call to the provider with the donor's key, encrypt the response. The app never runs a command, a tool, or code from a request, and the background app removes its own ability to start programs once it is running. Each request is checked in a throwaway process with no files, no network, and no keys. See [What runs on your machine](donor.md#what-runs-on-your-machine).

### Can someone use a donor's key for something else?

The donor's app serves a request only if it is signed by a device of a member the repository owner accepted with their own signature, is fresh (created in the last 10 minutes, and not before the donor's app started), and was never served before. It then runs safety checks against a strict list of what is allowed: no server-side tools, no remote MCP servers, no provider file storage, no paid extras unless the donor allowed them. The relay cannot invent requests, send one twice, or move a request to another project.

### Can I lose more than I chose to donate?

Three separate limits stop spending, and the smallest one wins:

1. the monthly limit of each donation, kept by Moochy;
2. your **device's monthly limit**, checked by the app on your machine before every call, whatever the relay does;
3. the **spending limit at your provider**, which does not depend on Moochy at all. Set it.

### Can a donor attack me through the model's response?

Treat model output as input you did not write. Tool calls from donated tokens only reach agents running inside `moochy run`, a sandbox that can touch your project and nothing else: no other files, no keys, no network except Moochy ([details](run.md)). Every tool call in a response is held until complete, checked against the tools and schemas your tool actually offered, scanned for dangerous patterns, and released only if a signature from the donor's device covers it. Results from `moochy_delegate` are marked as untrusted content from a named donor. A donor who misbehaves can be identified (every response is signed by their device) and removed.

### How do I know a donor really used the model they claim?

Nobody can prove that with cryptography today. What Moochy does: the donor signs a receipt for every request; the maintainer's app checks it against what it sent and received (sizes, token counts, the model the provider reported) and files a signed dispute when something does not match; disputed receipts do not count in rankings. Donors are accepted by the project owner, and they pay their own provider, so there is little to gain by cheating.

### What stops Moochy's servers from adding a fake donor or member?

The repository owner's own device signs every accepted donor and member, and those signatures are published in a public, append-only **public key log**. Every app keeps a copy and checks it: a maintainer's app encrypts only for donors the owner accepted, and a donor's app serves only members the owner accepted. Each app also warns its user if a key appears on their account, or a donor or member appears for their repository, that they did not add. The log's checkpoints are published every hour to a public Git repository, so a rewritten history would be visible to everyone.

### How do I check the app I run?

- Release files are signed with Sigstore and carry SLSA build provenance. Check them with `gh attestation verify <file> --repo moochy-dev/moochy-cli`, or with `cosign verify-blob` and the `.sigstore.json` bundle attached to the release.
- `moochy update --from-file <file>` installs a release only if its signature checks out.
- Builds are reproducible: build the tagged source yourself and compare.
- Or build from source and run your own build.

An app cannot vouch for itself, so the check always happens outside it.

## Handles

### Why can't I use capital letters or accented characters in my handle?

Handles use lowercase `a–z`, digits, and single hyphens (3–32 characters), so nobody can register a look-alike of yours with letters from another alphabet. `Alice` and `alice` are the same handle. After you change your handle, the old one is retired for good, so nobody can take over links that pointed to you.

## Using it

### Which tools work?

Anything that speaks MCP, and anything that lets you set an Anthropic- or OpenAI-compatible base URL. See [Connect your tools](integrations.md).

### Which providers can donors use?

Anthropic, OpenAI, OpenRouter, DeepSeek, and xAI (Grok). Only API keys are accepted, never chat-subscription logins.

### Why does my agent get a 400 or 403 instead of a retry?

On purpose. When a request could cost more than the donors' limit per request (400), or your monthly limit is used (403), retrying will not help, and agents retry 429 in a loop. Temporary problems, such as a busy or rate-limited donor, are retried on another donor automatically, and come back as 429 or 529 only if every donor failed.

### What happens if moochy.dev is down?

Requests fail with normal provider errors that tools retry. Donors' receipts wait safely on their own machines and are delivered afterwards, so nothing is lost or charged twice.
