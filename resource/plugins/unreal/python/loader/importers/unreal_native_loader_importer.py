# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import os

# import maya.cmds as cmds

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.constants.asset import modes as load_const
import ftrack_api


class UnrealNativeLoaderImporterPlugin(plugin.UnrealLoaderImporterPlugin):
    plugin_name = 'unreal_native_loader_importer'

    load_modes = load_const.LOAD_MODES

    def _get_unreal_options(self, load_options):
        unreal_options = {}

        if load_options.get('preserve_references'):
            unreal_options['pr'] = load_options.get('preserve_references')
        if load_options.get('add_namespace'):
            unreal_options['ns'] = load_options.get('namespace_option')

        return unreal_options

    def run(self, context_data=None, data=None, options=None):
        '''Import collected objects provided with *data* into Unreal based on *options*'''
        # cmds.loadPlugin('fbxmaya.so', qt=1)
        load_mode = options.get('load_mode', list(self.load_modes.keys())[0])
        load_options = options.get('load_options', {})
        load_mode_fn = self.load_modes.get(
            load_mode, list(self.load_modes.keys())[0]
        )

        unreal_options = {}
        if load_options:
            unreal_options = self._get_unreal_options(load_options)

        results = {}

        paths_to_import = []
        for collector in data:
            paths_to_import.extend(collector['result'])

        for component_path in paths_to_import:
            self.logger.debug('Loading path {}'.format(component_path))
            if unreal_options.get('ns') == 'file_name':
                unreal_options['ns'] = os.path.basename(component_path).split(
                    "."
                )[0]
            elif unreal_options.get('ns') == 'component':
                unreal_options['ns'] = data[0].get('name')

            load_result = load_mode_fn(component_path, unreal_options)

            results[component_path] = load_result

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealNativeLoaderImporterPlugin(api_object)
    plugin.register()
