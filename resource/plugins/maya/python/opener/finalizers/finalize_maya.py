# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_maya.utils import custom_commands as maya_utils


class MayaFinalize(plugin.MayaOpenerFinalizerPlugin):
    plugin_name = 'maya_finalize'

    def run(self, context_data=None, data=None, options=None):
        result = {}

        work_path, message = maya_utils.save_snapshot(
            context_data['context_id'], self.session
        )
        if work_path:
            result['work_path'] = work_path
        else:
            result = False
        maya_utils.init_maya(self.session)

        return (result, {'message': message})


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MayaFinalize(api_object)
    plugin.register()
