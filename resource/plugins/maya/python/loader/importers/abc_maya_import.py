# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class AbcMayaImportPlugin(plugin.LoaderImporterMayaPlugin):
    plugin_name = 'abc_maya_import'

    def run(self, context_data=None, data=None, options=None):
        # ensure to load the alembic plugin
        cmds.loadPlugin('AbcImport.so', qt=1)

        results = {}

        paths_to_import = []
        for collector in data:
            paths_to_import.extend(collector['result'])

        for component_path in paths_to_import:
            self.logger.debug('Importing path {}'.format(component_path))
            import_result = cmds.AbcImport(component_path)
            results[component_path] = import_result

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = AbcMayaImportPlugin(api_object)
    plugin.register()