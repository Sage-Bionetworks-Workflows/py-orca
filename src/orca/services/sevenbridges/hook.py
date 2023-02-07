"""Airflow hook for SevenBridges.

This hook was inspired by the Asana Airflow provider package:
https://github.com/apache/airflow/blob/main/airflow/providers/asana/hooks/asana.py
"""

from functools import cached_property, partial
from typing import TYPE_CHECKING, Any

from airflow.hooks.base import BaseHook
from sevenbridges import Api

from orca.services.sevenbridges.client import init_client
from orca.services.sevenbridges.tasks import SevenBridgesTasks

__all__ = ["SevenBridgesHook"]


class SevenBridgesHook(BaseHook):
    """Wrapper around SevenBridges client."""

    conn_name_attr = "sbg_conn_id"
    default_conn_name = "sbg_default"
    conn_type = "sbg"
    hook_name = "SevenBridges"

    def __init__(self, conn_id: str = default_conn_name, *args, **kwargs):
        """Construct SevenBridgesHook using an Airflow connection.

        Args:
            conn_id: An Airflow connection ID.
                Defaults to ``default_conn_name``.
        """
        super().__init__(*args, **kwargs)
        self.connection = self.get_connection(conn_id)
        extras = self.connection.extra_dejson
        self.project = extras.get("project")

    def get_conn(self) -> Api:
        """Retrieve authenticated SevenBridges client."""
        return self.client

    @cached_property
    def client(self) -> Api:
        """Retrieve authenticated SevenBridges client."""
        api_endpoint = str(self.connection.host)
        auth_token = str(self.connection.password)
        return init_client(api_endpoint, auth_token)

    @cached_property
    def tasks(self) -> SevenBridgesTasks:
        """Retrieve authenticated SevenBridgesTasks instance."""
        return SevenBridgesTasks(self.client, self.project)

    @staticmethod
    def get_connection_form_widgets() -> dict[str, Any]:
        """Customize SevenBridges connection form in Airflow UI."""
        from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
        from flask_babel import lazy_gettext
        from wtforms import StringField

        string_field = partial(StringField, widget=BS3TextFieldWidget())
        widgets = {"project": string_field(lazy_gettext("Project"))}
        return widgets

    @staticmethod
    def get_ui_field_behaviour() -> dict[str, Any]:
        """Customize SevenBridges connection fields in Airflow UI."""
        field_behaviour = {
            "hidden_fields": ["port", "login", "schema"],
            "relabeling": {
                "password": "Authentication token",
                "host": "API base endpoint",
                "project": "Project",
            },
            "placeholders": {
                "password": "Available under the Developer menu.",
                "host": "https://cavatica-api.sbgenomics.com/v2",
                "project": "<username>/<project-name>",
            },
        }
        return field_behaviour
