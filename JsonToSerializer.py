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
    "msg": [
        {
            "Authors": [
                "rafidteam@gmail.com"
            ],
            "ResourceName": "test-nested-wfgrps-refeed1",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/test-nested-wfgrps-refeed1",
            "Description": "",
            "ModifiedAt": 1720607883151,
            "CreatedAt": 1720607883151,
            "Tags": []
        },
        {
            "Authors": [
                "richard.loomis@stackguardian.io"
            ],
            "ResourceName": "richard-cli-workshop-test",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/richard-cli-workshop-test",
            "Description": "Automatically created by SG when creating a workflow",
            "ModifiedAt": 1720526630511,
            "CreatedAt": 1720526630511,
            "Tags": [
                "sg-created",
                "workflow"
            ]
        },
        {
            "Authors": [
                "support@stackguardian.io"
            ],
            "ResourceName": "stack-upgrade-bug-repro",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/stack-upgrade-bug-repro",
            "Description": "Created automatically with workflows",
            "ModifiedAt": 1720421208694,
            "CreatedAt": 1720421208694,
            "Tags": [
                "wfs"
            ]
        },
        {
            "Authors": [
                "rafidteam@gmail.com"
            ],
            "ResourceName": "refeed-8-July",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/refeed-8-July",
            "Description": "",
            "ModifiedAt": 1720377545101,
            "CreatedAt": 1720377545101,
            "Tags": []
        },
        {
            "Authors": [
                "support@stackguardian.io"
            ],
            "ResourceName": "dev-portal-tests",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/dev-portal-tests",
            "Description": "",
            "ModifiedAt": 1719994865913,
            "CreatedAt": 1719994865913,
            "Tags": []
        },
        {
            "Authors": [
                "richard.loomis@stackguardian.io"
            ],
            "ResourceName": "richard-25June-wfgrp",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/richard-25June-wfgrp",
            "Description": "",
            "ModifiedAt": 1719318131399,
            "CreatedAt": 1719318131399,
            "Tags": []
        },
        {
            "Authors": [
                "richard.loomis@stackguardian.io"
            ],
            "ResourceName": "richard-25-June",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/richard-25-June",
            "Description": "",
            "ModifiedAt": 1719299870097,
            "CreatedAt": 1719299870097,
            "Tags": []
        },
        {
            "Authors": [
                "support@stackguardian.io"
            ],
            "ResourceName": "github-app-custom-20-June",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/github-app-custom-20-June",
            "Description": "",
            "ModifiedAt": 1718827458326,
            "CreatedAt": 1718827458326,
            "Tags": []
        },
        {
            "Authors": [
                "support@stackguardian.io"
            ],
            "ResourceName": "test-ar",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/test-ar",
            "Description": "",
            "ModifiedAt": 1718201848211,
            "CreatedAt": 1718201848211,
            "Tags": []
        },
        {
            "Authors": [
                "support@stackguardian.io"
            ],
            "ResourceName": "eks-test-june-5",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/eks-test-june-5",
            "Description": "",
            "ModifiedAt": 1717586328927,
            "CreatedAt": 1717586328927,
            "Tags": []
        },
        {
            "Authors": [
                "richard.loomis@stackguardian.io"
            ],
            "ResourceName": "github-vcs-triggers-test-29-May",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/github-vcs-triggers-test-29-May",
            "Description": "",
            "ModifiedAt": 1716996682212,
            "CreatedAt": 1716996682212,
            "Tags": []
        },
        {
            "Authors": [
                "richard.loomis@stackguardian.io"
            ],
            "ResourceName": "git-auth-module-test",
            "IsActive": "1",
            "SubResourceId": "/wfgrps/git-auth-module-test",
            "Description": "",
            "ModifiedAt": 1716378647155,
            "CreatedAt": 1716378647155,
            "Tags": []
        }
    ],
    "lastevaluatedkey": "eyJsYXN0RXZhbHVhdGVkS2V5cyI6IHsiUmVzb3VyY2VJZCI6ICIvd2ZncnBzL2dpdC1hdXRoLW1vZHVsZS10ZXN0IiwgIlBhcmVudElkIjogIi9vcmdzL2RlbW8tb3JnIiwgIldmR3JwUGFyZW50SWQiOiAiL29yZ3MvZGVtby1vcmciLCAiQ3JlYXRlZEF0IjogMTcxNjM3ODY0NzE1NX19"
}
"""

serializer_str = generate_serializer(json_data, root_class_name="GeneratedSerializer")
print(serializer_str)
