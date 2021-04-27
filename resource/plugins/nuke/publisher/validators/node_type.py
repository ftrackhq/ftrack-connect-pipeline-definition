# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

from ftrack_connect_pipeline_nuke import plugin

import nuke


class NoneEmptyValidatorPlugin(plugin.PublisherValidatorNukePlugin):
    plugin_name = 'node_type'

    def run(self, context=None, data=None, options=None):
        node_type = options['node_type']
        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        if len(collected_objects) == 0:
            msg = 'No nodes selected!'
            self.logger.error(msg)
            return (False, {'message': msg})
        
        node_name = collected_objects[0]
        node = nuke.toNode(node_name)
        if node.Class() != node_type:
            msg = 'Node {} is not of type {}'.format(node, node_type)
            self.logger.error(msg)
            return (False, {'message': msg})
        return bool(node_name)


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = NoneEmptyValidatorPlugin(api_object)
    plugin.register()
