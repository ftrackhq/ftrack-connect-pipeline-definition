# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin


class PackagePlugin(plugin.PackageDefinition):

    def run(self):
        return {
            "name":"testPkg",
            "type": "geo",
            "context":[
                "Task"
            ],
            "components":[
                {
                    "name": "main"
                }
            ]
        }


def register(api_object, **kw):
    plugin = PackagePlugin(api_object)
    plugin.register()
