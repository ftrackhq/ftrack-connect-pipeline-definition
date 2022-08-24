# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline_houdini import plugin
from ftrack_connect_pipeline_houdini.constants.asset import modes as load_const
import ftrack_api


class HoudiniDefaultOpenerImporterPlugin(plugin.HoudiniOpenerImporterPlugin):
    plugin_name = 'houdini_default_opener_importer'

    def run(self, context_data=None, data=None, options=None):
        load_mode = load_const.OPEN_MODE
        load_mode_fn = self.load_modes.get(load_mode)

        houdini_options = {}

        results = {}

        paths_to_import = []
        for collector in data:
            paths_to_import.extend(collector['result'])

        for component_path in paths_to_import:
            self.logger.debug('Opening path {}'.format(component_path))

            load_result = load_mode_fn(component_path, houdini_options)

            results[component_path] = load_result

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = HoudiniDefaultOpenerImporterPlugin(api_object)
    plugin.register()
