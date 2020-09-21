# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_3dsmax import plugin
import ftrack_api

from pymxs import runtime as rt


class CollectSceneOrSelectionMayaPlugin(plugin.PublisherCollectorMaxPlugin):
    plugin_name = 'scene_or_selection'

    def run(self, context=None, data=None, options=None):
        export_option = options.get("export", 'scene')
        if export_option == 'scene':
            scene_name = rt.maxFilePath + rt.maxFileName
            export_object = [scene_name]
        else:
            export_object = [node.getmxsprop('name') for node in rt.selection]
        return export_object


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectSceneOrSelectionMayaPlugin(api_object)
    plugin.register()

