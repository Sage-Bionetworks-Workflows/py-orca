#!/usr/bin/env python3

"""
Nextflow workflow demonstration script (seqerakit edition)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the ``py-orca``-free replacement for ``demo.py``. It runs the same
three-step RNA-seq pipeline — ``nf-synapse/synstage``, ``nf-core/rnaseq``, and
``nf-synapse/synindex`` — orchestrated with Metaflow, but using the two
libraries that are actively maintained for this job:

- `seqerakit <https://github.com/seqeralabs/seqera-kit>`_, Seqera's Python
  wrapper around the Seqera Platform CLI (``tw``), for launching and monitoring
  workflow runs.
- `synapseclient <https://python-docs.synapse.org/>`_ for reading the dataset
  description and samplesheet out of Synapse.

Requirements
------------

The Seqera Platform CLI (``tw``, v0.11.0+) must be installed and on your PATH,
since ``seqerakit`` shells out to it. Then::

    python3 -m venv venv/
    source venv/bin/activate
    python3 -m pip install seqerakit synapseclient metaflow s3fs pyyaml

Environment variables
---------------------

- ``TOWER_ACCESS_TOKEN``: Seqera Platform personal access token.
- ``TOWER_API_ENDPOINT``: only for Seqera Enterprise; omit for Seqera Cloud.
- ``SYNAPSE_AUTH_TOKEN``: Synapse personal access token.
- ``AWS_PROFILE`` (or another source of AWS credentials) for the S3 transfers.

The ``nf-synapse`` steps also need a workspace secret named
``SYNAPSE_AUTH_TOKEN`` in the target Seqera workspace; this flow checks for it
before launching anything.

Usage
-----

::

    python3 demo_seqerakit.py run \\
        --dataset_id 'syn51514585' \\
        --s3_prefix 's3://example-dev-project-tower-scratch/work' \\
        --workspace 'my-org/example-dev-project'
"""

import logging
import os
import tempfile
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PurePosixPath
from textwrap import dedent
from typing import Any, Optional

import s3fs
import synapseclient
import yaml
from metaflow import FlowSpec, Parameter, step
from seqerakit import seqeraplatform

logger = logging.getLogger("demo")

# Workflow states that mean the run will not change again.
TERMINAL_STATES = {"SUCCEEDED", "FAILED", "CANCELLED", "UNKNOWN"}

# Secret that the nf-synapse pipeline expects to find in the workspace.
SYNAPSE_SECRET_NAME = "SYNAPSE_AUTH_TOKEN"


@lru_cache(maxsize=None)
def get_tw() -> seqeraplatform.SeqeraPlatform:
    """Construct a Seqera Platform client (one per process).

    ``json=True`` makes every ``tw`` command return parsed JSON instead of the
    human-readable table.
    """
    if not os.environ.get("TOWER_ACCESS_TOKEN"):
        raise EnvironmentError("TOWER_ACCESS_TOKEN is not set.")
    return seqeraplatform.SeqeraPlatform(json=True)


@lru_cache(maxsize=None)
def get_syn() -> synapseclient.Synapse:
    """Log into Synapse using the SYNAPSE_AUTH_TOKEN environment variable."""
    auth_token = os.environ.get("SYNAPSE_AUTH_TOKEN")
    if not auth_token:
        raise EnvironmentError("SYNAPSE_AUTH_TOKEN is not set.")
    syn = synapseclient.Synapse(silent=True)
    syn.login(authToken=auth_token)
    return syn


def read_synapse_file(synapse_id: str) -> str:
    """Download a Synapse file entity and return its contents as text."""
    with tempfile.TemporaryDirectory() as tmpdir:
        entity = get_syn().get(
            synapse_id, downloadLocation=tmpdir, ifcollision="overwrite.local"
        )
        return Path(entity.path).read_text()


@dataclass
class RnaseqDataset:
    """RNA-seq dataset and relevant details.

    Attributes:
        id: Unique dataset identifier.
        samplesheet: Synapse ID for nf-core/rnaseq CSV samplesheet.
        output_folder: Synapse ID for output folder (where workflow
            output files will be indexed).
    """

    id: str
    samplesheet: str
    output_folder: str

    def get_run_name(self, suffix: str) -> str:
        """Generate run name with given suffix."""
        return f"{self.id}_{suffix}"

    def synstage_params(self, samplesheet_uri: str) -> dict[str, Any]:
        """Generate parameters for nf-synapse/synstage."""
        return {"input": samplesheet_uri}

    def rnaseq_params(
        self, staged_samplesheet_uri: str, outdir_uri: str
    ) -> dict[str, Any]:
        """Generate parameters for nf-core/rnaseq."""
        ref_prefix = "https://raw.githubusercontent.com/nf-core/test-datasets/rnaseq3"
        return {
            "input": staged_samplesheet_uri,
            "outdir": outdir_uri,
            "fasta": f"{ref_prefix}/reference/genome.fasta",
            "gtf": f"{ref_prefix}/reference/genes.gtf.gz",
            "gff": f"{ref_prefix}/reference/genes.gff.gz",
            "transcript_fasta": f"{ref_prefix}/reference/transcriptome.fasta",
            "additional_fasta": f"{ref_prefix}/reference/gfp.fa.gz",
            "bbsplit_fasta_list": f"{ref_prefix}/reference/bbsplit_fasta_list.txt",
            "hisat2_index": f"{ref_prefix}/reference/hisat2.tar.gz",
            "salmon_index": f"{ref_prefix}/reference/salmon.tar.gz",
            "rsem_index": f"{ref_prefix}/reference/rsem.tar.gz",
            "skip_bbsplit": False,
            "pseudo_aligner": "salmon",
            "umitools_bc_pattern": "NNNN",
        }

    def synindex_params(self, rnaseq_outdir_uri: str) -> dict[str, Any]:
        """Generate parameters for nf-synapse/synindex."""
        return {"s3_prefix": rnaseq_outdir_uri, "parent_id": self.output_folder}


RNASEQ_CONFIG = dedent(
    """
    process {
        withName: 'RSEM_PREPAREREFERENCE_GENOME' {
            ext.args2 = "--genomeSAindexNbases 7"
        }
    }
    """
)


class TowerRnaseqFlow(FlowSpec):
    """Flow for processing an RNA-seq dataset on the Seqera Platform."""

    s3 = s3fs.S3FileSystem()

    dataset_id = Parameter(
        "dataset_id",
        type=str,
        required=True,
        help="Synapse ID for a YAML file describing an RNA-seq dataset",
    )

    s3_prefix = Parameter(
        "s3_prefix",
        type=str,
        required=True,
        help="S3 prefix for storing output files from different runs",
    )

    workspace = Parameter(
        "workspace",
        type=str,
        required=True,
        help="Fully qualified Seqera workspace name (<org>/<workspace>)",
    )

    compute_env = Parameter(
        "compute_env",
        type=str,
        default=None,
        help="Compute environment name (skips auto-detection)",
    )

    compute_env_filter = Parameter(
        "compute_env_filter",
        type=str,
        default="spot",
        help="Substring used to auto-detect the compute environment",
    )

    wait_time = Parameter(
        "wait_time",
        type=int,
        default=60 * 5,
        help="Number of seconds to wait between run status checks",
    )

    def resolve_compute_env(self) -> str:
        """Resolve a compute environment name in the target workspace.

        This is the ``seqerakit`` equivalent of py-orca's
        ``NextflowTowerOps.get_latest_compute_env()``. Note that ``tw launch``
        takes a compute environment *name* rather than an ID.

        Raises:
            ValueError: If zero or multiple compute environments match and none
                of them is marked as primary.

        Returns:
            Compute environment name.
        """
        response = get_tw().compute_envs("list", "--workspace", self.workspace)
        envs = [env for env in response["computeEnvs"] if env["status"] == "AVAILABLE"]
        if self.compute_env_filter:
            envs = [env for env in envs if self.compute_env_filter in env["name"]]

        if not envs:
            raise ValueError(
                f"No available compute environments (filter="
                f"'{self.compute_env_filter}')."
            )
        if len(envs) == 1:
            return envs[0]["name"]

        primary = [env for env in envs if env.get("primary")]
        if len(primary) != 1:
            names = ", ".join(env["name"] for env in envs)
            raise ValueError(
                f"Multiple compute environments match ({names}). "
                "Pass one explicitly with --compute_env."
            )
        return primary[0]["name"]

    def check_workspace_secret(self) -> None:
        """Warn if a workspace secret required by the pipelines is missing."""
        response = get_tw().secrets("list", "--workspace", self.workspace)
        names = {secret["name"] for secret in response.get("secrets", [])}
        if SYNAPSE_SECRET_NAME not in names:
            print(
                f"WARNING: Workspace secret '{SYNAPSE_SECRET_NAME}' not found in "
                f"'{self.workspace}'. The nf-synapse steps will fail without it. "
                f"Create it with: tw secrets add --workspace {self.workspace} "
                f"--name {SYNAPSE_SECRET_NAME} --value <token>"
            )

    def launch_workflow(
        self,
        run_name: str,
        pipeline: str,
        revision: str,
        params: dict[str, Any],
        profiles: Optional[list[str]] = None,
        nextflow_config: Optional[str] = None,
    ) -> str:
        """Launch a workflow run and return its ID.

        This is the ``seqerakit`` equivalent of py-orca's
        ``NextflowTowerOps.launch_workflow()``. Unlike py-orca, ``tw launch``
        is not idempotent: relaunching with the same run name creates a new run
        rather than resuming the previous one.

        Args:
            run_name: Human-readable name for the run.
            pipeline: Full pipeline repository URL (e.g.
                "https://github.com/nf-core/rnaseq"). A bare "org/repo" is
                looked up as a Launchpad pipeline name instead.
            revision: Git branch, tag, or commit.
            params: Pipeline parameters, written out to a params file.
            profiles: Configuration profiles to enable.
            nextflow_config: Extra Nextflow configuration, written out to a
                file and passed via ``--config``.

        Returns:
            Workflow run ID.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            params_file = Path(tmpdir, "params.yaml")
            params_file.write_text(yaml.safe_dump(params))

            args = [
                "--workspace",
                self.workspace,
                "--compute-env",
                self.resolved_compute_env,
                "--name",
                run_name,
                "--revision",
                revision,
                "--work-dir",
                self.s3_prefix,
                "--params-file",
                str(params_file),
            ]
            if profiles:
                args += ["--profile", ",".join(profiles)]
            if nextflow_config:
                config_file = Path(tmpdir, "nextflow.config")
                config_file.write_text(nextflow_config)
                args += ["--config", str(config_file)]
            args.append(pipeline)

            response = get_tw().launch(*args)

        workflow_id = response["workflowId"]
        print(f"Launched '{run_name}' ({workflow_id}): {response['workflowUrl']}")
        return workflow_id

    def monitor_workflow(self, workflow_id: str) -> str:
        """Poll a workflow run until it reaches a terminal state.

        This is the ``seqerakit`` equivalent of py-orca's
        ``NextflowTowerOps.monitor_workflow()``. For a simple blocking wait you
        can instead pass ``--wait SUCCEEDED`` to ``tw launch``, but polling
        lets the orchestrator own the schedule.

        Args:
            workflow_id: Workflow run ID.

        Raises:
            RuntimeError: If the run does not complete successfully.

        Returns:
            Final workflow state.
        """
        while True:
            run = get_tw().runs(
                "view", "--workspace", self.workspace, "--id", workflow_id
            )
            status = run["general"]["status"]
            if status in TERMINAL_STATES:
                break
            print(f"Run {workflow_id} is {status}; checking again in {self.wait_time}s")
            time.sleep(self.wait_time)

        if status != "SUCCEEDED":
            raise RuntimeError(f"Workflow did not complete successfully ({status}).")
        print(f"Run {workflow_id} is now done ({status}).")
        return status

    def get_staged_samplesheet(self, samplesheet: str, run_name: str) -> str:
        """Generate staged samplesheet based on synstage behavior."""
        scheme, _, samplesheet_resource = samplesheet.partition("://")
        if scheme != "s3":
            raise ValueError("Expected an S3 URI.")
        path = PurePosixPath(samplesheet_resource)
        return f"{scheme}://{path.parent}/synstage/{run_name}/{path.name}"

    @step
    def start(self):
        """Entry point."""
        self.next(self.check_workspace)

    @step
    def check_workspace(self):
        """Resolve the compute environment and check for required secrets."""
        self.resolved_compute_env = self.compute_env or self.resolve_compute_env()
        print(f"Using compute environment '{self.resolved_compute_env}'.")
        self.check_workspace_secret()
        self.next(self.load_dataset)

    @step
    def load_dataset(self):
        """Load dataset from Synapse YAML file."""
        kwargs = yaml.safe_load(read_synapse_file(self.dataset_id))
        self.dataset = RnaseqDataset(**kwargs)
        self.next(self.get_rnaseq_outdir)

    @step
    def get_rnaseq_outdir(self):
        """Generate output directory for nf-core/rnaseq."""
        run_name = self.dataset.get_run_name("rnaseq")
        self.rnaseq_outdir = f"{self.s3_prefix}/{run_name}"
        self.next(self.transfer_samplesheet_to_s3)

    @step
    def transfer_samplesheet_to_s3(self):
        """Transfer raw samplesheet from Synapse to Tower S3 bucket."""
        self.samplesheet_uri = f"{self.s3_prefix}/{self.dataset.id}.csv"
        sheet_contents = read_synapse_file(self.dataset.samplesheet)
        self.s3.write_text(self.samplesheet_uri, sheet_contents)
        self.next(self.launch_synstage)

    @step
    def launch_synstage(self):
        """Launch nf-synapse/synstage to stage Synapse files in samplesheet."""
        self.synstage_id = self.launch_workflow(
            run_name=self.dataset.get_run_name("synstage"),
            pipeline="https://github.com/Sage-Bionetworks-Workflows/nf-synapse",
            revision="main",
            profiles=["docker", "synstage"],
            params=self.dataset.synstage_params(self.samplesheet_uri),
        )
        self.next(self.monitor_synstage)

    @step
    def monitor_synstage(self):
        """Monitor nf-synapse/synstage workflow run (wait until done)."""
        self.monitor_workflow(self.synstage_id)
        self.next(self.launch_rnaseq)

    @step
    def launch_rnaseq(self):
        """Launch nf-core/rnaseq workflow to process RNA-seq data."""
        staged_uri = self.get_staged_samplesheet(
            self.samplesheet_uri, self.dataset.get_run_name("synstage")
        )
        self.rnaseq_id = self.launch_workflow(
            run_name=self.dataset.get_run_name("rnaseq"),
            pipeline="https://github.com/nf-core/rnaseq",
            revision="3.11.2",
            profiles=["sage"],
            params=self.dataset.rnaseq_params(staged_uri, self.rnaseq_outdir),
            nextflow_config=RNASEQ_CONFIG,
        )
        self.next(self.monitor_rnaseq)

    @step
    def monitor_rnaseq(self):
        """Monitor nf-core/rnaseq workflow run (wait until done)."""
        self.monitor_workflow(self.rnaseq_id)
        self.next(self.launch_synindex)

    @step
    def launch_synindex(self):
        """Launch nf-synindex to index S3 files back into Synapse."""
        self.synindex_id = self.launch_workflow(
            run_name=self.dataset.get_run_name("synindex"),
            pipeline="https://github.com/Sage-Bionetworks-Workflows/nf-synapse",
            revision="main",
            profiles=["docker", "synindex"],
            params=self.dataset.synindex_params(self.rnaseq_outdir),
        )
        self.next(self.monitor_synindex)

    @step
    def monitor_synindex(self):
        """Monitor nf-synindex workflow run (wait until done)."""
        self.monitor_workflow(self.synindex_id)
        self.next(self.end)

    @step
    def end(self):
        """End point."""
        print(f"Completed processing {self.dataset}")
        print(f"synstage workflow ID: {self.synstage_id}")
        print(f"nf-core/rnaseq workflow ID: {self.rnaseq_id}")
        print(f"synindex workflow ID: {self.synindex_id}")


if __name__ == "__main__":
    TowerRnaseqFlow()
