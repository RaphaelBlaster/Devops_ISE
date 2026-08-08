# Portfolio - static personal site

## Overview

A single static page that presents a short profile, an about section, a grid of
project cards and contact details. It is one HTML file and one stylesheet:

- `index.html` holds all the content and links to `portfolio.css`.
- `portfolio.css` holds a dark theme built from CSS custom properties, a
  responsive single-column to multi-column layout, a grid for the cards and
  visible focus styles.

There is no build step, no framework and no JavaScript. Nothing is loaded from
the internet: no CDN, no web fonts, no analytics. The page therefore renders
identically offline and can be opened straight from disk.

The name and the contact details are filled in. The four project cards are still
placeholders, and an HTML comment above the card list marks them as such.

## Prerequisites

- Any modern browser: Edge, Chrome, Firefox or Safari.
- Python 3.11 or newer, only for the optional local web server. The page works
  without it.
- A text editor, for replacing the placeholder text.

## Steps

1. Open the page. Either double-click `index.html` in File Explorer, or serve the
   directory over HTTP so the address bar shows a normal URL:

   ```powershell
   Set-Location .\Portfolio
   python -m http.server 8000
   ```

   Then open `http://localhost:8000/`. Stop the server with Ctrl+C.

   Opening the file directly works because the page needs nothing from the
   server. `python -m http.server` is still worth using while editing, because
   the browser then refreshes the stylesheet on reload instead of serving a
   cached copy.

2. The name is already set. It appears in three places in `index.html`: the
   `<title>` element in the head, the `<p class="brand">` element in the header,
   and the `<h1>` in the hero. Change all three together if the page ever needs a
   different name.

3. Replace the hero text. Edit the `<p class="eyebrow">`, the `<h1>` and the
   `<p class="lede">` inside `<section id="hero">`.

4. Replace the about text. Edit the two `<p>` elements inside
   `<section id="about">`, and change the `<li>` items in the `tag-list` so they
   name the tools you can actually use.

5. Replace the project cards. Inside `<section id="projects">` there is a
   `<ul class="project-grid">` whose four `<li class="project-card">` blocks are
   placeholders. For each real project:

   - change the `<h3>` to the project name,
   - rewrite the `<p>` so it says what the project does and what it achieved,
   - update the `tag-list` items with the technologies used,
   - point the `<a href>` at the repository or the live page and update its
     `aria-label`.

   Copy a whole `<li class="project-card">` block to add a project, and delete
   blocks you do not need. Delete the comment above the list once the cards are
   real.

6. The contact details are already set. In `<section id="contact">` the email
   address and the GitHub profile point at the owner of this repository. Update
   both the `href` value and the visible link text if either changes.

7. Adjust the theme if you want different colours. Every colour is a custom
   property at the top of `portfolio.css`:

   - `--bg` and `--bg-raised` for the page and card backgrounds,
   - `--text` and `--text-muted` for body copy,
   - `--accent` and `--accent-strong` for links and buttons,
   - `--focus` for the keyboard focus ring.

   Change those values only; nothing else in the stylesheet hard-codes a colour.

8. Check the result at a narrow width before you publish. Narrow the browser
   window to about 360 px and confirm the cards stack in one column and the
   header navigation wraps instead of overflowing.

## Verification

The page must load its stylesheet from a relative path. From this directory:

```powershell
Select-String -Path .\index.html -Pattern 'portfolio.css'
Test-Path .\portfolio.css
```

```text
index.html:9:    <link rel="stylesheet" href="portfolio.css">

True
```

No external resource may be referenced:

```powershell
Select-String -Path .\index.html -Pattern 'https?://' | Select-String -NotMatch 'example\.com|github\.com'
```

The filter removes the `example.com` placeholders inside the project cards and
the GitHub profile link in the contact section, so the command prints nothing
while the page loads nothing from the internet. If it prints a line, that line is
either a card filled in with a real link or an accidental CDN or font reference.

With `python -m http.server 8000` running, the browser console must show no
failed requests, and the page must still look correct after a hard reload
(Ctrl+F5). The visible checks:

- The header stays at the top while you scroll and its four links jump to the
  matching sections.
- On a wide window the four project cards sit in a grid; on a narrow window they
  stack in one column with no horizontal scrollbar.
- Pressing Tab walks through the skip link, the navigation, the two hero buttons,
  the card links and the contact links, and every stop shows a yellow focus ring.
- Nothing is requested from another domain, so the page renders the same with the
  network disconnected.

## Files

- `index.html` - the whole page. Semantic landmarks (`header`, `nav`, `main`,
  four `section` elements, `footer`), a skip link, a hero with two buttons, an
  about section with a tag list, a project grid with four placeholder cards and
  an HTML comment telling the owner to replace them, and a contact list.
- `portfolio.css` - dark theme built on CSS custom properties in `:root`,
  responsive layout, `grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr))`
  for the cards from 40rem upward, `:focus-visible` outline for keyboard users,
  plus reduced-motion and print rules.
- `README.md` - this file.
