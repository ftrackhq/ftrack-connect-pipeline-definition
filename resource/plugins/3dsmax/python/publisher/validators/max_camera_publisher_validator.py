# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline_3dsmax import plugin

# import maya.cmds as cmds

import ftrack_api


class MaxCameraPublisherValidatorPlugin(plugin.MaxPublisherValidatorPlugin):
    plugin_name = 'max_camera_publisher_validator'

    def run(self, context_data=None, data=None, options=None):
        '''Return true if all the collected Max node supplied with *data* are cameras'''
        if not data:
            return False

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        return True


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MaxCameraPublisherValidatorPlugin(api_object)
    plugin.register()
