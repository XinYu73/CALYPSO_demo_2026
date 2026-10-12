# CALYPSO Demo 2026

This repository contains the 2026 CALYPSO demonstration inputs used for local and cluster-side example runs.  The examples cover bulk, layer, cluster, molecular, and substitution workflows.

## Layout

```text
demo_2026/
  machine-1.json                 shared machine configuration
  sbatch.sh                      shared SLURM submission template
  <example>/
    run/input.toml               runnable input
    reference/input.toml         reference input for comparison
```

The current examples include:

- `bulk_molecular_FeOOH`
- `bulk_molecular_H2O_VIII`
- `bulk_substitute_LaFeO3`
- `cluster_cage_C60`
- `cluster_normal_CH4`
- `cluster_plane_N5`
- `layer_double_layer_BaBr3_Graphene`
- `layer_double_layer_CrI3`
- `layer_single_layer_Graphene`
- `layer_single_layer_In2Se3`
- `layer_single_layer_molecular_H2O`

## Environment

Use the CALYPSO development environment declared by `AGENTS.md`:

```bash
conda activate calypso_dev
```

Make sure `calypso.x` is available from this environment before running an example.

## Running An Example

From this repository root:

```bash
cd demo_2026/<example>/run
calypso.x -c input.toml
```

Most `input.toml` files reference the shared machine file as:

```toml
MachineList = ["../../machine-1.json"]
```

Edit `demo_2026/machine-1.json` and `demo_2026/sbatch.sh` for the target machine or cluster before submitting production jobs.  These two files are intentionally shared by all examples because they depend on the local execution environment.

## Local Run Notes

- Some examples use CHGNet/MLP relaxation, so the active Python environment must include the corresponding dependencies.
- `machine_capacity` in `demo_2026/machine-1.json` controls the maximum number of local jobs the machine entry will accept.
- `run/input.toml` and `reference/input.toml` should stay comparable; update both when changing shared demo parameters intentionally.
- The LaFeO3 substitution demo keeps `MP_EXP_Database/experimental.tar.gz` in Git and ignores the expanded `experimental/` directory.  Extract the archive locally when that example needs the database files.

## Git Tracking Policy

This repository tracks demo inputs, shared machine templates, and reference data needed to reproduce the examples.  Generated local run products are ignored, including:

- `BackStage/`
- `CALYPSO.logdir/`
- `results/`, `results1/`, `results2/`, ...
- `demo_2026/.local_run_state/`
- scheduler output files such as `job.*.out` and `job.*.err`

This directory is nested under `env_demonstration_donot_delete/`, which is ignored by the parent CALYPSO source repository through its `env_*/` ignore rule.  Keeping this as an independent Git repository does not affect the CALYPSO source repository unless it is explicitly added there as a tracked submodule or ordinary tracked path.
