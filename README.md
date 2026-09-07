# felixangell.com

A tiny static blog. Build with `make`, then commit the Markdown sources and
generated HTML before pushing. Output lives directly in the repository root.

Requires `make`, Python 3, and Discount's `markdown` command (already installed
on the current machine). No Python packages, JavaScript, or network access are
needed to build. On another machine, install these using its package manager.

## Writing

- Edit `content/index.md` for the home page and `content/now.md` for the now page.
  The now page is optional: deleting its Markdown file removes its navigation
  link and both generated now pages on the next build. Restore it to add them back.
- Add posts as `content/posts/YYYY-MM-DD-post-slug.md`. Use lowercase letters,
  digits, and hyphens in the slug. The date must be a valid calendar date.
- Start each post with `# Your post title` (plain text), followed by a blank line
  and the post's Markdown content. No front matter is required.

For example, `content/posts/2026-09-07-hello.md`:

```markdown
# Hello

My first post. Here's a [link to the now page](now/).
```

Run `make`. This creates `2026-09-07-hello.html` in the root and adds it to the
home page's post list, newest first. Every file in `content/posts/` is published,
including future-dated posts. Keep drafts elsewhere. Deleting or renaming a
post removes its old generated HTML on the next build.

The now page is also generated as `now/index.html`, so `/now` redirects to
`/now/` and serves the page. The existing `/now.html` URL still works.

Use output URLs in Markdown links (`now/`, `2026-09-07-hello.html`), and put
images in a root-level directory such as `images/`, linked as `images/photo.jpg`.
The shared template sets the URL base to the site root, so relative links and
images resolve there even on `/now/` or when hosted under a repository path.

Change `templates/page.html` for the shared layout and `style.css` for styling.
Generated HTML is overwritten by `make`.

## Preview and publish

Run `make dev` and open <http://localhost:8000>. Changes to Markdown, templates,
CSS, and assets automatically rebuild the site and reload the browser. Build
errors appear in the terminal; save a fix to retry. Stop with Ctrl-C.

The reload script is added only to local HTTP responses, never to generated
files. `make` still builds plain static HTML for publishing. `make serve` is also
available for a preview without watching or browser reloads.

Configure GitHub Pages to deploy from your publishing branch's **/ (root)**
directory. Commit the generated HTML (including `now/index.html`), `style.css`, and `.nojekyll` alongside the
sources. The `.nojekyll` file keeps the output served as plain static files.
