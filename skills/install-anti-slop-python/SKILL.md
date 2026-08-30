---
name: install-anti-slop-python
description: Install and configure anti-slop-python in a Python repository. Use when a user asks to add anti-slop Python checks, configure the anti-slop-python pre-commit hook, or update an existing anti-slop-python setup.
---

# Install anti-slop-python

Integrate the remote pre-commit hook from this repository with the target
repository's existing checks. Preserve unrelated work and the project's
package-manager, lint, and pre-commit conventions.

## Procedure

1. Inspect the target repository before changing it:
   - Read its agent instructions.
   - Check `git status` and preserve unrelated changes.
   - Identify its supported Python versions, package manager, lockfiles, lint
     commands, CI checks, and `.pre-commit-config.yaml` if present.
   - Search for an existing `anti-slop-python` dependency, command, or hook. Update
     an existing integration instead of adding a duplicate.

2. Confirm compatibility. This project requires Python 3.11 or later. If the
   target environment cannot provide a compatible interpreter, report the
   incompatibility instead of changing the project's supported Python version.

3. Resolve an immutable revision of this repository:

   ```console
   git ls-remote --tags --refs https://github.com/ruarfff/anti-slop-python.git 'v*'
   ```

   Use the newest compatible stable release tag. If no release tag exists,
   resolve `refs/heads/main` and use its full commit SHA. Do not use a moving
   branch name as a pre-commit revision.

4. Merge this hook into `.pre-commit-config.yaml`:

   ```yaml
   repos:
     - repo: https://github.com/ruarfff/anti-slop-python
       rev: <release-tag-or-full-commit-sha>
       hooks:
         - id: anti-slop-python
   ```

   Preserve every existing repository and hook setting. If this hook already
   has `files`, `exclude`, `args`, or `stages`, retain them unless the user asks
   to change its scope. Add scope filters only when requested or required by an
   existing repository convention.

5. Use the target repository's existing pre-commit installation and commands.
   If pre-commit is absent and local enforcement is part of the request, add it
   as a development tool with the existing package manager and update the
   normal lockfile. Install the Git hook when the repository's workflow uses
   local pre-commit hooks.

6. Validate the integration:

   ```console
   pre-commit run anti-slop-python --all-files
   ```

   Use the repository's package-manager wrapper when required. Then run its
   normal lint or check command that covers pre-commit configuration.

   Treat diagnostics as migration findings. Fix them only when the user also
   asked for cleanup or full adoption. Do not weaken Ruff settings, add broad
   exclusions, or add suppressions to make the first run pass. Policy notices
   are advisory and do not make the command fail.

7. Review the final diff and report the pinned revision, configuration changed,
   commands run, and any remaining findings.
