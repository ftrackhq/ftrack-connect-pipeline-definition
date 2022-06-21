# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline_qt.plugin.widgets import dynamic as dynamic_widget
from ftrack_connect_pipeline_qt.plugin import BasePluginWidget
import ftrack_api


class CommonDefaultSharedPluginWidget(BasePluginWidget):
    plugin_name = 'common_default_shared'
    plugin_type = '*'
    widget = dynamic_widget.DynamicWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonDefaultSharedPluginWidget(api_object)
    plugin.register()
