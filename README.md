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

This repository includes a demonstration script called [`demo.py`](demo.py), which showcases how you can use `py-orca` to launch and monitor your workflows on Nextflow Tower. Specifically, it illustrates how to process an RNA-seq dataset using a series of workflow runs, namely `nf-synstage`, `nf-core/rnaseq`, and `nf-synindex`. `py-orca` can be used with any Python-compatible workflow management system to orchestrate each step (_e.g._ Airflow, Prefect, Dagster). The demonstration script uses [Metaflow](https://metaflow.org/) because it's easy to run locally and has an intuitive syntax.

The script assumes that the following environment variables are set.
Refer to [`.env.example`](.env.example) for the format of their values as well as examples. You can set these environment variables using whatever method you prefer (_e.g._ using an `.env` file, sourcing a shell script).

- `NEXTFLOWTOWER_CONNECTION_URI`
- `SYNAPSE_CONNECTION_URI`
- `AWS_PROFILE` (or another source of AWS credentials)

Once your environment is set, you can create a virtual environment, install the Python dependencies, and run the demonstration script (after downloading it) as follows. Note that you will need to update the `s3_prefix` parameter so that it points to an S3 bucket that is accessible to your Tower workspace.

```bash
# Create and activate a Python virtual environment (tested with Python 3.10)
python3 -m venv venv/
source venv/bin/activate

# Install Python dependencies
python3 -m pip install 'py-orca[all]' 'metaflow' 'pyyaml' 's3fs'

# Run the script using an example dataset
python3 demo.py run --dataset_id 'syn51514585' --s3_prefix 's3://orca-service-test-project-tower-bucket/outputs'
```

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
