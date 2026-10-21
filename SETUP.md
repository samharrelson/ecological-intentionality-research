# Publication workflow

The public website is [ecologicalintentionality.org](https://ecologicalintentionality.org). This repository stores a guarded, versioned export of notes **already deliberately published** through Obsidian.

## Source and privacy boundary

Only explicitly mapped public pages and the curated `Public/Tracking/Sits` and `Concepts` folders may enter the GitHub export. See [PUBLIC-SOURCE-MAP.md](PUBLIC-SOURCE-MAP.md). Private working notes, audio attachments, and unresolved vault links are not mirrored. The privacy guard runs before every local push and again in GitHub Actions.

## Normal publication

1. Review and publish selected notes on the Obsidian website first.
2. Update the public Home page's **Recent sits** section with a link to any new sit.
3. On the Mac, run this from the repository directory:

```bash
./scripts/publish.sh "/Users/samharrelson/Vaults/Obsidian"
```

The script pulls remote changes with a fast-forward-only guard, exports the approved Markdown, generates the sits-only RSS file, runs the privacy guard, stages the public export and `docs` folder, commits, and pushes. If Terminal refuses the push with a 403 but GitHub Desktop is authenticated, push the one waiting commit from Desktop; do **not** repeat the export unnecessarily.

For a dry run from the repository root:

```bash
python3 scripts/sync_public_research.py --vault "/Users/samharrelson/Vaults/Obsidian"
python3 scripts/build_sits_feed.py --vault "/Users/samharrelson/Vaults/Obsidian"
```

## RSS: Black Walnut Field Notes only

The feed is generated at `docs/sits.xml`. It contains only the dated sit links intentionally listed under **Recent sits** in the public `Public/Tracking/Home.md`, cross-checked against exported public `field-notes/` metadata. Merely creating a file in the Sits folder doesn't add it to RSS, and editing Sources, thinker pages, site layout, or other research notes does not create a feed item.

Every entry has a permanent `https://ecologicalintentionality.org/sits/YYYY-MM-DD` GUID and link, the public sit title and short description, and a stable timestamp corresponding to the *sit date*. That timestamp is **not** claimed to be the exact website publishing hour. Revisions of an older sit can update its description, but not its identity or feed date. When multiple exported Markdown filenames refer to the same day (as on October 16, 2026), the RSS generator emits only one entry. It never exports the full private recording, photographs, or the full sit body into XML.

### Enable RSS hosting once

This is a small independent GitHub Pages site, not a replacement for Obsidian Publish.

1. Run the normal publication script once and push the commit, creating `docs/sits.xml`.
2. In this GitHub repository, open **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**, then **main** and **/docs**, and save.
4. After the Pages deployment succeeds, subscribe in Inoreader or NetNewsWire to:

   **https://samharrelson.github.io/ecological-intentionality-research/sits.xml**

5. The RSS link in the Obsidian public Home page can now be published. The RSS hosting does not affect Obsidian Publish's separate built-in all-site `/rss.xml` feed.

Future public-sit publication requires no new RSS-specific command: the existing guarded publication workflow updates the XML automatically. Because its contents are deterministic, routine site edits alone leave the XML unchanged.

To change the public RSS URL in the future, update the `FEED` constant in `scripts/build_sits_feed.py` only after a stable destination has been configured and tested.
