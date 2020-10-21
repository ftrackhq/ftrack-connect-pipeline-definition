# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_qt.client.widgets.options.base_collector_widget \
    import BaseCollectorWidget

import maya.cmds as cmds
import ftrack_api


class GenericCollectorWidget(BaseCollectorWidget):
    auto_fetch_on_init = True

    def __init__(
        self, parent=None, session=None, data=None, name=None,
        description=None, options=None, context=None
    ):
        super(GenericCollectorWidget, self).__init__(
            parent=parent, session=session, data=data, name=name,
            description=description, options=options, context=context
        )



class GenericCollectorPluginWidget(plugin.PublisherCollectorMayaWidget):
    plugin_name = 'generic_collector'
    widget = GenericCollectorWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = GenericCollectorPluginWidget(api_object)
    plugin.register()
