# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api

from ftrack_connect_pipeline_houdini import plugin
from ftrack_connect_pipeline_houdini.utils import (
    custom_commands as houdini_utils,
)


class HoudiniDefaultOpenerFinalizerPlugin(plugin.HoudiniOpenerFinalizerPlugin):
    plugin_name = 'houdini_default_opener_finalizer'

    def run(self, context_data=None, data=None, options=None):
        result = {}

        self.logger.debug('Rename Houdini scene on open')
        save_path, message = houdini_utils.save(
            context_data['context_id'], self.session, save=False
        )
        if save_path:
            result['save_path'] = save_path
        else:
            result = False

        return (result, {'message': message})


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = HoudiniDefaultOpenerFinalizerPlugin(api_object)
    plugin.register()
