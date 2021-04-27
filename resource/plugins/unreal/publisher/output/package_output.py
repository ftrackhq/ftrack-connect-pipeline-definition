# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

import os
import tempfile
from zipfile import ZipFile
import shutil

from ftrack_connect_pipeline_unreal_engine import plugin

import ftrack_api

import unreal as ue


class OutputUnrealPackagePlugin(plugin.PublisherOutputUnrealPlugin):
    plugin_name = 'package_output'
    _standard_structure = ftrack_api.structure.standard.StandardStructure()

    def _package_current_scene(
            self,
            destination_path,
            unreal_map_package_path,
            context
    ):

        # format package folder name
        asset_name = self._standard_structure.sanitise_for_filesystem(
            context['asset_name'])
        content_name = "{}_package".format(asset_name)

        output_filepath = os.path.normpath(
            os.path.join(destination_path, content_name)
        )

        # zip up folder
        output_zippath = (
            "{}.zip".format(output_filepath)
        )
        if os.path.isfile(output_zippath):
            # must delete it first,
            try:
                os.remove(output_zippath)
            except OSError as e:
                msg = 'Could not delete {}. The package process will not be '\
                    ' able to output to that file.'.format(
                        output_zippath
                    )
                self.logger.warning(msg)
                return False, {'message':msg}

        # process migration of current scene
        self.logger.info(
            "Migrate package {0} to folder: {1}".format(
                unreal_map_package_path, output_zippath)
        )

        # create (temporary) destination folder
        try:
            # TODO: Use a context manager like tempfile.TemporaryDirectory() to
            #  safely create and cleanup temp folders and files once Unreal
            #  provides support for Python 3.2+
            tempdir_filepath = tempfile.mkdtemp(dir=destination_path)
        except OSError:
            msg = 'Could not create {}. The package will not be able to ' \
                  'output to that folder.'.format(
                    destination_path
                )
            self.logger.warning(

            )
            return False, {'message': msg}

        # perform migration
        unreal_windows_logs_dir = os.path.join(
            ue.SystemLibrary.get_project_saved_directory(), "Logs"
        )
        self.logger.info('Detailed logs of editor output during migration '
                         'found at: "{0}"'.format(unreal_windows_logs_dir))

        # create a ZipFile object
        with ZipFile(output_zippath, 'w') as zipObj:
            # iterate over all the files in directory
            for folderName, subfolders, filenames in os.walk(tempdir_filepath):
                for filename in filenames:
                    # create complete and relative filepath of file in directory
                    filePath = os.path.join(folderName, filename)
                    truncated_path = os.path.relpath(filePath, tempdir_filepath)
                    # Add file to zip
                    zipObj.write(filePath, truncated_path)

        # remove temporary folder
        if os.path.isdir(tempdir_filepath):
            try:
                shutil.rmtree(tempdir_filepath)
            except OSError as e:
                msg = 'Could not delete {}. The package process cannot ' \
                      'cleanup temporary package folder.'.format(
                    tempdir_filepath
                )
                self.logger.warning(msg)
                return False, {'message': msg}

        return os.path.isfile(output_zippath), output_zippath

    def run(self, context=None, data=None, options=None):
        ''' Compress all project assets to a ZIP '''
        component_name = options['component_name']

        dest_folder = os.path.join(
            ue.SystemLibrary.get_project_saved_directory(), 'VideoCaptures'
        )
        unreal_map = ue.EditorLevelLibrary.get_editor_world()
        unreal_map_package_path = unreal_map.get_outermost().get_path_name()

        package_result, package_path = self._package_current_scene(
            dest_folder,
            unreal_map_package_path,
            context
        )
        if package_result:
            return [package_path]
        else:
            return (False, {'message': 'Failed to produce package of '\
            'current project.'})

def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    package_plugin = OutputUnrealPackagePlugin(api_object)
    package_plugin.register()
