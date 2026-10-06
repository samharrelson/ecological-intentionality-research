# Changelog

## 0.2.1 — First citable research snapshot

- Added DOI and ORCID-linked citation metadata.
- Preserved the current public research layer as the first archived Zenodo snapshot.
- Added citation support for the evolving field notes, concept pages, method documents, and research infrastructure.

## 0.2.0 — Linked public research graph and deliberate publication trigger

- Convert known public Obsidian wikilinks into relative GitHub Markdown links.
- Flatten unresolved or non-public wikilinks to plain text rather than exposing private targets.
- Make verified `/walnut-publish` completion the preferred trigger for GitHub synchronization.
- Keep the privacy guard before commit / push and GitHub Actions validation after push.
- Move detailed automation plumbing off the repository front page and into `SETUP.md`.

## 0.1.0 — Initial repository architecture

- Established a public research-layer structure distinct from the private Obsidian vault.
- Added conservative one-way export from `Public/Tracking`.
- Added privacy validation locally and in GitHub Actions.
- Added one-command sync / commit / push helper.
