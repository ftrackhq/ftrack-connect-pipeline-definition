# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin


class PackagePlugin(plugin.PackageDefinition):

    def run(self):
        return {
                "name":"Compositing",
                "type": "compPackage",
                "context":[
                    "Task",
                    "Compositing"
                ],
                "components":[
                    {
                        "name": "script",
                        "file_type": ["nk"]
                    },
                    {
                        "name": "cache",
                        "file_type": ["abc"]
                    },

                    {
                        "name": "beauty",
                        "file_type": ["exr"],
                        "optional": True
                    },
                    {
                        "name": "diffuse",
                        "file_type": ["exr"],
                        "optional": True
                    },
                    {
                        "name": "reflection",
                        "file_type": ["exr"],
                        "optional": True
                    },
                    {
                        "name": "shadow",
                        "file_type": ["exr"],
                        "optional": True
                    },
                    {
                        "name": "specular",
                        "file_type": ["exr"],
                        "optional": True
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
