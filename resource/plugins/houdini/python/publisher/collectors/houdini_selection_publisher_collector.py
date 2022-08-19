# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

import hou

from ftrack_connect_pipeline_houdini import plugin
import ftrack_api


class HoudiniSelectionPublisherCollectorPlugin(
    plugin.HoudiniPublisherCollectorPlugin
):
    plugin_name = 'houdini_selection_publisher_collector'

    def run(self, context_data=None, data=None, options=None):
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
    plugin = HoudiniSelectionPublisherCollectorPlugin(api_object)
    plugin.register()
