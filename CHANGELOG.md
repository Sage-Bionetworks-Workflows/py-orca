# Changelog

## Version 1.0.1

### Fixes

- Fix inconsistency between PyPI package name (py-orca) and Airflow provider package name (orca)

## Version 1.0.0

### New Features

- Add basic support for SevenBridges service (_i.e_ client factory, ops, and hook)
- Add the ability to draft, launch, and monitor SevenBridges tasks
- Register package as an Airflow provider

### Design Decisions

- The high-level structure for each service is described in `src/orca/services/__init__.py`.
- We have opted for Airflow-style connection URIs for passing credentials using environment variables.
  - The rationale is that these URIs can group related values such as an access token and the API base endpoint.
  - Otherwise, these values need to be provided in separate environment variables, which cause result in discordant values, such as an access token for the wrong API endpoint.
  - It's one less thing to learn and maintain since we'll need to use these URIs anyways for Airflow. It also means more code can be shared between services.
  - See `.env.example` for descriptions of how to build these URIs and examples.
- The Airflow hook doesn't include the `get_connection_form_widgets()` and `get_ui_field_behaviour()` static methods.
  - Although they were defined at first, we decided to remove them as we were writing tests because it didn't seem worth maintaining.
  - We plan on storing secrets using AWS SecretsManager, so we don't expect to be using the Connections UI for storing values.
  - We also want to purposely keep the hooks, which act as wrappers around the client and ops classes, as thin as possible to facilitate testing.
