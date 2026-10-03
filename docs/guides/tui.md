# The dashboard in your terminal: `moochy tui`

`moochy tui` opens a full-screen dashboard of everything you do with Moochy, as a donor and as a maintainer, without a browser. It shows the same data as the website and stays live as requests are served.

```sh
moochy tui        # or just `moochy`, with no arguments, in an interactive terminal
```

It talks only to the Moochy app on this machine (start it with `moochy up`). It never calls a provider, and it never shows a secret: no provider key values, tokens, or passphrases. Every action it offers is one of the CLI commands, with the same checks and confirmations.

```
 ◖•ᴗ•◗ moochy · @alice                ◆ 3 pending  ▲ 2 alerts  ● relay  ● node
 1 Over  2 Donations  3 Serv  4 Proj  5 Orga  6 Deci  7 Devi  8 Acti  9 Sett
╭ Donations (4) · $70.17 spent this month ─────────────────────────────────────╮
│  Status          Donating to                Spent / limit     Used           │
│▌ ✔ active        github/tokio-rs/axum       $27.42 / $40.00   ██████░░░  68% │
│  ‖ paused        github/rust-lang/rustfmt   $14.10 / $15.00   ████████░  94% │
│  ✔ active        org gitlab/inkscape        $18.65 / $60.00   ██░░░░░░░  31% │
╰──────────────────────────────────────────────────────────────────────────────╯
 j/k move  p pause/resume  - lower limit  x stop  / filter  ? help
```

The header shows the hamster (it reacts to new requests and dozes when the app is unreachable), your handle, how many decisions wait for you, alerts, and whether the server and the app are connected. The footer lists only the keys that work on the current screen.

---

## Tabs

| # | Tab | What it shows | Keys |
|---|---|---|---|
| 1 | **Overview** | This month's donations and use, the latest requests, what needs you, alerts | `d` donations, `v` live requests, `n` decisions, `a` activity |
| 2 | **Donations** | Your donations: status, monthly limit, spent, schedule, models; for an organisation donation, what each project used; the project's share link | `p` pause/resume, `-` lower the limit, `x` stop |
| 3 | **Served** | Live requests your devices serve and the ones your projects use: model, project, tokens, cost, latency, outcome | `g` back to the newest (live) |
| 4 | **Projects** | Your registered projects: donors, waiting requests, members, settings summary | `a` accept, `r` refuse |
| 5 | **Organisations** | Your organisations: covered projects, share caps, donors | `a` add a project or accept a donor, `x` remove a project, `r` refuse |
| 6 | **Decisions** | What waits for you, and the history: who, when, how | `a` accept, `r` refuse |
| 7 | **Devices & keys** | Your devices, cloud boxes and their tokens, which provider keys are present (never their values), lockdown and sandbox status | `x` revoke a box |
| 8 | **Activity** | What your key was used for (the journal) and receipts | `g`/`G` newest/oldest |
| 9 | **Settings** | This app's configuration (read only, never a secret) and the key bindings | `t` light/dark, `c` colours, `a` ASCII, `Enter` change |

Every list has an empty state that says what to do next, for example "No donations yet. Run `moochy donate <repo>`."

Devices & keys says it above the list: **Keys stay on this machine. Moochy never stores them online.** Your API keys stay on your machine. The dashboard only reads whether a key is present, from the app on this machine, never its value.

## Keys everywhere

| Key | Does |
|---|---|
| `1`–`9`, `Tab` / `Shift-Tab`, `[` / `]` | Go to a tab, next, previous |
| `j` / `k`, arrows | Move |
| `g` / `G`, `PgUp` / `PgDn` | First / last, page |
| `s` / `S` | Sort by the column, reverse |
| `Enter` | Open the detail, or act |
| `/` | Filter this list (fuzzy); the filter shows as a chip next to the tabs and survives live updates |
| `Esc` | Clear the filter, close a detail or overlay |
| `:` or `Ctrl-K` | Command palette: fuzzy search over tabs, this screen's actions, theme and colour toggles, refresh, suspend, quit, each with its key |
| `r` | Refresh |
| `?` | Help: every key that works here |
| `Ctrl-Z` | Suspend (`fg` to come back) |
| `q`, `Ctrl-C` | Quit |

The mouse works too: click a tab or a row, scroll lists. Paste works in the filter and palette.

## What the actions do

Anything that changes something asks first, in a dialog where **No** is the default: `y` runs it, `n` or `Esc` cancels. The result shows as a toast at the bottom right.

| Action | Runs | Like |
|---|---|---|
| Pause, resume, stop a donation; lower its limit | through the app on this machine | `moochy donations pause\|resume\|stop <id>` |
| Refuse a donor or member | through the app; no signature needed, a refusal grants nothing | `moochy decisions refuse <id>` |
| Revoke a cloud box | through the app | `moochy box revoke <d_…>` |
| **Accept** a donor (project, organisation, or person profile) | opens the real CLI | `moochy accept <donor> --repo …` / `--org …` / `--person …` |
| **Add or remove** a project of an organisation | opens the real CLI | `moochy org add\|remove <project> --org …` |
| Accept a donor who shows no handle | opens the real CLI | `moochy decisions accept <id>`: a link to accept with your passkey on moochy.dev |

**Owner-key actions open the real CLI.** For an accept or an organisation change, the dashboard steps aside exactly like `Ctrl-Z`, and runs the `moochy` command in your terminal. You see what it is about to sign, checked with the Moochy server and not through the app, and you type your owner key's passphrase into the CLI itself; the dashboard never sees it. Press `Enter` when the command is done and the dashboard comes back, refreshed. The background app cannot accept anyone, and neither can the dashboard.

## Colours, themes, and terminals

- **Light or dark** comes from `--theme light|dark`, then the `MOOCHY_THEME` variable, then your terminal's background (`COLORFGBG`), and is dark otherwise. `t` in Settings or the palette switches it. Your terminal's own background is never painted over.
- **Colours** follow the mint palette: mint for healthy and actions, butter for donated money and attention, coral for stop and errors, sky for information. Truecolor where the terminal supports it (`COLORTERM=truecolor`), else 256 colours, else 16. `c` cycles the depth.
- **`NO_COLOR`** (any non-empty value) turns colour off; `TERM=dumb` too. Selections then use reverse video and bold.
- **Never colour alone:** every state has a glyph and a word (`✔ active`, `‖ paused`, `■ stopped`, `✖ refused`, `◆ pending`, `▲ warn`).
- **`--ascii`** (also automatic with `TERM=linux` or `TERM=dumb`) draws borders with `+-|` and plain glyphs, for consoles and fonts without box drawing.
- **Size:** designed for 80×24 and wider; on wide terminals panes sit side by side, on narrow ones the detail opens full screen with `Enter` (`Esc` closes it). Below 60×15 it says the window is too small instead of cutting text.

Peer text (handles, project descriptions, model names) is cleaned before it is drawn, so a hostile name cannot send escape sequences to your terminal. Quitting, `Ctrl-C`, a crash, `kill`, or closing the terminal always restores it.

## Demo and snapshot mode

`--demo` runs the dashboard on a built-in example world, with no account and no running app: a safe way to look around.

```sh
moochy tui --demo
```

`--snapshot COLSxROWS` prints one frame as plain text and exits, after the keys in `--keys`: useful for docs, bug reports, and tests. The clock and data are fixed, so the output is the same every time.

```sh
moochy tui --demo --snapshot 80x24 --keys "2"                      # the Donations tab
moochy tui --demo --snapshot 100x30 --keys "4j<enter>" --theme light
moochy tui --demo --snapshot 80x24 --keys "/axum" --ascii
moochy tui --demo --snapshot 160x48 --keys "7" --ansi                # with colours
```

In `--keys`, characters are typed as they are (spaces ignored); named keys are `<enter> <esc> <tab> <s-tab> <up> <down> <left> <right> <pgup> <pgdn> <home> <end> <bs> <space> <lt> <c-x>` and `<click:COL,ROW>`. Without `--demo`, a snapshot shows your real data from the app on this machine.
