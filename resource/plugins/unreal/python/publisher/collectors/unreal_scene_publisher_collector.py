# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

# import maya.cmds as cmds

import ftrack_api

from ftrack_connect_pipeline_unreal.utils import custom_commands as unreal_utils

from ftrack_connect_pipeline_unreal import plugin


class UnrealScenePublisherCollectorPlugin(plugin.UnrealPublisherCollectorPlugin):
    plugin_name = 'unreal_scene_publisher_collector'

    def run(self, context_data=None, data=None, options=None):
        '''Collect Unreal scene name, save to temp if unsaved'''
        export_option = options.get("export")
        if export_option and isinstance(export_option, list):
            export_option = export_option[0]
        if export_option == 'scene':
            # scene_name = cmds.file(q=True, sceneName=True)
            if len(scene_name or '') == 0:
                # Scene is not saved, save it first.
                self.logger.warning('Unreal not saved, saving locally')
                save_path, message = unreal_utils.save(
                    context_data['context_id'], self.session
                )
                if not message is None:
                    self.logger.info(message)
                # scene_name = cmds.file(q=True, sceneName=True)
            if len(scene_name or '') == 0:
                self.logger.error(
                    "Error exporting the scene: Please save the scene with a "
                    "name before publish"
                )
                return []
            export_object = [scene_name]
        else:
            # export_object = cmds.ls(sl=True)
        return export_object


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealScenePublisherCollectorPlugin(api_object)
    plugin.register()
