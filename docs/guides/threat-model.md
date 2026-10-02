# How Moochy protects you

A summary of the attacks Moochy is designed against, and where each defence lives. Every defence listed here runs in the open-source Moochy app (Apache-2.0), so you can read it and check it. Moochy's servers (the relay) are closed source, and the design does not ask you to trust them: the relay only sees encrypted bytes and signed records.

To report a weakness, see [`cli/SECURITY.md`](../../cli/SECURITY.md).

---

## Who we defend against

| Attacker | What they might try |
|---|---|
| **The relay, or whoever controls it** | Read prompts, invent or replay requests, change a request's model or size, accept a fake donor, hide or alter receipts, inject bytes into a response, send a client to the wrong server |
| **A malicious donor** | Return output that makes the maintainer's agent run something harmful, fabricate usage, read more than the request it was sent |
| **A malicious member or requester** | Use a donor's key for things the donor did not allow: paid extras, server-side tools, file stores, more money than the limits |
| **A web page or local program** | Call the local API or MCP endpoints from a browser, or steal the project token |
| **Someone on the network** | Read or change traffic, replay a login |
| **A tampered release** | Ship a modified `moochy` app |
| **An impersonator** | Register a look-alike handle, or reuse a retired one |

## What the design guarantees, and where

### Your prompts and code stay between the two machines

- Each request is encrypted on the maintainer's machine under a fresh key and opened only on the donor device that serves it. Responses are encrypted under a key that is new for every attempt, so two streams never share a key whatever the relay does. Details: [`spec/protocol.md`](../../spec/protocol.md) §8–§10.
- The maintainer's app encrypts only for donor devices the repository owner accepted with their own signature, as recorded in the public key log, and refuses to encrypt at all when its copy of the log is missing, out of date, or shows a fork ([`spec/KEYLOG.md`](../../spec/KEYLOG.md) §6).
- Before encryption, the app removes text that looks like a secret, and inside `moochy run` secret files are hidden from the agent.
- The connection to the relay is TLS 1.3 and the login is bound to that exact connection, so a captured login is useless anywhere else.

### A donor's key is used only for what the donor allowed

- The donor's app serves a request only if it is signed by a member the owner accepted, is fresh, was never served before (also across restarts), and its visible routing data matches the encrypted body exactly. Otherwise it refuses before calling the provider ([`spec/protocol.md`](../../spec/protocol.md) §9).
- Safety checks compare every field of the request with a strict list of what is allowed: no server-side tools, code execution, remote MCP servers, provider file storage, or paid extras unless the donor allowed them.
- The donor's app enforces its own monthly limit and the limit per request (default $5) before every call, even if the relay ignores limits. A spending limit at the provider bounds everything else.
- The donor's machine never executes anything: the background app locks itself down after start-up (no starting programs, only its own state folder, connections only to the provider and Moochy), and each request is checked in a throwaway process with no files, network, or keys.

### Output from a donor cannot take over the maintainer's machine

- Tool calls from donated tokens are held until complete, checked against the tools and schemas the agent declared, scanned for dangerous commands, and released only with a signature from the donor's device covering them.
- They are released only to agents running inside `moochy run`, a sandbox that can touch the project and nothing else: no other files, no keys, no network except Moochy and hosts you allow, and git metadata the host would execute stays read-only ([Run your agent safely](run.md)).
- The maintainer's app rebuilds every streamed event from checked data instead of passing a donor's bytes through, and removes terminal control characters.
- Results from `moochy_delegate` are marked as untrusted content from a named donor.

### Nobody can quietly accept a donor or a member

- Accepting a donor, adding a member, and claiming a repository are signed with the owner's **owner key**: a key separate from every device key, encrypted with its own passphrase, used only by a command the owner types and confirms. The background app never reads it.
- These signatures go into a public, append-only key log. Every app keeps a copy, checks it, and warns its user about any key, approval, or claim they did not make. Checkpoints are published hourly to a public Git repository, so a rewritten history is visible to anyone.

### Money records cannot be faked or hidden

- Every served request gets a receipt signed by the donor's device. The maintainer's app checks it against what it actually sent and received and files a signed dispute when they differ.
- Every settled receipt is appended to a public receipt log, and both parties get proof that it was, so receipts cannot silently disappear from public totals.
- Public receipts show the model, cost, and day only: never prompts, times, or device names.

### Your local endpoints are yours

- The local API and MCP endpoints listen on `127.0.0.1` only, require a per-project token, refuse foreign `Host` headers, and send no CORS headers, so web pages cannot use them.
- The command-line app talks to the background app over a private socket only your user can open.

### The app you run is the app we published

- Releases are signed with Sigstore, carry SLSA build provenance, and build reproducibly. `moochy update --from-file` refuses unsigned files. See the [FAQ](faq.md#how-do-i-check-the-app-i-run).

### Handles cannot be imitated or recycled

- Handles are lowercase ASCII only, unique regardless of case, and a retired handle is never given to anyone else ([donor guide](donor.md#10-your-handle)).

## Known limits

- A donor sees the prompts it serves, as does its provider. You choose which donors to accept.
- A donor can return wrong or low-quality answers, and nobody can yet prove which model produced an answer. Receipts, disputes, and owner approval limit the damage; they do not remove it.
- Text in a response can still try to talk a person into running something. Inside `moochy run` the agent cannot do lasting damage; outside it, you are the safeguard.
- Local GPU donations report their own token counts, which cannot be checked; they are labelled self-reported and never counted as money ([Donate from your own GPU](local-gpu.md)).
- Malware already running as your user, or as root, is out of scope.
- The relay can refuse service. It cannot read your prompts or spend beyond your limits, but it can stop working.
