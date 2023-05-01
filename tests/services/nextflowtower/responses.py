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
        "id": 100,
        "userName": "foo",
        "email": "foo@example.com",
        "firstName": None,
        "lastName": None,
        "organization": "@Foo-Bar",
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


get_user_workspaces_and_orgs = {
    "orgsAndWorkspaces": [
        {
            "orgId": 123456789,
            "orgName": "Foo-Bar",
            "orgLogoUrl": None,
            "workspaceId": None,
            "workspaceName": None,
        },
        {
            "orgId": 123456789,
            "orgName": "Foo-Bar",
            "orgLogoUrl": None,
            "workspaceId": 54321,
            "workspaceName": "project-1",
        },
        {
            "orgId": 123456789,
            "orgName": "Foo-Bar",
            "orgLogoUrl": None,
            "workspaceId": 98765,
            "workspaceName": "project-2",
        },
    ]
}

get_workflow: dict = {
    "workflow": {
        "id": "123456789",
        "submit": "2023-04-28T16:22:31Z",
        "start": "2023-04-28T16:30:44Z",
        "complete": "2023-04-28T16:30:54Z",
        "dateCreated": "2023-04-28T16:22:31Z",
        "lastUpdated": "2023-04-28T16:30:54Z",
        "runName": "example-run",
        "sessionId": "abc-abc-abc-abc-abc",
        "profile": "standard",
        "workDir": "s3://example-bucket/work",
        "commitId": "123",
        "userName": "example-user",
        "scriptId": "123",
        "revision": None,
        "commandLine": "nextflow run nextflow-io/example-workflow\
              -name example-run -with-tower\
                'https://tower.sagebionetworks.org/api'\
                -r 123 -resume abc-abc-abc-abc-abc",
        "projectName": "nextflow-io/example-workflow",
        "scriptName": "main.nf",
        "launchId": "abc",
        "status": "SUCCEEDED",
        "configFiles": [
            "/.nextflow/assets/nextflow-io/example-workflow/nextflow.config",
            "/nextflow.config",
        ],
        "params": {},
        "configText": "example-config",
        "manifest": {
            "nextflowVersion": None,
            "defaultBranch": "master",
            "version": None,
            "homePage": None,
            "gitmodules": None,
            "description": None,
            "name": None,
            "mainScript": "main.nf",
            "author": None,
        },
        "nextflow": {
            "version": "22.10.6",
            "build": "5843",
            "timestamp": "2023-01-23T23:20:00Z",
        },
        "stats": {
            "computeTimeFmt": "(a few seconds)",
            "cachedCount": 4,
            "failedCount": 0,
            "ignoredCount": 0,
            "succeedCount": 0,
            "cachedCountFmt": "4",
            "succeedCountFmt": "0",
            "failedCountFmt": "0",
            "ignoredCountFmt": "0",
            "cachedPct": 100.0,
            "failedPct": 0.0,
            "succeedPct": 0.0,
            "ignoredPct": 0.0,
            "cachedDuration": 0,
            "failedDuration": 0,
            "succeedDuration": 0,
        },
        "errorMessage": None,
        "errorReport": None,
        "deleted": None,
        "peakLoadCpus": None,
        "peakLoadTasks": None,
        "peakLoadMemory": None,
        "projectDir": "/.nextflow/assets/nextflow-io/example-workflow",
        "homeDir": "/root",
        "container": "quay.io/nextflow/bash",
        "repository": "https://github.com/nextflow-io/example-workflow",
        "containerEngine": None,
        "scriptFile": "/.nextflow/assets/nextflow-io/example-workflow/main.nf",
        "launchDir": "/",
        "duration": 10508,
        "exitStatus": 0,
        "resume": True,
        "success": True,
        "logFile": None,
        "outFile": None,
        "operationId": None,
        "ownerId": 28,
    }
}
