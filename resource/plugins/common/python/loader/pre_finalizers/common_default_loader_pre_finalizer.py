# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin
import ftrack_api


class CommonDefaultLoaderPreFinalizerPlugin(plugin.LoaderPreFinalizerPlugin):
    plugin_name = 'common_default_loader_pre_finalizer'

    def run(self, context_data=None, data=None, options=None):
        user_data = None
        for step in data:
            if step['type'] != 'component':
                continue

            for stage in step['result']:
                if stage['type'] != 'post_import':
                    continue

                user_data = stage['result'][0].get('user_data')

        if user_data:
            print("user_data message: {}".format(user_data.get('message')))
            print("user_data data: {}".format(user_data.get('data')))
        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonDefaultLoaderPreFinalizerPlugin(api_object)
    plugin.register()
