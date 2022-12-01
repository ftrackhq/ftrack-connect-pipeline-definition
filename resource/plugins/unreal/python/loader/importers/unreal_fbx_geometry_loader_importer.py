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


class UnrealFbxGeometryLoaderImporterPlugin(plugin.UnrealLoaderImporterPlugin):
    load_modes = load_const.LOAD_MODES

    plugin_name = 'unreal_fbx_geometry_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        '''Load fbx file pointed out by collected *data*, with *options*.'''

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
            + unreal_utils.get_asset_relative_path(
                self.session, asset_version_entity
            )
            + context_data['asset_name']
        )

        task.destination_path = import_path.replace(' ', '_')

        # Geometry specific options

        # Fbx geo specific options

        task.options = unreal.FbxImportUI()
        task.options.import_mesh = options.get('ImportMesh', True)
        task.options.import_as_skeletal = options.get(
            'ImportAsSkeletal', False
        )
        task.options.import_materials = options.get('ImportMaterials', False)
        task.options.import_animations = options.get('ImportAnimations', False)
        task.options.create_physics_asset = options.get(
            'CreatePhysicsAsset', False
        )
        task.options.override_full_name = options.get('OverrideFullName', True)
        task.options.automated_import_should_detect_type = options.get(
            'AutomatedImportShouldDetectType', False
        )
        task.options.mesh_type_to_import = (
            unreal.FBXImportType.FBXIT_STATIC_MESH
        )
        task.options.static_mesh_import_data = unreal.FbxStaticMeshImportData()
        task.options.static_mesh_import_data.set_editor_property(
            'combine_meshes', options.get('CombineMeshes', True)
        )

        task.replace_existing = options.get('ReplaceExisting', True)
        task.automated = options.get('Automated', True)
        task.save = options.get('Save', True)

        import_result = unreal_utils.import_file(task)
        self.logger.info('Imported: {}'.format(import_result))
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

    fbx_geo_importer = UnrealFbxGeometryLoaderImporterPlugin(api_object)
    fbx_geo_importer.register()
