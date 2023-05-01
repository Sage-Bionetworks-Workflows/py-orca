class TaskStatus:
    """enum containing all possible status values for
    Nextflow Tower runs. terminal_states set which
    statuses result in a run being determined to be
    "complete"
    """

    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"

    terminal_states = [SUCCEEDED, FAILED, CANCELLED, UNKNOWN]
