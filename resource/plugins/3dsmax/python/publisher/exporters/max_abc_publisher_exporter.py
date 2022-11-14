# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import tempfile

from pymxs import mxstoken
from pymxs import runtime as rt

import ftrack_api

from ftrack_connect_pipeline_3dsmax import plugin


class MaxAlembicPublisherExporterPlugin(plugin.MaxPublisherExporterPlugin):
    plugin_name = 'max_abc_publisher_exporter'

    extension = None
    file_type = None

    def run(self, context_data=None, data=None, options=None):
        '''Export Max objects to a temp file for publish'''

        self.extension = '.max'

        new_file_path = tempfile.NamedTemporaryFile(
            delete=False, suffix=self.extension
        ).name

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        return [new_file_path]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    output_plugin = MaxAlembicPublisherExporterPlugin(api_object)
    output_plugin.register()
