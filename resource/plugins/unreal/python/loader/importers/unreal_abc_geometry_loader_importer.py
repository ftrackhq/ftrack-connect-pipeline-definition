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
        '''Load abc file pointed out by collected *data*, with *options*.'''

        # Build import task

        task = unreal.AssetImportTask()

        assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()

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
            + unreal_utils.get_asset_relative_path(asset_version_entity)
            + context_data['asset_name']
        )

        task.destination_path = import_path.replace(' ', '_')

        # Geometry specific options

        # Alembic geo specific options

        task.replace_existing = options.get('ReplaceExisting', True)
        task.automated = options.get('Automated', True)
        task.save = options.get('Save', True)

        import_result = unreal_utils.import_file(task)

        loaded_mesh = unreal.EditorAssetLibrary.load_asset(import_result)

        results = {}

        results[component_path] = unreal_utils.rename_object_with_prefix(
            loaded_mesh, 'S'
        )

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    abc_geo_importer = UnrealAbcGeometryLoaderImporterPlugin(api_object)
    abc_geo_importer.register()
