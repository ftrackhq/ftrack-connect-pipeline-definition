# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin


class PackagePlugin(plugin.PackageDefinition):

    def run(self):
        return {
            "name":"Shading",
            "type": "shadPackage",
            "context":[
                "Task",
                "Shading"
            ],
            "components":[
                {
                    "name": "main"
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


