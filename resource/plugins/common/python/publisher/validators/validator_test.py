# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
from ftrack_connect_pipeline import plugin
import ftrack_api

class TestValidatorPlugin(plugin.PublisherValidatorPlugin):
    plugin_name = 'publish_validator_test'

    def run(self, context_data=None, data=None, options=None):
        return True


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = TestValidatorPlugin(api_object)
    plugin.register()
