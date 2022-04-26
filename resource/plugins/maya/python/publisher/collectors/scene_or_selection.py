# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import maya.cmds as cmds
from ftrack_connect_pipeline import utils
from ftrack_connect_pipeline_maya.utils import custom_commands as maya_utils

from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class CollectSceneOrSelectionMayaPlugin(plugin.PublisherCollectorMayaPlugin):
    plugin_name = 'scene_or_selection'

    def run(self, context_data=None, data=None, options=None):
        export_option = options.get("export", 'scene')
        if export_option == 'scene':
            scene_name = cmds.file(q=True, sceneName=True)
            if len(scene_name or '') == 0:
                # Scene is not saved, save it first.
                self.logger.warning('Maya not saved, saving local snapshot..')
                work_path, message = maya_utils.save_snapshot(
                    utils.get_global_context_id(), self.session
                )
                if not message is None:
                    self.logger.info(message)
                scene_name = cmds.file(q=True, sceneName=True)
            if len(scene_name or '') == 0:
                self.logger.error(
                    "Error exporting the scene: Please save the scene with a "
                    "name before publish"
                )
                return []
            export_object = [scene_name]
        else:
            export_object = cmds.ls(sl=True)
        return export_object


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectSceneOrSelectionMayaPlugin(api_object)
    plugin.register()
