# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

from ftrack_connect_pipeline_unreal_engine import plugin
from ftrack_connect_pipeline_qt.client.widgets.options.base_collector_widget \
    import BaseCollectorWidget

import ftrack_api


class AssetsCollectorWidget(BaseCollectorWidget):
    # Run fetch function on widget initialization
    auto_fetch_on_init = False

    def __init__(
        self, parent=None, session=None, data=None, name=None,
        description=None, options=None, context=None
    ):
        super(AssetsCollectorWidget, self).__init__(
            parent=parent, session=session, data=data, name=name,
            description=description, options=options, context=context
        )


class AssetsCollectorPluginWidget(plugin.PublisherCollectorUnrealWidget):
    plugin_name = 'assets_collector'
    widget = AssetsCollectorWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = AssetsCollectorPluginWidget(api_object)
    plugin.register()
