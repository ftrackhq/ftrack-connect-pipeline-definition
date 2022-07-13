# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import tempfile

from pymxs import mxstoken
from pymxs import runtime as rt

from ftrack_connect_pipeline_3dsmax import plugin


class OutputMaxAlembicPlugin(plugin.PublisherOutputMaxPlugin):
    plugin_name = 'OutputMaxAlembicPlugin'

    def run(self, context_data=None, data=None, options=None):
        new_file_path = tempfile.NamedTemporaryFile(
            delete=False, suffix='.abc'
        ).name
        self.logger.debug('Calling extractor options: data {}'.format(data))
        self.logger.debug('Writing Alembic file to {}'.format(new_file_path))

        saved_selection = rt.GetCurrentSelection()
        self.logger.debug('Post SM1')

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        with mxstoken():
            rt.clearSelection()
            self.logger.debug('Post SM2')

            nodes = []

            for node_name in collected_objects:
                node = rt.getNodeByName(node_name)
                if node:
                    nodes.append(node)
            rt.select(nodes)
            rt.exportFile(
                new_file_path, rt.Name("noPrompt"), selectedOnly=True
            )
        return [new_file_path]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = OutputMaxAlembicPlugin(api_object)
    plugin.register()
