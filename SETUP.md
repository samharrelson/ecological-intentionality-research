# First setup and publication workflow

The repository is designed to be downstream from the intentional public boundary in the Obsidian vault.

## Source boundary

Only the explicit allowlist under `Public/Tracking` is eligible for export. See [`PUBLIC-SOURCE-MAP.md`](PUBLIC-SOURCE-MAP.md).

The exporter does not crawl the whole vault.

## Dry run

From the repository root:

```bash
python3 scripts/sync_public_research.py \
  --vault "/Users/samharrelson/Vaults/Obsidian" \
  --repo .
```

Review the proposed changes before writing them.

## Apply and validate

```bash
python3 scripts/sync_public_research.py \
  --vault "/Users/samharrelson/Vaults/Obsidian" \
  --repo . \
  --apply

python3 scripts/privacy_guard.py .
```

The exporter converts a wikilink into a relative GitHub Markdown link only when the target is itself part of the exportable public allowlist. Unresolved or non-public wikilinks are flattened to readable plain text rather than exposing a private vault target.

## One-command publication

Once the public layer has already been deliberately curated and the corresponding website publication has been verified:

```bash
./scripts/publish.sh "/Users/samharrelson/Vaults/Obsidian"
```

The script:

1. exports the allowlisted public research layer;
2. runs the privacy guard;
3. commits only when the public repository changed;
4. pushes the commit to GitHub.

If nothing changed, it exits without manufacturing a commit.

## Integration with the Black Walnut workflow

The preferred trigger is **not** a blind clock schedule.

The canonical order is:

**sit → private field note → philosophical analysis → research integration → curated public field note → verified website publish → guarded GitHub research sync**

The `/walnut-publish` workflow should invoke the one-command publication step only after the newest public sit has been verified in Obsidian Publish.

GitHub therefore records the public boundary; it never decides that boundary.

## GitHub validation

GitHub Actions runs the repository privacy guard again after each push. A green `Validate public research` workflow is the expected post-push state.

## Recommended topics

`ecological-intentionality`, `phenomenology`, `ecophenomenology`, `environmental-humanities`, `digital-humanities`, `field-notes`, `open-research`, `obsidian`
