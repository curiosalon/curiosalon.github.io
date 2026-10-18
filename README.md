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
