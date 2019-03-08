
# Asset schema

package_component_schema = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "name"
    ],
    "properties": {
        "name": {"type": "string"},
        "file_type": {"type": "array", "items":{"type": "string"}},
        "optional": {"type": "boolean"}
    }
}


package_schema = {
    "type": "object",
    "additionalProperties":False,
    "properties":{
        "name":{"type" : "string"},
        "asset_type": {"type": "string"},
        "context": {"type": "array", "items": {"type": "string"}},
        "components":{"type": "array", "items": package_component_schema}
    }

}

# Stage Plugin Schema

_plugin_schema = {
    "type": "object",
    "required": [
        "plugin"
    ],
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "plugin": {"type": "string"},
        "widget": {"type": "string"},
        "visible": {"type": "boolean"},
        "editable": {"type": "boolean"},
        "disabled": {"type": "boolean"},
        "options": {"type": "object"},

    }
}

# Package publisher Schema


publisher_schema = {
    "type": "object",
    "required": [
        "asset_type", "host", "ui", "context"
    ],
    "properties": {
        "asset_type": {"type": "string"},
        "host": {"type": "string"},
        "ui": {"type": "string"},
        "context": {"type": "array", "items": _plugin_schema},
        "components": {
            "type": "object",
            "properties": {
                "collect": {"type":"array", "items": _plugin_schema},
                "validate": {"type": "array", "items": _plugin_schema},
                "output": {"type": "array", "items": _plugin_schema}
            }
        },
        "publish": {
            "type": "array",
            "items": _plugin_schema
        }
    }
}

# Package loader Schema

loader_schema = {
    "type": "object",
    "required": [
        "host", "ui", "context"
    ],
    "properties": {
        "host": {"type": "string"},
        "ui": {"type": "string"},
        "context": {"type": "array", "items": _plugin_schema},
        "components": {
            "type": "array",
            "items": _plugin_schema
        },
        "post": {
            "type": "array",
            "items": _plugin_schema
        }
    }
}


import json
print json.dumps(loader_schema)