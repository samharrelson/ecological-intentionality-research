# Public source map

This file documents the only Obsidian sources that the automated exporter is allowed to copy into the versioned public research record.

## Included

| Vault source | Repository destination |
| --- | --- |
| `Public/Tracking/Sits/*.md` | `field-notes/` |
| `Public/Tracking/Concepts/*.md` | `concepts/` |
| `Public/Tracking/Where the Inquiry Stands.md` | `project/where-the-inquiry-stands.md` |
| `Public/Tracking/How the Inquiry Developed.md` | `project/how-the-inquiry-developed.md` |
| `Public/Tracking/Sources & Reading.md` | `project/sources-and-reading.md` |
| `Public/Tracking/About the Practice.md` | `method/about-the-practice.md` |
| `Public/Tracking/Sit Template.md` | `method/sit-template.md` |

Only allowlisted public notes can become navigable GitHub links. Wikilinks whose targets are not part of this public source map are rendered as plain text rather than exposing private vault structure.

The inquiry overview and research history are separate, explicit source entries. Links between them and heading-level navigation become GitHub Markdown links. The overview's spoken introduction stays on the public website: its media attachment is **not copied** to GitHub, but the exported note links to the hosted recording and includes its public transcript.

## Explicitly excluded

The exporter refuses to copy from paths containing any of these markers:

- `Daily Notes`
- `Field Journal`
- `CIIS`
- `Zotero`
- `People`
- `Media`
- `Private`
- `.obsidian`

`About Sam Harrelson.md`, `Contact.md`, and `Home.md` are also not exported automatically because they belong to the website layer rather than the versioned research record.

The allowlist is intentional. Add a source only after deciding that it belongs in the versioned public research record.