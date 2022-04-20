# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack
import os
import traceback
import clique

import ftrack_api

import nuke

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline.asset import asset_info as ainfo


class ImportNukeRenderPlugin(plugin.LoaderImporterNukePlugin):
    plugin_name = 'import_movie'

    def run(self, context_data=None, data=None, options=None):
        results = {}

        paths_to_import = []
        for collector in data:
            paths_to_import.extend(collector['result'])

        for component_path in paths_to_import:
            self.logger.debug('Loading render/movie {}'.format(component_path))
            resulting_node = nuke.createNode('Read', inpanel=False)
            # TODO: This code is not used, should we remove it? Check this on nuke test task
            # arguments_dict = ainfo.generate_asset_info_dict_from_args(
            #     context_data, data, options, self.session
            # )
            resulting_node['file'].fromUserText(component_path)

            results[component_path] = resulting_node.name()

        return results


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = ImportNukeRenderPlugin(api_object)
    plugin.register()
