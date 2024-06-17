# py-orca

<!--
[![ReadTheDocs](https://readthedocs.org/projects/orca/badge/?version=latest)](https://sage-bionetworks-workflows.github.io/orca/)
-->
[![PyPI-Server](https://img.shields.io/pypi/v/py-orca.svg)](https://pypi.org/project/py-orca/)
[![codecov](https://codecov.io/gh/Sage-Bionetworks-Workflows/py-orca/branch/main/graph/badge.svg?token=OCC4MOUG5P)](https://codecov.io/gh/Sage-Bionetworks-Workflows/py-orca)
[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](#pyscaffold)

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

# PyScaffold

This project has been set up using PyScaffold 4.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.

```console
putup --name orca --markdown --github-actions --pre-commit --license Apache-2.0 py-orca
```
