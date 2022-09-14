# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_maya.utils import custom_commands as maya_utils


class MayaDefaultOpenerFinalizerPlugin(plugin.MayaOpenerFinalizerPlugin):
    plugin_name = 'maya_default_opener_finalizer'

    def run(self, context_data=None, data=None, options=None):
        '''Save opened Maya scene to temp'''

        result = {}

        self.logger.debug('Rename Maya scene on open')
        save_path, message = maya_utils.save(
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
    plugin = MayaDefaultOpenerFinalizerPlugin(api_object)
    plugin.register()
