# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api
import os

from ftrack_connect_pipeline_nuke import plugin

class FileExistsValidatorPlugin(plugin.PublisherValidatorNukePlugin):
    plugin_name = 'file_exists'

    def run(self, context_data=None, data=None, options=None):
        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        if len(collected_objects) == 0:
            msg = 'No nodes selected!'
            self.logger.error(msg)
            return (False, {'message': msg})

        scene_path = collected_objects[0]
        if os.path.exists(scene_path):
            return True
        else:
            self.logger.debug("Nuke Scene file does not exists")
        return False


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = FileExistsValidatorPlugin(api_object)
    plugin.register()
