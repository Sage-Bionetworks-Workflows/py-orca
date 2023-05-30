#!/usr/bin/env python3

"""
py-orca demonstration script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See README.md for instructions on how to run this script.
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

    def synstage_info(self, samplesheet_uri: str) -> LaunchInfo:
        """Generate LaunchInfo for nf-synstage."""
        run_name = self.get_run_name("synstage")
        return LaunchInfo(
            run_name=run_name,
            pipeline="Sage-Bionetworks-Workflows/nf-synstage",
            revision="main",
            profiles=["sage"],
            params={
                "input": samplesheet_uri,
            },
            workspace_secrets=["SYNAPSE_AUTH_TOKEN"],
        )

    def rnaseq_info(self, staged_samplesheet_uri: str, outdir_uri: str) -> LaunchInfo:
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
            },
        )

    def synindex_info(self, rnaseq_outdir_uri: str) -> LaunchInfo:
        """Generate LaunchInfo for nf-synindex."""
        return LaunchInfo(
            run_name=self.get_run_name("synindex"),
            pipeline="Sage-Bionetworks-Workflows/nf-synindex",
            revision="main",
            profiles=["sage"],
            params={
                "s3_prefix": rnaseq_outdir_uri,
                "parent_id": self.output_folder,
            },
            workspace_secrets=["SYNAPSE_AUTH_TOKEN"],
        )


class TowerRnaseqFlow(FlowSpec):
    """Flow for processing RNA-seq dataset on Tower."""

    tower = NextflowTowerOps()
    synapse = SynapseOps()
    s3 = s3fs.S3FileSystem()

    dataset_id = Parameter(
        "dataset_id",
        type=str,
        help="Synapse ID for a YAML file describing an RNA-seq dataset",
    )

    s3_prefix = Parameter(
        "s3_prefix",
        type=str,
        help="S3 prefix for storing output files from different runs",
    )

    def get_staged_samplesheet(self, samplesheet: str) -> str:
        """Generate staged samplesheet based on synstage behavior."""
        scheme, _, samplesheet_resource = samplesheet.partition("://")
        if scheme != "s3":
            raise ValueError("Expected an S3 URI.")
        path = PurePosixPath(samplesheet_resource)
        return f"{scheme}://{path.parent}/synstage/{path.name}"

    def monitor_workflow(self, workflow_id):
        """Monitor any workflow run (wait until done)."""
        monitor_coro = self.tower.monitor_workflow(workflow_id)
        status = asyncio.run(monitor_coro)
        if not status.is_successful:
            message = f"Workflow did not complete successfully ({status})."
            raise RuntimeError(message)
        return status

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
        sheet_contents = self.synapse.fs.readtext(self.dataset.samplesheet)
        self.s3.write_text(self.samplesheet_uri, sheet_contents)
        self.next(self.launch_synstage)

    @step
    def launch_synstage(self):
        """Launch nf-synstage to stage Synapse files in samplesheet."""
        launch_info = self.dataset.synstage_info(self.samplesheet_uri)
        self.synstage_id = self.tower.launch_workflow(launch_info, "spot")
        self.next(self.monitor_synstage)

    @step
    def monitor_synstage(self):
        """Monitor nf-synstage workflow run (wait until done)."""
        self.monitor_workflow(self.synstage_id)
        self.next(self.launch_rnaseq)

    @step
    def launch_rnaseq(self):
        """Launch nf-core/rnaseq workflow to process RNA-seq data."""
        staged_uri = self.get_staged_samplesheet(self.samplesheet_uri)
        launch_info = self.dataset.rnaseq_info(staged_uri, self.rnaseq_outdir)
        self.rnaseq_id = self.tower.launch_workflow(launch_info, "spot")
        self.next(self.monitor_rnaseq)

    @step
    def monitor_rnaseq(self):
        """Monitor nf-core/rnaseq workflow run (wait until done)."""
        self.monitor_workflow(self.rnaseq_id)
        self.next(self.launch_synindex)

    @step
    def launch_synindex(self):
        """Launch nf-synindex to index S3 files back into Synapse."""
        launch_info = self.dataset.synindex_info(self.rnaseq_outdir)
        self.synindex_id = self.tower.launch_workflow(launch_info, "spot")
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
