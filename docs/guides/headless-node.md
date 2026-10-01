# Running a headless node

The same `moochy` binary runs without a desktop: on a small server, in a container, or inside a CI job. Use it to:

1. **donate around the clock** from a machine **you** control (your key stays on it; Moochy never hosts donor keys), or
2. **run an autonomous agent** in CI or a container on your project's pool.

Moochy runs one relay, at moochy.dev, and does not offer self-hosting it. You never need to run any server component: a node is just the client.

---

## 1. An always-on donor

### 1.1 Keystore and home directory

Without a desktop keychain, keys live in a passphrase-encrypted file. Give the node its own directory and the passphrase through the environment variable `MOOCHY_PASSPHRASE` (filled from a root-only file or your secret manager, never typed into shell history):

```sh
read -rs MOOCHY_PASSPHRASE && export MOOCHY_PASSPHRASE    # type it; stays out of history
moochy --home /var/lib/moochy login --roles worker --headless
# {"event":"device_code","user_code":"WXYZ-1234"}
```

Approve the code from any browser where you are signed in to moochy.dev. The command then prints `{"event":"logged_in","device_id":"d_…"}`.

### 1.2 Key and limits

```sh
printf '%s' "$ANTHROPIC_KEY" | moochy --home /var/lib/moochy keys add anthropic --key-stdin
moochy --home /var/lib/moochy config set device_monthly_cap_uusd 25000000   # $25/month for this machine
moochy --home /var/lib/moochy config set slots_max 4
```

Set a spending limit at your provider as well ([donor guide §4](donor.md#4-set-a-spending-limit-at-your-provider-strongly-recommended)). Then create the pledge on the web (`moochy donate` needs a terminal).

### 1.3 Run it as a service

`moochy service install` sets up a user service. On a server you may prefer an explicit systemd unit with a dedicated user:

```ini
# /etc/systemd/system/moochy.service
[Unit]
Description=Moochy node (donor)
After=network-online.target
Wants=network-online.target

[Service]
User=moochy
ExecStart=/usr/local/bin/moochy --home /var/lib/moochy up --foreground
# MOOCHY_PASSPHRASE=… in a file readable only by root (chmod 600)
EnvironmentFile=/etc/moochy/passphrase.env
Restart=on-failure
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/moochy
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

`up --foreground` prints one JSON line when ready and writes `/var/lib/moochy/state/node.json`. Check it at any time:

```sh
sudo -u moochy moochy --home /var/lib/moochy status
sudo -u moochy moochy --home /var/lib/moochy pause      # instant local kill switch
sudo -u moochy moochy --home /var/lib/moochy journal --follow
```

### 1.4 In a container

Run the official container image (static binary, non-root) or your own, with a persistent volume for the home directory, and the passphrase from your orchestrator's secret store:

```sh
docker run -d --name moochy --restart unless-stopped \
  -v moochy-home:/home/moochy \
  -e MOOCHY_PASSPHRASE \
  <moochy image> --home /home/moochy up --foreground
```

Run `login`, `keys add`, and `config set` once in the same volume before starting it (`docker run --rm -it … <moochy image> --home /home/moochy login --roles worker --headless`).

A donor node needs only **outbound** HTTPS (to the relay and to your provider). It opens no inbound port. The local API and MCP doors are bound to `127.0.0.1` inside the container and are not used by a pure donor.

---

## 2. An agent in CI or a container uses the pool

1. **Register a device for the job**, once, from your workstation:

   ```sh
   read -rs MOOCHY_PASSPHRASE && export MOOCHY_PASSPHRASE
   moochy --home ./ci-node login --roles gateway --headless
   ```

   In the browser approval, grant the `gateway` role **scoped to one repository**.
2. **Make it a member with its own cap.** The repository owner runs `moochy members add --device d_…` and sets the device's monthly cap on the console. An autonomous agent can then never drain the pool.
3. **Store the keystore** (`./ci-node`, encrypted) and its passphrase in your CI secret store.
4. **In the job**, restore the directory, start the node, and point the agent at it:

   ```sh
   moochy --home "$RUNNER_TEMP/ci-node" up --foreground &   # prints {"event":"ready",…} when connected
   eval "$(moochy --home "$RUNNER_TEMP/ci-node" env --repo owner/repo --json \
     | jq -r '"export ANTHROPIC_BASE_URL=\(.anthropic_base_url) OPENAI_BASE_URL=\(.openai_base_url) MOOCHY_TOKEN=\(.token)"')"
   ```

   Then use the MCP door (`moochy mcp --repo owner/repo`, or `http://127.0.0.1:PORT/mcp` with the token) or the API door, exactly as on a workstation: see [Integrations](integrations.md). Both doors stay on loopback inside the job.

There is no hosted endpoint to call instead: a hosted endpoint would require the relay to see your prompts. Running the small binary next to the agent keeps end-to-end encryption everywhere.

---

## 3. Notes

- **Relay URL.** `moochy login --relay <url>` exists for development and tests of the client. Production nodes use the default moochy.dev relay.
- **Updates.** Replace the binary and restart. Verify releases as described in the [FAQ](faq.md#how-do-i-check-the-binary-i-run). A restart never replays an old task: a Worker refuses tasks created before it started.
- **Clock.** Keep NTP on. Tasks older or newer than 10 minutes are refused, and `moochy doctor` warns about clock skew.
