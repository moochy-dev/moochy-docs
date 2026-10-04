# Claim your project, organisation or profile

Donors can donate tokens only to something that is claimed on Moochy. A claim proves that you control a repository, a GitHub organisation or GitLab group, or your own GitHub or GitLab profile.

Each claim has two halves:

1. On moochy.dev, your code host confirms your role. Moochy uses the code host's token for that one check and does not keep it.
2. Within one hour, the Moochy app on your machine signs the claim with your **owner key**. The signature goes into the public key log.

| You claim | Who can claim it | On moochy.dev | On your machine |
|---|---|---|---|
| A repository | An admin of the public repository | [Add a repository](https://moochy.dev/claim) | `moochy claim owner/repo` |
| An organisation | A GitHub organisation admin, or a GitLab group Owner | [Organisation](https://moochy.dev/claim#org) | `moochy claim --org github/ORG` |
| Your profile | Only you | [Your profile](https://moochy.dev/claim#person) | `moochy claim --person` |

---

## Before you start

Do these steps once. They are the same for the three kinds of claim.

### 1. Install the app

```sh
curl -fsSL https://moochy.dev/install.sh | sh
```

Other ways to install are in the [donor guide](donor.md#1-install).

### 2. Sign in on moochy.dev

Open [moochy.dev](https://moochy.dev) and sign in with GitHub or GitLab. The first time, you choose your handle and confirm an email address. You need the confirmed email for your owner key (step 5).

Only personal accounts can sign in. Organisation accounts and bot accounts cannot.

Moochy asks your code host for these permissions. Each one is used for one check and then dropped:

| Step | GitHub asks for | GitLab asks for |
|---|---|---|
| Sign in | `user:email` | `read_user` |
| Claim a repository | `user:email` (nothing more) | `read_api` |
| Claim an organisation | `read:org` | `read_api` |
| Claim your profile | `user:email` (nothing more) | `read_api` |

Your account at the code host must be at least **30 days old** to make any claim.

Sign in with the code-host account that has the role you claim. Your Moochy account can claim only on the code host you signed in with. A sign-in with the other code host opens a different Moochy account.

### 3. Add this device

```sh
moochy login --roles gateway
```

The command prints a code, such as `BCDF-GHJK`, and a link that already carries it (`https://relay.moochy.dev/device?code=BCDF-GHJK`). On a desktop it opens that link in your browser; over SSH, in a container or with `--no-browser` it only prints it (click it, or copy it into any browser). Check that the page shows the same code as your terminal, and press **Add this device**. The code works for 10 minutes. Use `--roles gateway,worker` if you also donate tokens from this machine.

### 4. Start the app

```sh
moochy up
```

`moochy claim` talks to the running app. If the app is not running, the command stops with `the Moochy app is not running: start it with moochy up`.

### 5. Create your owner key

```sh
moochy owner init
```

The owner key is a separate key for your decisions as an owner: claims, accepted donors, members, and the projects an organisation or your profile covers. A passphrase of at least 8 characters encrypts it. Only the commands you type use it. The app in the background never reads it.

The owner key exists so that nobody, not even Moochy's servers, can claim your project or accept a donor in your name. Every member's app checks these signatures in the public key log.

For your first owner key, Moochy emails your confirmed address a link that names the key id. Open the link while you are signed in on moochy.dev, and confirm within 10 minutes. If you already have a passkey on Moochy, approve the key with the passkey on moochy.dev instead. When the key is in the public key log, the command says how the log bound it, for example `bound with your confirmed email` (`"proof":"email"`); this can take up to a minute.

`moochy owner status` shows your owner key, how the log bound it, and the organisations and profiles it holds. If you skip this step, `moochy claim` offers to create the key first.

---

## Claim a repository

**Who can claim:** an admin of a **public** repository. On GitHub, you need the admin permission. On GitLab, you need the Maintainer or Owner role.

1. On moochy.dev, open **Repositories**, then **Add a repository** ([moochy.dev/claim](https://moochy.dev/claim)).
2. Choose GitHub or GitLab. Type the repository as `owner/name`. Press **Check with my code host**.
3. Approve the request at your code host. The page **Admin permission verified** shows the command for the next step.
4. Within one hour, run this command on your machine:

   ```sh
   moochy claim owner/repo                  # GitHub
   moochy claim gitlab/group/subgroup/name  # GitLab
   moochy claim                             # in the repository folder: uses the origin remote
   ```

   `moochy claim --repo owner/repo` does the same. The app shows what it will sign. Type `yes`, then your owner key's passphrase. The command prints the page to share, for example `Share: https://moochy.dev/p/github/owner/repo`.
5. In **Project settings**, set the monthly goal, a short note on what you use the tokens for, and the default model.

The next steps (accept donors, add members, connect your tools) are in [Use donated tokens in your project](maintainer.md).

## Claim an organisation

**Who can claim:**

| Code host | You claim | You must be |
|---|---|---|
| GitHub | An organisation, `github/acme` | An active **admin** of the organisation (its owner role) |
| GitLab | A **public** group or subgroup, `gitlab/group/subgroup` | An **Owner** of the group, direct or inherited from a parent group |

A personal account is not an organisation. On a personal account, claim each repository.

1. On moochy.dev, open [moochy.dev/claim](https://moochy.dev/claim#org) and go to **Organisation**.
2. Choose GitHub or GitLab. Type the organisation as `acme`, or the GitLab group as `group/subgroup`. Press **Check with my code host**.
3. Approve the request at your code host. On GitHub, allow the `read:org` permission. The page **Organisation owner verified** lists the public repositories of the organisation that you administer. These repositories are verified at the same time, so you can claim each of them in the next hour without another step on the web.
4. Within one hour, run this command on your machine:

   ```sh
   moochy claim --org github/acme
   moochy claim --org gitlab/group/subgroup
   ```

   The app shows the organisation, its id at the code host, and your owner key. Type `yes`, then your passphrase.
5. Choose the projects that the organisation's donations fund. Claim each project from the same Moochy account, then add it:

   ```sh
   moochy claim acme/api
   moochy org add github/acme/api --org github/acme
   moochy org list --org github/acme
   ```

The page of the organisation is `https://moochy.dev/org/github/acme`. Shared caps, donors, and owner changes are in [Donations for your organisation](organisations.md).

## Claim your profile

**Who can claim:** only you. You can claim the GitHub or GitLab profile of the account you signed in with, and no other. Moochy compares the code host's numeric user id, not the name. Nobody can take over a profile that you claimed.

1. On moochy.dev, open [moochy.dev/claim](https://moochy.dev/claim#person) and go to **Your profile**.
2. Choose GitHub or GitLab. Press **Check with my code host**.
3. Approve the request at your code host. The page **Profile verified** lists the public repositories that you maintain. A repository counts when you can push to it (GitLab: Developer role or higher). Forks never count.
4. Within one hour, run this command on your machine:

   ```sh
   moochy claim --person                 # finds the claim you started on the web
   moochy claim --person github/alice    # or names it
   ```

5. Choose the repositories that your sponsors' tokens serve:

   ```sh
   moochy person add tinyhttp/arrow
   moochy person list
   ```

Your page is `https://moochy.dev/people/github/LOGIN`. The rest is in [Sponsor a person](sponsor-a-person.md).

---

## Check the claim

1. `moochy owner status` lists your claims, organisations and profiles.
2. Ask the public API. It answers without a sign-in:

   ```sh
   curl -fsS "https://moochy.dev/api/v1/projects/github/owner/repo"   # "claimed": true
   curl -fsS "https://moochy.dev/api/v1/orgs/github/acme"             # "claimed": true
   curl -fsS "https://moochy.dev/api/v1/people/github/alice"          # 404 = not claimed
   ```

3. Open the button image, for example `https://moochy.dev/p/github/owner/repo/button.svg`. Before the claim, it shows "project not found". After the claim, it shows the **Donate tokens** button. The chart `…/chart.svg` also shows real numbers after the claim.

## Add the button and the chart

Put the **Donate tokens** button in your README so that donors find you:

- a repository: [the recipe](donate-button.md#recipe), or `moochy button` in the repository folder;
- an organisation: [organisation buttons](donate-button.md#organisations);
- a profile: [person buttons](donate-button.md#people), for your profile README;
- a live chart of donated and used tokens: [showcase charts](donate-button.md#showcase-charts), or `moochy button --chart`.

## Keep the claim active

Moochy keeps no code-host token. Each time you sign in on moochy.dev, Moochy checks your role again. If you do not sign in for **30 days**, the claim pauses: no new request uses its donations. You get an email a week before. Sign in to resume the claim at once. After **90 days** without a sign-in, or when a check finds that you lost the role, the claim ends.

## Troubleshooting

Messages on moochy.dev:

| Message | What it means and what to do |
|---|---|
| Only personal user accounts can sign in to Moochy: not organisations or bots. | You approved with an organisation or bot account. Sign in at the code host with your personal account. |
| Your provider account is too new to claim a repository. (or: an organisation, your profile) | Your code-host account is less than 30 days old. Claim again when it is 30 days old. |
| Sign in with this provider to claim its repositories. (or: its organisations, your profile there) | You signed in to Moochy with the other code host. Sign out, sign in with this code host, then claim again. |
| You approved with a different github account than the one linked to Moochy. | The code host is signed in with another account. Sign out there, then approve with the account linked to Moochy. |
| Repository not found. Only public repositories can be claimed with GitHub. | The name is wrong, or the repository is private. Check `owner/name`. |
| This repository was renamed or transferred. Claim it under its current owner/name. | Use the current name. |
| Only an administrator of the repository can claim it. | You are not an admin (GitLab: Maintainer or Owner). Ask an admin to claim it, or to give you the role. |
| Only public repositories can be claimed on this instance. | Moochy accepts only public repositories. |
| This repository is already claimed. | Another Moochy account holds the claim. It ends when that account loses the admin role, or after 90 days without a sign-in. |
| The provider did not grant Moochy permission to read your organisations (read:org). Please try again and allow it. | You did not allow `read:org` on GitHub. Claim again and allow it. |
| Organisation not found, or you are not one of its members. Personal accounts are not organisations. | Check the name. Accept any pending invitation to the organisation first. |
| Only an owner of the organisation can claim it. | You are not an organisation admin (GitLab: group Owner). |
| Only public organisations can be claimed on this instance. | The GitLab group is not public. |
| This organisation is already claimed. | Another owner holds it and is still an owner at the code host. See [When the owner changes](organisations.md#6-when-the-owner-changes). |
| This profile is already claimed by another Moochy account. | Your code-host account is linked to another Moochy account. Sign in with that account. |
| Another repository (or organisation, or account) was known under this name. It is being updated; please try again later. | A rename at the code host is not yet processed. Try again later. |
| Could not check the repository (or organisation) with the provider. Please try again. | The code host did not answer. Try again. |

Messages in the terminal:

| Message | What it means and what to do |
|---|---|
| `the Moochy app is not running: start it with moochy up` | Run `moochy up`, then the command again. |
| `not logged in: run moochy login first` | Sign in this device with `moochy login`, start the app with `moochy up`, then run the command again. |
| `this claim's GitHub check expired (1 hour), or it was never started` (GitLab: `GitLab check`) | No web check is waiting for this name, or it is more than one hour old. Do the web step again, then run the command within one hour. Use the name that the web page shows. `moochy pending` marks such a claim `"expired": true`. |
| `no pending ORG_CLAIMED request for github/org` | No web check is waiting for this organisation. Do the web step again, then run the command within one hour. |
| `no profile claim is waiting: sign in on the web and choose Claim your profile` | Do the web step for your profile, then run the command within one hour. |
| `email_required` | Your account has no confirmed email. Confirm one in **Settings** on moochy.dev, then run `moochy owner init` again. |
| `your email address changed less than 72 hours ago` | Wait 72 hours after an email change, or approve the key with a passkey that you already have. |
| `the confirmation came too late (more than 10 minutes)` or `nobody confirmed within 10 minutes` | Run `moochy owner init` again and confirm the new email within 10 minutes. |
| `no owner key on this device: run moochy owner init first` | Create the key, or run the command on the machine that has it. |
| `refusing to sign: …` | The app found a difference between what you asked for and what it was asked to sign. It signed nothing. Check the name and try again. If it happens again, [report it](faq.md#how-do-i-report-a-vulnerability). |
