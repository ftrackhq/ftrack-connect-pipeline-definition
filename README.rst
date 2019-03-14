Definitions
=============

* \* mark a mandatory field
* <> a variable
* <[, ...]> example of potential arguments of the variable

 
 
 
Package
-------

Defines what a package is, based on where to find it and what
components provides.

.. code :: json

    {
      * "name": "<display name [Animation, Modeling, ...]>",
      * "asset_type": "<asset Type [modelPkg, rigPkg, ...]>",
      * "context": [
          * "<context type [Task, Modeling, ...]>"
        ],
      * "components": [
           * {
                "name": "<component name>",
                "file_type": ["<component type [png, mb, ...]>"]
            }
        ]
    }
    
Plugin
------

All the fields are optional apart from plugin one.
Defines the plugin which will be called.

.. code :: json

    {
        "name": "<plugin display name>",
        "description": "<plugin description >",
      * "plugin": "<plugin id used to execute the process>",
        "widget": "<widget id used to render the process ui>",
        "visible": "<bool>",
        "editable": "<bool>",
        "disabled": "<bool>",
        "options": {
            "<key>": "<value>",
        }
    }

Package Publisher
-----------------

Defines what components to publish and how.

.. code :: json

    {
      * "name": "<display name>",
      * "type": "<asset Type [modelPkg, rigPkg, ...]>",
      * "host": "<host Type [maya, nuke, ...]>",
      * "ui": "<ui Type [qt, js, ...]>",
      * "context": [
          * "<context plugin Type>"
        ],
      * "components": {
          * "<component name [main, color, ...]>": {
              * "collect": [
                  * "<collect plugin Type [from_selection, from_set, from_filesystem, ...]>",
                ],
              * "validate": [
                  * "<validate plugin Type [non_mailfold, non_null, ...]>",
                ],
              * "output": [
                  * "<output plugin Type [mayabinary, nukefile, images, ...]>",
                ]
            }
        },
      * "publish": [
           * "<publish plugin Type [components, metadata, ...]>"
        ]
    }

Package Loader
--------------

Defines how to re load published packages.

.. code :: json

    {
       * "name": "<display name>",
       * "host": "<host Type [maya, nuke, ...]>",
       * "ui": "<ui Type [qt, js, ...]>",
       * "context": [
          * "<context plugin Type>"
       ],
       * "components": [
           * "<load plugin Type [geometry, textures]>"
        ],
       "post": [
           "<post import plugin Type[set_layout, attach_shaders, ...] >"
        ]
    }
