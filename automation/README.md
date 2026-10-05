# Optional macOS automation

Start with the manual command:

```bash
./scripts/publish.sh "/path/to/your/Obsidian/vault"
```

Only schedule this after the one-command workflow has behaved correctly for several runs.

## Why local scheduling?

GitHub Actions cannot safely reach a private local Obsidian vault. The export boundary therefore remains on the Mac, where the script can copy only the already-curated `Public/Tracking` material.

## Recommended schedule

If you eventually automate this, run it once daily in the evening or immediately after the existing walnut-publication workflow.

A `launchd` template is included. Replace `__REPO_PATH__` and `__VAULT_PATH__`, then install it under `~/Library/LaunchAgents/`.

The scheduled job will commit and push only when the allowlisted public export has changed and the privacy guard passes.
