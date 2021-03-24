# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import hou

from ftrack_connect_pipeline_houdini import plugin
import ftrack_api


class AbcHoudiniImportPlugin(plugin.LoaderImporterHoudiniPlugin):
    plugin_name = 'abc_houdini_import'

    def run(self, context=None, data=None, options=None):
        # ensure to load the alembic plugin

        results = {}
        paths_to_import = data
        for component_path in paths_to_import:
            self.logger.debug('Importing path {}'.format(component_path))

            node = hou.node('/obj').createNode(
                'alembicarchive', iAObj.assetName)
            node.parm('buildSubnet').set(False)
            node.parm('fileName').set(component_path)
            hou.hscript(
                "opparm -C {0} buildHierarchy (1)".format(
                    resultingNode.path()))
            node.moveToGoodPosition()

            results[component_path] = node

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = AbcHoudiniImportPlugin(api_object)
    plugin.register()