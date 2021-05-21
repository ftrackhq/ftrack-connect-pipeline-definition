# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

import hou

from ftrack_connect_pipeline_houdini import plugin
import ftrack_api


class FBXHoudiniImportPlugin(plugin.LoaderImporterHoudiniPlugin):
    plugin_name = 'fbx_houdini_import'

    def run(self, context=None, data=None, options=None):
        # ensure to load the alembic plugin

        results = {}
        paths_to_import = []
        for collector in data:
            paths_to_import.extend(collector['result'])
        for component_path in paths_to_import:
            self.logger.debug('Importing path {}'.format(component_path))

            (node, import_messages) = hou.hipFile.importFBX(component_path)
            self.logger.debug('FBX import messages: {}'.format(import_messages))

            results[component_path] = node.path()

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = FBXHoudiniImportPlugin(api_object)
    plugin.register()