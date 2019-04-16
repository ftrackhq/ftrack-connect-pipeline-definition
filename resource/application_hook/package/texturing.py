# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin


class PackagePlugin(plugin.PackageDefinition):

    def run(self):
        return {
            "name":"Texturing",
            "type": "textPackage",
            "context":[
                "Task",
                "Texturing"
            ],
            "components":[
                {
                    "name": "color",
                    "file_type": ["exr"]
                },
                {
                    "name": "diffuse",
                    "file_type": ["exr"],
                    "optional": True
                },
                {
                    "name": "specular",
                    "file_type": ["exr"],
                    "optional": True
                },
                {
                    "name": "bump",
                    "file_type": ["exr"],
                    "optional": True
                },
                {
                    "name": "thumbnail"
                }
            ]
        }


def register(api_object, **kw):
    plugin = PackagePlugin(api_object)
    plugin.register()




