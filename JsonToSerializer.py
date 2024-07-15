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
        "UserJobMemory": 1024.0,
        "UserJobCPU": 512.0,
        "NumberOfApprovalsRequired": 0.0,
        "RunnerConstraints": {
            "type": "shared"
        },
        "IsActive": "1",
        "Approvers": [],
        "Tags": [],
        "DeploymentPlatformConfig": [
            {
                "config": {
                    "profileName": "testAWSConnector",
                    "integrationId": "/integrations/testAWSConnector"
                },
                "kind": "AWS_RBAC"
            }
        ],
        "MiniSteps": {
            "webhooks": {
                "COMPLETED": [
                    {
                        "webhookName": "test",
                        "webhookSecret": "test",
                        "webhookUrl": "test"
                    }
                ],
                "DRIFT_DETECTED": [
                    {
                        "webhookName": "test",
                        "webhookSecret": "test",
                        "webhookUrl": "test"
                    }
                ],
                "ERRORED": [
                    {
                        "webhookName": "test",
                        "webhookSecret": "test",
                        "webhookUrl": "test"
                    }
                ]
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
        "Authors": [
            "larisoncarvalho@gmail.com"
        ],
        "WfStepsConfig": [],
        "ActivitySubscribers": [
            "larisoncarvalho@gmail.com"
        ],
        "SubResourceId": "/wfgrps/testWFG/wfs/aws-s3-demo-website-vg6P",
        "OrgId": "/orgs/charming-copper",
        "CreatedAt": 1720772420966.0,
        "IsArchive": "0",
        "Description": "test",
        "ResourceId": "/wfs/aws-s3-demo-website-vg6P",
        "WfType": "TERRAFORM",
        "ModifiedAt": 1720772929216.0,
        "ParentId": "/orgs/charming-copper/wfgrps/testWFG",
        "ResourceType": "WORKFLOW",
        "LatestWfrunStatus": "ERRORED",
        "DocVersion": "V3.BETA",
        "EnvironmentVariables": [
            {
                "config": {
                    "textValue": "testvalue",
                    "varName": "test"
                },
                "kind": "PLAIN_TEXT"
            }
        ],
        "EnforcedPolicies": [],
        "ResourceName": "aws-s3-demo-website-vg6P",
        "VCSConfig": {
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
        "TerraformConfig": {
            "terraformVersion": "1.5.7",
            "approvalPreApply": true,
            "managedTerraformState": true,
            "terraformPlanOptions": "--run ",
            "postApplyWfStepsConfig": [
                {
                    "name": "post-apply-step-1",
                    "mountPoints": [],
                    "wfStepTemplateId": "/stackguardian/terraform:19",
                    "wfStepInputData": {
                        "schemaType": "FORM_JSONSCHEMA",
                        "data": {
                            "terraformVersion": "1.5.3",
                            "managedTerraformState": true,
                            "terraformAction": "plan-destroy"
                        }
                    },
                    "cmdOverride": "test",
                    "approval": true
                }
            ],
            "prePlanWfStepsConfig": [
                {
                    "name": "pre-plan-step-1",
                    "mountPoints": [],
                    "wfStepTemplateId": "/stackguardian/terraform:19",
                    "wfStepInputData": {
                        "schemaType": "FORM_JSONSCHEMA",
                        "data": {
                            "terraformVersion": "1.4.3",
                            "managedTerraformState": true,
                            "terraformAction": "plan"
                        }
                    },
                    "cmdOverride": "test",
                    "approval": true
                }
            ],
            "preApplyWfStepsConfig": [
                {
                    "name": "pre-apply-step-1",
                    "mountPoints": [],
                    "wfStepTemplateId": "/stackguardian/terraform:19",
                    "wfStepInputData": {
                        "schemaType": "FORM_JSONSCHEMA",
                        "data": {
                            "terraformVersion": "1.4.1",
                            "managedTerraformState": true,
                            "terraformAction": "plan"
                        }
                    },
                    "cmdOverride": "test",
                    "approval": true
                }
            ],
            "driftCheck": true
        }
    }
}
"""

#Workflows ListAll
# json_data = '''
# {
#     "msg": [
#         {
#             "GitHubComRepoID": "stackguardian/template-tf-aws-s3-demo-website",
#             "IsActive": "1",
#             "Description": "test",
#             "ResourceId": "/wfs/aws-s3-demo-website-vg6P",
#             "WfType": "TERRAFORM",
#             "ModifiedAt": 1720772929216.0,
#             "ParentId": "/orgs/charming-copper/wfgrps/testWFG",
#             "LatestWfrunStatus": "ERRORED",
#             "Tags": [],
#             "Authors": [
#                 "larisoncarvalho@gmail.com"
#             ],
#             "ResourceName": "aws-s3-demo-website-vg6P",
#             "SubResourceId": "/wfgrps/testWFG/wfs/aws-s3-demo-website-vg6P",
#             "CreatedAt": 1720772420966.0
#         },
#         {
#             "Authors": [
#                 "larisoncarvalho@gmail.com"
#             ],
#             "ResourceName": "1",
#             "IsActive": "1",
#             "SubResourceId": "/wfgrps/testWFG/wfs/1",
#             "Description": "Automatically created by SG",
#             "ResourceId": "/wfs/1",
#             "WfType": "CUSTOM",
#             "ModifiedAt": 1719465949087.0,
#             "ParentId": "/orgs/charming-copper/wfgrps/testWFG",
#             "LatestWfrunStatus": "ERRORED",
#             "CreatedAt": 1719465947703.0,
#             "Tags": [
#                 "sg-created"
#             ]
#         }
#     ]
# }
# '''
serializer_str = generate_serializer(json_data, root_class_name="GeneratedSerializer")
print(serializer_str)