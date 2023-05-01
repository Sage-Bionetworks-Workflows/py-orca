"""Example responses for different Tower endpoints.

To generate these, you can visit the OpenAPI page linked below and
make example requests after setting your authentication token at the
top of the page. You'll have to replace JSON literals ('None', 'False',
'True') with Python equivalents ('None', 'False', 'True'). Take care
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
            "orgId": 12345,
            "orgName": "Foo-Bar",
            "orgLogoUrl": None,
            "workspaceId": None,
            "workspaceName": None,
        },
        {
            "orgId": 12345,
            "orgName": "Foo-Bar",
            "orgLogoUrl": None,
            "workspaceId": 54321,
            "workspaceName": "project-1",
        },
        {
            "orgId": 12345,
            "orgName": "Foo-Bar",
            "orgLogoUrl": None,
            "workspaceId": 98765,
            "workspaceName": "project-2",
        },
    ]
}


create_label = {"id": 12345, "name": "foo", "value": None, "resource": False}


list_labels = {
    "labels": [
        {"id": 89366, "name": "CostCenter", "value": "12345", "resource": True},
        {"id": 10567, "name": "Department", "value": "IBC", "resource": True},
        {"id": 17863, "name": "launched-by-orca", "value": None, "resource": False},
        {"id": 97881, "name": "ORCA-163", "value": None, "resource": False},
        {"id": 18898, "name": "Project", "value": "Infrastructure", "resource": True},
    ],
    "totalSize": 5,
}


get_compute_env: dict = {
    "computeEnv": {
        "id": "5ykJF",
        "name": "orca-service-test-project-ondemand-v11",
        "description": None,
        "platform": "aws-batch",
        "config": {
            "region": "us-east-1",
            "computeQueue": "TowerForge-5ykJF",
            "dragenQueue": None,
            "computeJobRole": "foo",
            "executionRole": "foo",
            "headQueue": "TowerForge-5ykJF",
            "headJobRole": "foo",
            "cliPath": "/home/ec2-user/miniconda/bin/aws",
            "volumes": [],
            "workDir": "s3://orca-service-test-project-tower-scratch/work",
            "preRunScript": "NXF_OPTS='-Xms7g -Xmx14g'",
            "postRunScript": None,
            "headJobCpus": 8,
            "headJobMemoryMb": 15000,
            "environment": None,
            "waveEnabled": False,
            "fusion2Enabled": False,
            "nvnmeStorageEnabled": False,
            "logsGroup": None,
            "forge": {
                "type": "EC2",
                "minCpus": 0,
                "maxCpus": 1000,
                "gpuEnabled": False,
                "ebsAutoScale": True,
                "instanceTypes": [
                    "c5a.large",
                    "m6a.large",
                    "r6a.large",
                ],
                "allocStrategy": "BEST_FIT",
                "imageId": None,
                "vpcId": "vpc-100",
                "subnets": [
                    "subnet-1",
                    "subnet-2",
                    "subnet-3",
                    "subnet-4",
                ],
                "securityGroups": [],
                "fsxMount": None,
                "fsxName": None,
                "fsxSize": None,
                "disposeOnDeletion": True,
                "ec2KeyPair": None,
                "allowBuckets": [],
                "ebsBlockSize": 1000,
                "fusionEnabled": None,
                "bidPercentage": None,
                "efsCreate": False,
                "efsId": None,
                "efsMount": None,
                "dragenEnabled": None,
                "dragenAmiId": None,
                "ebsBootSize": 1000,
                "ecsConfig": "foo",
            },
            "forgedResources": [
                {"IamRole": "foo"},
                {"IamRole": "foo"},
                {"IamInstanceProfile": "foo"},
                {"Ec2LaunchTemplate": "TowerForge-5ykJF"},
                {"BatchEnv": "foo"},
                {"BatchQueue": "foo"},
            ],
            "discriminator": "aws-batch",
        },
        "dateCreated": "2023-04-26T00:49:49Z",
        "lastUpdated": "2023-04-26T00:50:17Z",
        "lastUsed": "2023-04-27T23:44:45Z",
        "deleted": None,
        "status": "AVAILABLE",
        "message": None,
        "primary": None,
        "credentialsId": "S2AIo",
        "orgId": 12345,
        "workspaceId": 98765,
        "labels": list_labels["labels"],
    }
}


list_compute_envs = {
    "computeEnvs": [
        {
            "id": "3QGDs",
            "name": "orca-service-test-project-spot-v11",
            "platform": "aws-batch",
            "status": "AVAILABLE",
            "message": None,
            "lastUsed": None,
            "primary": True,
            "workspaceName": "orca-service-test-project",
            "visibility": "PRIVATE",
            "workDir": "s3://orca-service-test-project-tower-scratch/work",
        },
        {
            "id": "5ykJF",
            "name": "orca-service-test-project-ondemand-v11",
            "platform": "aws-batch",
            "status": "AVAILABLE",
            "message": None,
            "lastUsed": "2023-04-27T23:44:45Z",
            "primary": None,
            "workspaceName": "orca-service-test-project",
            "visibility": "PRIVATE",
            "workDir": "s3://orca-service-test-project-tower-scratch/work",
        },
        {
            "id": "9W2l7",
            "name": "orca-service-test-project-ondemand-v10",
            "platform": "aws-batch",
            "status": "AVAILABLE",
            "message": None,
            "lastUsed": "2023-01-20T18:27:12Z",
            "primary": None,
            "workspaceName": "orca-service-test-project",
            "visibility": "PRIVATE",
            "workDir": "s3://orca-service-test-project-tower-scratch/work",
        },
    ]
}


launch_workflow = {"workflowId": "23LNH"}


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
