# Ecological Intentionality — Public Research Layer

This repository is a public research layer for an ongoing inquiry in ecology, phenomenology, religion, and creaturely relation.

The work is grounded in repeated field encounters, currently centered on a black walnut tree in Spartanburg, South Carolina. The field practice is not treated as an illustration added after the philosophy is finished. It is one of the places where philosophical claims are tested, corrected, narrowed, and sometimes abandoned.

The primary public field-notes site is:

**https://ecologicalintentionality.org**

This repository serves a different purpose. It makes selected research materials easier to inspect as a versioned scholarly record: public field notes, concept pages, methodological documents, reading orientation, and the changing shape of the inquiry.

## What belongs here

- curated public Black Walnut field notes
- public concept pages
- `Where the Inquiry Stands`
- public sources / reading orientation
- the field-practice description
- the public sit template and method notes
- future public datasets, diagrams, or reproducible research materials when useful

## What does not belong here

This repository is **not** a mirror of the Obsidian vault.

It intentionally excludes private field journals, Daily Notes, unpublished CIIS / Comps material, family notes, Zotero PDFs and storage, meeting notes, private correspondence, and other working material.

The public workflow is:

**sit → private field note → philosophical analysis → research integration → curated public field note → public research layer**

## Current research pressure

Ecological intentionality began as a name for a disciplined form of creaturely attention: attending to another being as relationally given, irreducibly other, and never exhausted by its appearance within human experience.

The live question is whether ecological intentionality names a genuinely distinct phenomenological structure or instead a disciplined coordination of already available structures and methods: perception, embodiment, temporality, empathy, organismic normativity, ecological relation, historical evidence, ethical judgment, and theological interpretation.

Current work is especially concerned with:

- the difference between perceptual unity, organismic unity, ecological belonging, and ethical harmony
- Husserlian embodiment and tactile doubling
- Edith Stein on empathy, non-primordiality, living form, and proper good
- Merleau-Ponty on flesh, reversibility, noncoincidence, and *écart*
- Melanie Harris on ecowomanism, history, justice, and praxis
- Robin Wall Kimmerer and Vanessa Watts as constraints on generic relationality
- the methodological rule that stronger claims require additional evidence

A working formulation emerging from the field notes is:

> **Difference need not mean separation; belonging need not mean coincidence.**

## Repository structure

```text
field-notes/   Curated public sits
concepts/      Public concept and thinker pages
project/       Orientation pages such as "Where the Inquiry Stands"
method/        Public descriptions of the field practice and templates
scripts/       Local export, link conversion, privacy checks, and publishing helpers
automation/    Optional macOS scheduling instructions
```

## Automation philosophy

Automation here is deliberately conservative.

The sync script accepts only material under `Public/Tracking` in the Obsidian vault and copies only an explicit allowlist of public subfolders/files. It will not crawl the whole vault. A privacy guard scans the exported repository for private-path markers before publication.

The default command is a dry run:

```bash
python3 scripts/sync_public_research.py --vault "/path/to/your/Obsidian/vault" --repo .
```

To write changes:

```bash
python3 scripts/sync_public_research.py --vault "/path/to/your/Obsidian/vault" --repo . --apply
python3 scripts/privacy_guard.py .
```

To sync, validate, commit, and push in one step:

```bash
./scripts/publish.sh "/path/to/your/Obsidian/vault"
```

Do not schedule unattended publishing until the manual workflow has been used enough to earn trust.

## Public scholarship and provenance

The website remains the primary reading experience. This repository is the versioned research record.

The goal is not to pretend that unfinished work is finished. It is to make revision, correction, and methodological development visible while preserving the distinction between public research and the private working environment.

## Author

Sam Harrelson  
PhD candidate, Ecology, Spirituality, and Religion  
California Institute of Integral Studies

Public writing: https://samharrelson.com  
Field notes: https://ecologicalintentionality.org
