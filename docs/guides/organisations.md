# Donations for your organisation

If you own a GitHub organisation or a GitLab group, donors can give to the **organisation** instead of one repository. One donation then serves every project you choose in it, under one monthly limit. You accept each donor once for the whole organisation.

This guide is for the organisation's owner. Donors: see [Donate to an organisation](donate-to-an-organisation.md). The basics (owner key, accepting donors, members, tools) are in [Use donated tokens in your project](maintainer.md).

---

## Who can claim an organisation

| Code host | Organisation | You must be |
|---|---|---|
| GitHub | an organisation, `github/acme` | an **admin** of the organisation (its owner role) |
| GitLab | a group or a subgroup, `gitlab/group` or `gitlab/group/subgroup` | an **Owner** of the group (directly or inherited from a parent group) |

Personal accounts are not organisations: on a personal account, register each repository (see [Use donated tokens in your project](maintainer.md)). One Moochy account holds an organisation's claim at a time.

## 1. Claim the organisation

1. Sign in on moochy.dev with the GitHub or GitLab account that owns the organisation.
2. Open **Claim** and choose **Organisation**. Enter it as `github/acme` or `gitlab/group[/subgroup…]`. Moochy asks your code host, once, whether you are an owner. On GitHub this asks for the `read:org` permission; the token is used for that check and not stored. The page then lists the organisation's public repositories you administer.
3. Confirm on your own machine, within the hour:

   ```sh
   moochy claim --org github/acme
   ```

   The app checks the organisation with the Moochy server, shows what it is about to sign (the organisation, its id at the code host, your owner key), asks you to confirm, and asks for your owner key's passphrase. If you have no owner key yet, it creates one first. Your signature (`ORG_CLAIMED`) goes into the public key log.

`moochy owner status` lists the organisations your owner key holds. The organisation page is public from then on: `https://moochy.dev/org/github/acme`, or `https://moochy.dev/org/gitlab/group/subgroup` on GitLab.

## 2. Choose the projects it funds

An organisation donation serves only the projects you add, one by one, each with your owner key. A project can be added when:

- **you** registered it, from the same Moochy account that holds the organisation (`moochy claim owner/name`, as in the [maintainer guide](maintainer.md#2-register-your-repository)); and
- it belongs to the organisation at the code host (GitHub: the organisation owns it; GitLab: it sits in the group or one of its subgroups).

```sh
moochy claim acme/api                          # once per project, if it is not registered yet
moochy org add acme/api --org github/acme      # the organisation's donations now fund it
moochy org add gitlab/group/sub/app --org gitlab/group
moochy org list --org github/acme              # what the organisation's donations fund
moochy org remove acme/api --org github/acme   # stop funding it (add it back the same way)
```

Each `add` and `remove` shows what it will sign and asks for your passphrase, like a claim. **Organisation settings** on the organisation page lists the projects you can add (yours, inside the organisation, not added yet) with the exact command for each.

A project of the organisation that **another account** registered is never funded by your organisation's donations, and neither is a project outside the organisation, whatever its name. This is checked by every member's app against the public key log, not only by Moochy's servers.

## 3. Share caps (optional)

By default a covered project may use all of an organisation donation's monthly limit. To keep one busy project from using it all, open **Organisation settings → Projects** and set a **share cap** on it: the most that project may use of each organisation donation's monthly limit, as a whole percent from 1 to 100. Leave it empty for no cap. Share caps are a setting on moochy.dev, not a signature, and take effect at once.

The same table shows what each project used this month.

## 4. Accept donors, once for the organisation

A donor who donates to the organisation waits for you, as for a project. Accepting them covers every project you added, now and later.

```sh
moochy pending                                       # donors waiting for you, projects and organisations
moochy accept ps_7hc2qz… --org github/acme           # or the donor's handle; `moochy approve` is the same command
moochy accept ps_7hc2qz… --org github/acme --revoke  # remove a donor you accepted
moochy decisions --org github/acme                   # what was decided, who, when, how
```

The app shows exactly what it will sign (the organisation, the donor, your owner key) and asks for your passphrase. You can also refuse from **Organisation settings → Waiting donors** or from the email Moochy sends you; refusing needs no signature. Accepting always happens on your own device.

The donor's limits (monthly limit, limit per request, models, effort, schedule) apply to all your covered projects **together**. When a project also has its own donors, the project's own donation is used first on a tie; the organisation's donation fills the rest.

## 5. The button and the organisation page

The organisation page shows its projects, this month's donations, and its top donors. Each covered project's page shows "Also funded by" the organisation.

Put the organisation's **Donate tokens** button in your organisation's profile README (GitHub: `profile/README.md` in the organisation's `.github` repository; GitLab: the `README.md` of the group's `gitlab-profile` project), or in any of its projects' READMEs:

```markdown
[![Donate tokens](https://moochy.dev/org/github/acme/button.svg)](https://moochy.dev/org/github/acme/donate)
```

GitLab: `https://moochy.dev/org/gitlab/group/-/button.svg` and `…/-/donate`. Every option and snippet: [Add a "Donate tokens" button](donate-button.md#organisations). **Organisation settings → Donate button** has a copy button.

## 6. When the owner changes

The claim follows who owns the organisation at the code host, checked at each claim.

- **While you are an owner**, nobody else can claim the organisation: another owner's attempt is refused.
- **When you are no longer an owner** (you left the organisation, or lost the admin or Owner role), another owner can claim it. Moochy asks the code host, with the new owner's own sign-in, whether you are still an owner; only if you are not does the claim move.
- **What a move changes:** the new owner's `ORG_CLAIMED` goes into the public key log. Every donor you accepted for the organisation and every project you added are dropped: their donations stop serving until the new owner accepts each donor again and adds their own projects. Your projects stay yours, with their own donors; they are simply no longer funded by the organisation.
- **Both of you get an email** ("an organisation you claimed was claimed by another account"). This security email cannot be turned off. If you did not expect it, check your role at the code host.

To hand the organisation over, give the new person the owner role at the code host, step down, then they claim it.

Your app also warns you if the public key log ever shows an organisation entry for your account (claim, project added or removed, donor accepted) that you did not sign.

## Keep the claim active

Moochy keeps no code-host token. Your claim is re-checked each time you sign in on moochy.dev (your role: organisation admin or group Owner). Not signed in for **30 days**: the claim pauses (no new requests use its donations; donors, approvals and history stay), with an email a week before; signing in resumes it at once. Not signed in for **90 days**, or no longer an owner at a re-check: the claim ends, its approvals and covered projects drop, you get an email, and any current owner can claim it.

## Emails you get

The same kinds as for a project, for the organisation: a donor is waiting, a donation accepted, refused, or expired, the organisation claimed, a project added or removed, and the security email above. Turn each optional kind off in Settings.
