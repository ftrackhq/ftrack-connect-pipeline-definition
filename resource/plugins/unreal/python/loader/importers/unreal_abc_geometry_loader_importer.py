# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import os

import unreal

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.constants.asset import modes as load_const
from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)
import ftrack_api


class UnrealAbcGeometryLoaderImporterPlugin(plugin.UnrealLoaderImporterPlugin):
    load_modes = load_const.LOAD_MODES

    plugin_name = 'unreal_abc_geometry_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        '''Load Alembic geometry file pointed out by collected *data*, with *options*.'''

        # Build import task

        task = unreal.AssetImportTask()

        paths_to_import = []
        for collector in data:
            paths_to_import.extend(collector['result'])

        component_path = paths_to_import[0]

        task.filename = component_path

        asset_version_entity = self.session.query(
            'AssetVersion where id={}'.format(context_data['version_id'])
        ).first()
        import_path = (
            '/Game/'
            + unreal_utils.get_context_relative_path(
                self.session, asset_version_entity['task']
            )
            + context_data['asset_name']
        )

        task.destination_path = import_path.replace(' ', '_')

        task = unreal.AssetImportTask()

        # Alembic geo specific options

        task.options = unreal.AbcImportSettings()
        task.options.import_type = unreal.AlembicImportType.STATIC_MESH
        task.options.material_settings.set_editor_property(
            'find_materials', options.get('ImportMaterials', False)
        )

        # Geometry specific options

        task.replace_existing = options.get('ReplaceExisting', True)
        task.automated = options.get('Automated', True)
        task.save = options.get('Save', True)

        import_result = unreal_utils.import_file(task)

        if import_result is None:
            raise Exception('Alembic geo import failed!')

        self.logger.info('Imported Alembic geo: {}'.format(import_result))

        loaded_mesh = unreal.EditorAssetLibrary.load_asset(import_result)

        results = {}

        results[component_path] = unreal_utils.rename_node_with_prefix(
            loaded_mesh, 'S'
        )

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    abc_geo_importer = UnrealAbcGeometryLoaderImporterPlugin(api_object)
    abc_geo_importer.register()
