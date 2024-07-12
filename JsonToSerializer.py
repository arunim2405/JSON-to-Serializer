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
    code.append(f"{' ' * 4}{key} = serializers.DictField(child={nested_class_name}())")
    code.extend(serializer_code(value, nested_class_name))


def serializer_code(fields, class_name="GeneratedSerializer"):
    code = [f"class {class_name}(serializers.Serializer):"]
    nested_code_to_append = []
    for key, value in fields.items():
        if isinstance(value, OrderedDict):
            if len(value) == 0:
                code.append(f"{' ' * 4}{key} = serializers.DictField()")
            else:
                nested_class_name = key.capitalize() + "Serializer"
                nested_code_to_append.append({"key": key, "value": value, "nested_class_name": nested_class_name})
            # code.append(f"{' ' * 4}{key} = serializers.DictField(child={nested_class_name}())")
            # code.extend(serializer_code(value, nested_class_name))
        elif isinstance(value, list) and value and isinstance(value[0], OrderedDict):
            nested_class_name = key.capitalize() + "Serializer"
            nested_code_to_append.append({"key": key, "value": value[0], "nested_class_name": nested_class_name})
            # code.append(f"{' ' * 4}{key} = serializers.ListField(child={nested_class_name}())")
            # code.extend(serializer_code(value[0], nested_class_name))
        else:
            code.append(f"{' ' * 4}{key} = serializers.{value}")
    for nested_code in nested_code_to_append:
        extend_nested_class(**nested_code, code=code)
    return code


def generate_serializer(json_data, root_class_name):
    data = json.loads(json_data)
    fields = generate_serializer_fields(data)
    code_lines = serializer_code(fields, class_name=root_class_name)
    return "\n".join(code_lines)


# Example usage:
json_data = """
{
    "msg": {
        "UserJobMemory": 1024.0,
        "UserJobCPU": 512.0,
        "NumberOfApprovalsRequired": 0.0,
        "RunnerConstraints": {
            "selectors": [
                "shared"
            ],
            "type": "shared"
        },
        "IsActive": "1",
        "Approvers": [],
        "Tags": [
            "sg-created"
        ],
        "DeploymentPlatformConfig": {},
        "MiniSteps": {},
        "Authors": [
            "larisoncarvalho@gmail.com"
        ],
        "WfStepsConfig": [],
        "ActivitySubscribers": [
            "larisoncarvalho@gmail.com"
        ],
        "SubResourceId": "/wfgrps/testWFG/wfs/1",
        "OrgId": "/orgs/charming-copper",
        "CreatedAt": 1719465947703.0,
        "IsArchive": "0",
        "Description": "Automatically created by SG",
        "ResourceId": "/wfs/1",
        "WfType": "CUSTOM",
        "ModifiedAt": 1719465949087.0,
        "ParentId": "/orgs/charming-copper/wfgrps/testWFG",
        "ResourceType": "WORKFLOW",
        "LatestWfrunStatus": "ERRORED",
        "DocVersion": "V3.BETA",
        "EnvironmentVariables": [],
        "EnforcedPolicies": [],
        "ResourceName": "1",
        "VCSConfig": {},
        "TerraformConfig": {}
    }
}
"""
serializer_str = generate_serializer(json_data, root_class_name="GeneratedSerializer")
print(serializer_str)
