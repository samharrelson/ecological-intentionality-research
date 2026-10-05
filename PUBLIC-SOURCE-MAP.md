# Public source map

This file documents the only Obsidian sources that the automated exporter is allowed to copy.

## Included

| Vault source | Repository destination |
| --- | --- |
| `Public/Tracking/Sits/*.md` | `field-notes/` |
| `Public/Tracking/Concepts/*.md` | `concepts/` |
| `Public/Tracking/Where the Inquiry Stands.md` | `project/where-the-inquiry-stands.md` |
| `Public/Tracking/Sources & Reading.md` | `project/sources-and-reading.md` |
| `Public/Tracking/About the Practice.md` | `method/about-the-practice.md` |
| `Public/Tracking/Sit Template.md` | `method/sit-template.md` |

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

`About Sam Harrelson.md`, `Contact.md`, and `Home.md` are also not exported automatically because they belong to the website layer rather than the research record.

The allowlist is intentional. Add a source only after deciding that it belongs in the permanent public research layer.
