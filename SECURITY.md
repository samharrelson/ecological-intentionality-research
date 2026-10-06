# Security Policy

This repository contains Markdown research materials together with scripts used to export, validate, and publish the public research layer.

## Reporting a security or privacy issue

Please do **not** open a public issue if you discover:

- private-path leakage;
- private vault material;
- credentials, tokens, or secrets;
- personal information that should not have been published;
- a vulnerability in the export or publication scripts that could expose non-public material.

Instead, contact:

**Sam Harrelson**  
sam@samharrelson.com

Include only the information necessary to identify and reproduce the problem.

## Privacy boundary

The repository is designed around an explicit public allowlist. The private Obsidian vault must not be crawled or mirrored wholesale.

The local privacy guard and GitHub Actions validation are intended to catch path and publication-boundary problems, but responsible disclosure is still welcome if something slips through.

## Supported version

Security and privacy fixes apply to the current `main` branch and the latest public repository release.
