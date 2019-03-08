
plugin_schema = {
    "type": "object",
    "required": [
        "name", "plugin"
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


asset_schema = {
    "type": "object",
    "additionalProperties":False,
    "properties":{
        "name":{"type" : "string"},
        "asset_type": {"type": "string"},
        "context": {"type": "array", "items": {"type": "string"}},
        "components":{"type": "array", "items": plugin_schema}
    }

}