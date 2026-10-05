# First setup

1. Create a new GitHub repository named `ecological-intentionality-research`.
2. Put the contents of this bundle in the repository root and commit them.
3. Run a dry export:

   ```bash
   python3 scripts/sync_public_research.py --vault "/ABSOLUTE/PATH/TO/YOUR/OBSIDIAN/VAULT" --repo .
   ```

4. Review every path printed by the dry run.
5. Apply the export:

   ```bash
   python3 scripts/sync_public_research.py --vault "/ABSOLUTE/PATH/TO/YOUR/OBSIDIAN/VAULT" --repo . --apply
   ```

6. Run:

   ```bash
   python3 scripts/privacy_guard.py .
   ```

7. Inspect everything in GitHub Desktop before the first push.
8. Commit and push manually.
9. After several trustworthy runs, use `./scripts/publish.sh "/ABSOLUTE/PATH/TO/YOUR/OBSIDIAN/VAULT"`.
10. Only then consider optional `launchd` scheduling.

Recommended topics:

`ecological-intentionality`, `phenomenology`, `ecophenomenology`, `environmental-humanities`, `digital-humanities`, `field-notes`, `open-research`, `obsidian`
