# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline_qt import plugin
from ftrack_connect_pipeline_qt.plugin.widgets import load_widget
import ftrack_api


class CommonDefaultLoaderImporterPluginWidget(
    plugin.LoaderImporterPluginWidget
):
    plugin_name = 'common_passthrough_loader_importer'
    widget = load_widget.LoadBaseWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonDefaultLoaderImporterPluginWidget(api_object)
    plugin.register()
