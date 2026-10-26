# Documentation Library content backup

Content from https://docs.bradbarrish.com/.

## Documentation Pages

The GitHub Actions workflow **Back up documentation Pages** runs daily and can also be started manually from Actions. It discovers documents from the homepage, saves the full rendered HTML plus standalone content HTML and plain text under `pages/`, and commits changes. It uses only public pages and requires no Micro.blog credentials. Git history preserves earlier versions. A failed fetch stops the job before snapshots are changed. Removed documents are retained in the archive.

Edit documents in **Micro.blog → Pages**, with the documentation blog selected. Do not edit backup files as a publishing method.

## Micro.blog archive

Micro.blog's built-in GitHub archive remains enabled for this repository. Its files are separate from `pages/`. The additional workflow ensures the date-free documentation Pages are backed up even if the built-in archive covers only blog posts.
