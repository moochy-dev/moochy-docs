# Use Moochy in cloud boxes

Coding agents increasingly run in hosted boxes: persistent VMs such as boat.dev, sandboxes such as E2B, Daytona, Modal, Morph, and Fly Machines, and GitHub Codespaces. Donors rent GPU machines on RunPod, Vast.ai, or Lambda. This page covers all three uses:

1. [Use donated tokens from a cloud box](#1-use-donated-tokens-from-a-cloud-box): your agent runs in a box and uses your project's donations.
2. [Donate from a cloud machine](#2-donate-from-a-cloud-machine): an always-on donation with an API key.
3. [Donate your own GPU server](#3-donate-your-own-gpu-server): a model you run on a rented GPU.

**Availability.** Everything on this page works with the current app, except reaching a GPU server on another machine over TLS (section 3, option B), which is being built. Check with `moochy --help`.

**AI agents inside a box:** this page is also at `https://moochy.dev/docs/boxes.md`. Follow section 1 for your platform. You need an enrollment token from the maintainer; never ask for their keys or passphrases.

---

## Install the app in a box

Every platform below uses the same installer. It needs outbound HTTPS and puts `moochy` in `~/.local/bin`:

```sh
curl -fsSL https://github.com/moochy-dev/moochy-cli/releases/latest/download/moochy-installer.sh | sh
```

On Ubuntu 23.10 and later (boat.dev, recent Lambda images), `moochy run` also needs the app installed system-wide with its AppArmor profile, as described in [Run your agent safely](run.md#linux). The release archives include the profile as `apparmor/moochy`.

Network: the app connects to `moochy.dev` on port 443 and to `relay.moochy.dev` on port **8443**. Most platforms allow both by default. If you restrict outbound traffic with a list of domains, note that several platforms match domains on ports 80 and 443 only: allow the relay's IP addresses for port 8443 instead.

---

## 1. Use donated tokens from a cloud box

### How it works

A box never gets a copy of your device's keys. Instead:

1. **You create an enrollment token** on your own machine (or on moochy.dev, Repositories → the project → Boxes). It is shown once.

   ```sh
   moochy box token create --repo owner/repo --ttl 24h --cap '$20' --max-boxes 5
   ```

   - `--ttl`: how long the token can be used to enroll new boxes.
   - `--cap`: the monthly limit for each box it enrolls, within your own limit as a member.
   - `--max-boxes`: how many boxes it may enroll in total (default 1).
2. **The box enrolls itself** with that token: `MOOCHY_ENROLL=<token> moochy up --headless`. The app creates the box's own keys inside the box. The box becomes a separate device: limited to that one project, with its own monthly limit and an expiry, and no power to accept donors, add members, or donate.
3. **You get an email** each time a box enrolls.
4. **You list and remove boxes** like devices:

   ```sh
   moochy box list                       # boxes enrolled for your projects
   moochy box revoke d_…                 # one box: its keys stop working immediately
   moochy box token list                 # your enrollment tokens
   moochy box token revoke bt_…          # a token and every box it enrolled
   ```

**One box, one identity.** Many platforms can fork, branch, or snapshot a running box. A copy carries the original box's keys, and Moochy refuses it: only one copy of a device can be connected at a time, and the app refuses to start when it notices it was moved to another machine. You get an alert. To use the copy, delete its Moochy home folder and enroll it again (with the same token, if it still has boxes left, or a new one).

**Rules that follow from this:**

- **Enroll when the box starts, never in a template, image, or snapshot.** Install the app in the template; run `moochy up` with the token only in the running box. Otherwise every box made from the template is a copy of the same identity.
- **Pass the token as a plain environment variable** from the platform's secret store. Some platforms offer "secrets" that only appear inside HTTPS headers through their own proxy (E2B's `Secret.fill`, Daytona's Secrets); those do not work for Moochy.
- **Tokens and boxes expire.** A short `--ttl` limits the damage if a token leaks, and revoking a box stops it at once.

### Sandboxing inside a box

- **In a full VM** (boat.dev, E2B, Morph, Lambda, Daytona and Modal VM classes): `moochy run -- <agent>` works as on any Linux machine. Run `moochy doctor` first; it says what is missing, such as the Ubuntu AppArmor profile.
- **In a container or a gVisor sandbox** where user namespaces or Landlock are not available (Modal's default runtime, some container platforms): `moochy doctor` names what is missing. `moochy run --box-is-sandbox -- <agent>` treats the box itself as the sandbox. The agent still gets a clean environment, the per-run token, and hidden secret files, and the app prints a warning. Tool calls from donated tokens reach such a session only if the project allows platform sandboxes (Project settings; on by default for box devices).
- **What `--box-is-sandbox` exposes.** Nothing isolates a donor's tool call from the rest of the box. It runs as the box's user, so it can read every file and the environment of every process of that user, including the `MOOCHY_ENROLL` token, and it can send them anywhere. Use the flag only in a box that holds no other credential: no `GITHUB_TOKEN`, no git credential helper, no cloud or registry keys. Create its enrollment token with the default `--max-boxes 1` and a short `--ttl`, so a token read after enrollment cannot enroll another box.
- **Never in GitHub Codespaces or a devcontainer.** A codespace always holds a `GITHUB_TOKEN` that can push to the repository, and a git credential helper. A donor's tool call could take them and push to your project. There, and in any box with credentials, do one of these instead:
  - Use a VM box (for example boat.dev, E2B, or the Daytona and Modal VM classes) where `moochy doctor` says that plain `moochy run` works.
  - Run the agent without donated tool calls: `moochy connect <agent>` or the `moochy_delegate` tool. Donated tokens still answer, and tool calls from them are replaced by a `[moochy]` notice.
  - Turn off platform sandboxes in the project's settings, so that no `--box-is-sandbox` session receives tool calls.

### Lifetimes and idle timers

Platforms stop boxes on their own schedule, and a background process often does not count as activity. When a box pauses and resumes, Moochy reconnects by itself; when a box is deleted, revoke it (or let it expire).

### boat.dev

Persistent Ubuntu 24.04 VMs with systemd, Docker, and disk-level fork.

```sh
boat env set-var base MOOCHY_ENROLL=<token>     # injected into sandboxes using the "base" environment
boat new --setup-file ./setup.sh                 # add --no-auto-stop to keep it running (paid plans)
```

`setup.sh`:

```sh
#!/bin/sh
set -eu
curl -fsSL https://github.com/moochy-dev/moochy-cli/releases/latest/download/moochy-installer.sh | sh
"$HOME/.local/bin/moochy" --home "$HOME/.moochy-box" up --headless
```

Then, over `boat ssh <id>`: `moochy --home ~/.moochy-box run --repo owner/repo -- claude`.

- Sandboxes stop 1 hour after creation by default; processes do not survive stop and resume, so start the app again (or use a systemd unit).
- `boat fork` and templates copy the disk, including the Moochy home folder: the fork must enroll again (delete `~/.moochy-box` first). Environment variables carry into forks, so a fork can re-enroll with the same token while it has boxes left.

### E2B

Firecracker microVMs, created from templates. Templates are built by snapshotting a running sandbox, so **install in the template, start in the sandbox**.

```ts
// template.ts: install only; do not start moochy here
import { Template } from 'e2b'
export const template = Template()
  .fromUbuntuImage('24.04')
  .runCmd('curl -fsSL https://github.com/moochy-dev/moochy-cli/releases/latest/download/moochy-installer.sh | sh')
```

```ts
import { Sandbox } from 'e2b'
const sbx = await Sandbox.create('my-moochy-template', {
  envs: { MOOCHY_ENROLL: process.env.MOOCHY_ENROLL },   // a plain env var, not an E2B Secret
  timeoutMs: 60 * 60 * 1000,
})
await sbx.commands.run('~/.local/bin/moochy up --headless', { background: true })
```

- The kernel has user namespaces, Landlock, and seccomp, so `moochy run` can sandbox the agent; check with `moochy doctor`.
- Sandboxes run up to 1 hour (Base) or 24 hours (Pro). With `onTimeout: 'pause'`, a resumed sandbox reconnects on its own.
- `fork()` and snapshots copy memory and disk: each copy must enroll again.
- With a domain allow-list, port 8443 needs the relay's IP addresses allowed.

### Daytona

Containers by default, or VM sandboxes.

```python
from daytona import Daytona, CreateSandboxFromImageParams, Image

image = Image.debian_slim("3.12").run_commands(
    "curl -fsSL https://github.com/moochy-dev/moochy-cli/releases/latest/download/moochy-installer.sh | sh")
sandbox = Daytona().create(CreateSandboxFromImageParams(
    image=image,
    env_vars={"MOOCHY_ENROLL": token},   # env_vars, not Daytona Secrets
    auto_stop_interval=0))               # a background process does not count as activity
sandbox.process.exec("~/.local/bin/moochy up --headless")
```

- On the lower Daytona tiers, outbound traffic is limited to a fixed list of services and cannot be changed per sandbox; Moochy cannot connect there. `moochy doctor` shows it.
- In containers, check `moochy doctor`. If user namespaces are missing, use a VM sandbox, or `--box-is-sandbox` only if the sandbox holds no credential other than `MOOCHY_ENROLL` ([what it exposes](#sandboxing-inside-a-box)). VM sandboxes support fork, which copies the identity: re-enroll.

### Modal

gVisor sandboxes by default, or VMs (`runtime="vm"`).

```sh
modal secret create moochy-enroll MOOCHY_ENROLL=<token>
```

```python
import modal
app = modal.App.lookup("moochy-agents", create_if_missing=True)
image = modal.Image.debian_slim().run_commands(
    "curl -fsSL https://github.com/moochy-dev/moochy-cli/releases/latest/download/moochy-installer.sh | sh")
sb = modal.Sandbox.create(image=image, app=app, timeout=24 * 3600,
                          secrets=[modal.Secret.from_name("moochy-enroll")])
sb.exec("bash", "-lc", "~/.local/bin/moochy up --headless")
```

- gVisor has no Landlock and only part of seccomp, so `moochy run` reports what is missing. Use the VM runtime, or `moochy run --box-is-sandbox` (the gVisor sandbox is the boundary) only if the sandbox holds no secret other than `moochy-enroll` ([what it exposes](#sandboxing-inside-a-box)).
- Sandboxes live at most 24 hours. Memory snapshots copy the identity: re-enroll.
- `outbound_domain_allowlist` allows port 443 only; to restrict traffic and still reach the relay, use `outbound_cidr_allowlist`.

### Morph Cloud

VM instances from snapshots, with branching.

```python
snap = client.snapshots.create(vcpus=2, memory=4096, disk_size=16384, digest="moochy-1")
snap = snap.setup("curl -fsSL https://github.com/moochy-dev/moochy-cli/releases/latest/download/moochy-installer.sh | sh")
inst = client.instances.start(snap.id, ttl_seconds=3600)
inst.exec("MOOCHY_ENROLL='<token>' ~/.local/bin/moochy up --headless")
```

- There is no secret store: pass the token at start, as above, never in a snapshot setup step.
- `branch` makes copies with memory and disk: each must enroll again.

### Fly Machines

Firecracker VMs from a Docker image; the root filesystem is fresh at every start.

```dockerfile
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y curl ca-certificates \
 && curl -fsSL https://github.com/moochy-dev/moochy-cli/releases/latest/download/moochy-installer.sh | sh
CMD ["/root/.local/bin/moochy", "--home", "/data/moochy", "up", "--headless", "--foreground"]
```

```sh
fly volumes create moochy_data --size 1
fly secrets set MOOCHY_ENROLL=<token>
fly machine run . --volume moochy_data:/data
```

- Keep the Moochy home on a volume so the box keeps one identity across restarts. A cloned machine gets a new, empty volume and enrolls as a new box.

### GitHub Codespaces and devcontainers

`.devcontainer/devcontainer.json`:

```json
{
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "postCreateCommand": "curl -fsSL https://github.com/moochy-dev/moochy-cli/releases/latest/download/moochy-installer.sh | sh",
  "postStartCommand": "nohup ~/.local/bin/moochy up --headless > /tmp/moochy.log 2>&1 &",
  "secrets": { "MOOCHY_ENROLL": { "description": "Moochy box enrollment token (moochy box token create)" } }
}
```

```sh
gh secret set MOOCHY_ENROLL --user        # or for one repository: --app codespaces --repo owner/repo
```

- The `secrets` block only reminds people to set the secret; `gh secret set` stores it. New secrets apply after the codespace restarts.
- Codespaces stop after the idle timeout (30 minutes by default) and live at most 12 hours.
- Prebuilds share one image between many codespaces: install there, but enroll only in `postStartCommand`, as above.
- Inside the codespace's container, check `moochy doctor`. If `moochy run` cannot sandbox there, do not use `--box-is-sandbox`: the codespace's `GITHUB_TOKEN` can push to the repository. Use `moochy connect <agent>` or `moochy_delegate` instead (no donated tool calls), or a VM box ([details](#sandboxing-inside-a-box)).

---

## 2. Donate from a cloud machine

A donation from a cloud VM works like one from any server: follow [Run Moochy on a server or in CI](headless-node.md#1-an-always-on-donation). In short:

```sh
read -rs MOOCHY_PASSPHRASE && export MOOCHY_PASSPHRASE
moochy --home /var/lib/moochy login --roles worker --headless
printf '%s' "$KEY" | moochy --home /var/lib/moochy keys add anthropic --key-stdin
moochy --home /var/lib/moochy safety --monthly-limit '$25' --accept-safety
moochy --home /var/lib/moochy service install --system
```

- Use a **separate API key with a spending limit at the provider** ([how](donor.md#4-set-a-spending-limit-at-your-provider-strongly-recommended)), and keep the key and passphrase in the platform's secret store or a root-only file.
- The app locks itself down after start-up. In a container that blocks those system calls, it refuses to donate and `moochy doctor` says what the container runtime blocks; use a VM, or the [container image](headless-node.md#14-in-a-container).
- **Do not clone a donor machine.** A copy has the same device keys and is refused. Give each machine its own `moochy login`.

---

## 3. Donate your own GPU server

You rent a GPU box, run a model server on it (vLLM, Ollama, llama.cpp, LM Studio), and donate tokens from it. See [Donate from your own GPU](local-gpu.md) for what is checked and why local usage is self-reported.

### Option A (recommended): the app on the same machine

Run the Moochy app **on the GPU box itself**, with the model server listening on `127.0.0.1`. Nothing is exposed to the internet, no TLS or API key is needed, and this works today on every platform.

Sign in as in section 2 (`login --roles worker --headless`), then:

```sh
vllm serve Qwen/Qwen2.5-7B-Instruct --host 127.0.0.1 --port 8000 --max-num-seqs 4 &
moochy --home /var/lib/moochy keys add local --base-url http://127.0.0.1:8000 \
  --model local/qwen2.5-7b=Qwen/Qwen2.5-7B-Instruct
moochy --home /var/lib/moochy config set slots_max 4
```

Then finish as in section 2 (safety step, service). On RunPod and Vast.ai, which run containers, start both from the container's start script; on Lambda, use systemd units.

### Option B: a GPU server you reach over TLS

When the Moochy app runs elsewhere, the model server must be reachable over **HTTPS with a valid certificate and an API key**. You add it explicitly: the exact host name is allowed, the key is kept in your keystore and sent as an `Authorization` header, and the certificate is checked. Plain HTTP and hosts you did not add are refused.

```sh
printf '%s' "$SERVER_KEY" | moochy keys add local --base-url https://<host> --key-stdin \
  --model local/qwen2.5-7b=Qwen/Qwen2.5-7B-Instruct
```

Start the server with a key: `vllm serve <model> --api-key "$SERVER_KEY"`. Ollama has no built-in key; put it behind a reverse proxy that checks one, or use option A.

| Platform | Stable HTTPS address | Notes |
|---|---|---|
| **RunPod** | Expose HTTP port 8000 in the pod; use `https://<pod id>-8000.proxy.runpod.net` | The address is public and goes through Cloudflare, which gives up after 100 seconds without a first response: very long prompts on slow models can time out. Store `SERVER_KEY` in RunPod Secrets and reference it as `{{ RUNPOD_SECRET_server_key }}` |
| **Vast.ai** | A named Cloudflare tunnel on your own domain | The default `trycloudflare.com` links change and are not suitable. Direct IP and port also work if you add your own certificate |
| **Lambda** | Your own DNS name, a reverse proxy with a certificate (for example from Let's Encrypt), port 443 opened in Lambda's inbound rules | Lambda allows only inbound SSH by default; nothing else is exposed until you open it |

---

## Platform summary

| Platform | Kind | `moochy run` | Copies of a box | Notes |
|---|---|---|---|---|
| boat.dev | Ubuntu 24.04 VM | Yes, with the AppArmor profile | `fork`, templates | Auto-stop 1 h by default |
| E2B | Firecracker microVM | Yes | `fork`, snapshots, every template | Up to 24 h; enroll in the sandbox, not the template |
| Daytona | Container, or VM | Container: check `doctor`; VM: yes | VM `fork` | Lower tiers cannot reach Moochy |
| Modal | gVisor, or VM | gVisor: `--box-is-sandbox` if it holds no other secret; VM: check `doctor` | Memory snapshots | Up to 24 h; domain allow-list is port 443 only |
| Morph Cloud | VM | Check `doctor` | `branch` | No secret store |
| Fly Machines | Firecracker microVM | Check `doctor` | `machine clone` (new empty volume) | Keep the home on a volume |
| GitHub Codespaces | Container on a VM | Check `doctor`; never `--box-is-sandbox` | Prebuilds share an image | Up to 12 h |
| RunPod | Container | Donors only | — | No UDP; proxy times out after 100 s |
| Vast.ai | Container, or KVM VM | Donors only | — | Use a VM for systemd |
| Lambda | Ubuntu VM | Donors only | — | Inbound SSH only by default |

Platforms change; when this table and `moochy doctor` disagree, trust `moochy doctor`.
