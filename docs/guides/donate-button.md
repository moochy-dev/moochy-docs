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

**Project addresses.** A project's pages live at `https://moochy.dev/p/<provider>/<path>`: `/p/github/tinyhttp/arrow`, `/p/gitlab/group/subgroup/project`. Add `/button.svg` for the image and `/donate` for the donation page. For GitHub, the short form without the provider (`/p/tinyhttp/arrow/button.svg`) also works and always will, so existing buttons keep working; `moochy button` prints it for GitHub projects.

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
[![Donate tokens](https://moochy.dev/p/gitlab/group/subgroup/project/button.svg)](https://moochy.dev/p/gitlab/group/subgroup/project/donate)
```

Keep the alt text "Donate tokens" (or the label you chose): screen readers announce it, and it shows when the image cannot load. Set `height` to match the size: 28 for `s`, 36 for `m`, 44 for `l`.

### 4. Put it in the README

1. Use the README at the repository root: `README.md`, `README.rst`, or `README` (in that order). If there is none, ask the maintainer before creating one.
2. **Avoid duplicates.** Search the README for `moochy.dev/p/`. If a Moochy button or badge is already there, do not add another; replace it only if the maintainer asked for a different style.
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

## Not on Moochy yet

If the project is not registered, give the maintainer this message (replace `PATH` with the path from step 1):

> Moochy lets people donate LLM tokens to this project from their own API accounts. To accept donations: sign in at https://moochy.dev/claim with the GitHub or GitLab account that administers `PATH`, register the repository, then confirm on your own machine with the Moochy app: `moochy owner init` (once) and `moochy claim PATH`. After that, the "Donate tokens" button can go in the README. Guide: https://moochy.dev/docs/maintainer

Do not register the project yourself, and do not run `moochy` commands that sign anything on the maintainer's behalf: claiming needs the maintainer's own owner key and confirmation.

## What not to do

- **No secrets.** The button needs no API key, token, password, or Moochy account. Never put one in a README, a URL, or a commit, and never ask the maintainer for one to add the button.
- **No tracking.** Do not add analytics or `utm_*` parameters, redirects, or link shorteners. Moochy does not track readers: it sees requests from GitHub's image proxy, not from visitors.
- **No scripts or embeds.** No JavaScript, iframes, or inline SVG copies of the button.
- **No donations or settings changes.** Adding a button never creates a donation, signs in, changes CI, or edits Moochy settings.
- **No other files.** Only the README changes.

## The studio

People can also build the button by hand: on moochy.dev, open the project and choose **Donate button** (or go to `https://moochy.dev/button`). Pick the label, style, theme, and size, see a live preview, and copy the Markdown or HTML. It produces exactly the snippets above.

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
