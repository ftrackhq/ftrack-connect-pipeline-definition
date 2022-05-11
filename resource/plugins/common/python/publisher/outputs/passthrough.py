# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class PassthroughPlugin(plugin.PublisherExporterPlugin):
    plugin_name = 'passthrough'

    def run(self, context_data=None, data=None, options=None):
        component_name = options['component_name']
        output = self.output
        for collector in data:
            output.append(collector['result'][0])

        return output


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = PassthroughPlugin(api_object)
    plugin.register()
