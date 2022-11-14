# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api

import re

# import maya.cmds as cmds

from ftrack_connect_pipeline_3dsmax import plugin


class MaxRegexPublisherCollectorPlugin(plugin.MaxPublisherCollectorPlugin):
    plugin_name = 'max_regex_publisher_collector'

    def run(self, context_data=None, data=None, options=None):
        '''Select and collect nodes matching regular expression from *options*'''

        selection = []
        return selection


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MaxRegexPublisherCollectorPlugin(api_object)
    plugin.register()
