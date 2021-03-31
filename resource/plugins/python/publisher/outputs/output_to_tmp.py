# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import shutil
import tempfile
from ftrack_connect_pipeline import plugin
import ftrack_api

class TmpOutputPlugin(plugin.PublisherOutputPlugin):
    plugin_name = 'to_tmp'

    def run(self, context=None, data=None, options=None):
        output = self.output

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        for item in collected_objects:
            new_file_path = tempfile.NamedTemporaryFile(delete=False).name
            shutil.copy(item, new_file_path)
            output.append(new_file_path)

        return output


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = TmpOutputPlugin(api_object)
    plugin.register()