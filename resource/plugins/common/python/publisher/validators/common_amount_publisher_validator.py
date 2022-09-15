# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonAmountPublisherValidatorPlugin(plugin.PublisherValidatorPlugin):
    plugin_name = 'common_amount_publisher_validator'

    def run(self, context_data=None, data=None, options=None):
        '''Return true if there is a correct amount of collected objects with *data* based on count value passed in *options*'''
        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])
        output = len(collected_objects) == options['count']
        return output


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonAmountPublisherValidatorPlugin(api_object)
    plugin.register()
