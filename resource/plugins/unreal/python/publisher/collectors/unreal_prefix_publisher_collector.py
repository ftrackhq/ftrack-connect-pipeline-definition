# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

# import maya.cmds as cmds

from ftrack_connect_pipeline_unreal import plugin
import ftrack_api


class UnrealPrefixPublisherCollectorPlugin(plugin.UnrealPublisherCollectorPlugin):
    plugin_name = 'unreal_prefix_publisher_collector'

    def run(self, context_data=None, data=None, options=None):
        '''Select and collect nodes matching prefix and suffix from *options*'''
        # cmds.select(cl=True)
        prefix = str(options['prefix'])
        suffix = str(options['sufix'])
        # cmds.select((prefix + '*' + suffix), r=True)
        # selection = cmds.ls(sl=True)
        return selection


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealPrefixPublisherCollectorPlugin(api_object)
    plugin.register()
