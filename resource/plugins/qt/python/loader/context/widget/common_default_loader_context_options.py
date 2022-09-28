# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline_qt import plugin
from ftrack_connect_pipeline_qt.plugin.widgets import context as context_widget
import ftrack_api


class CommonPassthroughLoaderContextPluginWidget(
    plugin.LoaderContextPluginWidget
):
    plugin_name = 'common_default_loader_context'
    widget = context_widget.LoadContextWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    load_plugin = CommonPassthroughLoaderContextPluginWidget(api_object)
    load_plugin.register()
