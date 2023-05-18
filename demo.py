#!/usr/bin/env python3

"""
py-orca demonstration script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script is intended to demonstrate how you can use py-orca to
process a dataset (in this case, RNA-seq) using a series of workflow
runs: nf-synstage, nf-core/rnaseq, and nf-synindex.

This script assumes that the following environment variables are set.
Refer to `.env.example` for the format, including examples.
    - NEXTFLOWTOWER_CONNECTION_URI
    - SYNAPSE_CONNECTION_URI
    - AWS_PROFILE (or another source of AWS credentials)
"""

import asyncio
from dataclasses import dataclass
from pathlib import PurePosixPath
from textwrap import dedent

import s3fs
import yaml
from metaflow import FlowSpec, Parameter, step

from orca.services.nextflowtower import LaunchInfo, NextflowTowerOps
from orca.services.synapse import SynapseOps

TMPDIR_PREFIX = "s3://orca-service-test-project-tower-scratch/30days"
OUTDIR_PREFIX = "s3://orca-service-test-project-tower-bucket/outputs"


@dataclass
class RnaseqDataset:
    """RNA-seq dataset and relevant details."""

    id: str
    samplesheet: str
    output_folder: str

    def get_run_name(self, suffix: str) -> str:
        """Generate run name with given suffix."""
        return f"{self.id}_{suffix}"

    def get_staged_samplesheet(self) -> str:
        """Generate staged samplesheet based on synstage behavior."""
        path = PurePosixPath(self.samplesheet)
        return f"{path.parent}/synstage/{path.name}"

    def synstage_info(self) -> LaunchInfo:
        """Generate LaunchInfo for nf-synstage."""
        run_name = self.get_run_name("synstage")
        return LaunchInfo(
            run_name=run_name,
            pipeline="Sage-Bionetworks-Workflows/nf-synstage",
            revision="main",
            profiles=["sage"],
            params={
                "input": self.samplesheet,
            },
            workspace_secrets=["SYNAPSE_AUTH_TOKEN"],
        )

    def rnaseq_info(self) -> LaunchInfo:
        """Generate LaunchInfo for nf-core/rnaseq."""
        run_name = self.get_run_name("rnaseq")
        ref_prefix = "https://raw.githubusercontent.com/nf-core/test-datasets/rnaseq3"

        nextflow_config = """
        process {
            withName: 'RSEM_PREPAREREFERENCE_GENOME' {
                ext.args2 = "--genomeSAindexNbases 7"
            }
        }
        """

        return LaunchInfo(
            run_name=run_name,
            pipeline="nf-core/rnaseq",
            revision="3.11.2",
            profiles=["sage"],
            nextflow_config=dedent(nextflow_config),
            params={
                "input": self.get_staged_samplesheet(),
                "outdir": f"{OUTDIR_PREFIX}/{run_name}",
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
            },
        )

    def synindex_info(self) -> LaunchInfo:
        """Generate LaunchInfo for nf-synindex."""
        rnaseq_info = self.rnaseq_info()
        assert rnaseq_info.params

        return LaunchInfo(
            run_name=self.get_run_name("synindex"),
            pipeline="Sage-Bionetworks-Workflows/nf-synindex",
            revision="main",
            profiles=["sage"],
            params={
                "s3_prefix": rnaseq_info.params["outdir"],
                "parent_id": self.output_folder,
            },
            workspace_secrets=["SYNAPSE_AUTH_TOKEN"],
        )


class TowerRnaseqFlow(FlowSpec):
    """Flow for processing RNA-seq dataset on Tower."""

    tower = NextflowTowerOps()
    synapse = SynapseOps()
    s3 = s3fs.S3FileSystem()

    # Synapse ID for a YAML file that describes an RNA-seq dataset
    # Here's an example:
    #   id: my_test_dataset
    #   samplesheet: syn51514475
    #   output_folder: syn51514559
    dataset_id = Parameter("dataset_id", help="Dataset Synapse ID", type=str)

    @step
    def start(self):
        """Entry point."""
        self.next(self.load_dataset)

    @step
    def load_dataset(self):
        """Load dataset from Synapse YAML file."""
        with self.synapse.fs.open(self.dataset_id, "r") as fp:
            kwargs = yaml.safe_load(fp)
        self.dataset = RnaseqDataset(**kwargs)
        self.next(self.transfer_samplesheet_to_s3)

    @step
    def transfer_samplesheet_to_s3(self):
        """Transfer raw samplesheet from Synapse to Tower S3 bucket."""
        sheet_uri = f"{TMPDIR_PREFIX}/{self.dataset.id}.csv"
        sheet_contents = self.synapse.fs.readtext(self.dataset.samplesheet)
        self.s3.write_text(sheet_uri, sheet_contents)
        self.dataset.samplesheet = sheet_uri
        self.next(self.launch_synstage)

    @step
    def launch_synstage(self):
        """Launch nf-synstage to stage Synapse files in samplesheet."""
        launch_info = self.dataset.synstage_info()
        self.synstage_id = self.tower.launch_workflow(launch_info, "spot")
        self.next(self.monitor_synstage)

    @step
    def monitor_synstage(self):
        """Monitor nf-synstage workflow run (wait until done)."""
        monitor_coro = self.tower.monitor_workflow(self.synstage_id)
        status = asyncio.run(monitor_coro)
        assert status.is_successful
        self.next(self.launch_rnaseq)

    @step
    def launch_rnaseq(self):
        """Launch nf-core/rnaseq workflow to process RNA-seq data."""
        launch_info = self.dataset.rnaseq_info()
        self.rnaseq_id = self.tower.launch_workflow(launch_info, "spot")
        self.next(self.monitor_rnaseq)

    @step
    def monitor_rnaseq(self):
        """Monitor nf-core/rnaseq workflow run (wait until done)."""
        monitor_coro = self.tower.monitor_workflow(self.rnaseq_id)
        status = asyncio.run(monitor_coro)
        assert status.is_successful
        self.next(self.launch_synindex)

    @step
    def launch_synindex(self):
        """Launch nf-synindex to index S3 files back into Synapse."""
        launch_info = self.dataset.synindex_info()
        self.synindex_id = self.tower.launch_workflow(launch_info, "spot")
        self.next(self.monitor_synindex)

    @step
    def monitor_synindex(self):
        """Monitor nf-synindex workflow run (wait until done)."""
        monitor_coro = self.tower.monitor_workflow(self.synindex_id)
        status = asyncio.run(monitor_coro)
        assert status.is_successful
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
