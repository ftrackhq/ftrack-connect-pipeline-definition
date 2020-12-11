# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_maya import plugin

import maya.cmds as cmds
import ftrack_api


class CheckGeoNamesValidatorPlugin(plugin.PublisherValidatorMayaPlugin):
    plugin_name = 'name_validator'

    def run(self, context=None, data=None, options=None):
        allObj = cmds.ls(data, tr=True)
        if not allObj:
            return False
        for obj in allObj:
            if obj.startswith('ftrack_') == False:
                return False
        return True


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CheckGeoNamesValidatorPlugin(api_object)
    plugin.register()
