# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonNonEmptyPublisherValidatorPlugin(plugin.PublisherValidatorPlugin):
    plugin_name = 'common_non_empty_publisher_validator'

    def run(self, context_data=None, data=None, options=None):
        '''Validate that there are collected objects in *data* and they have a value'''

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])
        output = len(collected_objects) > 0 and all(
            bool(datum is not None and len(datum) > 0)
            for datum in collected_objects
        )
        return output


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonNonEmptyPublisherValidatorPlugin(api_object)
    plugin.register()
