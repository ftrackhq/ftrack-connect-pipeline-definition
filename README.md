
# Asset definition
##### Defines what belongs to an a package and where is suitable to store and retrieve it, 

    {
        "name": "<display name>",
        "asset_type": "<asset Type [modelPkg, rigPkg, ...]>",
        "context": [
            "<context type [Task, Modeling, ...]>"
        ],
        "components": [
            {
                "name": "<component name>",
                "file_type": ["<component type [png, mb, ...]>"]
            }
        ]
    }

# Plugin definition
##### Complete plugin definition  

    {
        "name": "<plugin display name>",
        "description": "<plugin description >",
        "plugin": "<plugin id>",
        "widget": "<widget id>",
        "visible": "<bool>",
        "editable": "<bool>",
        "disabled": "<bool>"
        "options": {
            "<key>": "<value>",
        }
    }

# Publish Package definition
##### Defines what components to publish and how

    {
        "asset": "<asset Type [modelPkg, rigPkg, ...]>",
        "host": "<host Type [maya, nuke, ...]>",
        "ui": "<ui Type [qt, js, ...]>",
        "context": [
            "<context plugin Type>"
        ],
        "components": {
            "<component name>": {
                "collect": [
                    "<context plugin Type>"
                ],
                "validate": [
                    "<validate plugin Type>"
                ],
                "output": [
                    "<output plugin Type>"
                ]
            }
        },
        "publish": [
            "<output plugin Type>"
        ]
    }

# load Package definition
##### Defines how to re load packages

    {
        "name": "<display name>",
        "host": "<host Type [maya, nuke, ...]>",
        "ui": "<ui Type [qt, js, ...]>",
        "load": [
            "<import plugin Type>"
        ],
        "post": [
            "<post import plugin Type>"
        ]
    }