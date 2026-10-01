# Add a "Donate tokens" button

A **Donate tokens** button in your README takes visitors straight to your project's donation page on moochy.dev. Anyone can add one for a registered public repository: the maintainer, or a donor who wants to help a project be found.

## 1. Make the button in the studio

On moochy.dev, open your project and choose **Donate button**. Pick:

| Option | Choices |
|---|---|
| Repository | Any registered public repository |
| Label | "Donate tokens" by default |
| Style | Mascot and text, text only, or compact |
| Theme | Light, dark, or auto (follows the reader's GitHub theme) |
| Size | Small, medium, or large |

The preview updates as you change options. Press **Copy Markdown** or **Copy HTML** and paste the result into your `README.md`.

The studio writes the exact image address, including the options you chose. The examples below show the shape of what it gives you; copy yours from the studio rather than typing the options by hand.

## 2. Markdown

Works everywhere Markdown images work, including GitHub, GitLab, and most package registries:

```markdown
[![Donate tokens](https://moochy.dev/p/owner/repo/button.svg?style=mascot&theme=light)](https://moochy.dev/p/owner/repo/donate)
```

Replace `owner/repo` with your repository.

## 3. Light and dark with `<picture>`

GitHub shows READMEs in the reader's light or dark theme. To match it, use HTML with a `<picture>` element (choose **Theme: auto** in the studio):

```html
<a href="https://moochy.dev/p/owner/repo/donate">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://moochy.dev/p/owner/repo/button.svg?style=mascot&theme=dark">
    <img alt="Donate tokens" src="https://moochy.dev/p/owner/repo/button.svg?style=mascot&theme=light">
  </picture>
</a>
```

Keep the `alt="Donate tokens"` text: screen readers announce it, and it shows if the image cannot load.

## 4. Good to know

- The button is a plain SVG image with no scripts and no outside resources, so GitHub displays it through its image proxy like any other image. It may take a few minutes for a change of options to show, because GitHub caches images.
- The button does not track readers. Moochy sees an image request from GitHub's proxy, not from your visitors.
- The link opens your project's page, where visitors see your monthly goal, how much donors give, and the **Donate tokens** form.
- If you rename the repository on GitHub, update the address in your README.
