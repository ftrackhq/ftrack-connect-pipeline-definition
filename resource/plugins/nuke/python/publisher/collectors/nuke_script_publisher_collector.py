# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

import nuke

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline import utils
from ftrack_connect_pipeline_nuke.utils import custom_commands as nuke_utils


class NukeScriptPublisherCollectorPlugin(plugin.NukePublisherCollectorPlugin):
    plugin_name = 'nuke_script_publisher_collector'

    def run(self, context_data=None, data=None, options=None):
        script_name = nuke.root().name()
        if script_name == 'Root':
            # Script is not saved, save it first.
            self.logger.warning('Nuke not saved, saving local snapshot..')
            work_path, message = nuke_utils.save_snapshot(
                utils.global_context(), self.session
            )
            if not message is None:
                self.logger.info(message)
            script_name = nuke.root().name()
        if len(script_name or '') == 0:
            self.logger.error(
                "Error exporting the scene: Please save the script with a "
                "name before publish"
            )
            return []
        return [script_name]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = NukeScriptPublisherCollectorPlugin(api_object)
    plugin.register()
