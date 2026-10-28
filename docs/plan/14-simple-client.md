# 14 — Simple client: the desktop app, a shorter CLI, cheaper tokens, a node in one file

> Product owner, 2026-10-28: "Moochy is too complicated right now. Simplify the client a lot, with a tiny GUI (Rust, Tauri) and the best simple UI/UX for the existing features. Make donated tokens extremely cheap. Make the donor node installable with a skill or Docker Compose."
>
> This plan adds no new trust: every action still runs through the `moochy` binary and its rules (CONTRACT §3, §15, §23). It removes steps, not checks.

---

## 1. What "simple" means, measured

| Path | Today | Target |
|---|---|---|
| New donor: install → first donation waiting for the maintainer | 6–7 commands, 2–3 browser visits, shell quoting (`'$20'`, stdin for the key) | Desktop: 4 screens, 1 browser visit (approve the code). CLI: 1 command (`moochy start`) |
| Donor with a GPU: install → serving | Read local-gpu.md, `keys add local --base-url … --model local/x=id`, `up` | `docker compose up -d`, approve one code |
| `moochy --help` | 130 lines, 40 command forms | ≤ 30 lines: the 10 commands people use; `moochy help all` keeps the full list |
| Pause donating | `moochy pause` or a TUI key | One switch in the desktop window |

Non-goals: Windows (the node is Unix-only, CONTRACT §15), a hosted or custodial mode, any change to the wire protocol or the key log.

---

## 2. The desktop app (`desktop/` in moochy-cli)

### 2.1 Shape

- **Tauri 2**, one small window (420 × 680, resizable, remembers its size). A separate Cargo workspace at `desktop/` (not under `cli/crates/`, so the CLI's dependency budget, crates.io publishing and the 15 MB binary target are unchanged). `publish = false`. Apache-2.0.
- **No frontend toolchain.** `desktop/ui/` is plain `index.html`, `app.css`, `app.js` (ES modules, no framework, no npm). Tauri serves it from the bundle.
- **The `moochy` binary is bundled** as a Tauri sidecar (`externalBin`). The app finds it next to its own executable, else on `PATH`. One download gives the GUI and the CLI.
- **The app is a remote control, never a second node.** The node stays the locked-down background process (`moochy up`). The window:
  - reads state and receives live updates over the existing `LocalControl` socket through `moochy_node::tuisrc::NodeSource` (`snapshot`, `events`, `act`): the same data and actions as the TUI (CONTRACT §20.4);
  - runs every other action as a child process `moochy --home H <command> … --json`, parsing its JSON event lines (exit codes per CONTRACT §6). The provider key goes to the child on **stdin** only, then the buffer is zeroized.
- The model types of `moochy-tui` get `Serialize` behind an optional `serde` feature (off for the CLI build, so the CLI does not grow).

### 2.2 Security rules (fail closed)

- Strict CSP: `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src ipc: http://ipc.localhost`. No remote content, no `eval`, no `innerHTML` with data (text nodes only).
- Tauri capabilities: `core:default` and events only. No shell, fs, http, opener or updater plugins. The app's own commands are a closed list (§2.4); each validates its arguments (project slugs with the CLI's `canonical_slug` rules, dollar amounts as integers 1–100,000, provider in the fixed list) before spawning anything.
- Links open in the system browser only for `https://moochy.dev/…` (and the configured web origin of a dev relay); every other URL is refused.
- **Owner-key actions are not done in the window** (accept a donor, claim, org/person coverage): they need the owner passphrase or a passkey. The window shows the decision and opens the matching `moochy.dev` page (`/decide/…`, `/claim`), where the passkey signs it (as `decisions accept` already does). Refusing a donor, pausing, stopping and lowering limits go through the socket like the TUI.
- Server and peer strings are rendered as text, never markup, and sanitized with the TUI's `sanitize::clean`.
- The key field is a password field, never logged, never in an event payload, cleared after submit; the app never reads a key back (it shows provider and status only).

### 2.3 Screens

**First run** (shown until the device is logged in as a worker, has a key and has a donation; each step is skipped when already done, so the app also "repairs" a half-done CLI setup):

1. **Connect this computer.** One button, "Sign in with GitHub or GitLab". Runs `login --roles gateway,worker --no-browser`, shows the 8-character code large with a copy button, opens the approval page, and waits (spinner, "Waiting for approval…", Cancel).
2. **Add your API key.** Provider tiles (Anthropic, OpenAI, OpenRouter, DeepSeek, xAI) plus a paste field that picks the provider from the key's prefix (`sk-ant-`, `sk-or-`, `xai-`; `sk-` asks OpenAI or DeepSeek). Under the field: "Stored in your keychain on this machine. Never sent to Moochy." The key is checked with the provider's free models call (the CLI does it) and errors are shown inline. A link "Donate your own GPU instead" opens the GPU guide.
3. **Set a monthly limit for this computer.** Chips $10 / $20 / $50 / Custom; one checkbox "I set a spend limit at my provider too" with a link to the provider's limits page. Runs `safety --monthly-limit N --accept-safety`, then `up`, then `service install` when "Start Moochy when I log in" is on (default on).
4. **Pick a project.** A field for `owner/name` (GitHub default; `gitlab/…` accepted) or a GitHub/GitLab URL pasted as is, the monthly amount (defaults to the limit from step 3), and "Donate tokens". Runs `donate --repo P --cap N --yes`. Done screen: "Waiting for the maintainer to accept you", with a Share link to the project page.

**Main window** (four tabs in a bottom bar, keyboard 1–4):

- **Home.** A large status line with one switch: *Donating* / *Paused* / *Offline* (device pause/resume, works offline). This month: used of the computer's limit (a ring), tokens served, saved by caching. Live list of requests served (project, model, tokens, cost), new rows slide in. Alerts from the node (limit nearly used, key failing, lockdown not enforced) with one action each.
- **Donations.** One card per donation: target, status, used / monthly limit bar, models. Actions: Pause / Resume, Lower the limit, Stop (confirm in place, no modal stack). "+ Donate tokens" opens step 4.
- **Projects** (shown when the account maintains something): projects with this month's use, donors waiting (Accept → opens moochy.dev, Refuse → reason field), and **Connect your tools**: the coding agents `moochy connect list` knows, each with "Set up" (`connect <client> --write`) and a copy button for the env snippet.
- **Settings.** Keys (provider, added, status; Add, Remove), this computer's monthly limit, start at login, theme (System / Light / Dark), "Check this computer" (runs `doctor`, shows each line as pass/warn/fail), sign out (`logout`, confirm), version and links (docs, source, public key log).

### 2.4 App commands (the whole IPC surface)

`state()`, `act(action)` (the TUI's `Action` enum, minus Accept/OrgAdd/OrgRemove which become `open_web`), `login_start()` / `login_cancel()` (streams `device_code` and `logged_in` as events), `add_key(provider, key)`, `set_limit(dollars, start_at_login)`, `donate(target, dollars, kind)`, `donation(op, id)`, `connect(client)`, `doctor()`, `remove_key(provider)`, `logout()`, `open_web(path)`.

### 2.5 Look and motion

Brand tokens from CONTRACT §9 and `docs/brand/VOICE.md`: Ink / Paper / Sky base, Mint for the one call to action, Butter for tokens, Coral-soft for stop. Instrument Sans (OFL, bundled), tabular numbers for money. Dark follows the system by default. One drawn mint hamster (idle when serving, sleeping when paused, worried on an alert). Motion: 150–250 ms transform/opacity only; new rows slide in; the ring animates to its value; `prefers-reduced-motion` turns it all off. No emoji, no exclamation marks.

### 2.6 Packaging and verification

- CI (moochy-cli `desktop.yml`, on `v*` tags and by hand): Linux x86_64 AppImage + .deb (Ubuntu 22.04 runner, webkit2gtk 4.1), macOS arm64 and x86_64 .dmg. Each bundle includes the `moochy` binary built in the same run. Artifacts are attached to the release with SHA-256 sums and GitHub attestations like the CLI. macOS builds are unsigned until a Developer ID exists; the release notes say how to open them.
- Tests: Rust unit tests for argument validation, key prefix detection and the snapshot JSON shape; a UI smoke test that loads `ui/index.html` in headless Chromium with a fake `__TAURI__` (fixture snapshot) and checks every screen renders without console errors at 420 × 680 and 900 × 700, light and dark.

---

## 3. A shorter CLI

- `moochy start` (new): the desktop first run in the terminal. Each step is skipped when already done: login as gateway + worker (opens the browser), ask the provider key with hidden input (or `--key-stdin`), the safety step, `up`, offer `service install`, then ask the project and the amount and donate. Ends with what to expect. Re-running it is safe.
- `moochy login` with no `--roles` asks "Use donated tokens, donate yours, or both?" on a terminal (default both); scripts keep the old default (gateway).
- `keys add <provider>` on a terminal without `--key-stdin` prompts for the key with echo off (it stays out of argv and shell history); scripts still use `--key-stdin`.
- Dollar amounts accept `20`, `$20`, `20.50` (already true for `--cap`; the help stops showing `$N`, which needs quoting).
- `donate` starts the app when it is not running, instead of failing.
- After `keys add`, `keys remove`, `config set`: if the app is running, it restarts it (`down` + `up`) and says so, instead of telling the user to.
- `moochy --help`: the short list (start, donate, donations, pause/resume, status, keys, connect, run, tui, doctor) and "moochy help all" for everything. Every existing command and flag keeps working (scripts, the e2e suite, the skills).

---

## 4. Cheaper donated tokens

The donor pays the provider; the maintainer's tools pick the model. Cheap means more useful tokens per donated dollar. In order of effect:

1. **Cheapest model by default.** Today the pool's models are sorted alphabetically and tools take the first one, often the most expensive. The relay orders `PoolSync` models by catalog price (input + output per million, cheapest first, ties by name); `moochy_delegate` and `moochy connect` take the cheapest model that fits the request's needs as the default and the next tier as the "main" model only when the project set no preference.
2. **Price-aware routing.** Among workers that can serve the same model, the scheduler adds the expected cost (from the catalog entry of the worker's provider) to the P2C score, so a local GPU (cost 0) and a cache-warm worker win over a cold paid one. Affinity and fairness stay as they are.
3. **Later: flex tier.** OpenAI `service_tier: "flex"` is about half price, but the relay recomputes every receipt's cost from usage × catalog and refuses a mismatch, so it needs a receipt field for the tier (wire, vectors, both languages). Not in this round.
4. **Caching everywhere it is safe.** Automatic Anthropic `cache_control` stays on by default; the gateway adds an OpenAI `prompt_cache_key` derived from the session affinity key when the client sent none, so repeated prefixes hit the provider cache.
5. **A real catalog.** The production relay loads a curated catalog file (`--catalog`), refreshed with current prices (a reviewed import from OpenRouter's public model list for the curated slugs, then `relay admin catalog publish` + `approve`), including the cheap models (Haiku, mini, DeepSeek, Grok fast) and realistic local models (Qwen 3, Llama, Gemma at 4–32B) so GPU donors can serve useful work.
6. **The cost line everywhere.** The web, the TUI and the desktop app show "saved by caching" and "served for free on donors' GPUs" next to the dollars.

Batch APIs (50% off but hours of latency) do not fit live requests; out of scope.

---

## 5. A donor node in one file

- **Container image**: the existing `deploy/client/container/Containerfile` (static musl, `FROM scratch`, uid 65532, `/data`) is built and pushed by the release workflow to `ghcr.io/moochy-dev/moochy:<version>` and `:latest`, linux/amd64 and linux/arm64, with a provenance attestation.
- **`deploy/client/compose/compose.yaml`** with two profiles:
  - `api`: one `moochy` service; the provider key from a Docker secret file; the keystore passphrase from a second secret.
  - `gpu`: `ollama` (GPU reservation for NVIDIA) plus `moochy` with `network_mode: service:ollama`, so the model server is `http://127.0.0.1:11434` (loopback: no LAN or remote vetting needed, no port published to the host).
  - The container runs `moochy start --headless`: the same steps as §3, non-interactive and idempotent. Log in if needed (prints the device code and link in `docker compose logs`, waits), add the key from `--key-file` (the secret) or the local model from `--local URL --model …` if not present, run the safety step from `MOOCHY_MONTHLY_LIMIT`, donate when `MOOCHY_DONATE` (a project) and `MOOCHY_DONATE_CAP` are set and no such donation exists, then run the app in the foreground. A human approves the code once; nothing else needs a terminal.
- **Skill**: `moochy-donate` gets a "Run a node with Docker Compose" section (download the compose file, write the two secrets with the user typing the key, `docker compose --profile gpu up -d`, show the code from the logs). It passes `check-skills.py` (no `curl | sh`, no banned flags).
- Guide: `docs/guides/headless-node.md` §1.4 rewritten around the compose file.

---

## 6. Web (private repository)

The landing and the dashboard get three polish rounds (review notes in the relay repository's `relay/internal/web/review/`). The web keeps every existing rule: no-JS works, budgets, palette, motion limits, WCAG AA.

---

## 7. Rollout

Each item lands as its own commits, tested: CLI changes with `cargo test` and the e2e scenarios they touch; relay changes with `go test -race` and the e2e suite. Then a moochy-cli release (crates, CLI binaries, desktop bundles, container image), the relay pointer and deploy, and two security passes over the new surfaces (desktop IPC, compose secrets, routing changes) before the release is announced.
