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


# The following list of workflows includes a standalone workflow and a
# pair of workflows, one having been relaunched from the other.
# Some long fields (params, configText, stats) have been truncated.
list_workflows = {
    "workflows": [
        {
            "workflow": {
                "id": "4qqHV",
                "ownerId": 2,
                "submit": "2023-05-03T17:12:28Z",
                "start": "2023-05-03T17:19:40Z",
                "complete": None,
                "dateCreated": "2023-05-03T17:12:28Z",
                "lastUpdated": "2023-05-03T17:19:40Z",
                "runName": "hungry_cori_2",
                "sessionId": "18f304ea",
                "profile": "test",
                "workDir": "s3://orca-service-test-project-tower-scratch/work",
                "commitId": "5671b65af97fe78a2f9b4d05d850304918b1b86e",
                "userName": "bgrande",
                "scriptId": "f421d",
                "revision": "3.11.2",
                "commandLine": "nextflow run nf-core/rnaseq -name hungry_cori_2 ...",
                "projectName": "nf-core/rnaseq",
                "scriptName": "main.nf",
                "launchId": "weG6r",
                "status": "RUNNING",
                "configFiles": [
                    "/.nextflow/assets/nf-core/rnaseq/nextflow.config",
                    "/nextflow.config",
                ],
                "params": {"outdir": "foo"},
                "configText": "foo",
                "manifest": {
                    "nextflowVersion": "!>=22.10.1",
                    "defaultBranch": "master",
                    "version": "3.11.2",
                    "homePage": "https://github.com/nf-core/rnaseq",
                    "gitmodules": None,
                    "description": "RNA sequencing analysis pipeline for ...",
                    "name": "nf-core/rnaseq",
                    "mainScript": "main.nf",
                    "author": "Harshil Patel, Phil Ewels, Rickard Hammarén",
                },
                "nextflow": {
                    "version": "22.10.6",
                    "build": "5843",
                    "timestamp": "2023-01-23T23:20:00Z",
                },
                "stats": None,
                "errorMessage": None,
                "errorReport": None,
                "deleted": None,
                "peakLoadCpus": None,
                "peakLoadTasks": None,
                "peakLoadMemory": None,
                "projectDir": "/.nextflow/assets/nf-core/rnaseq",
                "homeDir": "/root",
                "container": "",
                "repository": "https://github.com/nf-core/rnaseq",
                "containerEngine": None,
                "scriptFile": "/.nextflow/assets/nf-core/rnaseq/main.nf",
                "launchDir": "/",
                "duration": None,
                "exitStatus": None,
                "resume": True,
                "success": None,
            },
            "progress": None,
            "orgId": 23810,
            "orgName": "Sage-Bionetworks",
            "workspaceId": 17703,
            "workspaceName": "orca-service-test-project",
            "labels": None,
            "starred": False,
            "optimized": None,
        },
        {
            "workflow": {
                "id": "1QYjg",
                "ownerId": 28,
                "submit": "2023-05-02T16:31:16Z",
                "start": "2023-05-02T16:40:32Z",
                "complete": "2023-05-02T17:11:56Z",
                "dateCreated": "2023-05-02T16:31:16Z",
                "lastUpdated": "2023-05-02T17:11:58Z",
                "runName": "hungry_cori",
                "sessionId": "18f304ea",
                "profile": "test",
                "workDir": "s3://orca-service-test-project-tower-scratch/work",
                "commitId": "5671b",
                "userName": "orca-service-account",
                "scriptId": "f421d",
                "revision": "3.11.2",
                "commandLine": "nextflow run nf-core/rnaseq ...",
                "projectName": "nf-core/rnaseq",
                "scriptName": "main.nf",
                "launchId": "5q0uw",
                "status": "SUCCEEDED",
                "configFiles": [
                    "/.nextflow/assets/nf-core/rnaseq/nextflow.config",
                    "/nextflow.config",
                ],
                "params": {"outdir": "foo"},
                "configText": "foo",
                "manifest": {
                    "nextflowVersion": "!>=22.10.1",
                    "defaultBranch": "master",
                    "version": "3.11.2",
                    "homePage": "https://github.com/nf-core/rnaseq",
                    "gitmodules": None,
                    "description": "RNA sequencing analysis pipeline ...",
                    "name": "nf-core/rnaseq",
                    "mainScript": "main.nf",
                    "author": "Harshil Patel, Phil Ewels, Rickard Hammarén",
                },
                "nextflow": {
                    "version": "22.10.6",
                    "build": "5843",
                    "timestamp": "2023-01-23T23:20:00Z",
                },
                "stats": {},
                "errorMessage": None,
                "errorReport": None,
                "deleted": None,
                "peakLoadCpus": None,
                "peakLoadTasks": None,
                "peakLoadMemory": None,
                "projectDir": "/.nextflow/assets/nf-core/rnaseq",
                "homeDir": "/root",
                "container": "",
                "repository": "https://github.com/nf-core/rnaseq",
                "containerEngine": None,
                "scriptFile": "/.nextflow/assets/nf-core/rnaseq/main.nf",
                "launchDir": "/",
                "duration": 1895231,
                "exitStatus": 0,
                "resume": False,
                "success": True,
            },
            "progress": None,
            "orgId": 23810,
            "orgName": "Sage-Bionetworks",
            "workspaceId": 17703,
            "workspaceName": "orca-service-test-project",
            "labels": None,
            "starred": False,
            "optimized": None,
        },
        {
            "workflow": {
                "id": "3a6Fn",
                "ownerId": 28,
                "submit": "2023-05-01T18:38:10Z",
                "start": "2023-05-01T18:46:03Z",
                "complete": "2023-05-01T19:16:08Z",
                "dateCreated": "2023-05-01T18:38:10Z",
                "lastUpdated": "2023-05-01T19:16:10Z",
                "runName": "boring_curie",
                "sessionId": "2d729ac7",
                "profile": "test",
                "workDir": "s3://orca-service-test-project-tower-scratch/work",
                "commitId": "5671b",
                "userName": "orca-service-account",
                "scriptId": "f421d",
                "revision": "3.11.2",
                "commandLine": "nextflow run nf-core/rnaseq -name boring_curie ...",
                "projectName": "nf-core/rnaseq",
                "scriptName": "main.nf",
                "launchId": "2ZAjK",
                "status": "SUCCEEDED",
                "configFiles": [
                    "/.nextflow/assets/nf-core/rnaseq/nextflow.config",
                    "/nextflow.config",
                ],
                "params": {"outdir": "foo"},
                "configText": "foo",
                "manifest": {
                    "nextflowVersion": "!>=22.10.1",
                    "defaultBranch": "master",
                    "version": "3.11.2",
                    "homePage": "https://github.com/nf-core/rnaseq",
                    "gitmodules": None,
                    "description": "RNA sequencing analysis pipeline for ...",
                    "name": "nf-core/rnaseq",
                    "mainScript": "main.nf",
                    "author": "Harshil Patel, Phil Ewels, Rickard Hammarén",
                },
                "nextflow": {
                    "version": "22.10.6",
                    "build": "5843",
                    "timestamp": "2023-01-23T23:20:00Z",
                },
                "stats": {},
                "errorMessage": None,
                "errorReport": None,
                "deleted": None,
                "peakLoadCpus": None,
                "peakLoadTasks": None,
                "peakLoadMemory": None,
                "projectDir": "/.nextflow/assets/nf-core/rnaseq",
                "homeDir": "/root",
                "container": "",
                "repository": "https://github.com/nf-core/rnaseq",
                "containerEngine": None,
                "scriptFile": "/.nextflow/assets/nf-core/rnaseq/main.nf",
                "launchDir": "/",
                "duration": 1816350,
                "exitStatus": 0,
                "resume": False,
                "success": True,
            },
            "progress": None,
            "orgId": 23810,
            "orgName": "Sage-Bionetworks",
            "workspaceId": 17703,
            "workspaceName": "orca-service-test-project",
            "labels": None,
            "starred": False,
            "optimized": None,
        },
    ],
    "totalSize": 3,
}

get_workflow_tasks = {
    "tasks": [
        {
            "task": {
                "id": 4638140,
                "taskId": 1,
                "status": "COMPLETED",
                "dateCreated": "2023-10-16T21:04:14Z",
                "lastUpdated": "2023-10-16T21:07:27Z",
                "name": "sayHello (1)",
                "module": [],
                "queue": "TowerForge-5im9knMLfGTl9qrPNcDk0t-work",
                "memory": None,
                "script": "\necho 'Bonjour world!'\n",
                "tag": None,
                "time": None,
                "executor": "awsbatch",
                "duration": 178310,
                "start": "2023-10-16T21:07:03Z",
                "container": "wave.seqera.io/wt/35bcf310401b/nextflow/bash:latest",
                "process": "sayHello",
                "attempt": 1,
                "scratch": None,
                "workdir": "s3://example-bucket/work/53/d1a4bedd867b9b005c1e86291334cf",
                "disk": None,
                "cloudZone": "us-east-1d",
                "priceModel": "spot",
                "cost": 0.0000576389,
                "errorAction": None,
                "realtime": 2,
                "nativeId": "1ffe9499-1566-4140-b652-cb930413cf77",
                "pcpu": 66.7,
                "pmem": 0.0,
                "rss": 0,
                "vmem": 0,
                "peakRss": 0,
                "peakVmem": 0,
                "rchar": 54098,
                "wchar": 199,
                "syscr": 147,
                "syscw": 13,
                "readBytes": 352256,
                "writeBytes": 0,
                "volCtxt": 0,
                "invCtxt": 0,
                "env": None,
                "submit": "2023-10-16T21:04:15Z",
                "exitStatus": 0,
                "complete": "2023-10-16T21:07:13Z",
                "cpus": 1,
                "machineType": "c6i.2xlarge",
                "hash": "53/d1a4be",
                "exit": "0",
            }
        },
        {
            "task": {
                "id": 4638141,
                "taskId": 2,
                "status": "COMPLETED",
                "dateCreated": "2023-10-16T21:04:14Z",
                "lastUpdated": "2023-10-16T21:07:27Z",
                "name": "sayHello (2)",
                "module": [],
                "queue": "TowerForge-5im9knMLfGTl9qrPNcDk0t-work",
                "memory": None,
                "script": "\necho 'Ciao world!'\n",
                "tag": None,
                "time": None,
                "executor": "awsbatch",
                "duration": 178068,
                "start": "2023-10-16T21:07:03Z",
                "container": "wave.seqera.io/wt/35bcf310401b/nextflow/bash:latest",
                "process": "sayHello",
                "attempt": 1,
                "scratch": None,
                "workdir": "s3://example-bucket/work/8b/96b02f951f46594c6d6f310e77abc7",
                "disk": None,
                "cloudZone": "us-east-1d",
                "priceModel": "spot",
                "cost": 0.0000634028,
                "errorAction": None,
                "realtime": 3,
                "nativeId": "aa5d92fe-c2f1-4879-a768-dbc6b1c6a277",
                "pcpu": 53.3,
                "pmem": 0.0,
                "rss": 0,
                "vmem": 0,
                "peakRss": 0,
                "peakVmem": 0,
                "rchar": 54092,
                "wchar": 196,
                "syscr": 147,
                "syscw": 13,
                "readBytes": 352256,
                "writeBytes": 0,
                "volCtxt": 0,
                "invCtxt": 0,
                "env": None,
                "submit": "2023-10-16T21:04:15Z",
                "exitStatus": 0,
                "complete": "2023-10-16T21:07:13Z",
                "cpus": 1,
                "machineType": "c6i.2xlarge",
                "hash": "8b/96b02f",
                "exit": "0",
            }
        },
        {
            "task": {
                "id": 4638142,
                "taskId": 3,
                "status": "COMPLETED",
                "dateCreated": "2023-10-16T21:04:14Z",
                "lastUpdated": "2023-10-16T21:07:27Z",
                "name": "sayHello (3)",
                "module": [],
                "queue": "TowerForge-5im9knMLfGTl9qrPNcDk0t-work",
                "memory": None,
                "script": "\necho 'Hello world!'\n",
                "tag": None,
                "time": None,
                "executor": "awsbatch",
                "duration": 177940,
                "start": "2023-10-16T21:07:13Z",
                "container": "wave.seqera.io/wt/35bcf310401b/nextflow/bash:latest",
                "process": "sayHello",
                "attempt": 1,
                "scratch": None,
                "workdir": "s3://example-bucket/work/0f/929495d8a0f66c9e85a4c4f0820a54",
                "disk": None,
                "cloudZone": "us-east-1d",
                "priceModel": "spot",
                "cost": 0.0000057639,
                "errorAction": None,
                "realtime": 3,
                "nativeId": "7696237a-8cc1-42cb-847a-a352fdbdfcff",
                "pcpu": 53.3,
                "pmem": 0.0,
                "rss": 0,
                "vmem": 0,
                "peakRss": 0,
                "peakVmem": 0,
                "rchar": 54094,
                "wchar": 197,
                "syscr": 147,
                "syscw": 13,
                "readBytes": 352256,
                "writeBytes": 0,
                "volCtxt": 0,
                "invCtxt": 0,
                "env": None,
                "submit": "2023-10-16T21:04:15Z",
                "exitStatus": 0,
                "complete": "2023-10-16T21:07:13Z",
                "cpus": 1,
                "machineType": "c6i.2xlarge",
                "hash": "0f/929495",
                "exit": "0",
            }
        },
        {
            "task": {
                "id": 4638143,
                "taskId": 4,
                "status": "COMPLETED",
                "dateCreated": "2023-10-16T21:04:14Z",
                "lastUpdated": "2023-10-16T21:07:27Z",
                "name": "sayHello (4)",
                "module": [],
                "queue": "TowerForge-5im9knMLfGTl9qrPNcDk0t-work",
                "memory": None,
                "script": "\necho 'Hola world!'\n",
                "tag": None,
                "time": None,
                "executor": "awsbatch",
                "duration": 178217,
                "start": "2023-10-16T21:07:03Z",
                "container": "wave.seqera.io/wt/35bcf310401b/nextflow/bash:latest",
                "process": "sayHello",
                "attempt": 1,
                "scratch": None,
                "workdir": "s3://example-bucket/work/de/3458310872e3784b889a5b7abe823e",
                "disk": None,
                "cloudZone": "us-east-1d",
                "priceModel": "spot",
                "cost": 0.0000576389,
                "errorAction": None,
                "realtime": 3,
                "nativeId": "fecc5768-5d45-479e-8f37-89e17a32d216",
                "pcpu": 72.7,
                "pmem": 0.0,
                "rss": 0,
                "vmem": 0,
                "peakRss": 0,
                "peakVmem": 0,
                "rchar": 54093,
                "wchar": 196,
                "syscr": 147,
                "syscw": 13,
                "readBytes": 352256,
                "writeBytes": 0,
                "volCtxt": 0,
                "invCtxt": 0,
                "env": None,
                "submit": "2023-10-16T21:04:15Z",
                "exitStatus": 0,
                "complete": "2023-10-16T21:07:13Z",
                "cpus": 1,
                "machineType": "c6i.2xlarge",
                "hash": "de/345831",
                "exit": "0",
            }
        },
    ],
    "total": 4,
}

get_task_logs = {
    "log": {
        "entries": ["Ciao world!"],
        "rewindToken": None,
        "forwardToken": None,
        "pending": False,
        "message": None,
        "downloads": [
            {
                "fileName": ".command.out",
                "displayText": "Task stdout",
                "saveName": "task-2.command.out.txt",
            },
            {
                "fileName": ".command.err",
                "displayText": "Task stderr",
                "saveName": "task-2.command.err.txt",
            },
            {
                "fileName": ".command.log",
                "displayText": "Task log file",
                "saveName": "task-2.command.log.txt",
            },
        ],
        "truncated": False,
    }
}
