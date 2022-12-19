# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class UnrealProjectPublisherContextPlugin(plugin.PublisherContextPlugin):
    '''Unreal project publisher context plugin'''

    plugin_name = 'unreal_project_publisher_context'

    def run(self, context_data=None, data=None, options=None):
        '''Find out the project context'''

        output = self.output
        output.update(options)
        return output


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealProjectPublisherContextPlugin(api_object)
    plugin.register()
