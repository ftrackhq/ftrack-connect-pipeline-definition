# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import os

import unreal

import ftrack_api

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)


class UnrealReviewablePublisherExporterPlugin(
    plugin.UnrealPublisherExporterPlugin
):
    plugin_name = 'unreal_reviewable_publisher_exporter'

    _standard_structure = ftrack_api.structure.standard.StandardStructure()

    def run(self, context_data=None, data=None, options=None):
        '''Export a Unreal reviewable to a temp file for publish'''
        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])

        master_sequence = None

        all_sequences = unreal_utils.get_all_sequences(as_names=False)
        for seq_name in collected_objects:
            for seq in all_sequences:
                if seq.get_name() == seq_name or seq_name.startswith(
                    '{}_'.format(seq.get_name())
                ):
                    master_sequence = seq
                    break
            if master_sequence:
                break

        destination_path = os.path.join(
            unreal.SystemLibrary.get_project_saved_directory(), 'VideoCaptures'
        )
        unreal_map = unreal.EditorLevelLibrary.get_editor_world()
        unreal_map_path = unreal_map.get_path_name()
        unreal_asset_path = master_sequence.get_path_name()

        asset_name = self._standard_structure.sanitise_for_filesystem(
            context_data['asset_name']
        )

        movie_name = '{}_reviewable'.format(asset_name)
        rendered, path = unreal_utils.render(
            unreal_asset_path,
            unreal_map_path,
            movie_name,
            destination_path,
            master_sequence.get_display_rate().numerator,
            unreal_utils.compile_capture_args(options),
            self.logger,
        )

        return [path]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealReviewablePublisherExporterPlugin(api_object)
    plugin.register()
