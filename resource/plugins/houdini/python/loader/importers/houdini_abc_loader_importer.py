# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import os

import hou

from ftrack_connect_pipeline_houdini import plugin
import ftrack_api


class HoudiniAbcImportPlugin(plugin.HoudiniLoaderImporterPlugin):
    plugin_name = 'houdini_abc_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        results = {}
        paths_to_import = []
        for collector in data:
            paths_to_import.extend(collector['result'])
        for component_path in paths_to_import:
            self.logger.debug('Importing path {}'.format(component_path))

            node = hou.node('/obj').createNode(
                'alembicarchive', context_data['asset_name']
            )
            node.parm('buildSubnet').set(False)
            node.parm('fileName').set(component_path)
            hou.hscript('opparm -C {0} buildHierarchy (1)'.format(node.path()))
            node.moveToGoodPosition()

            if context_data['asset_type_name'] == 'cam':
                for obj in node.glob('*'):
                    if 'cam' in obj.type().name():
                        bcam = self.bakeCamAnim(
                            obj, [os.getenv('FS'), os.getenv('FE')]
                        )
                        node = bcam
                        break

            results[component_path] = node.path()

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = HoudiniAbcImportPlugin(api_object)
    plugin.register()
