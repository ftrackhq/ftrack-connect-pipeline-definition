# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_qt.client.widgets.options.base_collector_widget \
    import BaseCollectorWidget

import maya.cmds as cmds
import ftrack_api


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
        self._collected_objects = cmds.ls(geometry=True, l=True)

    def _on_add_objects(self):
        selected_objects = cmds.ls(sl=True, l=True)
        check_type = "geometryShape"
        current_objects = self.get_current_objects()
        for obj in selected_objects:
            if not cmds.objectType(obj, isAType=check_type):
                relatives = cmds.listRelatives(obj, f=True)
                for relative in relatives:
                    if cmds.objectType(relative, isAType=check_type):
                        obj = relative
            if obj in current_objects:
                continue
            self.add_object(obj)

    def ctx_select(self):
        '''
        Triggered when select action menu been clicked.
        '''
        selected_items  = super(GeometryCollectorWidget, self).ctx_select()
        cmds.select(cl=True)
        for item in selected_items:
            cmds.select(item.text(), add=True)



class GeometryCollectorPluginWidget(plugin.PublisherCollectorMayaWidget):
    plugin_name = 'geometry_collector'
    widget = GeometryCollectorWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = GeometryCollectorPluginWidget(api_object)
    plugin.register()