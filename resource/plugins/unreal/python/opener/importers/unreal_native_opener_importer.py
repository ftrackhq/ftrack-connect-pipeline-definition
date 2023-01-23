# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import copy
import os

# import maya.cmds as cmds

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.constants.asset import modes as load_const
import ftrack_api


class UnrealNativeOpenerImporterPlugin(plugin.UnrealOpenerImporterPlugin):
    '''Unreal native importer plugin.'''

    plugin_name = 'unreal_native_opener_importer'

    def run(self, context_data=None, data=None, options=None):
        '''Open an Unreal asset from path stored in collected object provided with *data*'''

        load_mode = load_const.OPEN_MODE
        load_mode_fn = self.load_modes.get(
            load_mode, list(self.load_modes.keys())[0]
        )

        # Pass version ID to enable evaluation of content browser path
        unreal_options = copy.deepcopy(options)
        unreal_options.update(
            {'version_id': context_data['version_id']}.items()
        )

        results = {}

        paths_to_import = []
        for collector in data:
            paths_to_import.extend(collector['result'])

        for component_path in paths_to_import:
            self.logger.debug('Opening path: "{}"'.format(component_path))

            load_result = load_mode_fn(
                component_path, unreal_options, self.session
            )

            self.logger.debug('Imported asset to: "{}"'.format(load_result))

            results[component_path] = load_result

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealNativeOpenerImporterPlugin(api_object)
    plugin.register()
