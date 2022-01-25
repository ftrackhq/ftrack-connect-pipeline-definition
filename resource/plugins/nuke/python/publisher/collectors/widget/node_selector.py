# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

from functools import partial

from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline_qt.plugin.widgets import BaseOptionsWidget

from Qt import QtWidgets


class NodeSelectorWidget(BaseOptionsWidget):
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

        self.node_names = []
        self.last_selected_node = []

        super(NodeSelectorWidget, self).__init__(
            parent=parent,
            session=session,
            data=data,
            name=name,
            description=description,
            options=options,
            context_id=context_id,
            asset_type_name=asset_type_name,
        )

    def on_fetch_callback(self, result):
        '''This function is called by the _set_internal_run_result function of
        the BaseOptionsWidget'''
        self.node_names = result.get('all_nodes')
        self.last_selected_node = result.get('last_selected_node')
        if self.node_names:
            self.nodes_cb.setDisabled(False)
        else:
            self.nodes_cb.setDisabled(True)
        self.nodes_cb.clear()
        self.nodes_cb.addItems(self.node_names)

    def build(self):
        super(NodeSelectorWidget, self).build()
        self.nodes_cb = QtWidgets.QComboBox()
        self.nodes_cb.setToolTip(self.description)
        self.layout().addWidget(self.nodes_cb)

        if self.options.get('node_name'):
            self.node_names.append(self.options.get('node_name'))

        if not self.node_names:
            self.nodes_cb.addItem('No ftrack_objects found.')
            self.nodes_cb.setDisabled(True)
        else:
            self.nodes_cb.addItems(self.node_names)

    def post_build(self):
        super(NodeSelectorWidget, self).post_build()
        update_fn = partial(self.set_option_result, key='node_name')

        self.nodes_cb.editTextChanged.connect(update_fn)
        if self.last_selected_node:
            index = self.nodes_cb.findText(self.last_selected_node)
            self.nodes_cb.setCurrentIndex(index)
            self.set_option_result(self.last_selected_node, 'node_name')
        else:
            self.set_option_result(self.nodes_cb.currentText(), 'node_name')


class NodeSelectorPluginWidget(plugin.PublisherCollectorNukeWidget):
    plugin_name = 'node_selector'
    widget = NodeSelectorWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = NodeSelectorPluginWidget(api_object)
    plugin.register()
