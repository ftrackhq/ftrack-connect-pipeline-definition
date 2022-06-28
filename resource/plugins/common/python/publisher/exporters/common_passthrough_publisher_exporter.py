# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonPassThroughPublisherExporterPlugin(plugin.PublisherExporterPlugin):
    plugin_name = 'common_passthrough_publisher_exporter'

    def run(self, context_data=None, data=None, options=None):
        output = self.output
        for collector in data:
            output.append(collector['result'][0])

        return output


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonPassThroughPublisherExporterPlugin(api_object)
    plugin.register()
