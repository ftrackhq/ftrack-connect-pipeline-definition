# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin


class PackagePlugin(plugin.PackageDefinition):

    def run(self):
        return {
            "name":"Modeling",
            "type": "modelPackage",
            "context":[
                "Task",
                "Modeling"
            ],
            "components":[
                {
                    "name": "main",
                    "optional": True
                },
                {
                    "name": "cache",
                    "file_type": ["alembic"]
                },
                {
                    "name": "reviewable"
                },
                {
                    "name": "thumbnail"
                }
            ]
        }


def register(api_object, **kw):
    plugin = PackagePlugin(api_object)
    plugin.register()
