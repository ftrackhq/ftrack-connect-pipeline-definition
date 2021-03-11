# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import unreal as ue

import ftrack_api

from ftrack_connect_pipeline_unreal_engine import plugin
from ftrack_connect_pipeline_unreal_engine.constants import asset as asset_const

from ftrack_connect_pipeline_unreal_engine.constants.asset import modes as load_const

##########################################
# Loader plugin common                   #
##########################################

class UnrealImportPlugin(plugin.LoaderImporterUnrealPlugin):
    ''' Commons shared by all importers. '''

    load_modes = load_const.LOAD_MODES

    def _find_asset_instance(self, path_root, ftrack_asset_version, ftrack_asset_type_name):
        ''' TODO: move to integration asset '''
        ftrack_asset_id = ftrack_asset_version['parent']['id']
        assets = (
            ue.AssetRegistryHelpers()
            .get_asset_registry()
            .get_assets_by_path(path_root, True)
        )
        for asset_data in assets:
            # unfortunately to access the tag values objects needs to be
            # in memory....
            asset = asset_data.get_asset()
            asset_id = ue.EditorAssetLibrary.get_metadata_tag(
                asset, 'ftrack.{}'.format(asset_const.ASSET_ID)
            )
            asset_type = ue.EditorAssetLibrary.get_metadata_tag(
                asset, 'ftrack.{}'.format(asset_const.ASSET_TYPE)
            )
            if asset_id and asset_type:
                if asset_id == ftrack_asset_id and asset_type == ftrack_asset_type_name:
                    return asset
        return None

    def _get_asset_relative_path(self, ftrack_asset_version):
        ftrack_task = ftrack_asset_version['task']
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
        '''This method allow renaming a UObject to put a prefix to work along with UE4 naming convention
            https://github.com/Allar/ue4-style-guide'''
        assert loaded_obj != None
        new_name_with_prefix = ''
        if loaded_obj:
            object_ad = ue.EditorAssetLibrary.find_asset_data(
                loaded_obj.get_path_name()
            )
            if object_ad:
                if ue.EditorAssetLibrary.rename_asset(
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

    def run(self, context=None, data=None, options=None):
        ''' Format independent init '''

        print('@@@; UnrealImportPlugin::run(context={}, data={}, options={})'.format(context, data, options))
        # Sample output:
        # LogPython: @@@; UnrealImportPlugin::run(context={'context_id': '8954cbac-7d08-11eb-9cb6-76f7e85c7329', 'asset_name': 'animation', 
        # 'comment': None, 'status_id': None, 'asset_id': '71127a43-98ac-42ec-97b1-c5659594718b', 'is_valid_name': True, 
        # 'version_number': '1', 'version_id': '54c778e0-2a17-4f26-be3f-03b5774e83c9', 'asset_type': 'anim'}, data=['C:\\Accsyn_s
        # torage\\testproject\\sq010\\unreal\\animation\\v001\\alembic.abc'], options={'component_name': 'alembic'})
        
        #self.session = ftrack_api.Session()

        self.assetRegistry = ue.AssetRegistryHelpers.get_asset_registry()

        self.version = self.session.query('AssetVersion where id={}'.format(context['version_id'])).first()
        self.import_path = (
            '/Game/'
            + self._get_asset_relative_path(self.version)
            + context['asset_name']
        )

        self.import_path = self.import_path.replace(' ', '_')
 
        paths_to_import = data
        self.component_path = paths_to_import[0]

        current_ftrack_asset = None
        try:
            current_ftrack_asset = self._find_asset_instance(
                self.import_path, self.version, context['asset_type']
            )
        except Exception as error:
            self.logger.error(error)

        self.build_asset_import_task(context, data, options)

        if current_ftrack_asset:
            if options['UpdateExistingAsset'] is False:
                return (False, 'Existing asset found("{}"), not updating!'.format(current_ftrack_asset.asset_name))
            if self.change_version(self.component_path, current_ftrack_asset):
                results = {}
                results[self.component_path] = node
                return results
            else:
                return (False, 'Could not change version on existing asset!')

        self.logger.info('Importing path {}'.format(self.component_path))
        ue.AssetToolsHelpers.get_asset_tools().import_asset_tasks([self.task])
        if len(self.task.imported_object_paths or []) == 0:
            return (False, 'Alembic import failed! See Output log for hints.')
            
        self.loaded_asset = ue.EditorAssetLibrary.load_asset(
            self.task.imported_object_paths[0]
        )

        return None

    def build_asset_import_task(self, context, data, options):
        ''' Create a generic import task. '''
        self.task = ue.AssetImportTask()
        self.task.replace_existing = True
        self.task.automated = True
        self.task.filename = self.component_path
        self.task.destination_path = self.import_path

    def change_version(self, options, current_ftrack_asset):
        ''' Base generic asset reimport. '''
        assets = (
            ue.AssetRegistryHelpers()
                .get_asset_registry()
                .get_assets_by_path('/Game', True)
        )
        for asset_data in assets:
            # unfortunately to access the tag values objects needs to be
            # in memory....
            asset = asset_data.get_asset()
            if str(asset.get_name()) == str(current_ftrack_asset.get_name()):
                self.task.filename = self.component_path
                self.task.destination_path = str(asset_data.package_path)
                self.task.destination_name = str(asset_data.asset_name)
                ue.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
                    [self.task]
                )
                if len(self.task.imported_object_paths):
                    return True
        return False

##########################################
# Rig base                               #
##########################################

class UnrealRigImportPlugin(UnrealImportPlugin):
    ''' Covering rig specific initializations. '''

    def run(self, context=None, data=None, options=None):
        ''' Requires a selected skeleton.'''

        skeletons = self.assetRegistry.get_assets_by_class('Skeleton')

        skeleton_name = options['ChooseSkeleton']
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

        return super(UnrealRigImportPlugin, self).run(context, data, options)

        self.loaded_assets = [self.loaded_asset]

        mesh_skeleton = loaded_skeletal_mesh.skeleton
        if mesh_skeleton:
            self.loaded_assets.append(self._rename_object_with_prefix(mesh_skeleton, 'SKEL'))

        self.mesh_physics_asset = loaded_skeletal_mesh.physics_asset
        if mesh_physics_asset:
            self.loaded_assets.append(self._rename_object_with_prefix(mesh_physics_asset, 'PHAT'))

    def build_asset_import_task(self, context, data, options):
        ''' Add asset type specific import task options. '''
        super(UnrealRigImportPlugin, self).build_asset_import_task(context, data, options)

    def change_version(self, options, current_ftrack_asset):
        ''' Reimport rig asset '''
        assets = (
            ue.AssetRegistryHelpers()
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
                    'skeleton', asset.skeleton)
                self.task.filename = self.component_path
                self.task.destination_path = str(asset_data.package_path)
                self.task.destination_name = str(asset_data.asset_name)
                ue.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
                    [self.task]
                )
                if len(self.task.imported_object_paths):
                    return True
        return False

# Rig plugins

class AbcRigUnrealImportPlugin(UnrealRigImportPlugin):
    plugin_name = 'abc_rig_unreal_import'

    def run(self, context=None, data=None, options=None):
        results = super(AbcRigUnrealImportPlugin, self).run(context, data, options)
        if results is None:                    
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.loaded_assets
        return results

    def build_asset_import_task(self, context, data, options):

        super(AbcRigUnrealImportPlugin, self).build_asset_import_task(context, data, options)

        self.task.options = ue.AbcImportSettings()
        self.task.options.import_type = ue.AlembicImportType.SKELETAL
        if options['ImportMaterial']:
            self.task.options.material_settings.set_editor_property('find_materials', True)


class FbxRigUnrealImportPlugin(UnrealRigImportPlugin):
    plugin_name = 'fbx_rig_unreal_import'

    def run(self, context=None, data=None, options=None):
        results = super(FbxRigUnrealImportPlugin, self).run(context, data, options)
        if results is None:                    
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.loaded_assets
        return results

    def build_asset_import_task(self, context, data, options):
        super(FbxRigUnrealImportPlugin, self).build_asset_import_task(context, data, options)
        # FBX specific
        self.task.options = ue.FbxImportUI()
        self.task.options.import_as_skeletal = True
        self.task.options.import_materials = False
        self.task.options.import_animations = False
        self.task.options.create_physics_asset = True
        self.task.options.automated_import_should_detect_type = False
        self.task.options.mesh_type_to_import = ue.FBXImportType.FBXIT_SKELETAL_MESH
        self.task.options.skeletal_mesh_import_data = ue.FbxSkeletalMeshImportData()
        self.task.options.skeletal_mesh_import_data.set_editor_property(
            'use_t0_as_ref_pose', True
        )
        self.task.options.skeletal_mesh_import_data.normal_import_method = (
            ue.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
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

class UnrealAnimationImportPlugin(UnrealImportPlugin):
    ''' Covering animation specific initializations. '''

    def run(self, context=None, data=None, options=None):
        ''' Requires a selected skeleton.'''

        skeletons = self.assetRegistry.get_assets_by_class('Skeleton')

        skeleton_name = options['ChooseSkeleton']
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

        return super(UnrealAnimationImportPlugin, self).run(context, data, options)

    def build_asset_import_task(self, context, data, options):
        ''' Add asset type import task options. '''
        super(UnrealAnimationImportPlugin, self).build_asset_import_task(context, data, options)

    def change_version(self, options, current_ftrack_asset):
        ''' Reimport animation asset '''
        assets = (
            ue.AssetRegistryHelpers()
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
                ue.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
                    [self.task]
                )
                if len(self.task.imported_object_paths):
                    return True
        return False


# Animation plugins

class AbcAnimationUnrealImportPlugin(UnrealAnimationImportPlugin):
    plugin_name = 'abc_animation_unreal_import'

    def run(self, context=None, data=None, options=None):
        results = super(AbcAnimationUnrealImportPlugin, self).run(context, data, options)
        if results is None:                    
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.loaded_asset
        return results

    def build_asset_import_task(self, context, data, options):

        super(AbcAnimationUnrealImportPlugin, self).build_asset_import_task(context, data, options)

        self.task.options = ue.AbcImportSettings()
        self.task.options.import_type = ue.AlembicImportType.GEOMETRY_CACHE

        if options['UseCustomRange']:
            self.task.options.sampling_settings.frame_start = options['AnimRangeMin']
            self.task.options.sampling_settings.frame_end = options['AnimRangeMax']


class FbxAnimationUnrealImportPlugin(UnrealAnimationImportPlugin):
    plugin_name = 'fbx_animation_unreal_import'

    def run(self, context=None, data=None, options=None):
        results = super(FbxAnimationUnrealImportPlugin, self).run(context, data, options)
        if results is None:                    
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.loaded_asset
        return results

    def build_asset_import_task(self, context, data, options):
        super(FbxAnimationUnrealImportPlugin, self).build_asset_import_task(context, data, options)
        # FBX specific
        self.task.options = ue.FbxImportUI()
        self.task.options.import_as_skeletal = False
        self.task.options.import_materials = False
        self.task.options.import_mesh = False
        self.task.options.import_animations = True
        self.task.options.create_physics_asset = False
        self.task.options.automated_import_should_detect_type = False
        self.task.options.set_editor_property(
            'mesh_type_to_import', ue.FBXImportType.FBXIT_ANIMATION
        )
        self.task.options.anim_sequence_import_data = ue.FbxAnimSequenceImportData()
        self.task.options.anim_sequence_import_data.set_editor_property(
            'import_bone_tracks', True
        )
        self.task.options.anim_sequence_import_data.set_editor_property(
            'import_custom_attribute', True
        )
        self.task.options.set_editor_property(
            'skeleton', self.skeleton_asset.get_asset())

        if options['UseCustomRange']:
            self.task.options.anim_sequence_import_data.set_editor_property(
                'animation_length',
                ue.FBXAnimationLengthImportType.FBXALIT_SET_RANGE,
            )
            rangeInterval = ue.Int32Interval()
            rangeInterval.set_editor_property(
                'min', options['AnimRangeMin']
            )
            rangeInterval.set_editor_property(
                'max', options['AnimRangeMax']
            )
            self.task.options.anim_sequence_import_data.set_editor_property(
                'frame_import_range', rangeInterval
            )
        else:
            self.task.options.anim_sequence_import_data.set_editor_property(
                'animation_length',
                ue.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME,
            )


##########################################
# Geometry base                         #
##########################################

class UnrealGeometryImportPlugin(UnrealImportPlugin):
    ''' Covering animation specific initializations. '''

    def run(self, context=None, data=None, options=None):
        ''' '''
        return super(UnrealGeometryImportPlugin, self).run(context, data, options)

    def build_asset_import_task(self, context, data, options):
        ''' Add asset type import task options. '''
        super(UnrealGeometryImportPlugin, self).build_asset_import_task(context, data, options)


# Geometry plugins

class AbcGeometryUnrealImportPlugin(UnrealGeometryImportPlugin):
    plugin_name = 'abc_geometry_unreal_import'

    def run(self, context=None, data=None, options=None):
        results = super(AbcGeometryUnrealImportPlugin, self).run(context, data, options)
        if results is None:                    
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.loaded_asset
        return results

    def build_asset_import_task(self, context, data, options):

        super(AbcGeometryUnrealImportPlugin, self).build_asset_import_task(context, data, options)

        self.task.options = ue.AbcImportSettings()
        self.task.options.import_type = ue.AlembicImportType.STATIC_MESH
        if options['ImportMaterial']:
            self.task.options.material_settings.set_editor_property('find_materials', True)



class FbxGeometryUnrealImportPlugin(UnrealGeometryImportPlugin):
    plugin_name = 'fbx_geometry_unreal_import'

    def run(self, context=None, data=None, options=None):
        results = super(FbxGeometryUnrealImportPlugin, self).run(context, data, options)
        if results is None:                    
            results = {}
            # Build and post process result
            # ftrack metadata will be added by plugin importer
            results[self.component_path] = self.loaded_asset
        return results

    def build_asset_import_task(self, context, data, options):
        super(FbxGeometryUnrealImportPlugin, self).build_asset_import_task(context, data, options)
        # FBX specific
        self.task.options = ue.FbxImportUI()
        self.task.options.import_mesh = True
        self.task.options.import_as_skeletal = False
        self.task.options.import_materials = False
        self.task.options.import_animations = False
        self.task.options.create_physics_asset = False
        self.task.options.override_full_name = True
        self.task.options.automated_import_should_detect_type = False
        self.task.options.mesh_type_to_import = ue.FBXImportType.FBXIT_STATIC_MESH
        self.task.options.static_mesh_import_data = ue.FbxStaticMeshImportData()
        self.task.options.static_mesh_import_data.set_editor_property(
            'combine_meshes', True
        )
        self.task.options.import_materials = options['ImportMaterial']

##########################################
# Image sequence base                    #
##########################################

class UnrealImageSequenceImportPlugin(UnrealImportPlugin):
    ''' Covering animation specific initializations. '''

    def run(self, context=None, data=None, options=None):
        ''' '''
        return super(UnrealImageSequenceImportPlugin, self).run(context, data, options)

    def build_asset_import_task(self, context, data, options):
        ''' Add asset type import task options. '''
        super(UnrealImageSequenceImportPlugin, self).build_asset_import_task(context, data, options)


# Image sequence plugins

class ZipImageSequenceUnrealImportPlugin(UnrealImageSequenceImportPlugin):
    plugin_name = 'asset_package_unreal_import'

    def run(self, context=None, data=None, options=None):

        # unzip package asset
        path_zip = iAObj.filePath
        override_existing = options['OverrideExisting']
        self.loaded_assets = []

        # use integration-specific logger
        self.logger.info("Importing package asset: {0}".format(path_zip))

        with ZipFile(path_zip, 'r') as package_asset:
            map_package_path = None

            # In Unreal, asset paths are relative to the Content directory.
            # In order to migrate assets correctly between projects, they must
            # be moved from one Content directory to another. 
            content_dir = ue.SystemLibrary.get_project_content_directory()

            for asset in package_asset.namelist():
                # override existing assets if specified by user
                asset_path = os.path.normpath(
                    os.path.join(content_dir, asset)
                )

                if override_existing or not os.path.isfile(asset_path):
                    self.loaded_assets.append(asset)
                
                    # check if asset is a umap file
                    (_, src_name) = os.path.split(asset_path)
                    (_, src_extension) = os.path.splitext(src_name)
                    if src_extension.lower() == ".umap":
                        map_package_path = asset_path
            
            import_count = len(self.loaded_assets)
            # extract contents of the package_asset
            if import_count > 0:
                try:
                    # Note: ZipFile.extractall overwrites existing files by default
                    package_asset.extractall(path = content_dir, members = self.loaded_assets)
                except Exception as error:
                    self.logger.error(error)
                    return []

                # load the extracted map, if one was imported
                if map_package_path:
                    self.logger.info("Loading the map imported from package: {0}".format(map_package_path))
                    try:
                        ue.EditorLoadingAndSavingUtils.load_map(map_package_path)
                    except Exception as error:
                        self.logger.error(error)

            self.logger.info("Number of assets imported: {0}".format(import_count))


        results[self.component_path] = self.loaded_assets
        return results

    def build_asset_import_task(self, context, data, options):

        super(AbcImageSequenceUnrealImportPlugin, self).build_asset_import_task(context, data, options)

        self.task.options = ue.AbcImportSettings()
        self.task.options.import_type = ue.AlembicImportType.STATIC_MESH
        if options['ImportMaterial']:
            self.task.options.material_settings.set_editor_property('find_materials', True)


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    abc_rig_importer = AbcRigUnrealImportPlugin(api_object)
    abc_rig_importer.register()

    fbx_rig_importer = FbxRigUnrealImportPlugin(api_object)
    fbx_rig_importer.register()

    abc_anim_importer = AbcAnimationUnrealImportPlugin(api_object)
    abc_anim_importer.register()

    fbx_anim_importer = FbxAnimationUnrealImportPlugin(api_object)
    fbx_anim_importer.register()

    abc_geo_importer = AbcGeometryUnrealImportPlugin(api_object)
    abc_geo_importer.register()

    fbx_geo_importer = FbxGeometryUnrealImportPlugin(api_object)
    fbx_geo_importer.register()

    zip_img_importer = ZipImageSequenceUnrealImportPlugin(api_object)
    zip_img_importer.register()