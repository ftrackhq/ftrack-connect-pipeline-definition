# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack
import os
import traceback
import clique

import ftrack_api

import nuke

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline.asset import asset_info
from ftrack_connect_pipeline_nuke.constants import asset as asset_const
from ftrack_connect_pipeline_nuke.utils import custom_commands as nuke_utils


class ImportNukeImageSequencePlugin(plugin.LoaderImporterNukePlugin):
    plugin_name = 'import_image_sequence'

    def run(self, context_data=None, data=None, options=None):
        results = {}

        paths_to_import = []
        for collector in data:
            paths_to_import.extend(collector['result'])

        for component_path in paths_to_import:
            self.logger.debug(
                'Loading image sequence {}'.format(component_path)
            )
            resulting_node = nuke.createNode('Read', inpanel=False)
            arguments_dict = asset_info.generate_asset_info_dict_from_args(
                context_data, data, options, self.session
            )
            asset_info_class = asset_info.FtrackAssetInfo(arguments_dict)
            # unique_name = nuke_utils.get_unique_scene_name(
            #    '{}_{}'.format(
            #        asset_info_class[asset_const.ASSET_NAME],
            #        asset_info_class[asset_const.COMPONENT_NAME],
            #    )
            # )
            # resulting_node['name'].setValue(unique_name)
            resulting_node['file'].fromUserText(component_path)
            # Detect frame range based on files on disk (safe)
            if component_path.find('%0') > 0:
                try:
                    directory, sequence_pattern = os.path.split(component_path)
                    if os.path.exists(directory):
                        prefix = sequence_pattern[: sequence_pattern.find('%')]
                        suffix = sequence_pattern[
                            sequence_pattern.rfind('d') + 1
                        ]
                        files = []
                        for filename in os.listdir(directory):
                            if filename.startswith(
                                prefix
                            ) and filename.endswith(suffix):
                                files.append(filename)
                        collection = clique.assemble(files)
                        range = collection.format('{range}')
                        read_first = int(range.split('-')[0])
                        read_last = int(range.split('-')[1])
                        resulting_node["first"].setValue(read_first)
                        resulting_node["last"].setValue(read_last)
                        resulting_node["origfirst"].setValue(read_first)
                        resulting_node["origlast"].setValue(read_last)
                except:
                    self.logger.warning(traceback.format_exc())

            results[component_path] = resulting_node.name()

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = ImportNukeImageSequencePlugin(api_object)
    plugin.register()
