# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack
import os

import unreal

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.constants.asset import modes as load_const
from ftrack_connect_pipeline_unreal.constants import (
    asset as asset_const,
)
import ftrack_api


##########################################
# Loader plugin common                   #
##########################################


class UnrealLoaderImporterPluginBase(plugin.UnrealLoaderImporterPlugin):
    '''Commons shared by all importers.'''

    load_modes = load_const.LOAD_MODES

    def _find_asset_instance(
        self, path_root, asset_version_entity, ftrack_asset_type_name
    ):
        ftrack_asset_id = asset_version_entity['parent']['id']
        assets = (
            unreal.AssetRegistryHelpers()
            .get_asset_registry()
            .get_assets_by_path(path_root, True)
        )
        for asset_data in assets:
            # unfortunately to access the tag values objects needs to be
            # in memory....
            asset = asset_data.get_asset()
            asset_id = unreal.EditorAssetLibrary.get_metadata_tag(
                asset, 'ftrack.{}'.format(asset_const.ASSET_ID)
            )
            asset_type_name = unreal.EditorAssetLibrary.get_metadata_tag(
                asset, 'ftrack.{}'.format(asset_const.ASSET_TYPE_NAME)
            )
            if asset_id and asset_type_name:
                if (
                    asset_id == ftrack_asset_id
                    and asset_type_name == ftrack_asset_type_name
                ):
                    return asset
        return None

    def _get_asset_relative_path(self, asset_version_entity):
        ftrack_task = asset_version_entity['task']
        # location.
        links_for_task = self.session.query(
            'select link from Task where id is "{}"'.format(ftrack_task['id'])
        ).first()['link']
        relative_path = ""
        # remove the project
        links_for_task.pop(0)
        for link in links_for_task:
            relative_path += link['name'].replace(' ', '_')
            relative_path += '/'
        return relative_path

    def _rename_object_with_prefix(self, loaded_obj, prefix):
        '''This method allow renaming a UObject to put a prefix to work along
        with UE4 naming convention.
          https://github.com/Allar/ue4-style-guide'''
        assert loaded_obj != None
        new_name_with_prefix = ''
        if loaded_obj:
            object_ad = unreal.EditorAssetLibrary.find_asset_data(
                loaded_obj.get_path_name()
            )
            if object_ad:
                if unreal.EditorAssetLibrary.rename_asset(
                    object_ad.object_path,
                    str(object_ad.package_path)
                    + '/'
                    + prefix
                    + '_'
                    + str(object_ad.asset_name),
                ):
                    new_name_with_prefix = '{}_{}'.format(
                        prefix, object_ad.asset_name
                    )
        return new_name_with_prefix

    def assets_to_paths(self, assets):
        result = []
        for asset in assets:
            result.append(asset.get_path_name())
        return result

    def run(self, context_data=None, data=None, options=None):
        '''Format independent init and import of main asset.'''

        self.assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()

        self.asset_version_entity = self.session.query(
            'AssetVersion where id={}'.format(context_data['version_id'])
        ).first()
        self.import_path = (
            '/Game/'
            + self._get_asset_relative_path(self.asset_version_entity)
            + context_data['asset_name']
        )

        self.import_path = self.import_path.replace(' ', '_')

        paths_to_import = []
        for collector in data:
            paths_to_import.extend(collector['result'])
        self.component_path = paths_to_import[0]

        current_ftrack_asset = None
        try:
            current_ftrack_asset = self._find_asset_instance(
                self.import_path,
                self.asset_version_entity,
                context_data['asset_type_name'],
            )
        except Exception as error:
            self.logger.error(error)

        self.build_asset_import_task(context_data, data, options)

        if current_ftrack_asset:
            if options['UpdateExistingAsset'] is False:
                return (
                    False,
                    {
                        'message': 'Existing asset found("{}")'
                        ', not updating!'.format(
                            current_ftrack_asset.asset_name
                        )
                    },
                )
            if self.change_version(self.component_path, current_ftrack_asset):
                results = {}
                results[self.component_path] = self.assets_to_paths(
                    [current_ftrack_asset]
                )
                return results
            else:
                return (
                    False,
                    {'message': 'Could not change version on existing asset!'},
                )

        self.logger.debug('Importing path {}'.format(self.component_path))
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
            [self.task]
        )
        if len(self.task.imported_object_paths or []) == 0:
            return (
                False,
                {'message': 'Import failed! See Output log' ' for hints.'},
            )

        self.loaded_asset = unreal.EditorAssetLibrary.load_asset(
            self.task.imported_object_paths[0]
        )

        return None


##########################################
# Rig base                               #
##########################################


class UnrealRigLoaderImporterPluginBase(UnrealLoaderImporterPluginBase):
    '''Covering rig specific initializations.'''

    def run(self, context_data=None, data=None, options=None):
        '''Requires a selected skeleton.'''

        skeletons = self.assetRegistry.get_assets_by_class('Skeleton')

        skeleton_name = options['Skeleton']
        if len(skeleton_name or "") == 0:
            return (False, 'Please select a skeleton')

        # Locate the asset
        self.skeleton_asset = None
        for skeleton in skeletons:
            if skeleton.asset_name == skeleton_name:
                self.skeleton_asset = skeleton
                break
        if self.skeleton_asset is None:
            return (False, 'Skeleton "{}" not found!'.format(skeleton_name))

        results = super(UnrealRigLoaderImporterPluginBase, self).run(
            context_data, data, options
        )

        if results is None:
            self.loaded_assets = [self.loaded_asset]

            # Collect eventual additional loaded assets
            mesh_skeleton = self.loaded_asset.skeleton
            if mesh_skeleton:
                self.loaded_assets.append(
                    self._rename_object_with_prefix(mesh_skeleton, 'SKEL')
                )

            self.mesh_physics_asset = self.loaded_asset.physics_asset
            if self.mesh_physics_asset:
                self.loaded_assets.append(
                    self._rename_object_with_prefix(
                        self.mesh_physics_asset, 'PHAT'
                    )
                )

            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.assets_to_paths(
                self.loaded_assets
            )

        return results

    def build_asset_import_task(self, context_data, data, options):
        '''Add asset type specific import task options.'''
        super(UnrealRigLoaderImporterPluginBase, self).build_asset_import_task(
            context_data, data, options
        )
        if self.skeleton_asset != None:
            self.task.options.set_editor_property(
                'skeleton', self.skeleton_asset.get_asset()
            )

    def change_version(self, options, current_ftrack_asset):
        '''Reimport rig asset'''
        assets = (
            unreal.AssetRegistryHelpers()
            .get_asset_registry()
            .get_assets_by_path('/Game', True)
        )
        for asset_data in assets:
            # unfortunately to access the tag values objects needs to be
            # in memory....
            asset = asset_data.get_asset()
            if str(asset.get_name()) == str(current_ftrack_asset.get_name()):
                self.task.options.create_physics_asset = options[
                    'CreatePhysicsAsset'
                ]
                self.task.options.set_editor_property(
                    'skeleton', asset.skeleton
                )
                self.task.filename = self.component_path
                self.task.destination_path = str(asset_data.package_path)
                self.task.destination_name = str(asset_data.asset_name)
                unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
                    [self.task]
                )
                if len(self.task.imported_object_paths):
                    return True
        return False


# Rig plugins


class UnrealAbcRigLoaderImporterPlugin(UnrealRigLoaderImporterPluginBase):
    plugin_name = 'unreal_abc_rig_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        results = super(UnrealAbcRigLoaderImporterPlugin, self).run(
            context_data, data, options
        )
        if results is None:
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.assets_to_paths(
                self.loaded_assets
            )
        return results

    def build_asset_import_task(self, context_data, data, options):

        super(UnrealAbcRigLoaderImporterPlugin, self).build_asset_import_task(
            context_data, data, options
        )

        self.task.options = unreal.AbcImportSettings()
        self.task.options.import_type = unreal.AlembicImportType.SKELETAL
        if options['ImportMaterial']:
            self.task.options.material_settings.set_editor_property(
                'find_materials', True
            )


class UnrealFbxRigLoaderImporterPlugin(UnrealRigLoaderImporterPluginBase):
    plugin_name = 'unreal_fbx_rig_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        results = super(UnrealFbxRigLoaderImporterPlugin, self).run(
            context_data, data, options
        )
        if results is None:
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.assets_to_paths(
                self.loaded_assets
            )
        return results

    def build_asset_import_task(self, context_data, data, options):
        super(UnrealFbxRigLoaderImporterPlugin, self).build_asset_import_task(
            context_data, data, options
        )
        # FBX specific
        self.task.options = unreal.FbxImportUI()
        self.task.options.import_as_skeletal = True
        self.task.options.import_materials = False
        self.task.options.import_animations = False
        self.task.options.create_physics_asset = True
        self.task.options.automated_import_should_detect_type = False
        self.task.options.mesh_type_to_import = (
            unreal.FBXImportType.FBXIT_SKELETAL_MESH
        )
        self.task.options.skeletal_mesh_import_data = (
            unreal.FbxSkeletalMeshImportData()
        )
        self.task.options.skeletal_mesh_import_data.set_editor_property(
            'use_t0_as_ref_pose', True
        )
        self.task.options.skeletal_mesh_import_data.normal_import_method = (
            unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
        )
        self.task.options.skeletal_mesh_import_data.set_editor_property(
            'import_morph_targets', True
        )
        self.task.options.skeletal_mesh_import_data.set_editor_property(
            'import_meshes_in_bone_hierarchy', True
        )
        self.task.options.import_materials = options['ImportMaterial']


##########################################
# Animation base                         #
##########################################


class UnrealAnimationLoaderImporterPluginBase(UnrealLoaderImporterPluginBase):
    '''Covering animation specific initializations.'''

    def run(self, context_data=None, data=None, options=None):
        '''Requires a selected skeleton.'''

        skeletons = self.assetRegistry.get_assets_by_class('Skeleton')

        skeleton_name = options['Skeleton']
        if len(skeleton_name or "") == 0:
            return (False, {'message': 'Please select a skeleton'})

        # Locate the asset
        self.skeleton_asset = None
        for skeleton in skeletons:
            if skeleton.asset_name == skeleton_name:
                self.skeleton_asset = skeleton
                break
        if self.skeleton_asset is None:
            return (
                False,
                {'message': 'Skeleton "{}" not found!'.format(skeleton_name)},
            )

        return super(UnrealAnimationLoaderImporterPluginBase, self).run(
            context_data, data, options
        )

    def build_asset_import_task(self, context_data, data, options):
        '''Add asset type import task options.'''
        super(
            UnrealAnimationLoaderImporterPluginBase, self
        ).build_asset_import_task(context_data, data, options)

    def change_version(self, options, current_ftrack_asset):
        '''Reimport animation asset'''
        assets = (
            unreal.AssetRegistryHelpers()
            .get_asset_registry()
            .get_assets_by_path('/Game', True)
        )
        for asset_data in assets:
            # unfortunately to access the tag values objects needs to be
            # in memory....
            asset = asset_data.get_asset()
            if str(asset.get_name()) == str(current_ftrack_asset.get_name()):
                self.task.filename = self.component_path
                self.task.options.set_editor_property(
                    'skeleton', asset.get_editor_property('skeleton')
                )
                self.task.destination_path = str(asset_data.package_path)
                self.task.destination_name = str(asset_data.asset_name)
                unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
                    [self.task]
                )
                if len(self.task.imported_object_paths):
                    return True
        return False


# Animation plugins


class UnrealAbcAnimationLoaderImporterPlugin(
    UnrealAnimationLoaderImporterPluginBase
):
    plugin_name = 'unreal_abc_animation_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        results = super(UnrealAbcAnimationLoaderImporterPlugin, self).run(
            context_data, data, options
        )
        if results is None:
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.assets_to_paths(
                [self.loaded_asset]
            )
        return results

    def build_asset_import_task(self, context_data, data, options):

        super(
            UnrealAbcAnimationLoaderImporterPlugin, self
        ).build_asset_import_task(context_data, data, options)

        self.task.options = unreal.AbcImportSettings()
        self.task.options.import_type = unreal.AlembicImportType.GEOMETRY_CACHE

        if options['UseCustomRange']:
            self.task.options.sampling_settings.frame_start = options[
                'AnimRangeMin'
            ]
            self.task.options.sampling_settings.frame_end = options[
                'AnimRangeMax'
            ]


class UnrealFbxAnimationUnrealImportPlugin(
    UnrealAnimationLoaderImporterPluginBase
):
    plugin_name = 'unreal_fbx_animation_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        results = super(UnrealFbxAnimationUnrealImportPlugin, self).run(
            context_data, data, options
        )
        if results is None:
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.assets_to_paths(
                [self.loaded_asset]
            )
        return results

    def build_asset_import_task(self, context_data, data, options):
        super(
            UnrealFbxAnimationUnrealImportPlugin, self
        ).build_asset_import_task(context_data, data, options)
        # FBX specific
        self.task.options = unreal.FbxImportUI()
        self.task.options.import_as_skeletal = False
        self.task.options.import_materials = False
        self.task.options.import_mesh = False
        self.task.options.import_animations = True
        self.task.options.create_physics_asset = False
        self.task.options.automated_import_should_detect_type = False
        self.task.options.set_editor_property(
            'mesh_type_to_import', unreal.FBXImportType.FBXIT_ANIMATION
        )
        self.task.options.anim_sequence_import_data = (
            unreal.FbxAnimSequenceImportData()
        )
        self.task.options.anim_sequence_import_data.set_editor_property(
            'import_bone_tracks', True
        )
        self.task.options.anim_sequence_import_data.set_editor_property(
            'import_custom_attribute', True
        )
        self.task.options.set_editor_property(
            'skeleton', self.skeleton_asset.get_asset()
        )

        if options['UseCustomRange']:
            self.task.options.anim_sequence_import_data.set_editor_property(
                'animation_length',
                unreal.FBXAnimationLengthImportType.FBXALIT_SET_RANGE,
            )
            rangeInterval = unreal.Int32Interval()
            rangeInterval.set_editor_property('min', options['AnimRangeMin'])
            rangeInterval.set_editor_property('max', options['AnimRangeMax'])
            self.task.options.anim_sequence_import_data.set_editor_property(
                'frame_import_range', rangeInterval
            )
        else:
            self.task.options.anim_sequence_import_data.set_editor_property(
                'animation_length',
                unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME,
            )


##########################################
# Geometry base                         #
##########################################


class UnrealGeometryLoaderImporterPluginBase(UnrealLoaderImporterPluginBase):
    '''Covering animation specific initializations.'''

    def run(self, context_data=None, data=None, options=None):
        ''' '''
        return super(UnrealGeometryLoaderImporterPluginBase, self).run(
            context_data, data, options
        )

    def build_asset_import_task(self, context_data, data, options):
        '''Add asset type import task options.'''
        super(
            UnrealGeometryLoaderImporterPluginBase, self
        ).build_asset_import_task(context_data, data, options)


# Geometry plugins


class UnrealAbcGeometryLoaderImporterPlugin(
    UnrealGeometryLoaderImporterPluginBase
):
    plugin_name = 'unreal_abc_geometry_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        results = super(UnrealAbcGeometryLoaderImporterPlugin, self).run(
            context_data, data, options
        )
        if results is None:
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.assets_to_paths(
                [self.loaded_asset]
            )
        return results

    def build_asset_import_task(self, context_data, data, options):

        super(
            UnrealAbcGeometryLoaderImporterPlugin, self
        ).build_asset_import_task(context_data, data, options)

        self.task.options = unreal.AbcImportSettings()
        self.task.options.import_type = unreal.AlembicImportType.STATIC_MESH
        if options['ImportMaterial']:
            self.task.options.material_settings.set_editor_property(
                'find_materials', True
            )


class UnrealFbxGeometryLoaderImporterPlugin(
    UnrealGeometryLoaderImporterPluginBase
):
    plugin_name = 'unreal_fbx_geometry_loader_importer'

    def run(self, context_data=None, data=None, options=None):
        results = super(UnrealFbxGeometryLoaderImporterPlugin, self).run(
            context_data, data, options
        )
        if results is None:
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.assets_to_paths(
                [self.loaded_asset]
            )
        return results

    def build_asset_import_task(self, context_data, data, options):
        super(
            UnrealFbxGeometryLoaderImporterPlugin, self
        ).build_asset_import_task(context_data, data, options)
        # FBX specific
        self.task.options = unreal.FbxImportUI()
        self.task.options.import_mesh = True
        self.task.options.import_as_skeletal = False
        self.task.options.import_materials = False
        self.task.options.import_animations = False
        self.task.options.create_physics_asset = False
        self.task.options.override_full_name = True
        self.task.options.automated_import_should_detect_type = False
        self.task.options.mesh_type_to_import = (
            unreal.FBXImportType.FBXIT_STATIC_MESH
        )
        self.task.options.static_mesh_import_data = (
            unreal.FbxStaticMeshImportData()
        )
        self.task.options.static_mesh_import_data.set_editor_property(
            'combine_meshes', True
        )
        self.task.options.import_materials = options['ImportMaterial']


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    abc_rig_importer = UnrealAbcRigLoaderImporterPlugin(api_object)
    abc_rig_importer.register()

    fbx_rig_importer = UnrealFbxRigLoaderImporterPlugin(api_object)
    fbx_rig_importer.register()

    abc_anim_importer = UnrealAbcAnimationLoaderImporterPlugin(api_object)
    abc_anim_importer.register()

    fbx_anim_importer = UnrealFbxAnimationUnrealImportPlugin(api_object)
    fbx_anim_importer.register()

    abc_geo_importer = UnrealAbcGeometryLoaderImporterPlugin(api_object)
    abc_geo_importer.register()

    fbx_geo_importer = UnrealFbxGeometryLoaderImporterPlugin(api_object)
    fbx_geo_importer.register()
