import json
from collections.abc import Collection
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any, Iterable, Optional

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from orca.services.nextflowtower.utils import parse_datetime


class TaskStatus(Enum):
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


@dataclass(kw_only=False)
class User:
    """Nextflow Tower user."""

    id: int
    username: str
    email: str

    @classmethod
    def from_json(cls, response: dict[str, Any]) -> Self:
        """Create user from API JSON response.

        Returns:
            User instance.
        """
        return cls(response["id"], response["userName"], response["email"])


@dataclass(kw_only=False)
class Organization:
    """Nextflow Tower organization."""

    id: int
    name: str

    @classmethod
    def from_json(cls, response: dict[str, Any]) -> Self:
        """Create organization from API JSON response.

        Returns:
            Organization instance.
        """
        return cls(response["orgId"], response["orgName"])


@dataclass(kw_only=False)
class Workspace:
    """Nextflow Tower workspace."""

    id: int
    name: str
    org: Organization

    @property
    def full_name(self) -> str:
        """Fully-qualified workspace name (with organization name)."""
        return f"{self.org.name}/{self.name}".lower()

    @classmethod
    def from_json(cls, response: dict[str, Any]) -> Self:
        """Create workspace from API JSON response.

        Returns:
            Workspace instance.
        """
        org = Organization.from_json(response)
        return cls(response["workspaceId"], response["workspaceName"], org)


@dataclass(kw_only=False)
class LaunchInfo:
    """Nextflow Tower workflow launch specification."""

    pipeline: Optional[str] = None
    compute_env_id: Optional[str] = None
    work_dir: Optional[str] = None
    revision: Optional[str] = None
    params: Optional[dict] = None
    nextflow_config: Optional[str] = None
    run_name: Optional[str] = None
    pre_run_script: Optional[str] = None
    profiles: list[str] = field(default_factory=list)
    user_secrets: list[str] = field(default_factory=list)
    workspace_secrets: list[str] = field(default_factory=list)
    label_ids: list[int] = field(default_factory=list)

    @staticmethod
    def dedup(items: Collection[str]) -> list[str]:
        """Deduplicate items in a collection.

        Args:
            items: Collection of items.

        Returns:
            Deduplicated collection or None.
        """
        return list(set(items))

    def fill_in(self, attr: str, value: Any):
        """Fill in any missing values.

        Args:
            attr: Attribute name.
            value: Attribute value.
        """
        if not getattr(self, attr, None):
            setattr(self, attr, value)

    def add_in(self, attr: str, values: Iterable[Any]):
        """Add values to a list attribute.

        Args:
            attr: Attribute name.
            values: New attribute values.
        """
        current_values = getattr(self, attr)
        if not isinstance(current_values, list):
            message = f"Attribute '{attr}' is not a list and cannot be extended."
            raise ValueError(message)
        updated_values = current_values + list(values)
        setattr(self, attr, updated_values)

    def get(self, name: str) -> Any:
        """Retrieve attribute value, which cannot be None.

        Args:
            name: Atribute name.

        Returns:
            Attribute value (not None).
        """
        if getattr(self, name, None) is None:
            message = f"Attribute '{name}' must be set (not None) by this point."
            raise ValueError(message)
        return getattr(self, name)

    def to_dict(self) -> dict[str, Any]:
        """Generate JSON representation of a launch specification.

        Returns:
            JSON representation.
        """
        output = {
            "launch": {
                "computeEnvId": self.get("compute_env_id"),
                "configProfiles": self.dedup(self.profiles),
                "configText": self.nextflow_config,
                "dateCreated": None,
                "entryName": None,
                "headJobCpus": None,
                "headJobMemoryMb": None,
                "id": None,
                "labelIds": self.label_ids,
                "mainScript": None,
                "optimizationId": None,
                "paramsText": json.dumps(self.params),
                "pipeline": self.get("pipeline"),
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
                "workDir": self.get("work_dir"),
                "workspaceSecrets": self.dedup(self.workspace_secrets),
            }
        }
        return output


@dataclass(kw_only=False)
class Label:
    """Nextflow Tower workflow run label."""

    id: int
    name: str
    value: Optional[str]
    resource: bool

    @classmethod
    def from_json(cls, response: dict[str, Any]) -> Self:
        """Create label from API JSON response.

        Returns:
            Label instance.
        """
        return cls(**response)


@dataclass(kw_only=False)
class ComputeEnvSummary:
    """Nextflow Tower compute environment summary."""

    id: str
    name: str
    status: str
    work_dir: str
    raw: dict

    @classmethod
    def from_json(cls, response: dict[str, Any]) -> Self:
        """Create compute environment from API JSON response.

        Returns:
            Compute environment instance.
        """
        return cls(
            response["id"],
            response["name"],
            response["status"],
            response["workDir"],
            response,
        )


@dataclass(kw_only=False)
class ComputeEnv(ComputeEnvSummary):
    """Nextflow Tower compute environment details."""

    date_created: datetime
    pre_run_script: str
    labels: list[Label]

    @classmethod
    def from_json(cls, response: dict[str, Any]) -> Self:
        """Create compute environment from API JSON response.

        Returns:
            Compute environment instance.
        """
        return cls(
            id=response["id"],
            name=response["name"],
            status=response["status"],
            work_dir=response["config"]["workDir"],
            date_created=parse_datetime(response["dateCreated"]),
            pre_run_script=response["config"]["preRunScript"],
            labels=[Label.from_json(label) for label in response["labels"]],
            raw=response,
        )
