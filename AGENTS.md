# AGENTS.md

Guidance for future Codex sessions working in this repository.

## Scope

This repository is the independent demo repository:

```text
/Users/yuxin/temp/CALYPSO-Python/env_demonstration_donot_delete/CALYPSO_demo_2026
```

The parent CALYPSO source repository is:

```text
/Users/yuxin/temp/CALYPSO-Python
```

Do not modify files outside this demo repository unless the user explicitly asks. The parent repository ignores `env_*/`, so this nested Git repository should not affect the parent CALYPSO Git status unless it is explicitly added there as a submodule or tracked path.

## Codex Permissions And Working Directory

Codex may start from a different workspace directory, for example:

```text
/Users/yuxin/temp/calypso
```

When commands need to read or write this demo repository under `/Users/yuxin/temp/CALYPSO-Python`, they may require escalated filesystem permission in Codex. Use escalation for those commands instead of working around the sandbox.

Network operations such as `git push`, dependency installation, or downloading model/data files may also require explicit approval.

## Environment

Use the conda environment:

```bash
conda activate calypso_dev
```

When running commands non-interactively from Codex, prefer the explicit Python path if activation is unreliable:

```bash
/Users/yuxin/anaconda3/envs/calypso_dev/bin/python
```

Before running examples, verify:

```bash
which calypso.x
calypso.x --help
```

## Repository Goal

Maintain `demo_2026` as a reproducible CALYPSO demo suite.

Primary goals:

- Keep runnable demo inputs in each `run/input.toml`.
- Keep comparable reference inputs in each `reference/input.toml`.
- Track `reference/` outputs so users can compare their local results against known outputs.
- Keep local rerun products in `run/` ignored by Git.
- Keep shared machine/cluster files at `demo_2026/machine-1.json` and `demo_2026/sbatch.sh`.

## Git Policy

This repository has its own remote:

```bash
git remote -v
# origin git@github.com:XinYu73/CALYPSO_demo_2026.git
```

Use normal Git commands from this directory:

```bash
git status --short --branch
git add .
git commit -m "<message>"
git push
```

Before committing, check that generated `run/` outputs are still ignored:

```bash
git status --short --ignored
```

The `.gitignore` intentionally tracks reference outputs but ignores local run outputs, `.DS_Store`, `.local_run_state/`, and the expanded LaFeO3 experimental database directory.

## Updating CALYPSO Source Code

This demo repository is not the CALYPSO source tree. If the user asks to update or rebuild CALYPSO itself, work in:

```text
/Users/yuxin/temp/CALYPSO-Python
```

The source repository may need:

```bash
git -c fetch.recurseSubmodules=false pull origin main
git submodule sync --recursive
git submodule update --init --recursive
```

Then rebuild or reinstall the `calypso_dev` environment as requested by the user.

## Running Demos Locally

Use local runs unless the user explicitly asks to submit to a cluster.

Typical command:

```bash
cd demo_2026/<example>/run
calypso.x -c input.toml
```

Many examples use CHGNet or another MLP backend. Avoid launching too many structure optimizations at once; use at most 4 concurrent CHGNet optimizations unless the user says otherwise.

For local testing, keep temporary cache/state inside this demo repository when possible, for example under:

```text
demo_2026/.local_run_state/
```

Do not write caches or generated files into the CALYPSO source tree unless explicitly requested.

## Input File Conventions

Shared machine configuration should be referenced from example inputs as:

```toml
MachineList = ["../../machine-1.json"]
```

If changing shared execution settings, update `demo_2026/machine-1.json` and/or `demo_2026/sbatch.sh` instead of copying machine files into each example directory.

When comparing `run/input.toml` and `reference/input.toml`, ignore intentional path differences only when they are documented. Otherwise, keep them consistent.

## Reference Outputs

Reference outputs are tracked intentionally:

```text
demo_2026/<example>/reference/results/
demo_2026/<example>/reference/BackStage/
demo_2026/<example>/reference/CALYPSO.logdir/
demo_2026/<example>/reference/job.*.out
demo_2026/<example>/reference/job.*.err
```

Local reruns in `run/` should remain untracked:

```text
demo_2026/<example>/run/results*/
demo_2026/<example>/run/BackStage/
demo_2026/<example>/run/CALYPSO.logdir/
```

The LaFeO3 substitution demo tracks:

```text
demo_2026/bulk_substitute_LaFeO3/MP_EXP_Database/experimental.tar.gz
```

The expanded directory is ignored because it contains many small files:

```text
demo_2026/bulk_substitute_LaFeO3/MP_EXP_Database/experimental/
```

Extract it locally only when needed for that example.
