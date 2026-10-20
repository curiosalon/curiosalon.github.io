# Curio Museum

Jekyll blog at https://curiosalon.github.io. Source lives in V:\src\web.

## Local tools

Ruby 3.4.11 with DevKit is installed in
%LOCALAPPDATA%\Programs\Ruby34.
Open a fresh terminal after installing or upgrading Ruby or Git.

```powershell
cd V:\src\web
bundle install
bundle exec jekyll serve --host 127.0.0.1 --port 4000
```

Open http://localhost:4000. Stop the preview with Ctrl+C.
For a production build:

```powershell
$env:JEKYLL_ENV = 'production'
bundle exec jekyll build --trace
```

## Add content

Create posts in `_posts/YYYY-MM-DD-title.md`:

```markdown
---
title: "My article"
categories: [Blog]
---

Write the article here.
```

Create standalone pages in `_pages/name.md` with `title` and
`permalink: /name/` between the `---` markers. Add menu links under `main`
in `_data/navigation.yml`. Images and videos belong in `assets/images`.
The `_samples` folder contains retained historical examples, not published pages.

## Dependencies

Gemfile.lock is versioned to keep builds reproducible. The theme is pinned in
Gemfile. MathJax is pinned in `_includes/head/custom.html`.
Use `bundle update --all`, then build and check the existing articles before publishing.
Do not edit `_site`: it is generated output. `bundle exec jekyll clean` removes
Jekyll's generated output and caches.

## Publishing

The workflow in `.github/workflows/pages.yml` builds pull requests and deploys
pushes to master. Before the first deployment, set the GitHub repository's
Settings > Pages > Source to GitHub Actions. The older branch-based Jekyll
builder does not use this modern dependency setup.
Commit and push the source, including Gemfile.lock, to publish. Local preview
and build commands do not publish. Repository settings must be checked before
pushing this migration.

Universal Analytics and the retired Google 404 helper were removed.
The existing GA4 property (297793263), web stream 3120490094, uses measurement ID G-CDHQJ8XG0Y. The theme emits its tag only in production builds; normal local previews do not send analytics.

## How the theme and your files fit together

This is a Jekyll static site using the Minimal Mistakes theme, with its sunrise
color scheme. Most HTML layouts and CSS are inherited from the installed theme
gem. They are not missing from this folder. Do not edit files inside the Ruby
installation: theme updates replace them.

Your changes live here:

| What to change | File or folder |
| --- | --- |
| Homepage welcome and featured links | `index.html` |
| Article text and summary | `_posts/*.md` |
| About and archive introductions | `_pages/*.md` |
| Menu links | `_data/navigation.yml` |
| Site title, theme skin, and default post layout | `_config.yml` |
| Small local style additions | `assets/css/custom.css` |
| Load local CSS and MathJax | `_includes/head/custom.html` |

The CSS file is loaded using the theme's custom-head extension point. The theme's
main stylesheet and layouts remain inherited. Posts use the theme's `wide` class:
this moves the table of contents above the article and frees the right column for
content. At desktop widths of 1024px and above, the layout is intended to show at
least 80 monospace characters at the configured 16px code size. Smaller screens
and longer lines scroll inside the code block instead of widening the page.
Browser zoom effectively reduces the available viewport width.

### Preview without remembering the Ruby setup

From PowerShell in `V:\src\web`, run:

```powershell
.\scripts\site.ps1
```

Visit http://127.0.0.1:4000. Save an article to see Jekyll rebuild it, then refresh
the browser. Stop with Ctrl+C. Restart after changing `_config.yml`.
The script finds Ruby either on PATH or in the existing per-user Ruby34 install.
It only changes environment variables for the duration of the command.

To check a production build without publishing:

```powershell
.\scripts\site.ps1 Build
```

The current theme produces Sass deprecation warnings; these are upstream theme
warnings, not failed builds. Look for the final success or error result.

### Article summaries and videos

Add a short `excerpt` in the YAML header at the top of each post. It is used in
article listings and search metadata. Keep the category spelled `Blog` consistently;
both older spellings generated `/blog/` URLs, which this cleanup preserves.

```yaml
excerpt: "Explain the problem and what the reader will learn in one or two sentences."
categories:
  - Blog
```

Use the following markup for a silent looping demonstration. It waits for the
reader to press Play and provides native playback controls:

```html
<video controls muted playsinline loop preload="none">
  <source src="/assets/images/example.webm" type="video/webm">
</video>
```

Use fenced Markdown code blocks (three backticks on the opening and closing lines)
for commands and code. Preserve indentation; do not add manual line breaks solely
to fit the old narrow layout. The local CSS handles overflow.

Previewing and building do not publish. Publishing still requires committing and
pushing to `master`, which runs the GitHub Pages workflow described above.

### Homepage and contents refinements

The homepage uses `author_profile: false` and the local `museum-home` class,
so its intro is not preceded by a second museum biography. The banner is a copy
of the existing channel-art export; its CorelDRAW source remains outside this repo
at `V:\youtube\assets\Wizardry 7\Vi Domina.cdr`. The original export is at
`V:\youtube\channel-art-vidomina.png`. Local CSS controls its framing.

`assets/js/site.js`, loaded through `_includes/footer/custom.html`, wraps the
theme-generated table of contents in a keyboard-accessible disclosure. Without
JavaScript the original full table of contents remains available. No theme layouts
are copied or modified.

The SunBlade article is now an impersonal historical guide. It deliberately omits
mailing-list links and personal project history. Its distinctive technical details
and patch can still be correlated with public archives; this is not anonymization.

### Audit maintenance (October 2026)

- Navigation now uses Articles, Topics, and About; old category and tag URLs remain.
- `assets/css/main.scss` sets a few accessible color variables, then imports the
  sunrise skin and the entire upstream theme. This is a supported Sass customization,
  not a replacement theme. `custom.css` contains only local layout/focus adjustments.
- Posts use the local `media-figure.html` include with `_data/media.json` for responsive
  WebP variants, intrinsic dimensions, lazy loading, and links to the original image.
  The theme's own figure include is untouched. Original artwork and screenshots remain.
- `scripts/optimize-media.py` regenerates the variants using the existing FFmpeg and
  Python/Pillow installation. It is a local maintenance tool, not a build dependency.
- Only posts with `math: true` load MathJax. Silent videos use native controls and
  `preload="none"`; they start downloading when the reader presses Play.
- Build, then run `python scripts/check-site.py _site` to check internal targets,
  image variants, duplicate anchors, alt attributes and video controls. GitHub Actions
  runs this check before uploading the Pages artifact.
- `scripts/check-ffmpeg.py` tests the tutorial's standalone FFmpeg commands against
  short synthetic inputs. Local tools/outputs are explicitly configured in that script.
- The preview helper also accepts a port: `.\scripts\site.ps1 -Port 4001`.
  Stop/restart the server after editing `_config.yml`; Jekyll does not reload it.
- The theme still fetches Font Awesome from its upstream `@latest` CDN URL. Ruby
  dependency-audit results do not cover that remote stylesheet or its future changes.

The 2026 review is not a claim that historical Windows, OpenBSD, Resolve, or browser
behavior has been reproduced on every current platform. Tested versions and limits
are noted in the articles. Local browser timings are not production Core Web Vitals.
