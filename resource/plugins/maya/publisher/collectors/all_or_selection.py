# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class CollectAllOrSelectionMayaPlugin(plugin.PublisherCollectorMayaPlugin):
    plugin_name = 'all_or_selection'

    def run(self, context=None, data=None, options=None):
        export_option = options.get("export", 'all')
        if export_option == 'all':
            export_object = cmds.ls(ap=True, assemblies=True, dag=True)
        else:
            export_object = cmds.ls(sl=True)
        return export_object


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectAllOrSelectionMayaPlugin(api_object)
    plugin.register()

