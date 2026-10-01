# Run Moochy on a server or in CI

The same `moochy` app runs without a desktop: on a small server, in a container, or inside a CI job. Use it to:

1. **donate tokens around the clock** from a machine **you** control (your key stays on it; Moochy never holds donors' keys), or
2. **run an agent** in CI or a container on your project's donations.

You never run any Moochy server yourself. Moochy runs its own service at moochy.dev, and the app on your machine is all you need.

---

## 1. An always-on donation

### 1.1 Keys and home directory

Without a desktop keychain, the app keeps its keys in a file encrypted with a passphrase. Give the app its own directory, and pass the passphrase in the `MOOCHY_PASSPHRASE` environment variable (from a file only root can read, or from your secret manager; never typed into shell history):

```sh
read -rs MOOCHY_PASSPHRASE && export MOOCHY_PASSPHRASE    # type it; stays out of history
moochy --home /var/lib/moochy login --roles worker --headless
# {"event":"device_code","user_code":"WXYZ-1234"}
```

Confirm the code from any browser where you are signed in to moochy.dev. The command then prints `{"event":"logged_in","device_id":"d_…"}`.

### 1.2 Provider key and limits

```sh
printf '%s' "$ANTHROPIC_KEY" | moochy --home /var/lib/moochy keys add anthropic --key-stdin   # key from your secret store
moochy --home /var/lib/moochy config set monthly_limit 25      # $25 a month from this machine
moochy --home /var/lib/moochy config set slots_max 4
```

Providers: `anthropic`, `openai`, `openrouter`, `deepseek`, `xai`. Set a spending limit at your provider as well ([how, per provider](donor.md#4-set-a-spending-limit-at-your-provider-strongly-recommended)). Then press **Donate tokens** on the project's page on moochy.dev.

### 1.3 Run it as a service

On a server, run the app as a systemd service with its own user:

```ini
# /etc/systemd/system/moochy.service
[Unit]
Description=Moochy (donation)
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

`up --foreground` prints one JSON line when ready and writes `/var/lib/moochy/state/node.json`. Check on it at any time:

```sh
sudo -u moochy moochy --home /var/lib/moochy status
sudo -u moochy moochy --home /var/lib/moochy pause      # stops serving immediately
sudo -u moochy moochy --home /var/lib/moochy journal --follow
```

### 1.4 In a container

The public repository ships a `Containerfile` (`deploy/client/container/`): the app alone on an empty base image, running as an unprivileged user, with its state in the `/data` volume. Build it, then run it with the passphrase from your platform's secret store:

```sh
docker build -f deploy/client/container/Containerfile -t moochy .
docker run --rm -it -v moochy-data:/data -e MOOCHY_PASSPHRASE moochy login --roles worker --headless
docker run --rm -i  -v moochy-data:/data -e MOOCHY_PASSPHRASE moochy keys add anthropic --key-stdin < key.txt
docker run --rm     -v moochy-data:/data -e MOOCHY_PASSPHRASE moochy config set monthly_limit 25
docker run -d --name moochy --restart unless-stopped -v moochy-data:/data -e MOOCHY_PASSPHRASE moochy up --foreground
```

The image already passes `--home /data`. Delete `key.txt` afterwards, or pipe the key from your secret store instead.

A machine that only donates needs **outgoing** HTTPS (to moochy.dev and to your provider) and opens no incoming port. The local API and MCP endpoints listen on `127.0.0.1` inside the container and are not used when you only donate.

---

## 2. An agent in CI or a container

1. **Add a device for the job**, once, from your workstation:

   ```sh
   read -rs MOOCHY_PASSPHRASE && export MOOCHY_PASSPHRASE
   moochy --home ./ci-node login --roles gateway --headless
   ```

   When you confirm the code in the browser, limit the device to **one repository**.
2. **Make it a member with its own monthly limit.** The repository owner runs `moochy members add --device d_… --repo owner/repo --cap '$5'` on their own machine. An agent running on its own can then never use up the project's donations.
3. **Store the key file** (`./ci-node`, encrypted) and its passphrase in your CI secret store.
4. **In the job**, restore the directory, start the app, and run the agent:

   ```sh
   moochy --home "$RUNNER_TEMP/ci-node" up --foreground &   # prints {"event":"ready",…} when connected
   moochy --home "$RUNNER_TEMP/ci-node" run --repo owner/repo -- <agent command>
   ```

   `moochy run` starts the agent inside the sandbox, already pointed at Moochy. Tool calls from donated tokens only reach agents inside `moochy run` ([why](run.md)). On Ubuntu 23.10 and later runners, the sandbox needs the one-time AppArmor profile described in [Linux](run.md#linux). For MCP or API access without tool calls, use `moochy mcp --repo owner/repo` or the settings printed by `moochy env --repo owner/repo`: see [Connect your tools](integrations.md). Everything stays on `127.0.0.1` inside the job.

There is no hosted endpoint to call instead, because a hosted endpoint would have to see your prompts. Running the small app next to the agent keeps end-to-end encryption everywhere.

---

## 3. Notes

- **Server address.** `moochy login --relay <url>` exists only for developing and testing the app. Normal use needs no address: the app connects to moochy.dev.
- **Updates.** `moochy update --from-file <file>` installs a signed release and refuses unsigned files; or replace the app yourself and restart. Check new releases as described in the [FAQ](faq.md#how-do-i-check-the-app-i-run). A restart never serves an old request again: the app refuses requests created before it started.
- **Clock.** Keep time sync (NTP) on. Requests more than 10 minutes old or ahead are refused, and `moochy doctor` warns about a wrong clock.
