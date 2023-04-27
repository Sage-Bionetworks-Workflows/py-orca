import pytest
from sevenbridges.models.enums import TaskStatus

from orca.services.sevenbridges import SevenBridgesHook


@pytest.mark.cost
@pytest.mark.acceptance
def test_cavatica_launch_poc_v2(run_id):
    def create_task():
        hook = SevenBridgesHook()
        task_inputs = {
            "input_type": "FASTQ",
            "reads1": hook.client.files.get("63e569217a0654635c558c84"),
            "reads2": hook.client.files.get("63e5694ebfc712185ac37a27"),
            "runThreadN": 36,
            "wf_strand_param": "default",
            "sample_name": "HCC1187_1M",
            "rmats_read_length": 101,
            "outSAMattrRGline": "ID:HCC1187_1M\tLB:NA\tPL:Illumina\tSM:HCC1187_1M",
            "output_basename": run_id,
        }
        app_id = "orca-service/test-project/kfdrc-rnaseq-workflow"
        task_id = hook.ops.create_task(run_id, app_id, task_inputs)
        return task_id

    def monitor_task(task_name):
        hook = SevenBridgesHook()
        return hook.ops.get_task_status(task_name)

    task_id = create_task()
    task_status, _ = monitor_task(task_id)
    assert hasattr(TaskStatus, str(task_status))
