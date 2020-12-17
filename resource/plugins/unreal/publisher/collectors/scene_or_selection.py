# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import unreal

from ftrack_connect_pipeline_houdini import plugin
import ftrack_api


class CollectSceneOrSelectionHoudiniPlugin(plugin.PublisherCollectorHoudiniPlugin):
    plugin_name = 'scene_or_selection'

    def run(self, context=None, data=None, options=None):
        export_option = options.get("export", 'scene')
        if export_option == 'scene':
            scene_name = hou.hipFile.path()
            export_object = [scene_name]
        else:
            export_object = []
            for obj in hou.selectedNodes():
                export_object.append(obj.path())
        return export_object


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectSceneOrSelectionHoudiniPlugin(api_object)
    plugin.register()
