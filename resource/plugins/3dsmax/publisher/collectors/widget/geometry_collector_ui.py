# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_3dsmax import plugin
from ftrack_connect_pipeline_qt.client.widgets.options.base_collector_widget \
    import BaseCollectorWidget

import ftrack_api
from pymxs import runtime as rt


class GeometryCollectorWidget(BaseCollectorWidget):

    def __init__(
        self, parent=None, session=None, data=None, name=None,
        description=None, options=None, context=None
    ):
        super(GeometryCollectorWidget, self).__init__(
            parent=parent, session=session, data=data, name=name,
            description=description, options=options, context=context
        )

    def collect_objects(self):
        collected_objects = []
        all_objects = rt.objects
        for obj in all_objects:
            if rt.superClassOf(obj) == rt.GeometryClass:
                collected_objects.append(obj.name)

        self._collected_objects = collected_objects

    def _on_add_objects(self):
        selected_objects = rt.selection
        check_type = rt.GeometryClass
        current_objects = self.get_current_objects()
        for obj in selected_objects:
            if (
                    rt.superClassOf(obj) == check_type and
                    obj.name not in current_objects
            ):
                self.add_object(obj.name)

    def ctx_select(self):
        '''
        Triggered when select action menu been clicked.
        '''
        selected_items  = super(GeometryCollectorWidget, self).ctx_select()
        nodes_to_select=[]
        for item in selected_items:
            nodes_to_select .append(rt.getNodeByName(item))
        rt.select(nodes_to_select)



class GeometryCollectorPluginWidget(plugin.PublisherCollectorMaxWidget):
    plugin_name = 'geometry_collector'
    widget = GeometryCollectorWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = GeometryCollectorPluginWidget(api_object)
    plugin.register()