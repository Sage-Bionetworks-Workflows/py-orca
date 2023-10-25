import asyncio
from typing import List

import pandas as pd
from metaflow import FlowSpec, Parameter, step

from orca.services.nextflowtower import NextflowTowerOps
from orca.services.nextflowtower.models import WorkflowTask


class LogsFlow(FlowSpec):
    """Retrieve execution logs and failure reasons for all
    failed tasks in a workflow."""

    tower = NextflowTowerOps()

    workflow_id = Parameter(
        "workflow_id",
        type=str,
        help="Nextflow workflow ID",
    )

    # Example error reasons for nf-histoqc
    log_reasons = [
        "NO tissue remains detectable!",
        "NO tissue remains detectable in mask!",
        "Inappropriate argument value (of correct type)",
    ]

    async def get_logs(self, task: WorkflowTask):
        """Retrieve execution logs for an individual task."""
        print(f"Getting logs for task: {task.task_id}")
        return {
            "task_id": task.task_id,
            "tag": task.tag,
            "execution_log": self.tower.get_task_logs(
                workflow_id=self.workflow_id, task_id=task.task_id
            ),
        }

    async def retrieve_workflow_task_logs(self):
        """Asynchronously retrieve execution logs for all failed tasks in a workflow."""
        print("Getting workflow tasks")
        tasks = self.tower.get_workflow_tasks(workflow_id=self.workflow_id)
        failed_tasks = [task for task in tasks if task.status == "FAILED"]
        print("Getting logs for each failed task")
        task_log_list = await asyncio.gather(
            *[self.get_logs(task) for task in failed_tasks]
        )
        return task_log_list

    def determine_failure_reasons(self, task_log_list: List[dict]):
        """Check for failure reasons in execution logs.
        Attribute failure reasons to each task."""
        for task in task_log_list:
            failure_reasons = []
            for reason in self.log_reasons:
                if reason in task["execution_log"]:
                    failure_reasons.append(reason)
            task["failure_reasons"] = ", ".join(failure_reasons)
            if not task["failure_reasons"]:
                task["failure_reasons"] = "Failure Reason Undetermined"
            task.pop("execution_log")

    @step
    def start(self):
        """Entry point."""
        self.next(self.get_task_logs)

    @step
    def get_task_logs(self):
        """Collect task logs for a workflow."""
        self.task_log_list = asyncio.run(self.retrieve_workflow_task_logs())
        self.next(self.compile_failure_reasons)

    @step
    def compile_failure_reasons(self):
        """Compile failure reasons for each task."""
        self.determine_failure_reasons(self.task_log_list)
        self.next(self.export_results)

    @step
    def export_results(self):
        """Export results to CSV."""
        logs_df = pd.DataFrame(self.task_log_list)
        logs_df.to_csv("task_logs.csv", index=False)
        self.next(self.end)

    @step
    def end(self):
        """End point."""
        print("Done")


if __name__ == "__main__":
    LogsFlow()
