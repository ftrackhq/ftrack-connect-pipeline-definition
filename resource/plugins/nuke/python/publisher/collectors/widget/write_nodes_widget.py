# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

from functools import partial

from Qt import QtWidgets


from ftrack_connect_pipeline_nuke import plugin
from ftrack_connect_pipeline_qt.client.widgets.options import BaseOptionsWidget



class WriteNodesNukeWidget(BaseOptionsWidget):
    # Run fetch function on widget initialization
    auto_fetch_on_init = True

    def __init__(
            self, parent=None, session=None, data=None, name=None,
            description=None, options=None, context_id=None, asset_type_name=None
    ):

        self.node_names = []

        super(WriteNodesNukeWidget, self).__init__(
            parent=parent,
            session=session, data=data, name=name,
            description=description, options=options,
            context_id=context_id, asset_type_name=asset_type_name
        )

    def on_fetch_callback(self, result):
        ''' This function is called by the _set_internal_run_result function of
        the BaseOptionsWidget'''
        self.node_names = result
        if self.node_names:
            self.nodes_cb.setDisabled(False)
        else:
            self.nodes_cb.setDisabled(True)
        self.nodes_cb.clear()
        self.nodes_cb.addItems(self.node_names)

    def build(self):
        super(WriteNodesNukeWidget, self).build()
        self.nodes_cb = QtWidgets.QComboBox()
        self.layout().addWidget(self.nodes_cb)

        if self.options.get('node_name'):
            self.node_names.append(self.options.get('node_name'))

        if not self.node_names:
            self.nodes_cb.addItem('No Write Node found.')
            self.nodes_cb.setDisabled(True)
        else:
            self.nodes_cb.addItems(self.node_names)

    def post_build(self):
        super(WriteNodesNukeWidget, self).post_build()
        update_fn = partial(self.set_option_result, key='node_name')

        self.nodes_cb.editTextChanged.connect(update_fn)
        if self.node_names:
            self.set_option_result(self.node_names[0], 'node_name')


class WriteNodesPluginWidget(plugin.PublisherCollectorNukeWidget):
    plugin_name = 'write_node'
    widget = WriteNodesNukeWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = WriteNodesPluginWidget(api_object)
    plugin.register()
