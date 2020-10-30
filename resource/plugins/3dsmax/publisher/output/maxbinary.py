# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import os
import tempfile

from pymxs import mxstoken
from pymxs import runtime as rt

from ftrack_connect_pipeline_3dsmax import plugin


class OutputMaxBinaryPlugin(plugin.PublisherOutputMaxPlugin):
    plugin_name = 'OutputMaxBinaryPlugin'

    def run(self, context=None, data=None, options=None):
        component_name = options['component_name']
        new_file_path = tempfile.NamedTemporaryFile(
            delete=False, suffix='.max'
        ).name

        if os.path.isfile(data[0]):
            rt.savemaxFile(new_file_path, useNewFile=False)
        else:
            self.logger.debug('Calling extractor options: data {}'.format(data))
            self.logger.debug('Writing Max file to {}'.format(new_file_path))
            with mxstoken():
                rt.clearSelection()
            for node_name in data:
                rt.selectMore(node_name)
            rt.saveNodes(rt.selection, new_file_path, quiet=True)
        return {component_name: new_file_path}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = OutputMaxBinaryPlugin(api_object)
    plugin.register()
