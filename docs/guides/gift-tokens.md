# Give AI tokens with a link or a QR code

A **gift** is a fixed amount of AI tokens behind one link. You make the link, then send it or print its QR code. The first person who claims it gets the tokens. They can use them on an open-source project, or for their own AI work on any project, public or private.

A token gift is paid by your own provider key, on your own machine. Your API keys stay on your machine. You pay your provider only for the requests that the gift serves. You can also pay a gift from your [Moochy Credits](credits.md), when credits are available.

The first half of this guide is for givers. The second half is for the person who claims the gift.

---

## For givers: make a gift

Set up the app first ([Donate tokens](donor.md), steps 1 to 6). Your device serves the gift with your key, as for any donation.

### On the web

1. Open **Donations**, then **Gift tokens** (`https://moochy.dev/gifts`).
2. Type the amount, from $1 to $1,000.
3. Optional: add a note (140 characters at most), choose the models, the visibility and the expiry.
4. Press **Create**.

The next page shows the link one time only. Copy it now. The page also gives:

- the QR code of the link, with **Download SVG**;
- a gift card that prints alone (QR code, amount and note);
- the warning: "Anyone who scans this first can claim it. Treat it like cash."

Moochy keeps only a hash of the link. Nobody can show the link again, and Moochy cannot either.

### In the terminal

```sh
moochy gift create 20                                   # a $20 gift, shown once
moochy gift create 50 --note 'For your next release' --expires 60
moochy gift create 10 --models anthropic/claude-sonnet-5
moochy gift create 20 --credits                         # paid from your credits
```

The command prints the link one time. Send it or turn it into a QR code where you want.

### Rules for a gift

| Rule | Value |
|---|---|
| Amount | $1 to $1,000 of tokens (credits: up to your available balance) |
| Expiry | 30 days by default, 90 days at most |
| Use | One claim only; the first claim wins |
| Open gifts | 20 at most for each giver |
| Spend window | 12 months after the claim |
| Note | 140 characters at most |
| Visibility | Public by default (**Show my handle**); you can choose a pseudonym or **Hide me** |
| Limit per request | $5 by default; $2 for a gift claimed for own use |

### List, revoke and replace

```sh
moochy gift list                        # open, claimed (by whom, for what), revoked, expired
moochy gift revoke gf_01J…              # the link stops working
moochy gift revoke gf_01J… --replace    # a new link for the same gift; the old link stops working
```

On the web, `https://moochy.dev/gifts` lists the same gifts with **Revoke** and **Replace link**. Use **Replace link** when you lose a link or send it to the wrong person. You can revoke a gift until somebody claims it.

### After a claim

- Moochy sends you an email: who claimed the gift, and for which project or for their own use.
- The claim makes a donation with a **total** in place of a monthly limit, for example "Total $20 · ends 2027-10-28". Your device serves it until it uses the total or until the end date.
- You can pause or stop it like any donation ([Donate tokens](donor.md#8-pause-or-stop-donating)). Tokens that the gift did not use never left your provider account.
- When the claimer declines the donation, or does not answer in 30 days, Moochy undoes the claim. The link then works again until its own expiry.

---

## For claimers: claim a gift

You need a Moochy account. Sign in on moochy.dev with GitHub or GitLab.

### On the web

1. Open the link or scan the QR code. The page shows the amount, the giver (or "Someone"), the note and the models. Opening the page changes nothing.
2. Sign in, if you are not signed in.
3. Choose where the gift goes. **For my own use** is always the first option. Your claimed projects, organisations and your own profile follow it.
4. Press **Accept the gift**.
5. Accept the donation with your passkey on the next page. Without a passkey, the page shows a `moochy approve` command for your owner key.

The gift is not kept for you until you press **Accept the gift**. Another person can claim it first.

### In the terminal

```sh
moochy gift claim https://moochy.dev/g/… --personal          # for your own use
moochy gift claim https://moochy.dev/g/… --repo owner/name    # for a project you claimed
moochy gift claim https://moochy.dev/g/… --org github/acme    # for an organisation you claimed
moochy gift claim https://moochy.dev/g/… --person github/you  # for your profile
```

You can give the link or only the token after `/g/`. The command accepts the donation at once when your owner key is on this machine. It asks for the owner key's passphrase one time. Without an owner key, it prints the page where you accept with your passkey.

### Which targets can receive a gift

- **For my own use.** Your Moochy account itself. Your linked GitHub or GitLab account must be at least 30 days old at the code host.
- **A project.** You claimed it on Moochy. It is public, is not a fork, is not archived, and is at least 30 days old at the code host.
- **An organisation or your profile.** You claimed it, and it covers at least one project that meets the project rules.

### Use a gift for your own work

A gift for your own use pays for requests from **your own devices**, on any repository, public or private, or outside a repository. Nobody else can spend it, not even the members of your projects. Your app checks this in the public key log.

```sh
moochy login --roles gateway                    # once, on each device you work from
moochy run --personal -- claude                 # your agent, with your own-use donations
moochy connect --personal                       # or wire your tools to them
```

`moochy env` and `moochy mcp` also take `--personal`. In a repository that is not on Moochy, the app uses your own-use donations without the flag. See [Run your agent safely](run.md) and [Connect your tools](integrations.md).

### Limits for own use

These limits stop people from farming gifts:

- Your linked GitHub or GitLab account must be at least 30 days old.
- You cannot claim your own gift. Moochy also refuses a claim between accounts that share a linked identity, a confirmed email address or a device.
- 3 claims a day for each account.
- 10 live gift donations for each account.
- A limit per request of $2 by default.

### Errors

| Message | Meaning |
|---|---|
| Page not found (404) | The link is unknown, used, expired or revoked. Moochy gives the same answer for all four. |
| `self_gift` | The gift comes from your own account, or from an account that shares a sign-in, an email or a device with yours. |
| `not_eligible` | The project is private, a fork, archived or younger than 30 days. For own use: your GitHub or GitLab account is younger than 30 days. |
| `already_donating` | The giver already donates to this project. Choose another target. |
| Limit reached | 20 open gifts, 3 claims a day or 10 live gift donations. Try again later. |

### Safety

- Treat a gift link like cash. Anyone who has it can claim it.
- Moochy never writes the link in its logs. The claim sends the token in the request body, not in the address.
- The gift page asks you only to sign in and to accept. It never asks for an API key.
