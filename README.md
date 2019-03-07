# Definitions

## Asset
Defines what belongs to an a package and where is suitable to store and retrieve it.

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

## Plugin
Complete plugin definition,

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

## Publish Package
Defines what components to publish and how.

    {
        "asset_type": "<asset Type [modelPkg, rigPkg, ...]>",
        "host": "<host Type [maya, nuke, ...]>",
        "ui": "<ui Type [qt, js, ...]>",
        "context": [
            "<context plugin Type>"
        ],
        "components": {
            "<component name>": {
                "collect": [
                    "<collect plugin Type [from_selection, from_set, from_filesystem, ...]>"
                ],
                "validate": [
                    "<validate plugin Type [non_mailfold, non_null, ...]>"
                ],
                "output": [
                    "<output plugin Type [mayabinary, nukefile, images]>"
                ]
            }
        },
        "publish": [
            "<publish plugin Type [server, metadata, ...]>"
        ]
    }

## Load Package
Defines how to re load published packages.

    {
        "name": "<display name>",
        "host": "<host Type [maya, nuke, ...]>",
        "ui": "<ui Type [qt, js, ...]>",
        "load": [
            "<import plugin Type [geometry, textures]>"
        ],
        "post": [
            "<post import plugin Type[set_layout, attach_shaders, ...] >"
        ]
    }
