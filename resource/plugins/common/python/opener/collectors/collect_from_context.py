# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
from ftrack_connect_pipeline import plugin

import ftrack_api


class CollectFromContextOpenerPlugin(plugin.OpenerCollectorPlugin):
    plugin_name = 'collect_from_context'

    def run(self, context_data=None, data=None, options=None):
        version_id = context_data.get('version_id', [])

        asset_version_entity = self.session.query(
            'AssetVersion where id is "{}"'.format(version_id)
        ).one()

        component_name = options['component_name']
        file_formats = options.get('file_formats', [])
        location = self.session.pick_location()
        component_paths = []
        for component in asset_version_entity['components']:
            if component['name'] == component_name:
                component_path = location.get_filesystem_path(component)
                if (
                    file_formats
                    and os.path.splitext(component_path)[-1]
                    not in file_formats
                ):
                    self.logger.warning(
                        '{} not among accepted format {}'.format(
                            component_path, file_formats
                        )
                    )
                    continue
                component_paths.append(component_path)

        return component_paths


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectFromContextOpenerPlugin(api_object)
    plugin.register()
