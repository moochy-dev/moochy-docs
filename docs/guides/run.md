# Run your agent safely with `moochy run`

Donated tokens come from someone else's machine. A donor, or anyone who took over their machine, could send back a response that tries to make your agent run something harmful, such as a tool call with `curl … | sh`. Moochy checks every tool call before your agent sees it, but checks can miss things. `moochy run` adds a second wall: your coding agent, and everything it starts, runs in a sandbox where a bad command cannot reach your files, your keys, or the network.

It is built into the Moochy app. You do not need Docker or any other service.

```sh
moochy up                          # once, if the app is not running
cd ~/src/my-project
moochy run -- claude               # or: opencode, aider, goose, any command-line agent
```

`moochy run` finds the project from the git remote of the current directory (or use `--repo owner/name`), points the agent at Moochy, and starts it. When the agent exits, the sandbox and everything in it are gone.

---

## What the agent can and cannot do

| | Inside `moochy run` |
|---|---|
| **Your project** | Read and write the project's folder (the git worktree). Use `--worktree DIR` to pick another one |
| **Secrets in the project** | Hidden: `.env` and `.env.*`, `*.pem`, `*.key`, `id_*`, `.npmrc`, `.netrc`, `.pypirc`, `credentials*`, cloud tool folders (`.aws`, `.gcloud`, `.azure`, `.kube`, `.docker`, `.ssh`), and every file ignored by git. The agent sees an empty file in their place |
| **Git** | Read `git status`, `git log`, and `git diff` as usual. Every `.git` folder is **read-only** inside by default, so the agent cannot commit, rewrite history, or plant a hook or setting that your own git would run later. You review the changes and commit them yourself after the run. `--git-writable` lets the agent commit to the project's own repository; `hooks/`, `config`, and submodules stay read-only even then. If git metadata changes in a way the sandbox cannot block (a new `.git` folder created somewhere inside), `moochy run` tells you after the run so you can review it |
| **The rest of your computer** | Not there: your real home folder, `~/.ssh`, `~/.aws`, your keychain, browser profiles, other repositories, and Moochy's own keys and settings do not exist inside. System folders (`/usr`, `/bin`, `/etc`, …) are read-only. `$HOME` and `/tmp` are empty, private, and deleted at the end |
| **Network** | Nothing except Moochy, and the hosts you allow with `--allow-host` (below). The agent reaches donated tokens through the usual base URLs; every other address fails |
| **Environment** | Clean: only `PATH`, `HOME`, `TMPDIR`, `USER`, `TERM`, and the Moochy settings for the agent. Your shell's tokens and variables are not passed in |
| **Processes** | Cannot see or signal processes outside, cannot gain privileges, and has limits on memory, open files, and process count. Stopping `moochy run`, even with `kill -9`, stops everything inside |

**Tool calls from donated tokens only reach agents inside `moochy run`.** If you connect a tool to Moochy without `moochy run`, it still gets the text of each response, but each tool call is replaced by a visible `[moochy]` notice. A project can turn this off for itself with `moochy config set allow_unsandboxed_tools owner/name` (a comma-separated list of projects); the app then warns you at every start. Use it only if you run your agent in your own sandbox.

## Tools installed in your home folder

Agents installed under your home folder (for example `~/.local/bin/claude`, or tools from nvm or cargo) are made visible inside, read-only, so they start normally. Nothing else from your home folder is.

## How the agent finds Moochy

Agents work unchanged: inside the sandbox, the standard variables point to Moochy. `ANTHROPIC_BASE_URL`, `OPENAI_BASE_URL`, and `OPENAI_API_BASE` name the local endpoints, and `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, and `OPENAI_API_KEY` (plus `MOOCHY_TOKEN`) carry a token made for this run only. That token is the agent's key to Moochy; it works only while the run lasts. No provider API key is ever visible inside the sandbox. `MOOCHY_MCP_URL` gives the MCP endpoint.

## Allowing other hosts

By default the agent can reach nothing but Moochy, so installing packages from inside the run fails. Allow the hosts you need, one `--allow-host` each:

```sh
moochy run --allow-host registry.npmjs.org --allow-host pypi.org --allow-host files.pythonhosted.org -- claude
```

- Each entry is an exact host name: no wildcards and no IP addresses. An invalid entry stops the run before it starts.
- Only HTTPS on port 443 goes through, by way of a small proxy that `moochy run` starts (`HTTPS_PROXY` points to it inside). Plain HTTP is refused.
- The proxy connects only if every address the name resolves to is public, so an allowed name cannot be pointed at your local network, at Moochy itself, or at cloud metadata.
- Each refusal is printed as one line, so you can see what the agent tried to reach.

Allow as little as you can: every allowed host is somewhere the agent can send data.

## Linux

The sandbox uses Linux user namespaces, Landlock, and seccomp. It needs Linux 5.13 or later with unprivileged user namespaces.

**Ubuntu 23.10 and later** block unprivileged user namespaces through AppArmor by default. `moochy run` and `moochy doctor` detect this and print the exact fix: a small AppArmor profile that allows namespaces for the `moochy` app only. It looks like this, with the real path of your `moochy`:

```
# /etc/apparmor.d/moochy
abi <abi/4.0>,
include <tunables/global>
profile moochy /usr/local/bin/moochy flags=(unconfined) {
  userns,
  include if exists <local/moochy>
}
```

Then load it with `sudo apparmor_parser -r /etc/apparmor.d/moochy`. Do not turn the restriction off for the whole system (`kernel.apparmor_restrict_unprivileged_userns=0`): that gives the same permission to every program on your machine.

## macOS

The sandbox uses macOS's built-in Seatbelt, the same mechanism other coding-agent tools use. Everything is blocked unless allowed: the agent can read system folders and your project, write only to your project and a private scratch folder, and connect only to Moochy on your machine, plus the allowed-hosts proxy when you use `--allow-host`. Writes to any `.git` folder are refused, at any depth.

## Windows

Not available yet. `moochy run` refuses to start rather than run your agent without a sandbox.

## If the sandbox cannot start

`moochy run` never falls back to running without a sandbox. It stops and tells you why; `moochy doctor` shows the same checks.

`--unsafe-no-sandbox` runs the command with no sandbox at all, after a warning. It exists for debugging Moochy itself. Do not use it with donated tokens.

## What `moochy run` does not change

- A donor can still return a wrong or low-quality answer. Review the changes your agent makes, as you would with any model.
- Text in a response can still try to talk you, or your agent, into running something. Inside `moochy run` the agent cannot do lasting damage; outside it, you are the safeguard.
- Another program running as your user outside the sandbox could read your project folder while a run is active. The sandbox protects you from the agent, not from malware already on your machine.
