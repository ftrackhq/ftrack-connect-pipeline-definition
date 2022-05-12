# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline_qt import plugin
from ftrack_connect_pipeline_qt.plugin.widgets import context as context_widget
import ftrack_api


class ContextLoadPluginWidget(plugin.LoaderContextPluginWidget):
    plugin_name = 'context.load'
    widget = context_widget.LoadContextWidget


class ContextOpenPluginWidget(plugin.OpenerContextPluginWidget):
    plugin_name = 'context.open'
    widget = context_widget.OpenContextWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    load_plugin = ContextLoadPluginWidget(api_object)
    load_plugin.register()

    open_plugin = ContextOpenPluginWidget(api_object)
    open_plugin.register()
