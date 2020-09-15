# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from functools import partial

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_qt.client.widgets.options import BaseOptionsWidget

from Qt import QtCore, QtWidgets, QtGui

import maya.cmds as cmds
import ftrack_api


class GeometryCollectorWidget(BaseOptionsWidget):

    def __init__(
        self, parent=None, session=None, data=None, name=None,
        description=None, options=None, context=None
    ):

        # list all perspective camera
        self.geometry_objects = cmds.ls(geometry=True, l=True)

        super(GeometryCollectorWidget, self).__init__(
            parent=parent,
            session=session, data=data, name=name,
            description=description, options=options,
            context=context)

    def build(self):
        '''build function , mostly used to create the widgets.'''
        super(GeometryCollectorWidget, self).build()
        self.add_button = QtWidgets.QPushButton("add Object")
        self.list_widget = QtWidgets.QListWidget()

        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        row = 0
        for obj in self.geometry_objects:
            item = QtWidgets.QListWidgetItem(obj)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.list_widget.addItem(item)
            row += 1

        self.layout().addWidget(self.add_button)
        self.layout().addWidget(self.list_widget)

    def contextMenuEvent(self, event):
        '''
        Executes the context menu
        '''
        self.menu = QtWidgets.QMenu(self)
        action_widget = QtWidgets.QAction('Select', self)
        action_widget.setData('ctx_select')
        self.menu.addAction(action_widget)
        self.menu.triggered.connect(self.menu_triggered)

        # add other required actions
        self.menu.exec_(QtGui.QCursor.pos())

    def post_build(self):
        super(GeometryCollectorWidget, self).post_build()
        self.add_button.clicked.connect(self._on_add_objects)
        self.list_widget.itemChanged.connect(self._on_item_changed)

        self.set_option_result(self.geometry_objects, key='geometry_objects')

    def _on_add_objects(self):
        selected_objects = cmds.ls(sl=True, l=True)
        current_objects = []
        for idx in range(0, self.list_widget.count()):
            current_objects.append(self.list_widget.item(idx).text())
        for obj in selected_objects:
            if not cmds.objectType(obj, isAType="geometryShape"):
                relatives = cmds.listRelatives(obj, f=True)
                for relative in relatives:
                    if cmds.objectType(relative, isAType="geometryShape"):
                        obj = relative
            if obj in current_objects:
                continue
            item = QtWidgets.QListWidgetItem(obj)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.list_widget.addItem(item)
            self._options['geometry_objects'].append(item.text())

    def _on_item_changed(self, item):
        if not item.checkState():
            self._options['geometry_objects'].remove(item.text())
        else:
            if item.text() not in self._options['geometry_objects']:
                self._options['geometry_objects'].append(item.text())

    def menu_triggered(self, action):
        '''
        Find and call the clicked function on the menu
        '''
        ui_callback = action.data()
        if hasattr(self, ui_callback):
            callback_fn = getattr(self, ui_callback)
            callback_fn()

    def ctx_select(self):
        '''
        Triggered when select action menu been clicked.
        '''
        selected_items = self.list_widget.selectedItems()
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
