# Sponsor a person

Besides a project or an organisation, you can sponsor a **person**: a GitHub or GitLab user who maintains open source. A sponsorship pays for **that person's own requests** on the public repositories they maintain, with one monthly limit, wherever they work. It is not money: like every donation it is a limit on your own provider account, and you pay your provider only for requests actually served.

The first half of this guide is for the person being sponsored, the second for sponsors.

---

## For maintainers: claim your profile

Only you can claim your own profile, and nobody can ever take it over.

1. On moochy.dev, sign in with the GitHub or GitLab account of the profile. Open **Repositories**, then **Add a repository**, and go to **Your profile** ([moochy.dev/claim#person](https://moochy.dev/claim#person)). Press **Check with my code host**. The account must be at least 30 days old. Moochy checks that the account you just signed in with *is* that user (by the code host's numeric user id, not the name, so a renamed or re-registered login inherits nothing). Organisation and bot accounts cannot be claimed as a person.
2. Confirm on your own machine, within the hour, with the app running (`moochy up`):

   ```sh
   moochy claim --person                 # finds the claim you started on the web
   moochy claim --person github/alice    # or name it
   ```

   As for a project, the app shows what it is about to sign, asks you to confirm, and asks for your owner key's passphrase (it creates the owner key first if you have none). Your signature goes into the public key log. The command then prints your page to share (`Share: https://moochy.dev/people/github/alice`) and the public repositories you maintain, each with the command that adds it.

The owner key, the sign-in steps, and every error message are in [Claim your project, organisation or profile](claim.md#claim-your-profile).

Your page is `https://moochy.dev/people/github/LOGIN` (or `https://moochy.dev/people/gitlab/USERNAME`), linked from your Moochy profile.

### Choose the repositories it serves

```sh
moochy person add tinyhttp/arrow           # your sponsors' tokens now serve your requests there
moochy person add gitlab/group/tool
moochy person list                         # what your sponsorships serve
moochy person remove tinyhttp/arrow        # stop (add it back the same way)
```

Each `add` and `remove` is signed with your owner key. A repository can be added when:

- it is **public**;
- you **maintain** it: GitHub write access (push) or higher, GitLab Developer or higher, checked with your fresh sign-in on the code host;
- it is **not a fork**: you cover the projects you maintain, not your copies of someone else's.

The repository does not need to be registered on Moochy, and it may belong to someone else or to an organisation. Private repositories are never covered or listed. If you lose your role on a repository, it is dropped at your next sign-in; a repository that turns private is dropped at once.

Person settings on your page lets you set a **share cap** per repository: the most one repository may use of each sponsorship's monthly limit, in percent.

### Accept sponsors, once

```sh
moochy pending                                   # sponsors waiting for you
moochy accept ps_7hc2qz… --person                # or their handle; `moochy approve` is the same command
moochy accept ps_7hc2qz… --person --revoke       # remove a sponsor
moochy decisions --person github/alice           # what was decided
```

One acceptance covers every repository you add, now and later. Refusing needs no signature and can be done from the email Moochy sends you or on moochy.dev.

### What a sponsorship pays for

- **Your requests only.** Only requests from **your own devices** (signed in to your account) on a covered repository use your sponsors' tokens. Other members of those repositories never spend them, and every member's app checks this against the public key log.
- **One limit for all your repositories.** A sponsor's monthly limit, weekly and daily limits, limit per request, models, effort, and schedule apply to all your covered repositories together.
- **Projects and organisations first.** When a repository also has its own donors or an organisation's, they are used first on a tie: project, then organisation, then person.
- **No self-sponsoring.** You cannot sponsor yourself: Moochy refuses (`self_donation`) a sponsorship between accounts that are the same, share a linked GitHub or GitLab identity, a confirmed email address, or a device.

### Keep it active

Moochy keeps no code-host token. Your claim is re-checked each time you sign in on moochy.dev. Not signed in for **30 days**: the claim pauses (no new requests use your sponsorships; nothing else is lost), with an email a week before; signing in resumes it at once. Not signed in for **90 days**: the claim ends and its sponsors and repositories are dropped; claim again to come back.

Your app warns you if the public key log ever shows an entry for your profile (claim, repository, sponsor) that you did not sign.

---

## For sponsors: sponsor someone's tokens

Set up the app first ([Donate tokens](donor.md), steps 1 to 6). Your API keys stay on your machine: a sponsorship, like every donation, is served by the Moochy app on your own device with your own key.

On the person's page (`https://moochy.dev/people/github/LOGIN`), press **Sponsor tokens**, or from the terminal:

```sh
moochy donate --person github/alice --cap '$20'      # up to $20 a month for alice's own requests
moochy donate --person gitlab/bob --cap '$10'
```

Always write `--person` with the code host. `--repo alice/tool` is a project and `--org github/acme` an organisation, never a person.

- The page lists the repositories a sponsorship serves. `moochy person list --person github/alice` shows the same.
- The sponsorship waits until the person accepts you, once. Then your device serves their requests on those repositories, within your one monthly limit.
- **Not on Moochy yet?** A person must claim their profile before anyone can sponsor them: `moochy donate --person` answers `not_found` until then. Ask them to read [Claim your project, organisation or profile](claim.md).
- `moochy donations` lists it (with its id) next to your other donations; the dashboard shows what each repository used; every receipt names the repository served and the sponsorship that paid. Pause and stop work as for any donation ([Donate tokens](donor.md#8-pause-or-stop-donating)).

The person's profile README can carry a **Donate tokens** button and a live chart: see [Add a "Donate tokens" button](donate-button.md#people).
