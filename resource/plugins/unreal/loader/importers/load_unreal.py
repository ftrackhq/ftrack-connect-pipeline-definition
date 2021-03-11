# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import unreal as ue

import ftrack_api

from ftrack_connect_pipeline_unreal_engine import plugin
from ftrack_connect_pipeline_unreal.constants import asset as asset_const

class UnrealImportPlugin(plugin.LoaderImporterUnrealPlugin):
    ''' Commons shared by all importers. '''

    def _find_asset_instance(self, path_root, version, ftrack_asset_type):
        ''' TODO: move to integration asset '''
        ftrack_asset_id = version['parent']['id']
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
                if asset_id == ftrack_asset_id and asset_type == ftrack_asset_type:
                    return asset
        return None

    def _get_asset_relative_path(self, ftrack_asset_version):
        task = ftrack_asset_version['task']
        # location.
        links_for_task = self.session.query(
            'select link from Task where id is "{}"'.format(task['id'])
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

        self.session = ftrack_api.Session()

        self.assetRegistry = ue.AssetRegistryHelpers.get_asset_registry()

        self.version = self.session.query('AssetVersion where id={}'.format(context['version_id'])).first()
        self.path_import = (
            '/Game/'
            + self._get_asset_relative_path(self.version)
            + '/' + context['asset_name']
        )

        self.path_import = self.path_import.replace(' ', '_')
        current_ftrack_asset = None
        try:
            current_ftrack_asset = self._find_asset_instance(
                self.path_import, self.version, context['asset_type']
            )
        except Exception as error:
            self.logger.error(error)

        self.path_component = paths_to_import[0]

        self._get_asset_import_task(options)

        if current_ftrack_asset:
            if options['UpdateExistingAsset'] is False:
                return (False, 'Existing asset found("{}"), not updating!'.format(current_ftrack_asset.asset_name))
            if self._change_version(self.path_component, current_ftrack_asset):
                results = {}
                results[self.path_component] = node
                return results
            else:
                return (False, 'Could not change version on existing asset!')

        return None

    def _get_asset_import_task(self, options):
        ''' Create a generic import task. '''
        self.task = ue.AssetImportTask()
        self.task.replace_existing = True
        self.task.automated = True
        self.task.filename = self.path_component
        self.task.destination_path = self.path_import


class UnrealAnimationImportPlugin(plugin.LoaderImporterUnrealPlugin):
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

        return None

    def _get_asset_import_task(self, options):
        ''' Add anim specific import task options. '''

        self.task.options.set_editor_property(
            'skeleton', self.skeleton_asset.get_asset())

    def _change_version(self, options, current_ftrack_asset):
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
                self.task.filename = self.path_import
                self.task.options.set_editor_property(
                    'skeleton', asset.get_editor_property('skeleton')
                )
                self.task.destination_path = str(asset_data.package_path)
                self.task.destination_name = str(asset_data.asset_name)
                ue.AssetToolsHelpers.get_asset_tools().import_asset_tasks(
                    [self.task]
                )
                if len(task.imported_object_paths):
                    return True
        return False


class AbcAnimationUnrealImportPlugin(UnrealImportPlugin, UnrealAnimationImportPlugin):
    plugin_name = 'abc_animation_unreal_import'

    def run(self, context=None, data=None, options=None):

        results = UnrealImportPlugin.run(self, context, data, options)
        if not results is None:
            return results

        results = UnrealAnimationImportPlugin.run(self, context, data, options)
        if not results is None:
            return results

        results = {}
        self.logger.info('Importing path {}'.format(self.path_component))
        ue.AssetToolsHelpers.get_asset_tools().import_asset_tasks([self.task])
        loaded_asset = ue.EditorAssetLibrary.load_asset(
            self.task.imported_object_paths[0]
        )
        # ftrack metadata will be added by plugin importer
        results[self.path_component] = loaded_asset
        return results

    def _get_asset_import_task(self, options):

        UnrealImportPlugin._get_asset_import_task(self, options)

        self.task.options = ue.AbcImportSettings()
        self.task.options.import_type = ue.AlembicImportType.GEOMETRY_CACHE

        if context['asset_type'] == 'anim':
            if options['UseCustomRange']:
                self.task.options.sampling_settings.frame_start = options['AnimRangeMin']
                self.task.options.sampling_settings.frame_end = options['AnimRangeMax']

        UnrealAnimationImportPlugin._get_asset_import_task(self, options)


class FbxAnimationUnrealImportPlugin(UnrealImportPlugin, UnrealAnimationImportPlugin):
    plugin_name = 'fbx_animation_unreal_import'

    def run(self, context=None, data=None, options=None):

        result = UnrealImportPlugin.run(self, context, data, options)
        if not result is None:
            return result

        result = UnrealAnimationImportPlugin.run(self, context, data, options)
        if not result is None:
            return result

        if context['asset_type'] == 'anim':
            # Animation specific FBX options
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

        results = {}
        self.logger.info('Importing path {}'.format(self.path_component))
        ue.AssetToolsHelpers.get_asset_tools().import_asset_tasks([self.task])
        loaded_asset = ue.EditorAssetLibrary.load_asset(
            self.task.imported_object_paths[0]
        )
        # ftrack metadata will be added by plugin importer
        results[self.path_component] = loaded_asset
        return results

    def _get_asset_import_task(self, options):
        UnrealImportPlugin._get_asset_import_task(self, options)
        # FBX specific
        self.task.options = ue.FbxImportUI()
        if context['asset_type'] == 'anim':
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

        UnrealAnimationImportPlugin._get_asset_import_task(self, options)


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    abcimporter = AbcAnimationUnrealImportPlugin(api_object)
    abcimporter.register()

    fbximporter = AbcAnimationUnrealImportPlugin(api_object)
    fbximporter.register()