# py-orca

<!--
[![ReadTheDocs](https://readthedocs.org/projects/orca/badge/?version=latest)](https://sage-bionetworks-workflows.github.io/orca/)
-->
[![PyPI-Server](https://img.shields.io/pypi/v/py-orca.svg)](https://pypi.org/project/py-orca/)
[![codecov](https://codecov.io/gh/Sage-Bionetworks-Workflows/py-orca/branch/main/graph/badge.svg?token=OCC4MOUG5P)](https://codecov.io/gh/Sage-Bionetworks-Workflows/py-orca)
[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](#pyscaffold)

> ## ⚠️ Deprecation Notice
>
> **`py-orca` is deprecated and is no longer actively maintained.**
>
> The Nextflow Tower service in this package (`orca.services.nextflowtower`) was written
> against the Tower API before Seqera published first-class automation tooling. That
> tooling now exists and is maintained upstream, so we recommend migrating to
> [**`seqerakit`**](https://github.com/seqeralabs/seqera-kit), Seqera's official Python
> wrapper around the [Seqera Platform CLI](https://github.com/seqeralabs/tower-cli).
>
> - No new features will be added to `py-orca`.
> - Existing releases remain installable from PyPI, but expect no compatibility fixes as
>   the Seqera Platform API evolves.
> - See [**Launching Nextflow workflows from Python with `seqerakit`**](#launching-nextflow-workflows-from-python-with-seqerakit)
>   below for the recommended replacement, including a mapping from `py-orca` concepts.
>
> The Synapse (`orca.services.synapse`) and SevenBridges (`orca.services.sevenbridges`)
> helpers are similarly frozen; use [`synapseclient`](https://python-docs.synapse.org/)
> and [`sevenbridges-python`](https://sevenbridges-python.readthedocs.io/) directly.

> Python package for connecting services and building data pipelines

This Python package provides the components to connect various third-party services such as Synapse, Nextflow Tower, and SevenBridges to build data pipelines using a workflow management system like Airflow.

## Demonstration Script

This repository includes a demonstration script called [`demo.py`](demo.py), which showcases how you can use `py-orca` to launch and monitor your workflows on Nextflow Tower. Specifically, it illustrates how to process an RNA-seq dataset using a series of workflow runs, namely `nf-synapse/synstage`, `nf-core/rnaseq`, and `nf-synapse/synindex`. `py-orca` can be used with any Python-compatible workflow management system to orchestrate each step (_e.g._ Airflow, Prefect, Dagster). The demonstration script uses [Metaflow](https://metaflow.org/) because it's easy to run locally and has an intuitive syntax.

The script assumes that the following environment variables are set. Before setting them up, ensure that you have an AWS profile configured for a role that has access to the dev/ops tower workspace you plan to launch your workflows from. You can set these environment variables using whatever method you prefer (_e.g._ using an `.env` file, sourcing a shell script, etc).
Refer to [`.env.example`](.env.example) for the format of their values as well as examples.

- `NEXTFLOWTOWER_CONNECTION_URI`
- `SYNAPSE_CONNECTION_URI`
- `AWS_PROFILE` (or another source of AWS credentials)

Once your environment variables are set, you can create a virtual environment, install the Python dependencies, and run the demonstration script (after downloading it) as follows. Note that you will need to update the `s3_prefix` parameter so that it points to an S3 bucket that is accessible to your Tower workspace.

### Creating and setting up your py-`orca` virtual environment and executing `demo.py`

Below are the instructions for creating and setting up your virtual environment and executing the `demo.py`. You can also check the tutorial [here](https://sagebionetworks.jira.com/wiki/spaces/IBC/pages/3018489902/py-orca+Getting+Started). If you would like to set up a developer environment with the relevant dependencies, you can execute the shell script [dev_setup](https://github.com/Sage-Bionetworks-Workflows/py-orca/blob/main/dev_setup.sh) in a clone of this repository stored on your machine. You can run it either on your local or on the EC2 instance. Establishing a development environment on an EC2 instance could encounter hurdles. You might need to install Python build dependencies before using [pyenv](https://github.com/pyenv/pyenv/wiki#suggested-build-environment) to manage Python versions. You can refer to this [doc](https://github.com/pyenv/pyenv/wiki#suggested-build-environment:~:text=devel%20xz%2Ddevel-,Amazon%20Linux%202%3A,-yum%20install%20gcc) to resolve the dependency issue. The `openssl11-devel` is not available on `EC2: Linux Docker v1.3.9` so you can install `openssl-devel` instead. Moreover, you might run into missing GCC error, you can install GCC usng `sudo yum install gcc`.
```bash
# Create and activate a Python virtual environment (tested with Python 3.10)
python3 -m venv venv/
source venv/bin/activate

# Install Python dependencies
python3 -m pip install 'py-orca[all]' 'metaflow' 'pyyaml' 's3fs'
```

Before running the example below, ensure that the `s3_prefix` points to an S3 bucket your Nextflow `dev`
or `prod` tower workspace has access to. In the example below, we will point to the `example-dev-project-tower-scratch` S3 bucket because we will be launching our workflows within the
`example-dev-project` workspace in `tower-dev`. In this case, you can use either of the `workflows-nextflow-dev` profiles to access the S3 bucket.
```bash
# Run the script using an example dataset
python3 demo.py run --dataset_id 'syn51514585' --s3_prefix 's3://example-dev-project-tower-scratch/work'
```

Once your run takes off, you can follow the output logs in your terminal, or stay updated with your workflow progress on the web client. Be sure that your `synstage` workflow run has a unique name, and is not an iteration of a previous run (i.e. `my_test_dataset_synstage_2`, `my_test_dataset_synstage_3`, and so on). This is because the `demo.py` script does not currently support being able to locate the staged samplesheet file if it has been staged under a run name that is non-unique.

The above dataset ID ([`syn51514585`](https://www.synapse.org/#!Synapse:syn51514585)) refers to the following YAML file, which should be accessible to Sage employees. Similarly, the samplesheet ID below ([`syn51514475`](https://www.synapse.org/#!Synapse:syn51514475)) should also be accessible to Sage employees. However, there is no secure way to make the output folder accessible to Sage employees, so the `synindex` step will fail if you attempt to run this script using the example dataset ID. This should be sufficient to get a feel for using `py-orca`, but feel free to create your own dataset YAML file on Synapse with an output folder that you own.

```yaml
id: my_test_dataset
samplesheet: syn51514475
output_folder: syn51514559
```

# Launching Nextflow workflows from Python with `seqerakit`

[`seqerakit`](https://github.com/seqeralabs/seqera-kit) is Seqera's Python wrapper around
the [Seqera Platform CLI](https://github.com/seqeralabs/tower-cli) (`tw`). It covers the
same ground as `orca.services.nextflowtower` — launching runs, passing params and
profiles, selecting a compute environment, waiting on status — and it is maintained by
Seqera against the current Platform API.

## Prerequisites

`seqerakit` shells out to the `tw` CLI, so both must be installed and on your `PATH`:

```bash
# 1. Install the Seqera Platform CLI (v0.11.0+); see the tower-cli README for
#    other platforms and for the Homebrew/Conda options.
#    https://github.com/seqeralabs/tower-cli#installation

# 2. Install seqerakit (Python 3.10+)
pip install seqerakit
# or, to keep it isolated from your project environment:
uv tool install seqerakit
```

Authentication uses the same personal access token as `py-orca`, but read from Seqera's
standard environment variables rather than from a `*_CONNECTION_URI`:

```bash
export TOWER_ACCESS_TOKEN='<your-seqera-platform-access-token>'

# Only needed for Seqera Enterprise; omit for Seqera Cloud (cloud.seqera.io)
export TOWER_API_ENDPOINT='https://<your-tower-host>/api'
```

If your pipeline reads from or writes to S3 (as the Sage compute environments do), keep
exporting `AWS_PROFILE` — or another source of AWS credentials — exactly as you did for
`demo.py`.

## Launching a run from Python

This is the direct equivalent of `NextflowTowerOps.launch_workflow(launch_info)`. The
`SeqeraPlatform` object forwards any attribute to the corresponding `tw` subcommand, so
`tw.launch(...)` runs `tw launch ...` and returns its output:

```python
from seqerakit import seqeraplatform

# json=True makes every command return parsed JSON instead of raw stdout
tw = seqeraplatform.SeqeraPlatform(json=True)

result = tw.launch(
    "--workspace", "my-org/my-project",
    "--compute-env", "my-spot-compute-env",
    "--name", "my_test_dataset_rnaseq",
    "--revision", "3.11.2",
    "--profile", "sage",
    "--work-dir", "s3://example-dev-project-tower-scratch/work",
    "--params-file", "rnaseq-params.yaml",
    "nf-core/rnaseq",
)

workflow_id = result["workflowId"]
print(f"Launched run: {workflow_id}")
```

Pipeline parameters go in the `--params-file` YAML rather than the `params` dict that
`LaunchInfo` took:

```yaml
# rnaseq-params.yaml
input: s3://example-dev-project-tower-scratch/work/synstage/my_test_dataset_synstage/my_test_dataset.csv
outdir: s3://example-dev-project-tower-scratch/work/my_test_dataset_rnaseq
pseudo_aligner: salmon
skip_bbsplit: false
```

Note that `--compute-env` takes a compute environment *name*, so there is no equivalent
of `get_latest_compute_env()`; pin the name explicitly, or list what is available with
`tw.compute_envs("list", "--workspace", workspace)` and pick from the result.

## Waiting for a run to finish

`tw launch --wait` blocks until the run reaches a given state, which replaces the
`asyncio` polling in `NextflowTowerOps.monitor_workflow()`. Valid states are `SUBMITTED`,
`RUNNING`, and `SUCCEEDED`; the command exits non-zero if the run fails first.

```python
# Blocks until the run succeeds (or raises if it fails)
tw.launch(
    "--workspace", "my-org/my-project",
    "--compute-env", "my-spot-compute-env",
    "--name", "my_test_dataset_rnaseq",
    "--wait", "SUCCEEDED",
    "nf-core/rnaseq",
)
```

For long-running pipelines you usually want to return control to your orchestrator
between checks instead of holding a blocking process open. Launch with
`--wait SUBMITTED`, then poll:

```python
import time

def monitor_workflow(tw, workspace, workflow_id, wait_time=300):
    """Poll a run until it reaches a terminal state; return that state."""
    terminal = {"SUCCEEDED", "FAILED", "CANCELLED", "UNKNOWN"}
    while True:
        run = tw.runs("view", "--workspace", workspace, "--id", workflow_id)
        status = run["general"]["status"]
        if status in terminal:
            return status
        time.sleep(wait_time)

status = monitor_workflow(tw, "my-org/my-project", workflow_id)
if status != "SUCCEEDED":
    raise RuntimeError(f"Workflow did not complete successfully ({status}).")
```

In Airflow, Prefect, or Dagster, prefer that pattern split across two tasks — a launch
task that returns the workflow ID and a deferrable sensor task that checks status — so a
scheduler restart does not lose the run.

## Declarative alternative (YAML)

`seqerakit` can also drive everything from a YAML file, which is convenient when the run
configuration is checked into a repository rather than computed at runtime:

```yaml
# rnaseq-launch.yaml
launch:
  - name: 'my_test_dataset_rnaseq'
    workspace: 'my-org/my-project'
    compute-env: 'my-spot-compute-env'
    pipeline: 'nf-core/rnaseq'
    revision: '3.11.2'
    profile: 'sage'
    work-dir: 's3://example-dev-project-tower-scratch/work'
    params:
      input: 's3://example-dev-project-tower-scratch/work/my_test_dataset.csv'
      outdir: 's3://example-dev-project-tower-scratch/work/my_test_dataset_rnaseq'
```

```bash
seqerakit rnaseq-launch.yaml --dryrun   # print the tw commands without running them
seqerakit rnaseq-launch.yaml            # actually launch
```

The same file can define organizations, workspaces, compute environments, secrets, and
labels alongside `launch:` blocks, so the workspace setup that `py-orca` expected to
already exist can be managed as code.

## Concept mapping

| `py-orca` | `seqerakit` / `tw` |
| --- | --- |
| `NEXTFLOWTOWER_CONNECTION_URI` | `TOWER_ACCESS_TOKEN` (+ `TOWER_API_ENDPOINT` for Enterprise) |
| `NextflowTowerOps()` | `seqeraplatform.SeqeraPlatform()` |
| `LaunchInfo(pipeline=..., run_name=...)` | `tw.launch("<pipeline>", "--name", ...)` |
| `LaunchInfo(params={...})` | `--params-file params.yaml` or `params:` in YAML |
| `LaunchInfo(profiles=[...])` | `--profile a,b` |
| `LaunchInfo(revision=...)` | `--revision` |
| `LaunchInfo(work_dir=...)` | `--work-dir` |
| `LaunchInfo(nextflow_config=...)` | `--config <file>` |
| `LaunchInfo(workspace_secrets=[...])` | workspace secrets managed via `tw secrets` / a `secrets:` YAML block |
| `ops.get_latest_compute_env(filter)` | `tw.compute_envs("list", ...)`, then pass `--compute-env <name>` |
| `ops.launch_workflow(...)` | `tw.launch(...)` |
| `ops.monitor_workflow(id)` | `--wait SUCCEEDED`, or poll `tw.runs("view", "--id", id)` |
| `ops.list_workflows(filter)` | `tw.runs("list", "--workspace", ws, "--filter", ...)` |
| `ops.get_workflow_tasks(id)` | `tw.runs("view", "--id", id, "--tasks")` |

If you need something neither the CLI nor `seqerakit` exposes, the
[Seqera Platform REST API](https://docs.seqera.io/platform-cloud/api/overview) is
available directly and is what `py-orca` was calling under the hood.

# PyScaffold

This project has been set up using PyScaffold 4.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.

```console
putup --name orca --markdown --github-actions --pre-commit --license Apache-2.0 py-orca
```
