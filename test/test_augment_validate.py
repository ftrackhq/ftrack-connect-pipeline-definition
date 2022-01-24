from jsonschema import Draft7Validator, validators

orig_schema = {
    "title": "Publisher",
    "type": "object",
    "additionalProperties": False,
    "definitions": {
        "Config": {
            "title": "Config",
            "type": "object",
            "required": ["stage_order", "engine_type", "type"],
            "order": ["type", "stage_order", "engine_type"],
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "pattern": "^config$",
                    "default": "config",
                },
                "stage_order": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["collector", "validator", "output"],
                },
                "engine_type": {"type": "string", "default": "publisher"},
            },
        },
        "Stage": {
            "title": "Stage",
            "type": "object",
            "required": ["name", "plugins", "type"],
            "order": ["type", "name", "plugins"],
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "pattern": "^stage$",
                    "default": "stage",
                },
                "name": {
                    "type": "string",
                    "enum": [
                        "collector",
                        "validator",
                        "output",
                        "context",
                        "finalizer",
                    ],
                },
                "plugins": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Plugin"},
                    "default": [],
                    "minItems": 1,
                    "uniqueItems": True,
                },
            },
        },
        "CollectorStage": {
            "allOf": [{"$ref": "#/definitions/Stage"}],
            "properties": {
                "name": {"pattern": "^collector$", "default": "collector"},
                "plugins": {
                    "items": {
                        "allOf": [{"$ref": "#/definitions/Plugin"}],
                        "properties": {
                            "plugin_type": {
                                "pattern": "^collector$",
                                "default": "collector",
                            }
                        },
                    }
                },
            },
        },
        "ValidatorStage": {
            "allOf": [{"$ref": "#/definitions/Stage"}],
            "properties": {
                "name": {"pattern": "^validator$", "default": "validator"},
                "plugins": {
                    "items": {
                        "allOf": [{"$ref": "#/definitions/Plugin"}],
                        "properties": {
                            "plugin_type": {
                                "pattern": "^validator$",
                                "default": "validator",
                            }
                        },
                    }
                },
            },
        },
        "OutputStage": {
            "allOf": [{"$ref": "#/definitions/Stage"}],
            "properties": {
                "name": {"pattern": "^output$", "default": "output"},
                "plugins": {
                    "items": {
                        "allOf": [{"$ref": "#/definitions/Plugin"}],
                        "properties": {
                            "plugin_type": {
                                "pattern": "^output$",
                                "default": "output",
                            }
                        },
                    }
                },
            },
        },
        "ContextStage": {
            "allOf": [{"$ref": "#/definitions/Stage"}],
            "properties": {
                "name": {"pattern": "^context$", "default": "context"},
                "plugins": {
                    "items": {
                        "allOf": [{"$ref": "#/definitions/Plugin"}],
                        "properties": {
                            "plugin_type": {
                                "pattern": "^context$",
                                "default": "context",
                            }
                        },
                    }
                },
            },
        },
        "FinalizerStage": {
            "allOf": [{"$ref": "#/definitions/Stage"}],
            "properties": {
                "name": {"pattern": "^finalizer$", "default": "finalizer"},
                "plugins": {
                    "items": {
                        "allOf": [{"$ref": "#/definitions/Plugin"}],
                        "properties": {
                            "plugin_type": {
                                "pattern": "^finalizer$",
                                "default": "finalizer",
                            }
                        },
                    }
                },
            },
        },
        "Plugin": {
            "title": "Plugin",
            "type": "object",
            "required": ["name", "plugin", "type", "plugin_type"],
            "order": [
                "type",
                "plugin_type",
                "name",
                "description",
                "plugin",
                "widget",
                "options",
            ],
            "additionalProperties": True,
            "properties": {
                "type": {
                    "type": "string",
                    "pattern": "^plugin$",
                    "default": "plugin",
                },
                "plugin_type": {
                    "type": "string",
                    "enum": [
                        "collector",
                        "validator",
                        "output",
                        "context",
                        "finalizer",
                    ],
                },
                "name": {"type": "string"},
                "description": {"type": "string"},
                "plugin": {"type": "string"},
                "widget": {"type": "string"},
                "widget_ref": {"type": "string"},
                "visible": {"type": "boolean", "default": True},
                "editable": {"type": "boolean", "default": True},
                "options": {"type": "object", "default": {}},
            },
        },
        "Component": {
            "title": "Component",
            "type": "object",
            "required": ["name", "stages", "type"],
            "order": ["type", "name", "stages"],
            "additionalProperties": False,
            "properties": {
                "name": {"type": "string"},
                "type": {
                    "type": "string",
                    "pattern": "^component$",
                    "default": "component",
                },
                "optional": {"type": "boolean", "default": False},
                "enabled": {"type": "boolean", "default": True},
                "stages": {
                    "type": "array",
                    "maxItems": 3,
                    "uniqueItems": True,
                    "items": [
                        {"$ref": "#/definitions/CollectorStage"},
                        {"$ref": "#/definitions/ValidatorStage"},
                        {"$ref": "#/definitions/OutputStage"},
                    ],
                },
            },
        },
    },
    "required": [
        "name",
        "package",
        "host_type",
        "contexts",
        "components",
        "finalizers",
        "type",
        "_config",
    ],
    "order": [
        "type",
        "name",
        "package",
        "host_type",
        "contexts",
        "components",
        "finalizers",
    ],
    "properties": {
        "type": {
            "type": "string",
            "pattern": "^publisher$",
            "default": "publisher",
        },
        "name": {"type": "string", "default": None},
        "package": {"type": "string", "default": None},
        "host_type": {"type": "string", "default": None},
        "ui_type": {"type": "string", "default": ""},
        "contexts": {"$ref": "#/definitions/ContextStage"},
        "components": {
            "type": "array",
            "items": {"$ref": "#/definitions/Component"},
            "default": [],
            "minItems": 1,
            "uniqueItems": True,
        },
        "finalizers": {"$ref": "#/definitions/FinalizerStage"},
        "_config": {"$ref": "#/definitions/Config", "default": {}},
    },
}
simple_schema = {
    "title": "Publisher",
    "type": "object",
    "additionalProperties": False,
    "definitions": {
        "Config": {
            "title": "Config",
            "type": "object",
            "required": ["stage_order", "engine_type", "type"],
            "order": ["type", "stage_order", "engine_type"],
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "pattern": "^config$",
                    "default": "config",
                },
                "stage_order": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["collector", "validator", "output"],
                },
                "engine_type": {"type": "string", "default": "publisher"},
            },
        },
        "Stage": {
            "title": "Stage",
            "type": "object",
            "required": ["name", "plugins", "type"],
            "order": ["type", "name", "plugins"],
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "pattern": "^stage$",
                    "default": "stage",
                },
                "name": {
                    "type": "string",
                    "enum": [
                        "collector",
                        "validator",
                        "output",
                        "context",
                        "finalizer",
                    ],
                },
                "plugins": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Plugin"},
                    "default": [],
                    "minItems": 1,
                    "uniqueItems": True,
                },
            },
        },
        "ValidatorStage": {
            "allOf": [{"$ref": "#/definitions/Stage"}],
            "properties": {
                "name": {"pattern": "^validator$", "default": "validator"},
                "plugins": {
                    "items": {
                        "allOf": [{"$ref": "#/definitions/Plugin"}],
                        "properties": {
                            "plugin_type": {
                                "pattern": "^validator$",
                                "default": "validator",
                            },
                        },
                    },
                },
            },
        },
        "Plugin": {
            "title": "Plugin",
            "type": "object",
            "required": ["name", "plugin", "type", "plugin_type"],
            "order": [
                "type",
                "plugin_type",
                "name",
                "description",
                "plugin",
                "widget",
                "options",
            ],
            "additionalProperties": True,
            "properties": {
                "type": {
                    "type": "string",
                    "pattern": "^plugin$",
                    "default": "plugin",
                },
                "name": {"type": "string"},
                "description": {"type": "string"},
                "plugin": {"type": "string"},
                "plugin_type": {
                    "type": "string",
                    "enum": [
                        "collector",
                        "validator",
                        "output",
                        "context",
                        "finalizer",
                    ],
                },
                "widget": {"type": "string"},
                "widget_ref": {"type": "string"},
                "visible": {"type": "boolean", "default": True},
                "editable": {"type": "boolean", "default": True},
                "options": {"type": "object", "default": {}},
            },
        },
        "Component": {
            "title": "Component",
            "type": "object",
            "required": ["name", "stages", "type"],
            "order": ["type", "name", "stages"],
            "additionalProperties": False,
            "properties": {
                "name": {"type": "string"},
                "type": {
                    "type": "string",
                    "pattern": "^component$",
                    "default": "component",
                },
                "optional": {"type": "boolean", "default": False},
                "enabled": {"type": "boolean", "default": True},
                "stages": {
                    "type": "array",
                    "maxItems": 3,
                    "uniqueItems": True,
                    "items": {"$ref": "#/definitions/ValidatorStage"},
                },
            },
        },
    },
    "required": [
        "name",
        "type",
        "_config",
        "components",
    ],
    "order": ["name"],
    "properties": {
        "type": {
            "type": "string",
            "pattern": "^publisher$",
            "default": "publisher",
        },
        "name": {"type": "string", "default": None},
        "_config": {"$ref": "#/definitions/Config", "default": {}},
        "components": {
            "type": "array",
            "items": {"$ref": "#/definitions/Component"},
            "default": [],
            "minItems": 1,
            "uniqueItems": True,
        },
    },
}
orig_definition = {
    "type": "publisher",
    "name": "File Publisher",
    "package": "pythonPkg",
    "host_type": "python",
    "contexts": {
        "name": "context",
        "plugins": [
            {
                "name": "context selector",
                "plugin": "context.publish",
                "widget": "context.publish",
            }
        ],
    },
    "components": [
        {
            "name": "main",
            "stages": [
                {
                    "name": "collector",
                    "plugins": [
                        {
                            "name": "collect from given path",
                            "plugin": "filesystem",
                            "widget": "file_collector.widget",
                            "options": {"path": None},
                        }
                    ],
                },
                {
                    "name": "validator",
                    "plugins": [
                        {"name": "file exists", "plugin": "file_exists"}
                    ],
                },
                {
                    "name": "output",
                    "plugins": [
                        {"name": "passthrough output", "plugin": "passthrough"}
                    ],
                },
            ],
        }
    ],
    "finalizers": {
        "name": "finalizer",
        "plugins": [
            {"name": "to ftrack server", "plugin": "result", "visible": False}
        ],
    },
}
simple_definition = {
    "name": "File Publisher",
    "components": [
        {
            "name": "main",
            "stages": [
                {
                    "name": "validator",
                    "plugins": [
                        {"name": "file exists", "plugin": "file_exists"}
                    ],
                }
            ],
        }
    ],
}

######### TEST 1 #############


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]
    validate_required = validator_class.VALIDATORS["required"]
    validate_ref = validator_class.VALIDATORS["$ref"]

    def set_default_property(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema and not instance.get(property):
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator,
            properties,
            instance,
            schema,
        ):
            yield error

    def set_default_required(validator, required, instance, schema):
        if validator.is_type(instance, "object"):
            print("instance --> {}".format(instance))
            print("schema --> {}".format(schema))
            for property in required:
                if not instance.get(property):
                    default_value = schema['properties'][property].get(
                        'default'
                    )
                    print("default_value --> {}".format(default_value))
                    print("property --> {}".format(property))
                    if default_value is not None:
                        instance[property] = default_value

        for error in validate_required(
            validator,
            required,
            instance,
            schema,
        ):
            yield error

    return validators.extend(
        validator_class,
        {"required": set_default_required, "properties": set_default_property},
    )


DefaultValidatingDraft7Validator = extend_with_default(Draft7Validator)

obj = orig_definition
schema = orig_schema
DefaultValidatingDraft7Validator(schema).validate(obj)
print("obj ---> {}".format(obj))
import json

print(json.dumps(obj))
