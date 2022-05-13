# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_qt.plugin.widgets.base_collector_widget import (
    BaseCollectorWidget,
)

import ftrack_api


class MayaDefaultPublisherCollectorOptionsWidget(BaseCollectorWidget):
    # Run fetch function on widget initialization
    auto_fetch_on_init = True

    def __init__(
        self,
        parent=None,
        session=None,
        data=None,
        name=None,
        description=None,
        options=None,
        context_id=None,
        asset_type_name=None,
    ):
        super(MayaDefaultPublisherCollectorOptionsWidget, self).__init__(
            parent=parent,
            session=session,
            data=data,
            name=name,
            description=description,
            options=options,
            context_id=context_id,
            asset_type_name=asset_type_name,
        )


class MayaDefaultPublisherCollectorPluginWidget(
    plugin.MayaPublisherCollectorPluginWidget
):
    plugin_name = 'maya_default_publisher_collector'
    widget = MayaDefaultPublisherCollectorOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MayaDefaultPublisherCollectorPluginWidget(api_object)
    plugin.register()
