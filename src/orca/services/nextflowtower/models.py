import json as json_module
from dataclasses import field, fields
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Iterable, Optional

from pydantic import root_validator
from pydantic.dataclasses import dataclass
from typing_extensions import Self

from orca.services.nextflowtower.utils import dedup


class WorkflowStatus(Enum):
    """Valid values for the status of a Tower workflow.

    Attributes:
        terminate_states: List of status values for a workflow
            that is no longer in progress.
    """

    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"

    terminal_states = [SUCCEEDED, FAILED, CANCELLED, UNKNOWN]


@dataclass(kw_only=False)
class BaseTowerModel:
    """Base model for Nextflow Tower models.

    Attributes:
        _key_mapping: Mapping between Python and API key names.
            Only discordant names need to be listed.
    """

    _key_mapping: ClassVar[dict[str, str]]

    @classmethod
    def from_json(cls, json: dict[str, Any], **kwargs: Any) -> Self:
        """Create instance from API JSON response.

        Args:
            json: API JSON response.
            **kwargs: Special values.

        Returns:
            Class instance.
        """
        cls_kwargs = dict()

        # First: populate with special values
        cls_kwargs.update(kwargs)

        # Second: populate with values with discordant key names
        key_mapping = getattr(cls, "_key_mapping", {})
        for python_name, api_name in key_mapping.items():
            if python_name not in cls_kwargs:
                value = None
                target = json
                for api_name_part in api_name.split("."):
                    if api_name_part in target:
                        value = target[api_name_part]
                        target = value
                if value is not None:
                    cls_kwargs[python_name] = value

        # Third: populate with remaining dataclass fields
        for cls_field in fields(cls):
            if cls_field.name not in cls_kwargs and cls_field.name in json:
                cls_kwargs[cls_field.name] = json[cls_field.name]

        return cls(**cls_kwargs)


@dataclass(kw_only=False)
class User(BaseTowerModel):
    """Nextflow Tower user."""

    id: int
    username: str
    email: str

    _key_mapping = {"username": "userName"}


@dataclass(kw_only=False)
class Organization(BaseTowerModel):
    """Nextflow Tower organization."""

    id: int
    name: str

    _key_mapping = {"id": "orgId", "name": "orgName"}


@dataclass(kw_only=False)
class Workspace(BaseTowerModel):
    """Nextflow Tower workspace."""

    id: int
    name: str
    org: Organization

    _key_mapping = {"id": "workspaceId", "name": "workspaceName"}

    @property
    def full_name(self) -> str:
        """Fully-qualified workspace name (with organization name)."""
        return f"{self.org.name}/{self.name}".lower()

    @classmethod
    def from_json(cls, json: dict[str, Any], **kwargs: Any) -> Self:
        """Create instance from API JSON response.

        Args:
            json: API JSON response.
            **kwargs: Special values.

        Returns:
            Class instance.
        """
        org = Organization.from_json(json)
        return super().from_json(json, org=org, **kwargs)


@dataclass(kw_only=False)
class LaunchInfo(BaseTowerModel):
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
    resume: bool = False
    session_id: Optional[str] = None

    @root_validator()
    def check_resume_and_session_id(cls, values: dict[str, Any]):
        """Make sure that resume and session_id are in sync.

        Args:
            values: Dictionary of attributes.

        Raises:
            ValueError: If resume is enabled and a session ID
                is not provided.

        Returns:
            Unmodified dictionary of attributes.
        """
        if values["resume"] and values["session_id"] is None:
            message = "Resume can only be enabled with a session ID."
            raise ValueError(message)
        return values

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
        updated_values = dedup(updated_values)
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

    def to_json(self) -> dict[str, Any]:
        """Generate JSON representation of a launch specification.

        Returns:
            JSON representation.
        """
        launch = {
            "computeEnvId": self.get("compute_env_id"),
            "configProfiles": dedup(self.profiles),
            "configText": self.nextflow_config,
            "dateCreated": None,
            "entryName": None,
            "headJobCpus": None,
            "headJobMemoryMb": None,
            "id": None,
            "labelIds": dedup(self.label_ids),
            "mainScript": None,
            "optimizationId": None,
            "paramsText": json_module.dumps(self.params),
            "pipeline": self.get("pipeline"),
            "postRunScript": None,
            "preRunScript": self.pre_run_script,
            "pullLatest": False,
            "revision": self.revision,
            "runName": self.run_name,
            "schemaName": None,
            "stubRun": False,
            "towerConfig": None,
            "userSecrets": dedup(self.user_secrets),
            "workDir": self.get("work_dir"),
            "workspaceSecrets": dedup(self.workspace_secrets),
        }
        if self.resume:
            launch["resume"] = self.resume
            launch["sessionId"] = self.get("session_id")
        return {"launch": launch}


@dataclass(kw_only=False)
class Label(BaseTowerModel):
    """Nextflow Tower workflow run label."""

    id: int
    name: str
    value: Optional[str]
    resource: bool


@dataclass(kw_only=False)
class ComputeEnvSummary(BaseTowerModel):
    """Nextflow Tower compute environment summary."""

    id: str
    name: str
    status: str
    work_dir: str

    _key_mapping = {"work_dir": "workDir"}


@dataclass(kw_only=False)
class ComputeEnv(ComputeEnvSummary):
    """Nextflow Tower compute environment details."""

    date_created: datetime
    pre_run_script: str
    labels: list[Label]

    _key_mapping = {
        "date_created": "dateCreated",
        "work_dir": "config.workDir",
        "pre_run_script": "config.preRunScript",
    }

    @classmethod
    def from_json(cls, json: dict[str, Any], **kwargs: Any) -> Self:
        """Create instance from API JSON response.

        Args:
            json: API JSON response.
            **kwargs: Special values.

        Returns:
            Class instance.
        """
        labels = [Label.from_json(label) for label in json["labels"]]
        return super().from_json(json, labels=labels, **kwargs)


@dataclass(kw_only=False)
class Workflow(BaseTowerModel):
    """Nextflow Tower workflow run details."""

    id: str
    complete: Optional[datetime]
    run_name: str
    session_id: str
    username: str
    projectName: str
    status: WorkflowStatus

    _key_mapping = {
        "run_name": "runName",
        "session_id": "sessionId",
        "username": "userName",
        "project_name": "projectName",
    }
