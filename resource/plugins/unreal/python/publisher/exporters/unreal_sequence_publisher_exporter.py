# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import os

import unreal

import ftrack_api

from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)
from ftrack_connect_pipeline_unreal import plugin


class UnrealSequencePublisherExporterPlugin(
    plugin.UnrealPublisherExporterPlugin
):
    '''Unreal file sequence exporter plugin'''

    plugin_name = 'unreal_sequence_publisher_exporter'

    _standard_structure = ftrack_api.structure.standard.StandardStructure()

    def run(self, context_data=None, data=None, options=None):
        '''Render and export a image file sequence from the selected sequence given
        in *data* and options given with *options*.'''

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        master_sequence = None

        seq_name = None
        all_sequences = unreal_utils.get_all_sequences(as_names=False)
        for _seq_name in collected_objects:
            seq_name = _seq_name
            for seq in all_sequences:
                if seq.get_name() == _seq_name or _seq_name.startswith(
                    '{}_'.format(seq.get_name())
                ):
                    master_sequence = seq
                    break
            if master_sequence:
                break

        if master_sequence is None:
            return False, {
                'message': 'Sequence {} not found, please refresh publisher!'.format(
                    seq_name
                )
            }

        # Determine next expected version on context
        next_version = 1
        task = self.session.query(
            'Task where id={}'.format(context_data['context_id'])
        ).one()
        asset = self.session.query(
            'Asset where parent.id={} and name={}'.format(
                task['parent']['id'], context_data['asset_name']
            )
        ).first()
        if asset:
            latest_version = self.session.query(
                'AssetVersion where asset.id={} and is_latest_version is "True"'.format(
                    asset['id']
                )
            ).first()
            if latest_version:
                next_version = latest_version['version'] + 1
        destination_path = os.path.join(
            unreal.SystemLibrary.get_project_saved_directory(),
            'VideoCaptures',
            seq_name,
            'v{}'.format(next_version),
        )
        self.logger.info(
            'Rendering sequence to next expected version folder: {}'.format(
                destination_path
            )
        )

        unreal_map = unreal.EditorLevelLibrary.get_editor_world()
        unreal_map_path = unreal_map.get_path_name()
        unreal_asset_path = master_sequence.get_path_name()

        asset_name = self._standard_structure.sanitise_for_filesystem(
            context_data['asset_name']
        )

        file_format = options.get('file_format', 'exr')
        result = unreal_utils.render(
            unreal_asset_path,
            unreal_map_path,
            asset_name,
            destination_path,
            master_sequence.get_display_rate().numerator,
            unreal_utils.compile_capture_args(options),
            self.logger,
            image_format=file_format,
        )

        if isinstance(result, tuple):
            return result

        path = result

        # try to get start and end frames from sequence this allow local
        # control for test publish(subset of sequence)
        frameStart = master_sequence.get_playback_start()
        frameEnd = master_sequence.get_playback_end() - 1
        base_file_path = (
            path[:-12]
            if path.endswith('.{frame}.%s' % (file_format))
            else path
        )

        new_file_path = '{0}.%04d.{1} [{2}-{3}]'.format(
            base_file_path, file_format, frameStart, frameEnd
        )

        return [new_file_path]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    output_plugin = UnrealSequencePublisherExporterPlugin(api_object)
    output_plugin.register()
