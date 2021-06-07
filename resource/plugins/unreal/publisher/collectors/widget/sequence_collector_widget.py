# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

from ftrack_connect_pipeline_unreal_engine import plugin
from ftrack_connect_pipeline_qt.client.widgets.options.base_collector_widget \
    import BaseCollectorWidget

import ftrack_api


class SequenceCollectorWidget(BaseCollectorWidget):
    # Run fetch function on widget initialization
    auto_fetch_on_init = False

    def __init__(
        self, parent=None, session=None, data=None, name=None,
        description=None, options=None, context_id=None, asset_type=None
    ):
        super(SequenceCollectorWidget, self).__init__(
            parent=parent, session=session, data=data, name=name,
            description=description, options=options, context_id=context_id, asset_type=asset_type
        )


class SequenceCollectorPluginWidget(plugin.PublisherCollectorUnrealWidget):
    plugin_name = 'sequence_collector'
    widget = SequenceCollectorWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = SequenceCollectorPluginWidget(api_object)
    plugin.register()
