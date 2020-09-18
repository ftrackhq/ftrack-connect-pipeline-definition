# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import tempfile

import MaxPlus
import pymxs

from ftrack_connect_pipeline_3dsmax import plugin


class OutputMaxBinaryPlugin(plugin.PublisherOutputMaxPlugin):
    plugin_name = 'OutputMaxBinaryPlugin'

    def run(self, context=None, data=None, options=None):
        component_name = options['component_name']
        new_file_path = tempfile.NamedTemporaryFile(
            delete=False, suffix='.max'
        ).name

        publish_scene = bool(options.get('export', 'export_selected'))
        if publish_scene == "scene":
            pymxs.runtime.savemaxFile(new_file_path, useNewFile=False)
        else:
            self.logger.debug('Calling extractor options: data {}'.format(data))
            self.logger.debug('Writing Max file to {}'.format(new_file_path))
            with pymxs.mxstoken():
                pymxs.runtime.execute('clearSelection()')
            for node_name in data:
                MaxPlus.Core.EvalMAXScript('selectMore ${}'.format(node_name))
            MaxPlus.FileManager.SaveSelected(new_file_path)
        return {component_name: new_file_path}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = OutputMaxBinaryPlugin(api_object)
    plugin.register()
