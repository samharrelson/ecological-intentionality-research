# Public source map

This file documents the only Obsidian sources that the automated exporter is allowed to copy into the versioned public research record.

## Included

| Vault source | Repository destination |
| --- | --- |
| `Public/Tracking/Sits/*.md` | `field-notes/` |
| `Public/Tracking/Concepts/*.md` | `concepts/` |
| `Public/Tracking/Essays/Overview.md` (current) or `Essays.md` (legacy name) | `essays/README.md` |
| `Public/Tracking/Essays/Consciousness in a World We Cannot Possess.md` | `essays/consciousness-in-a-world-we-cannot-possess.md` |
| `Public/Tracking/Essays/Whose Good - Ecological Intentionality and the Formation of Practical Purpose.md` | `essays/whose-good.md` |
| `Public/Tracking/Essays/Whose Good.md` or `Whose Good?.md` (after sidebar rename) | `essays/whose-good.md` |
| `Public/Tracking/Essays/What Flesh Explains.md` | `essays/what-flesh-explains.md` |
| `Public/Tracking/Essays/How a Purpose Takes Shape.md` | `essays/how-a-purpose-takes-shape.md` |
| `Public/Tracking/Essays/A Life of Its Own.md` | `essays/a-life-of-its-own.md` |
| `Public/Tracking/Essays/Seeing a Life Develop.md` | `essays/seeing-a-life-develop.md` |
| `Public/Tracking/Essays/Learning, Flesh, and Continuing Lives.md` | `essays/learning-flesh-and-continuing-lives.md` |
| `Public/Tracking/Essays/What Fuller Understanding Requires.md` | `essays/what-fuller-understanding-requires.md` |
| `Public/Tracking/Essays/A Commitment with a Future.md` | `essays/a-commitment-with-a-future.md` |
| `Public/Tracking/Essays/Who Has a Say in the Record.md` | `essays/who-has-a-say-in-the-record.md` |
| `Public/Tracking/Where the Inquiry Stands.md` | `project/where-the-inquiry-stands.md` |
| `Public/Tracking/How the Inquiry Developed.md` | `project/how-the-inquiry-developed.md` |
| `Public/Tracking/Sources & Reading.md` | `project/sources-and-reading.md` |
| `Public/Tracking/About the Practice.md` | `method/about-the-practice.md` |
| `Public/Tracking/Sit Template.md` | `method/sit-template.md` |

The Essays entries are an **individual-file allowlist**, not a wildcard on `Public/Tracking/Essays`. Each new essay requires explicit approval for public release and its own entry in this map and the exporter. An entry prepares export eligibility; it does not establish that website publication has happened. Publish the reviewed public source and verify its served website version before running the export.

The two entries for *What Flesh Explains* and *How a Purpose Takes Shape* were prepared on November 17, 2026, for the approved next publication. This configuration change does not copy either essay into the repository. Their website publication and verification must precede the first export; private working drafts are not eligible sources.

The individual mapping for *A Life of Its Own* was prepared on November 19, 2026, for its approved working-essay publication. It permits export only after the reviewed website version is published and verified. The private manuscript is not an export source.

The individual mapping for *Learning, Flesh, and Continuing Lives* was prepared on November 23, 2026, for the reviewed continuity comparison. It establishes export eligibility for that one public source. Verify the served website version before its first export; the private comparison and source record remain outside this mapping.

The individual mapping for *What Fuller Understanding Requires* was prepared on November 24, 2026, for the reviewed Stein and Husserl comparison. It establishes export eligibility for that one public source. Verify the served website version before its first export; the private comparison and source record remain outside this mapping.

The individual mapping for *A Commitment with a Future* was prepared on November 25, 2026, for the reviewed Mariandale case assessment. It establishes eligibility for that public essay source. Publish and verify its served website version before the first export; the private assessment, source dossier and transcript remain outside this mapping.

The current essay index is `Overview.md`, with the stable website permalink `/essays`; the older `Essays.md` source name remains supported. Only one may exist at a time. The long and short approved names for *Whose Good?* are also alternatives, not separate files to export together; duplicate sources are rejected. Its stable website permalink is `/essays/whose-good` regardless of the local filename.

Only allowlisted public notes can become navigable GitHub links. Wikilinks whose targets are not part of this public source map are rendered as plain text rather than exposing private vault structure.

The inquiry overview and research history are separate, explicit source entries. Links between them and heading-level navigation become GitHub Markdown links. The overview's spoken introduction stays on the public website: its media attachment is **not copied** to GitHub, but the exported note links to the hosted recording and includes its public transcript.

## Website preview metadata

Website preview properties, including `cover` and `image`, are removed from exported frontmatter. Their values may name attachments outside the public source tree. The selected website image remains on the published site; GitHub receives the public note's descriptive metadata and a link to its illustrated page. The privacy guard continues to reject private attachment paths.

## RSS sit index

The RSS builder reads its explicit dated sit allowlist from `Public/Tracking/Field Notes.md`, under `## All sits`. Month subheadings can organize this complete archive. If that file is absent, the builder supports the older `## Recent sits` section in `Public/Tracking/Home.md`. An existing empty or invalid archive fails without falling back to Home. The builder also refuses to remove any existing feed item, protecting the feed history during a partial migration.

Publish and verify the reviewed website index before generating the feed. Descriptions and full-text content still come only from already-exported public field notes. The archive index itself has no general export mapping.

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

`About Sam Harrelson.md`, `Contact.md`, `Home.md`, and `Field Notes.md` are also not exported automatically because they belong to the website layer rather than the versioned research record.

The allowlist is intentional. Add a source only after deciding that it belongs in the versioned public research record.