# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import os

import hou

from ftrack_connect_pipeline_houdini import plugin
from ftrack_connect_pipeline_houdini.constants.asset import modes as load_const
import ftrack_api

class LoadHoudiniPlugin(plugin.LoaderImporterHoudiniPlugin):

    load_modes = load_const.LOAD_MODES

    def _get_houdini_options(self, load_options):
        houdini_options = {}

        houdini_options['load_mode'] = load_options.get('load_mode')
        houdini_options['MergeOverwriteOnConflict'] = load_options.get('MergeOverwriteOnConflict')

        return houdini_options

    def run(self, context=None, data=None, options=None):

        load_mode = options.get('load_mode', list(self.load_modes.keys())[0])
        load_options = options.get('load_options', {})
        load_mode_fn = self.load_modes.get(load_mode, list(self.load_modes.keys())[0])

        houdini_options = {}
        if load_options:
            houdini_options = self._get_houdini_options(load_options)
        houdini_options['context'] = context

        results = {}
        paths_to_import = data
        for component_path in paths_to_import:
            self.logger.debug('Loading path {}'.format(component_path))

            load_result = load_mode_fn(component_path, context=context, options=houdini_options)

            results[component_path] = load_result

        return results

class LoadHoudiniScenePlugin(LoadHoudiniPlugin):
    plugin_name = 'load_houdini_scene'

class LoadHoudiniNodesPlugin(LoadHoudiniPlugin):
    plugin_name = 'load_houdini_nodes'


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    scene_plugin = LoadHoudiniScenePlugin(api_object)
    scene_plugin.register()

    nodes_plugin = LoadHoudiniNodesPlugin(api_object)
    nodes_plugin.register()

