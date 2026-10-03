# Donate to an organisation

You can donate tokens to a whole GitHub organisation or GitLab group instead of one repository. One donation, with one monthly limit, then serves every project the organisation's owner chose. Everything else works as in [Donate tokens](donor.md): your key stays on your machine, nothing is paid in advance, and you can pause or stop at any time.

Set up the app first ([Donate tokens](donor.md), steps 1 to 6): install, sign in, add a provider key, set this device's monthly limit, start the app.

---

## 1. Find the organisation

Organisations on Moochy have a public page:

| Code host | Organisation page |
|---|---|
| GitHub | `https://moochy.dev/org/github/acme` |
| GitLab, group or subgroup | `https://moochy.dev/org/gitlab/group` or `https://moochy.dev/org/gitlab/group/subgroup` |

The page shows **the projects a donation serves**, what was donated this month, and the top donors. Only projects the organisation's owner added from their own Moochy account are listed, and only those can use your donation: a repository under the organisation's name that someone else registered never does. A project page shows "Also funded by" the organisations that fund it.

Only organisations claimed by their owner have a page. Personal accounts are not organisations: donate to their projects one by one.

## 2. Donate

On the organisation page, press **Donate tokens**, or from the terminal:

```sh
moochy donate --org github/acme --cap '$20'           # up to $20 a month for all its projects together
moochy donate --org gitlab/group/subgroup --cap '$20'
```

Always write `--org` with the code host (`github/…` or `gitlab/…`): `moochy donate --repo acme/api` donates to the single project `acme/api`, never to the organisation. The settings are the same as for a project: monthly limit, limit per request, models, maximum effort, extras, schedule, and how you appear on public pages (see [Donate tokens](donor.md#7-donate-tokens)). From the terminal the defaults apply; change them on the website.

The donation shows **waiting for the maintainer** until the organisation's owner accepts you, **once for all its projects**, with a signature made on their own machine. Then your device starts serving.

## 3. One limit across every project

Your limits apply to all the organisation's covered projects **together**:

- **Monthly limit:** the total the organisation's projects can use in a month, not a limit per project. With a $20 limit and three projects, the three share the $20.
- **Limit per request, models, effort, schedule:** the same for every covered project.
- **Share caps:** the owner may cap how much of your monthly limit one project can use (for example 50 %), so one busy project does not use it all.
- **Projects with their own donors:** a project's own donation is used first on a tie; yours fills the rest.
- **When the owner changes the list:** a project added later is served by your donation; a project removed stops at once.

The most you can spend stays the smallest of: this donation's monthly limit, your device's monthly limit, and your provider's spending limit.

## 4. See where it went

| To see | Where |
|---|---|
| What each project used this month | Dashboard → the donation → **Where it went this month** |
| Your donations, the organisation's included (`org github/acme`), and their ids | `moochy donations` |
| Every request your key served, with the project | `moochy journal` |
| Proof of one request | its receipt: it names the project actually served and the organisation donation that paid |

## 5. Pause or stop

The same commands as for a project ([Donate tokens](donor.md#8-pause-or-stop-donating)): `moochy donations pause <id>`, `moochy donations stop <id>`, or `moochy pause` to stop serving from this device at once.

## When the organisation changes owner

If the organisation's owner on Moochy is replaced (they are no longer an owner at the code host and another owner claimed it), every donor accepted by the previous owner is dropped. Your donation stops serving until the new owner accepts you. Nothing was transferred, so there is nothing to recover.
