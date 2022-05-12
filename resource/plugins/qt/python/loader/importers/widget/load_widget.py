# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline_qt import plugin
from ftrack_connect_pipeline_qt.plugin.widgets import load_widget
import ftrack_api


class LoadBasePluginPluginWidget(plugin.LoaderImporterPluginWidget):
    plugin_name = 'load_base'
    widget = load_widget.LoadBaseWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = LoadBasePluginPluginWidget(api_object)
    plugin.register()
