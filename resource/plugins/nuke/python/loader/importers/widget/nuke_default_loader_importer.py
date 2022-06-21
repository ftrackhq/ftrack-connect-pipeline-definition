# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline_qt.plugin.widgets.load_widget import (
    LoadBaseWidget,
)
from ftrack_connect_pipeline_nuke.constants.asset import modes as load_const


class NukeDefaultLoaderImporterOptionsWidget(LoadBaseWidget):
    load_modes = list(load_const.LOAD_MODES.keys())


class NukeDefaultLoaderImporterPluginWidget(
    plugin.NukeLoaderImporterPluginWidget
):
    plugin_name = 'nuke_default_loader_importer'
    widget = NukeDefaultLoaderImporterOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = NukeDefaultLoaderImporterPluginWidget(api_object)
    plugin.register()
