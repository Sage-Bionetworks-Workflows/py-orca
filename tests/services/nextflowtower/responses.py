"""Example responses for different Tower endpoints.

To generate these, you can visit the OpenAPI page linked below and
make example requests after setting your authentication token at the
top of the page. You'll have to replace JSON literals ('null', 'false',
'true') with Python equivalents ('None', 'False', 'True'). Take care
of redacting any values that shouldn't be public.

https://tower-dev.sagebionetworks.org/api/openapi
"""

get_user_info = {
    "user": {
        "id": 2,
        "userName": "bgrande",
        "email": "bruno.grande@sagebase.org",
        "firstName": None,
        "lastName": None,
        "organization": "@Sage-Bionetworks",
        "description": None,
        "avatar": "REDACTED",
        "trusted": True,
        "notification": True,
        "termsOfUseConsent": None,
        "marketingConsent": None,
        "options": {
            "githubToken": "REDACTED",
            "maxRuns": None,
            "hubspotId": None,
        },
        "lastAccess": "2023-02-24T20:11:50Z",
        "dateCreated": "2021-08-31T20:44:08Z",
        "lastUpdated": "2023-02-24T20:11:50Z",
        "deleted": False,
    },
    "needConsent": False,
    "defaultWorkspaceId": None,
}
