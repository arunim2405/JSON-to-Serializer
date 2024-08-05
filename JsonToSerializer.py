import json
from collections import OrderedDict


def get_field_type(value):
    if isinstance(value, int):
        return "IntegerField()"
    elif isinstance(value, float):
        return "FloatField()"
    elif isinstance(value, bool):
        return "BooleanField()"
    elif isinstance(value, str):
        return "CharField()"
    elif isinstance(value, list):
        if value and isinstance(value[0], dict):
            return "ListField(child=serializers.DictField())"
        elif value and isinstance(value[0], int):
            return "ListField(child=serializers.IntegerField())"
        elif value and isinstance(value[0], float):
            return "ListField(child=serializers.FloatField())"
        elif value and isinstance(value[0], bool):
            return "ListField(child=serializers.BooleanField())"
        elif value and isinstance(value[0], str):
            return "ListField(child=serializers.CharField())"
        else:
            return "ListField()"
    elif isinstance(value, dict):
        return "DictField()"
    else:
        return "CharField()"


def generate_serializer_fields(data, indent=4):
    fields = OrderedDict()
    for key, value in data.items():
        if isinstance(value, dict):
            fields[key] = generate_serializer_fields(value, indent + 4)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            fields[key] = [generate_serializer_fields(value[0], indent + 4)]
        else:
            fields[key] = get_field_type(value)
    return fields


def extend_nested_class(key, value, nested_class_name, code):
    # no need to use DictField, we can just set the nested serializer as the value
    if isinstance(value, OrderedDict):
        code.append(f"{' ' * 4}{key} = {nested_class_name}()")
    # Handles cases where the value is a list of dicts like msg in Workflows ListAll
    elif isinstance(value, list):
        code.append(f"{' ' * 4}{key} = serializers.ListField(child={nested_class_name}())")
        code.extend(serializer_code(value[0], nested_class_name))
        return
    code.extend(serializer_code(value, nested_class_name))


def serializer_code(fields, class_name="GeneratedSerializer"):
    code = [f"class {class_name}(serializers.Serializer):"]
    nested_code_to_append = []
    for key, value in fields.items():
        if isinstance(value, OrderedDict):
            if len(value) == 0:
                code.append(f"{' ' * 4}{key} = serializers.DictField()")
            else:
                # Prepend the class name with the key name to avoid duplicate class names
                # In some cases the names get quite long depending on the depth but they are unique
                nested_class_name = class_name[:-10] + key.capitalize() + "Serializer"
                nested_code_to_append.append({"key": key, "value": value, "nested_class_name": nested_class_name})
            # code.append(f"{' ' * 4}{key} = serializers.DictField(child={nested_class_name}())")
            # code.extend(serializer_code(value, nested_class_name))
        elif isinstance(value, list) and value and isinstance(value[0], OrderedDict):
            nested_class_name = class_name[:-10] + key.capitalize() + "Serializer"
            nested_code_to_append.append({"key": key, "value": value, "nested_class_name": nested_class_name})
            # code.append(f"{' ' * 4}{key} = serializers.ListField(child={nested_class_name}())")
            # code.extend(serializer_code(value[0], nested_class_name))
        else:
            code.append(f"{' ' * 4}{key} = serializers.{value}")
    for nested_code in nested_code_to_append:
        extend_nested_class(**nested_code, code=code)
    return code

#reverse_classes is used to reverse the order of the classes in the generated serializer
#This is needed so that the classes that are referenced are defined before they are used
def reverse_classes(code_lines):
    class_blocks = []
    current_class = []
    inside_class = False

    for line in code_lines:
        if line.startswith('class '):
            if current_class:
                class_blocks.append(current_class)
            current_class = [line]
            inside_class = True
        elif inside_class:
            current_class.append(line)
    
    if current_class:
        class_blocks.append(current_class)

    reversed_class_blocks = class_blocks[::-1]

    reversed_code_lines = [line for block in reversed_class_blocks for line in block]
    return reversed_code_lines

def generate_serializer(json_data, root_class_name):
    data = json.loads(json_data)
    fields = generate_serializer_fields(data)
    code_lines = reverse_classes(serializer_code(fields, class_name=root_class_name))
    return "\n".join(code_lines)


# Example usage:
#Workflows Get
json_data = """
{
  "msg": {
    "SGInternals": {
      "resolvedVCSconfig": {
        "repo_url": "https://x-access-token:None@github.com/stackguardian/template-tf-aws-s3-demo-website",
        "repo_name": "template-tf-aws-s3-demo-website",
        "sparse_path": null,
        "repo_ref": "main",
        "repo_local_path": "/var/tmp/workspace/orgs/sg-provider-test/wfgrps/TPS-Test/wfs/aws-s3-demo-website-BGGY/shared-workspace/user/template-tf-aws-s3-demo-website",
        "workingDir": ""
      }
    },
    "LatestStatus": "COMPLETED",
    "LatestStatusKey": "on_1_apply-terraform-plan",
    "IsArchive": "0",
    "Comments": {
      "1722437675457": {
        "createdBy": "taher.kathanawala@stackguardian.io",
        "comment": "Workflow Run initiated"
      }
    },
    "ResumedWorkflowRun": false,
    "ResourceId": "/wfruns/o57svbi8gohj",
    "ModifiedAt": 1722437758940.0,
    "ParentId": "/orgs/sg-provider-test/wfgrps/TPS-Test/wfs/aws-s3-demo-website-BGGY",
    "ResourceType": "WORKFLOW_RUN",
    "RuntimeParameters": {
      "userJobMemory": 1024.0,
      "vcsTriggers": {},
      "tfDriftIacInputData": {},
      "deploymentPlatformConfigProcessed": {
        "config": [
          {
            "awsDefaultRegion": "eu-central-1",
            "awsAccessKeyId": "xxx",
            "awsSecretAccessKey": "xx+x+x"
          }
        ],
        "kind": "AWS_STATIC"
      },
      "iacTemplate": {
        "/stackguardian/aws-s3-demo-website:16": {
          "RuntimeSource": {
            "sourceConfigDestKind": "GITHUB_COM",
            "config": {
              "includeSubModule": false,
              "ref": "main",
              "isPrivate": false,
              "workingDir": "",
              "repo": "https://github.com/stackguardian/template-tf-aws-s3-demo-website"
            }
          },
          "IsArchive": "0",
          "IsActive": "1",
          "IsPublic": "1",
          "CreatedAt": 1696247453148.0,
          "TemplateName": "aws-s3-demo-website",
          "OwnerOrg": "/orgs/stackguardian",
          "TemplateType": "IAC",
          "TemplateId": "/stackguardian/aws-s3-demo-website:16",
          "SourceConfigKind": "TERRAFORM"
        }
      },
      "approvers": [],
      "userJobCpu": 512.0,
      "wfStepsConfig": [
        {
          "name": "generate-terraform-plan",
          "mountPoints": null,
          "wfStepTemplateId": "/stackguardian/terraform:19",
          "wfStepInputData": {
            "schemaType": "FORM_JSONSCHEMA",
            "data": {
              "terraformVersion": "1.5.7",
              "managedTerraformState": true,
              "terraformPlanOptions": "",
              "terraformAction": "plan",
              "applyPolicy": true
            }
          },
          "timeout": 2100.0,
          "approval": false
        },
        {
          "name": "apply-terraform-plan",
          "mountPoints": null,
          "wfStepTemplateId": "/stackguardian/terraform:19",
          "wfStepInputData": {
            "schemaType": "FORM_JSONSCHEMA",
            "data": {
              "terraformVersion": "1.5.7",
              "terraformAction": "apply",
              "applyPolicy": true,
              "terraformApplyOptions": ""
            }
          },
          "timeout": 2100.0,
          "approval": false
        }
      ],
      "cacheConfig": {
        "path": [
          "user/repo/.terraform",
          "user/repo/tf_plan.out"
        ],
        "enabled": true,
        "key": "tf_cache",
        "policy": "PULL_PUSH"
      },
      "miniSteps": {
        "webhooks": {
          "COMPLETED": [],
          "DRIFT_DETECTED": [],
          "ERRORED": []
        },
        "notifications": {
          "email": {
            "APPROVAL_REQUIRED": [],
            "CANCELLED": [],
            "COMPLETED": [],
            "ERRORED": []
          }
        },
        "wfChaining": {
          "COMPLETED": [],
          "ERRORED": []
        }
      },
      "runnerConstraints": {
        "selectors": [
          "shared"
        ],
        "type": "shared",
        "sharedType": "shared-ec2"
      },
      "terraformAction": {
        "action": "apply"
      },
      "runTaskDetails": [
        {
          "enableExecuteCommand": false,
          "attachments": [],
          "memory": "2048",
          "startedBy": "/orgs/sg-provider-test/wfruns/o57svbi8gohj",
          "taskArn": "arn:aws:ecs:eu-central-1:476299211833:task/admin-workflow-prod/e12e436e21b94612968aba4bb2b73929",
          "cpu": "1024",
          "overrides": {
            "inferenceAcceleratorOverrides": [],
            "containerOverrides": [
              {
                "name": "admin",
                "environmentFiles": [
                  {
                    "type": "s3",
                    "value": "arn:aws:s3:::stack-guardian-orchestrator-resources-prod/orgs/sg-provider-test/wfgrps/TPS-Test/wfs/aws-s3-demo-website-BGGY/sg.admin.env"
                  }
                ],
                "environment": [
                  {
                    "name": "RUNTIME_TYPE",
                    "value": "EC2"
                  }
                ]
              }
            ]
          },
          "availabilityZone": "eu-central-1b",
          "version": 1.0,
          "tags": [
            {
              "value": "/wfgrps/TPS-Test",
              "key": "wfGrpId"
            },
            {
              "value": "",
              "key": "stackId"
            },
            {
              "value": "/wfruns/o57svbi8gohj",
              "key": "wfRunId"
            },
            {
              "value": "prod",
              "key": "Resource-Type"
            },
            {
              "value": "/wfs/aws-s3-demo-website-BGGY",
              "key": "wfId"
            },
            {
              "value": "/orgs/sg-provider-test",
              "key": "orgId"
            },
            {
              "value": "admin-workflow-prod",
              "key": "aws:ecs:clusterName"
            }
          ],
          "createdAt": "2024-07-31 14:54:38.911000+00:00",
          "clusterArn": "arn:aws:ecs:eu-central-1:476299211833:cluster/admin-workflow-prod",
          "taskDefinitionArn": "arn:aws:ecs:eu-central-1:476299211833:task-definition/workflow-engine-admin-prod:244",
          "attributes": [
            {
              "name": "ecs.cpu-architecture",
              "value": "x86_64"
            }
          ],
          "containers": [
            {
              "image": "476299211833.dkr.ecr.eu-central-1.amazonaws.com/workflow-engine/admin:latest",
              "networkInterfaces": [],
              "taskArn": "arn:aws:ecs:eu-central-1:476299211833:task/admin-workflow-prod/e12e436e21b94612968aba4bb2b73929",
              "name": "admin",
              "cpu": "0",
              "containerArn": "arn:aws:ecs:eu-central-1:476299211833:container/admin-workflow-prod/e12e436e21b94612968aba4bb2b73929/5977b01c-2d1e-45a2-9370-20e25e218599",
              "lastStatus": "PENDING"
            }
          ],
          "containerInstanceArn": "arn:aws:ecs:eu-central-1:476299211833:container-instance/admin-workflow-prod/e4722726041d4cf088d8f3ac7b83c56e",
          "desiredStatus": "RUNNING",
          "lastStatus": "PENDING",
          "group": "family:workflow-engine-admin-prod",
          "launchType": "EC2"
        }
      ],
      "environmentVariables": [],
      "numberOfApprovalsRequired": 0.0,
      "deploymentPlatformConfig": [
        {
          "config": {
            "profileName": "sg-nonprod-1",
            "integrationId": "/integrations/sg-nonprod-1"
          },
          "kind": "AWS_STATIC"
        }
      ],
      "workflowStepsTemplates": {
        "/stackguardian/terraform:19": {
          "SharedOrgs": {
            "/orgs/adorsys-test": {},
            "/orgs/siemens-di": {},
            "/orgs/wicked-hop": {}
          },
          "RuntimeSource": {
            "sourceConfigDestKind": "CONTAINER_REGISTRY",
            "config": {
              "dockerImage": "476299211833.dkr.ecr.eu-central-1.amazonaws.com/workflow-steps/iac-terraform:1719332246-v3.2.5-terraform",
              "isPrivate": false
            }
          },
          "IsArchive": "0",
          "IsActive": "1",
          "IsPublic": "1",
          "CreatedAt": 1679583161499.0,
          "TemplateName": "terraform",
          "OwnerOrg": "/orgs/stackguardian",
          "TemplateType": "WORKFLOW_STEP",
          "TemplateId": "/stackguardian/terraform:19",
          "SourceConfigKind": "DOCKER_IMAGE"
        }
      },
      "iacPoliciesTemplates": {},
      "vcsConfig": {
        "iacVCSConfig": {
          "iacTemplateId": "/stackguardian/aws-s3-demo-website:16",
          "useMarketplaceTemplate": true
        },
        "iacInputData": {
          "schemaType": "FORM_JSONSCHEMA",
          "data": {
            "bucket_region": "eu-central-1"
          }
        }
      },
      "tfDriftWfRun": false,
      "enforcedPoliciesRaw": [],
      "terraformConfig": {
        "terraformVersion": "1.5.7",
        "preApplyWfStepsConfig": [],
        "managedTerraformState": true,
        "postApplyWfStepsConfig": [],
        "driftCheck": true,
        "prePlanWfStepsConfig": []
      },
      "wfType": "TERRAFORM"
    },
    "TriggerDetails": {},
    "DocVersion": "V3.BETA",
    "Authors": [
      "taher.kathanawala@stackguardian.io"
    ],
    "ResourceName": "o57svbi8gohj",
    "Statuses": {
      "on_0_generate-terraform-plan": [
        {
          "name": "PENDING",
          "createdAt": 1722437688754.0
        },
        {
          "name": "RUNNING",
          "createdAt": 1722437694746.0
        }
      ],
      "on_1_apply-terraform-plan": [
        {
          "name": "PENDING",
          "createdAt": 1722437725241.0
        },
        {
          "name": "RUNNING",
          "createdAt": 1722437731249.0
        },
        {
          "name": "COMPLETED",
          "createdAt": 1722437758940.0
        }
      ],
      "pre_0_step": [
        {
          "name": "QUEUED",
          "createdAt": 1722437675457.0
        },
        {
          "name": "PENDING",
          "createdAt": 1722437677940.0
        }
      ]
    },
    "SubResourceId": "/wfgrps/TPS-Test/wfs/aws-s3-demo-website-BGGY/wfruns/o57svbi8gohj",
    "OrgId": "/orgs/sg-provider-test",
    "CreatedAt": 1722437675457.0
  }
}
"""

serializer_str = generate_serializer(json_data, root_class_name="GeneratedSerializer")
print(serializer_str)