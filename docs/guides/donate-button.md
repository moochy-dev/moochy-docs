# Add a "Donate tokens" button

A **Donate tokens** button in a README takes visitors to the project's donation page on moochy.dev. This page is an exact recipe: a person or an AI coding agent working inside a repository can follow it step by step without guessing. Raw Markdown of this page: `https://moochy.dev/docs/donate-button.md`.

The button is a plain image link. Adding it needs no account, no key, and no token.

---

## Recipe

### 1. Find the project's provider and path

Run, in the repository:

```sh
url=$(git remote get-url origin)
host=$(printf '%s\n' "$url" | sed -E 's#^[a-z+]+://##; s#^[^@/]*@##; s#[:/].*$##')
path=$(printf '%s\n' "$url" | sed -E 's#^[a-z+]+://##; s#^[^@/]*@##; s#^[^:/]+(:[0-9]+)?[:/]##; s#/+$##; s#\.git$##')
case "$host" in github.com) provider=github ;; gitlab.com) provider=gitlab ;; *) provider= ;; esac
echo "$provider $path"
```

| `git remote get-url origin` | provider | path |
|---|---|---|
| `https://github.com/tinyhttp/arrow.git` | `github` | `tinyhttp/arrow` |
| `https://github.com/tinyhttp/arrow` | `github` | `tinyhttp/arrow` |
| `git@github.com:tinyhttp/arrow.git` | `github` | `tinyhttp/arrow` |
| `ssh://git@github.com/tinyhttp/arrow.git` | `github` | `tinyhttp/arrow` |
| `https://gitlab.com/group/project.git` | `gitlab` | `group/project` |
| `git@gitlab.com:group/project.git` | `gitlab` | `group/project` |
| `https://gitlab.com/group/subgroup/project.git` | `gitlab` | `group/subgroup/project` |

Stop and tell the maintainer instead of guessing when:

- `provider` is empty: only public repositories on github.com and gitlab.com can receive donations;
- `provider` is `github` and `path` does not have exactly one `/` (GitHub paths are always `owner/name`);
- there is no `origin` remote: ask which remote is the public one, and use `git remote get-url <name>`.

GitLab paths keep every group and subgroup (`group/subgroup/project`, up to 20 levels). Each segment is 1 to 100 characters from `A–Z a–z 0–9 . _ -` and starts with a letter or digit. Keep the case as it appears in the URL. Never print or store the remote URL itself: it can contain a token (`https://user:token@github.com/…`).

### 2. Check that the project is on Moochy, and get its addresses

```sh
curl -fsS "https://moochy.dev/api/v1/projects/$provider/$path"
```

The answer is public and contains no donor or amount. For `github` and `tinyhttp/arrow`:

```json
{"claimed": true, "donate_url": "https://moochy.dev/p/github/tinyhttp/arrow/donate", "button_url": "https://moochy.dev/p/github/tinyhttp/arrow/button.svg", "docs": "/docs/donate-button.md"}
```

- `"claimed": true`: go to step 3, and use `button_url` and `donate_url` exactly as returned.
- `"claimed": false`: do not add the button yet (it would show "project not found"). Tell the maintainer what is in [Not on Moochy yet](#not-on-moochy-yet).
- `404` with an `error` message: the provider or path is not valid; recheck step 1.

With the Moochy app installed, `moochy button` does steps 1 to 3 at once: it reads the git remote (offline) and prints the snippet. Options: `--repo <path>`, `--provider github|gitlab`, `--style mascot|text|compact`, `--theme light|dark|auto`, `--size s|m|l`, `--label TEXT`, `--format markdown|html|rst`.

**Project addresses.** A project's pages live at `https://moochy.dev/p/<provider>/<path>`: `/p/github/tinyhttp/arrow`, `/p/gitlab/group/subgroup/project`. Add `/button.svg` for the image and `/donate` for the donation page; on GitLab these come after GitLab's `/-/` separator (`/p/gitlab/group/subgroup/project/-/button.svg`, `/-/donate`), so nested group names stay unambiguous. For GitHub, the short form without the provider (`/p/tinyhttp/arrow/button.svg`) also works and always will, so existing buttons keep working; `moochy button` prints it for GitHub projects.

### 3. Pick the snippet

Replace `BUTTON_URL` and `DONATE_URL` with the values from step 2. The default button (mascot and text, light, medium) needs no options.

**Markdown** (`README.md`; works on GitHub, GitLab, and most package registries):

```markdown
[![Donate tokens](BUTTON_URL)](DONATE_URL)
```

**HTML, following the reader's light or dark theme** (GitHub and GitLab README files; recommended on GitHub):

```html
<a href="DONATE_URL">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="BUTTON_URL?theme=dark">
    <img alt="Donate tokens" height="36" src="BUTTON_URL">
  </picture>
</a>
```

**HTML, one theme** (when the README already uses HTML badges):

```html
<a href="DONATE_URL"><img alt="Donate tokens" height="36" src="BUTTON_URL"></a>
```

**reStructuredText** (`README.rst`):

```rst
.. image:: BUTTON_URL
   :target: DONATE_URL
   :alt: Donate tokens
```

For example, a GitLab project in a subgroup:

```markdown
[![Donate tokens](https://moochy.dev/p/gitlab/group/subgroup/project/-/button.svg)](https://moochy.dev/p/gitlab/group/subgroup/project/-/donate)
```

Keep the alt text "Donate tokens" (or the label you chose): screen readers announce it, and it shows when the image cannot load. Set `height` to match the size: 28 for `s`, 36 for `m`, 44 for `l`.

### 4. Put it in the README

1. Use the README at the repository root: `README.md`, `README.rst`, or `README` (in that order). If there is none, ask the maintainer before creating one.
2. **Avoid duplicates.** Search the README for `moochy.dev/p/` and `moochy.dev/org/`. If a Moochy button or badge is already there, do not add another; replace it only if the maintainer asked for a different style.
3. **Where.** If the README has a row of badges near the top (images linking to CI, coverage, package versions), add the button at the end of that row, on the same line or the same block, matching how the others are written (Markdown next to Markdown, HTML next to HTML). If there are no badges, add it on its own line right after the title (the first `#` heading or the `====` title), with one blank line before and after.
4. **Keep everything else as it is.** Do not reorder, reformat, or remove existing badges, and do not touch other files.
5. Commit only the README change, for example: `docs: add a "Donate tokens" button (Moochy)`.

### 5. Check

Open the image address in a browser or run `curl -s -o /dev/null -w '%{http_code}\n' "<image address>"`: `200` means the button renders. `400` means an option is wrong (the image then reads "invalid button options"); `404` means the project is not registered.

---

## `button.svg` reference

`https://moochy.dev/p/<provider>/<path>/button.svg` is the image and `…/donate` is where it links (for GitHub also the short form `/p/<owner>/<name>/…`). Query parameters are optional; these are all the accepted ones:

| Parameter | Values | Default | Meaning |
|---|---|---|---|
| `label` | 1 to 32 characters: letters, digits, spaces, and `. , : ; ! ? ' ’ & + - ( ) / # @` | `Donate tokens` | The text on the button. URL-encode it (`label=Fuel+this+project`) |
| `style` | `mascot`, `text`, `compact` | `mascot` | Mascot and text; text only; or two flat segments (the mascot on dark, the label on light blue) that look the same in every theme |
| `theme` | `light`, `dark`, `auto` | `light` | `auto` follows the viewer's system setting inside the image; on GitHub, use the `<picture>` snippet instead, which follows the reader's GitHub theme |
| `size` | `s`, `m`, `l` | `m` | Height 28, 36, or 44 pixels |

Rules, enforced by the server:

- Any other parameter, a parameter given twice, a value not listed above, or a query longer than 256 bytes makes the server answer `400` with an image that reads "invalid button options". Tracking parameters such as `utm_source` therefore break the button.
- Parameter order does not matter. The studio leaves out defaults and writes the rest in alphabetical order.
- The image is cached for a day by the server and by GitHub's image proxy. A changed option shows within that time; a new address (different options) shows at once.

## Organisations

A GitHub organisation or a GitLab group claimed on Moochy has its own button: a donation to the organisation serves every project its owner chose ([Donate to an organisation](donate-to-an-organisation.md)). Use it in the organisation's profile README, or in a project README when the maintainer asks for the organisation's button instead of the project's.

| Profile README | File |
|---|---|
| GitHub organisation | `profile/README.md` in the organisation's public `.github` repository |
| GitLab group | `README.md` in the group's `gitlab-profile` project |

Personal accounts are not organisations: a personal profile README uses the button of one of the person's projects.

**Check and get the addresses** (`ORG` is `acme` on GitHub; `group` or `group/subgroup` on GitLab):

```sh
curl -fsS "https://moochy.dev/api/v1/orgs/github/ORG"
```

```json
{"org_id": "o_01J…", "path": "github/acme", "claimed": true, "repos": [{"repo_id": "r_01J…", "slug": "github/acme/api"}], "donate_url": "https://moochy.dev/org/github/acme/donate", "button_url": "https://moochy.dev/org/github/acme/button.svg"}
```

Use `button_url` and `donate_url` exactly as returned. A `404` (`{"error":"not_found"}`) means the organisation is not on Moochy: do not add the button, and tell the maintainer what is in [Not on Moochy yet](#not-on-moochy-yet). An empty `repos` list is fine: donations start serving once the owner adds a project.

| Organisation | Image | Link |
|---|---|---|
| GitHub | `https://moochy.dev/org/github/ORG/button.svg` | `https://moochy.dev/org/github/ORG/donate` |
| GitLab, group or subgroup | `https://moochy.dev/org/gitlab/GROUP/SUBGROUP/-/button.svg` | `https://moochy.dev/org/gitlab/GROUP/SUBGROUP/-/donate` |

As for projects, GitLab actions come after `/-/`. The organisation path always starts with `github/` or `gitlab/`; there is no short form. The snippets of [step 3](#3-pick-the-snippet), the [query parameters](#buttonsvg-reference), the placement rules of [step 4](#4-put-it-in-the-readme) and the check of [step 5](#5-check) are the same. For example:

```markdown
[![Donate tokens](https://moochy.dev/org/github/acme/button.svg)](https://moochy.dev/org/github/acme/donate)
```

`moochy button` prints project buttons only (`moochy button --chart --org` prints the organisation's chart); the organisation owner finds this snippet, with a copy button, in **Organisation settings → Donate button**.

## People

A maintainer who claimed their own GitHub or GitLab profile can be sponsored: a sponsorship pays for that person's own requests on the public repos they maintain ([Sponsor a person](sponsor-a-person.md)). Their button goes in their personal profile README (GitHub: `README.md` of the repository named like the user, `LOGIN/LOGIN`; GitLab: the `README.md` of the project named like the user, `USERNAME/USERNAME`).

| Person | Page | Image |
|---|---|---|
| GitHub user | `https://moochy.dev/people/github/LOGIN` | `https://moochy.dev/people/github/LOGIN/button.svg` |
| GitLab user | `https://moochy.dev/people/gitlab/USERNAME` | `https://moochy.dev/people/gitlab/USERNAME/-/button.svg` |

Check first and get the addresses with `curl -fsS "https://moochy.dev/api/v1/people/github/LOGIN"` (or `…/people/gitlab/USERNAME`): the same shape as the organisations API, and `404` means the person has not claimed their profile, so do not add the button. Use `button_url` and `donate_url` exactly as returned. Snippets, options and placement are those of steps 3 to 5.

## Showcase charts

Next to the button, a project, an organisation or a person can show a live **chart** of the tokens donated to it and used by it. It is an image, so it works in GitHub and GitLab READMEs like the button, and updates by itself (every five minutes at most). It shows totals per day only: never a donor, never an amount per donor.

### Addresses

| For | Image (README) | Card (website `<iframe>`) | Links to |
|---|---|---|---|
| GitHub project | `https://moochy.dev/p/github/OWNER/NAME/chart.svg` | `…/card` | `https://moochy.dev/p/github/OWNER/NAME` |
| GitLab project | `https://moochy.dev/p/gitlab/GROUP/SUBGROUP/NAME/-/chart.svg` | `…/-/card` | `https://moochy.dev/p/gitlab/GROUP/SUBGROUP/NAME` |
| GitHub organisation | `https://moochy.dev/org/github/ORG/chart.svg` | `…/card` | `https://moochy.dev/org/github/ORG` |
| GitLab group | `https://moochy.dev/org/gitlab/GROUP/SUBGROUP/-/chart.svg` | `…/-/card` | `https://moochy.dev/org/gitlab/GROUP/SUBGROUP` |
| Person | `https://moochy.dev/people/github/LOGIN/chart.svg` | `…/card` | `https://moochy.dev/people/github/LOGIN` |

The chart links to the page (not to `/donate`), where visitors see the whole picture and the Donate button. The GitHub short form (`/p/OWNER/NAME/chart.svg`) works too. An organisation's chart sums the projects its donations serve.

### `chart.svg` options

All optional; the same rules as the button (any other key, a key given twice, or a value not listed answers `400` with an image reading "invalid chart options"):

| Parameter | Values | Default | Meaning |
|---|---|---|---|
| `metric` | `tokens`, `dollars` | `tokens` | Count tokens, or their cost in dollars |
| `series` | `both`, `donated`, `used` | `both` | Donated (mint, solid) against used (navy, dashed), or one of them |
| `kind` | `area`, `bars`, `line`, `sparkline` | `area` | Chart type; `sparkline` is a thin strip without axes |
| `period` | `7d`, `30d`, `90d`, `12m` | `30d` | Time span: one point per day (per week for `90d`, per month for `12m`) |
| `theme` | `light`, `dark`, `auto` | `light` | `auto` follows the viewer's system setting inside the image; on GitHub prefer the `<picture>` snippet |
| `size` | `s`, `m`, `l` | `m` | 320, 480 or 640 pixels wide (half as tall; a sparkline is an eighth) |
| `label` | 1 to 40 characters: letters, digits, spaces, and `. , : ; ! ? ' ’ & + - ( ) / # @` | the project's name | The title above the chart. URL-encode it |
| `goal` | `1` | off | Draw the monthly goal as a line (with `metric=dollars`, when a goal is set) |
| `total` | `1` | off | Show the period's total as a headline number |

A project that is not on Moochy, or not public, gets one neutral "not on moochy" image (HTTP `404`) instead of a chart.

### Snippets

`moochy button --chart` prints them for you, offline, with the same options (`--metric`, `--series`, `--kind`, `--period`, `--theme`, `--size`, `--label`, `--goal`, `--total`) and `--format markdown|html|rst|iframe`. Without `--repo` it reads the git remote, like `moochy button`; `--org ORG` and `--person PERSON` print the organisation's or the person's chart.

```sh
moochy button --chart                                             # this repository, Markdown
moochy button --chart --kind bars --period 90d --metric dollars --goal --total
moochy button --chart --format html                               # light and dark with <picture>
moochy button --chart --org github/acme --format iframe           # the card, for a website
moochy button --chart --person github/alice --kind sparkline --size s
```

**Markdown** (GitHub, GitLab):

```markdown
[![Tokens donated and used on Moochy](https://moochy.dev/p/github/tinyhttp/arrow/chart.svg)](https://moochy.dev/p/github/tinyhttp/arrow)
```

**HTML, light and dark** (GitHub; the `<source>` gets `theme=dark`):

```html
<a href="https://moochy.dev/p/github/tinyhttp/arrow">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://moochy.dev/p/github/tinyhttp/arrow/chart.svg?theme=dark">
    <img alt="Tokens donated and used on Moochy" src="https://moochy.dev/p/github/tinyhttp/arrow/chart.svg">
  </picture>
</a>
```

**GitLab project, with options** (`/-/` before the action):

```markdown
[![Tokens donated and used on Moochy](https://moochy.dev/p/gitlab/group/sub/project/-/chart.svg?goal=1&kind=bars&metric=dollars&period=90d&total=1)](https://moochy.dev/p/gitlab/group/sub/project)
```

**Organisation** (its profile README):

```markdown
[![Tokens donated and used on Moochy](https://moochy.dev/org/github/acme/chart.svg)](https://moochy.dev/org/github/acme)
```

**reStructuredText**:

```rst
.. image:: https://moochy.dev/p/github/tinyhttp/arrow/chart.svg?metric=dollars
   :target: https://moochy.dev/p/github/tinyhttp/arrow
   :alt: Tokens donated and used on Moochy
```

**Card for a website** (not for READMEs: GitHub and GitLab strip iframes). No script, no cookie, one link that opens the project page in a new tab:

```html
<iframe src="https://moochy.dev/org/github/acme/card" title="Tokens donated and used on Moochy" width="480" height="240" style="border:0" loading="lazy"></iframe>
```

Card sizes: `s` 320×160, `m` 480×240, `l` 640×320; sparklines 320×40, 480×60, 640×80.

Put the chart in the README right below the button row or in a "Support" section, never instead of the button; the placement rules of [step 4](#4-put-it-in-the-readme) apply. Keep the alt text (it is what screen readers announce); the image also carries its own text summary.

### The showcase studio

`https://moochy.dev/button` is the showcase studio: tab **Button** and tab **Chart**. Pick a project or organisation you can see, set every option above with a live preview in light and dark side by side, and copy the Markdown, HTML, reStructuredText or iframe snippet. The URLs are the canonical ones above (`/-/` on GitLab), exactly what `moochy button --chart` prints.

## Not on Moochy yet

If the project is not registered, give the maintainer this message (replace `PATH` with the path from step 1):

> Moochy lets people donate LLM tokens to this project from their own API accounts. To accept donations: sign in at https://moochy.dev/claim with the GitHub or GitLab account that administers `PATH`, register the repository, then confirm on your own machine with the Moochy app: `moochy owner init` (once) and `moochy claim PATH`. After that, the "Donate tokens" button can go in the README. Guide: https://moochy.dev/docs/maintainer

For an organisation (`ORG` as `github/acme` or `gitlab/group/subgroup`):

> To accept token donations for the whole organisation: sign in at https://moochy.dev/claim with an account that owns `ORG` (GitHub: an organisation admin; GitLab: a group Owner), choose Organisation, then confirm on your own machine with the Moochy app: `moochy claim --org ORG`, and add the projects it funds with `moochy org add PROJECT --org ORG`. Guide: https://moochy.dev/docs/organisations

Do not register the project or the organisation yourself, and do not run `moochy` commands that sign anything on the maintainer's behalf: claiming needs the maintainer's own owner key and confirmation.

## What not to do

- **No secrets.** The button needs no API key, token, password, or Moochy account. Never put one in a README, a URL, or a commit, and never ask the maintainer for one to add the button.
- **No tracking.** Do not add analytics or `utm_*` parameters, redirects, or link shorteners. Moochy does not track readers: it sees requests from GitHub's image proxy, not from visitors.
- **No scripts or embeds in a README.** No JavaScript, iframes (the chart card is for websites), or inline SVG copies of the button or chart.
- **No donations or settings changes.** Adding a button never creates a donation, signs in, changes CI, or edits Moochy settings.
- **No other files.** Only the README changes.

## The studio

People can also build the button by hand: on moochy.dev, open the project and choose **Donate button** (or go to `https://moochy.dev/button`, tab **Button**). Pick the label, style, theme, and size, see a live preview, and copy the Markdown or HTML. It produces exactly the snippets above. Tab **Chart** builds the [showcase chart](#showcase-charts).

## For maintainers: tell your agents

Add this to your repository's `AGENTS.md`, `CLAUDE.md`, or similar instructions file, so coding agents know about the button and keep it intact:

```markdown
## Moochy donate button

This project accepts LLM token donations through Moochy (https://moochy.dev).
- The README shows a "Donate tokens" button linking to the project's Moochy page (https://moochy.dev/p/…/donate).
  Keep it when you edit the README; do not duplicate it, change its address, or add tracking parameters.
- To add or change it, follow https://moochy.dev/docs/donate-button.md exactly.
- Never put API keys or tokens in the README or in commits.
```
