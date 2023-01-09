# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api

from ftrack_connect_pipeline_unreal.utils import (
    custom_commands as unreal_utils,
)


class UnrealProjectPublisherContextPlugin(plugin.PublisherContextPlugin):
    '''Unreal project publisher context plugin'''

    plugin_name = 'unreal_project_publisher_context'

    def run(self, context_data=None, data=None, options=None):
        '''Find out the project context'''

        root_context_id = options.get('root_context_id')
        if options.get('asset_parent_context_id') is None:
            asset_path = options.get('ftrack_asset_path')
            # Need to create the parent asset context
            try:
                asset_build = unreal_utils.push_ftrack_asset_path_to_server(
                    root_context_id, asset_path, self.session
                )
                self.logger.info(
                    'asset_build {} structure checks done'.format(
                        asset_build['name']
                    )
                )
                options['root_context_id'] = asset_build['id']
            except Exception as e:
                raise Exception(
                    'Failed to create project level asset build for asset "{}", '
                    'please check your ftrack permissions and for any existing '
                    'entities in conflict.\n\nDetails: {}'.format(
                        asset_path, e
                    )
                )

        output = self.output
        output.update(options)
        return output


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealProjectPublisherContextPlugin(api_object)
    plugin.register()
