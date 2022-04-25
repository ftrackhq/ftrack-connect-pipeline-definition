# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline_qt import plugin
from ftrack_connect_pipeline_qt.plugin.widgets import context as context_widget
import ftrack_api


class ContextLoadWidget(plugin.LoaderContextWidget):
    plugin_name = 'context.load'
    widget = context_widget.LoadContextWidget


class ContextOpenWidget(plugin.OpenerContextWidget):
    plugin_name = 'context.open'
    widget = context_widget.OpenContextWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    load_plugin = ContextLoadWidget(api_object)
    load_plugin.register()

    open_plugin = ContextOpenWidget(api_object)
    open_plugin.register()
