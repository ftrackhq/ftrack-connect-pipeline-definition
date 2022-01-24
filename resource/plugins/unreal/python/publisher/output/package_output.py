# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

import os
import tempfile
from zipfile import ZipFile
import shutil

from ftrack_connect_pipeline_unreal_engine import plugin
from ftrack_connect_pipeline_unreal_engine.constants import (
    asset as asset_const,
)

import ftrack_api

import unreal as ue


class OutputUnrealPackagePlugin(plugin.PublisherOutputUnrealPlugin):
    plugin_name = 'package_output'
    _standard_structure = ftrack_api.structure.standard.StandardStructure()

    def _package_current_scene(
        self, destination_path, unreal_map_package_path, context_data
    ):

        # format package folder name
        asset_name = self._standard_structure.sanitise_for_filesystem(
            context_data['asset_name']
        )
        content_name = "{}_package".format(asset_name)

        output_filepath = os.path.normpath(
            os.path.join(destination_path, content_name)
        )

        # zip up folder
        output_zippath = "{}.zip".format(output_filepath)
        if os.path.isfile(output_zippath):
            # must delete it first,
            try:
                os.remove(output_zippath)
            except OSError as e:
                msg = (
                    'Could not delete {}. The package process will not be '
                    ' able to output to that file.'.format(output_zippath)
                )
                self.logger.error(msg)
                return False, {'message': msg}

        # process migration of current scene
        self.logger.debug(
            "Migrate package {0} to folder: {1}".format(
                unreal_map_package_path, output_zippath
            )
        )

        # create (temporary) destination folder
        try:
            # TODO: Use a context manager like tempfile.TemporaryDirectory() to
            #  safely create and cleanup temp folders and files once Unreal
            #  provides support for Python 3.2+
            tempdir_filepath = tempfile.mkdtemp(dir=destination_path)
        except OSError:
            msg = (
                'Could not create {}. The package will not be able to '
                'output to that folder.'.format(destination_path)
            )
            self.logger.error()
            return False, {'message': msg}

        # perform migration
        unreal_windows_logs_dir = os.path.join(
            ue.SystemLibrary.get_project_saved_directory(), "Logs"
        )
        self.logger.debug(
            'Detailed logs of editor output during migration '
            'found at: "{0}"'.format(unreal_windows_logs_dir)
        )

        migrated_packages = ue.FTrackConnect.get_instance().migrate_packages(
            unreal_map_package_path, tempdir_filepath
        )

        # track the assets being published
        version_dependency_ids = []
        for package_name in migrated_packages:
            asset_data = (
                ue.AssetRegistryHelpers()
                .get_asset_registry()
                .get_assets_by_package_name(package_name)
            )

            for data in asset_data:
                asset = data.get_asset()
                version_id = ue.EditorAssetLibrary.get_metadata_tag(
                    asset, "ftrack.{}".format(asset_const.VERSION_ID)
                )
                if version_id:
                    version_dependency_ids.append(version_id)

        # create a ZipFile object
        with ZipFile(output_zippath, 'w') as zipObj:
            # iterate over all the files in directory
            for folderName, subfolders, filenames in os.walk(tempdir_filepath):
                for filename in filenames:
                    # create complete and relative filepath of file in directory
                    filePath = os.path.join(folderName, filename)
                    truncated_path = os.path.relpath(
                        filePath, tempdir_filepath
                    )
                    # Add file to zip
                    zipObj.write(filePath, truncated_path)

        # remove temporary folder
        if os.path.isdir(tempdir_filepath):
            try:
                shutil.rmtree(tempdir_filepath)
            except OSError as e:
                msg = (
                    'Could not delete {}. The package process cannot '
                    'cleanup temporary package folder.'.format(
                        tempdir_filepath
                    )
                )
                self.logger.error(msg)
                return False, {'message': msg}

        return (
            os.path.isfile(output_zippath),
            output_zippath,
            version_dependency_ids,
        )

    def run(self, context_data=None, data=None, options=None):
        '''Compress all project assets to a ZIP'''
        component_name = options['component_name']

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        unreal_map_package_path = collected_objects[0]

        dest_folder = os.path.join(
            ue.SystemLibrary.get_project_saved_directory(), 'VideoCaptures'
        )

        (
            package_result,
            package_path,
            version_dependency_ids,
        ) = self._package_current_scene(
            dest_folder, unreal_map_package_path, context_data
        )
        if package_result:
            return (
                [package_path],
                {'data': {'version_dependency_ids': version_dependency_ids}},
            )
        else:
            return (
                False,
                {
                    'message': (
                        'Failed to produce package of ' 'current project.'
                    )
                },
            )


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    package_plugin = OutputUnrealPackagePlugin(api_object)
    package_plugin.register()
