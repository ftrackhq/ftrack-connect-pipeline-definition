# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline_nuke.utils import custom_commands as nuke_utils
from ftrack_connect_pipeline_nuke.constants.asset import modes as load_const


def extract_load_mode_component_name(data):
    for step_result in data:
        if step_result['type'] != 'component':
            continue
        for stage_result in step_result['result']:
            if stage_result['name'] == 'importer':
                for plugin_result in stage_result['result']:
                    load_mode = plugin_result.get('options', {}).get(
                        'load_mode'
                    )
                    if load_mode:
                        return load_mode, step_result['name']
    return None


class NukeFinalize(plugin.LoaderFinalizerNukePlugin):
    plugin_name = 'nuke_finalize'

    def run(self, context_data=None, data=None, options=None):
        result = {}
        message = 'No work file copy needed.'
        load_mode, filename = extract_load_mode_component_name(data)
        if load_mode.lower() == load_const.OPEN_MODE.lower():
            work_path, message = nuke_utils.save_snapshot(
                filename,
                context_data['context_id'],
                self.session,
                ask_load=True,
            )
            if work_path:
                result['work_path'] = work_path
            else:
                result = False

        return (result, {'message': message})


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = NukeFinalize(api_object)
    plugin.register()
