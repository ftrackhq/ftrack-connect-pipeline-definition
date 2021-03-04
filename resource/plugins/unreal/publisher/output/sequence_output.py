# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import os
import sys
import subprocess

from ftrack_connect_pipeline_unreal_engine import plugin

import ftrack_api

import unreal as ue


class OutputUnrealPlugin(plugin.PublisherOutputUnrealPlugin):
    _standard_structure = ftrack_api.structure.standard.StandardStructure()

    def debug(s):
        import threading
        print('@@@: [thread:{}] {}'.format(threading.currentThread, s))

    def _render(
        self,
        destination_path,
        unreal_map_path,
        sequence_path,
        content_name,
        fps,
        is_image_sequence=False,
    ):
        def __generate_target_file_path(destination_path, content_name):
            # Sequencer can only render to avi file format
            output_filename = (
                "{}.avi".format(content_name)
                if not is_image_sequence
                else ("{}".format(content_name) + '.{frame}.exr')
            )
            output_filepath = os.path.join(destination_path, output_filename)
            return output_filepath

        def __build_process_args(
            destination_path,
            unreal_map_path,
            sequence_path,
            content_name,
            fps,
            is_image_sequence,
        ):
            # Render the sequence to a movie file using the following
            # command-line arguments
            cmdline_args = []

            # Note that any command-line arguments (usually paths) that could
            # contain spaces must be enclosed between quotes
            unreal_exec_path = '"{}"'.format(sys.executable)

            # Get the Unreal project to load
            unreal_project_filename = "{}.uproject".format(
                ue.SystemLibrary.get_game_name()
            )
            unreal_project_path = os.path.join(
                ue.SystemLibrary.get_project_directory(),
                unreal_project_filename,
            )
            unreal_project_path = '"{}"'.format(unreal_project_path)

            # Important to keep the order for these arguments
            cmdline_args.append(unreal_exec_path)  # Unreal executable path
            cmdline_args.append(unreal_project_path)  # Unreal project
            cmdline_args.append(
                unreal_map_path
            )  # Level to load for rendering the sequence

            # Command-line arguments for Sequencer Render to Movie
            # See: https://docs.unrealengine.com/en-us/Engine/Sequencer/Workflow/RenderingCmdLine
            sequence_path = "-LevelSequence={}".format(sequence_path)
            cmdline_args.append(sequence_path)  # The sequence to render

            output_path = '-MovieFolder="{}"'.format(destination_path)
            cmdline_args.append(
                output_path
            )  # output folder, must match the work template

            movie_name_arg = "-MovieName={}".format(content_name)
            cmdline_args.append(movie_name_arg)  # output filename

            cmdline_args.append("-game")
            cmdline_args.append(
                "-MovieSceneCaptureType=/Script/MovieSceneCapture.AutomatedLevelSequenceCapture"
            )
            cmdline_args.append("-ForceRes")
            cmdline_args.append("-Windowed")
            cmdline_args.append("-MovieCinematicMode=yes")
            if is_image_sequence:
                cmdline_args.append("-MovieFormat=EXR")
            else:
                cmdline_args.append("-MovieFormat=Video")
            cmdline_args.append("-MovieFrameRate=" + str(fps))
            ftrack_capture_args = (
                ue.FTrackConnect.get_instance().get_capture_arguments()
            )
            cmdline_args.append(ftrack_capture_args)
            cmdline_args.append("-NoTextureStreaming")
            cmdline_args.append("-NoLoadingScreen")
            cmdline_args.append("-NoScreenMessages")
            return cmdline_args

        output_filepath = __generate_target_file_path(
            destination_path, content_name
        )
        if os.path.isfile(output_filepath):
            # Must delete it first, otherwise the Sequencer will add a number
            # in the filename
            try:
                os.remove(output_filepath)
            except OSError as e:
                self.logger.warning(
                    "Couldn't delete {}. The Sequencer won't be able to output the movie to that file.".format(
                        output_filepath
                    )
                )
                return False, None

        # Unreal will be started in game mode to render the video
        cmdline_args = __build_process_args(
            destination_path,
            unreal_map_path,
            sequence_path,
            content_name,
            fps,
            is_image_sequence,
        )

        self.logger.info(
            "Sequencer command-line arguments: {}".format(cmdline_args)
        )

        # Send the arguments as a single string because some arguments could
        # contain spaces and we don't want those to be quoted
        envs = os.environ.copy()
        envs.update({'FTRACK_CONNECT_DISABLE_INTEGRATION_LOAD':"1"})
        subprocess.call(" ".join(cmdline_args), env = envs)

        return os.path.isfile(output_filepath), output_filepath

class OutputUnrealSequencePlugin(OutputUnrealPlugin):
    plugin_name = 'sequence_output'

    def run(self, context=None, data=None, options=None):
        ''' Render an image sequence '''
        component_name = options['component_name']
        masterSequence = data[0]

        dest_folder = os.path.join(
            ue.SystemLibrary.get_project_saved_directory(), 'VideoCaptures'
        )
        unreal_map = ue.EditorLevelLibrary.get_editor_world()
        unreal_map_package_path = unreal_map.get_outermost().get_path_name()
        unreal_map_path = unreal_map.get_path_name()
        unreal_asset_path = masterSequence.get_path_name()

        asset_name = self._standard_structure.sanitise_for_filesystem(context['asset_name'])

        # Publish Component: image_sequence

        rendered, path = self._render(
            dest_folder,
            unreal_map_path,
            unreal_asset_path,
            asset_name,
            masterSequence.get_display_rate().numerator,
            True,
        )

        # try to get start and end frames from sequence this allow local control for test publish(subset of sequence)
        frameStart = masterSequence.get_playback_start()
        frameEnd = masterSequence.get_playback_end() - 1
        base_file_path = path[:-12] if path.endswith('.{frame}.exr') else path

        new_file_path = "{0}.%04d.{1} [{2}-{3}]".format(
            base_file_path, 'exr', frameStart, frameEnd
        )

        return {component_name: new_file_path}

class OutputUnrealReviewablePlugin(OutputUnrealPlugin):
    plugin_name = 'reviewable_output'

    def run(self, context=None, data=None, options=None):
        component_name = options['component_name']
        masterSequence = data[0]

        dest_folder = os.path.join(
            ue.SystemLibrary.get_project_saved_directory(), 'VideoCaptures'
        )
        unreal_map = ue.EditorLevelLibrary.get_editor_world()
        unreal_map_path = unreal_map.get_path_name()
        unreal_asset_path = masterSequence.get_path_name()

        asset_name = self._standard_structure.sanitise_for_filesystem(context['asset_name'])

        movie_name = "{}_reviewable".format(asset_name)
        rendered, path = self._render(
            dest_folder,
            unreal_map_path,
            unreal_asset_path,
            movie_name,
            masterSequence.get_display_rate().numerator,
        )

        return {component_name: path}

def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    scene_plugin = OutputUnrealSequencePlugin(api_object)
    scene_plugin.register()

    nodes_plugin = OutputUnrealReviewablePlugin(api_object)
    nodes_plugin.register()