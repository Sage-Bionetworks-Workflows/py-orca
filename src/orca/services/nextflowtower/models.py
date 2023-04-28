import json
from collections.abc import Collection
from dataclasses import field
from datetime import datetime
from typing import Any, Optional

from pydantic.dataclasses import dataclass


@dataclass(kw_only=False)
class LaunchInfo:
    """Workflow launch specification"""

    compute_env_id: str
    pipeline: str
    work_dir: str
    revision: Optional[str] = None
    params: Optional[dict] = None
    nextflow_config: Optional[str] = None
    run_name: Optional[str] = None
    pre_run_script: Optional[str] = None
    profiles: list[str] = field(default_factory=list)
    user_secrets: list[str] = field(default_factory=list)
    workspace_secrets: list[str] = field(default_factory=list)

    @staticmethod
    def dedup(items: Collection[str]) -> list[str]:
        """Deduplicate items in a collection.

        Args:
            items: Collection of items.

        Returns:
            Deduplicated collection or None.
        """
        return list(set(items))

    @staticmethod
    def get_current_timestamp():
        """Generate current timestamp using Tower's UTC format.

        Returns:
            Current timestamp.
        """
        return datetime.now().isoformat()[:-3] + "Z"

    def to_dict(self) -> dict[str, Any]:
        """Generate JSON representation of a launch specification.

        Returns:
            JSON representation.
        """
        output = {
            "launch": {
                "computeEnvId": self.compute_env_id,
                "configProfiles": self.dedup(self.profiles),
                "configText": self.nextflow_config,
                "dateCreated": self.get_current_timestamp(),
                "entryName": None,
                "headJobCpus": None,
                "headJobMemoryMb": None,
                "id": None,
                "labelIds": [],
                "mainScript": None,
                "optimizationId": None,
                "paramsText": json.dumps(self.params),
                "pipeline": self.pipeline,
                "postRunScript": None,
                "preRunScript": self.pre_run_script,
                "pullLatest": False,
                "resume": False,
                "revision": self.revision,
                "runName": self.run_name,
                "schemaName": None,
                "stubRun": False,
                "towerConfig": None,
                "userSecrets": self.dedup(self.user_secrets),
                "workDir": self.work_dir,
                "workspaceSecrets": self.dedup(self.workspace_secrets),
            }
        }
        return output
