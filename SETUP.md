# Publication workflow

This repository is downstream from the intentional public boundary in the Obsidian research vault.

It does not decide what becomes public. It creates a versioned scholarly record of material that has already been deliberately curated for public use.

## Source boundary

Only the explicit allowlist under `Public/Tracking` is eligible for export.

See [`PUBLIC-SOURCE-MAP.md`](PUBLIC-SOURCE-MAP.md) for the current source-to-repository map.

The exporter does not crawl the whole vault.

Known public Obsidian wikilinks are converted into relative GitHub Markdown links. Wikilinks whose targets are unresolved or outside the public allowlist are rendered as plain text rather than exposing private vault structure.

## Manual dry run

From the repository root, define the local vault path:

```bash
VAULT="/absolute/path/to/your/Obsidian/vault"