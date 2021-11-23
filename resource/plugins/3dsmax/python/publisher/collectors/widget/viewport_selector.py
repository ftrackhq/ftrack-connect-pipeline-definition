# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

from ftrack_connect_pipeline_3dsmax import plugin
from ftrack_connect_pipeline_qt.plugin.widgets import BaseOptionsWidget

from Qt import QtWidgets


class Viewport3dsMaxWidget(BaseOptionsWidget):
    # Run fetch function on widget initialization
    auto_fetch_on_init = True

    def __init__(
            self, parent=None, session=None, data=None, name=None,
            description=None, options=None, context_id=None, asset_type_name=None
    ):

        self.viewports = []

        super(Viewport3dsMaxWidget, self).__init__(
            parent=parent, session=session, data=data, name=name,
            description=description, options=options, context_id=context_id,
            asset_type_name=asset_type_name
        )

    def on_fetch_callback(self, result):
        ''' This function is called by the _set_internal_run_result function of
        the BaseOptionsWidget'''
        self.viewports = result
        if self.viewports:
            self.nodes_cb.setDisabled(False)
        else:
            self.nodes_cb.setDisabled(True)
        self.nodes_cb.clear()
        for item in self.viewports:
            self.nodes_cb.addItem(item[0], item[1])

    def build(self):
        super(Viewport3dsMaxWidget, self).build()
        self.nodes_cb = QtWidgets.QComboBox()
        self.layout().addWidget(self.nodes_cb)

        if self.options.get('viewport_index'):
            self.viewports.append(self.options.get('viewport_index'))

        if not self.viewports:
            self.nodes_cb.setDisabled(True)
            self.nodes_cb.addItem('No Suitable Cameras found.')
        else:
            for item in self.viewports:
                self.nodes_cb.addItem(item[0], item[1])

    def post_build(self):
        super(Viewport3dsMaxWidget, self).post_build()
        self.nodes_cb.currentIndexChanged.connect(self._process_change)
        if self.viewports:
            self.set_option_result(
                self.nodes_cb.currentData(),
                'viewport_index'
            )

    def _process_change(self, *args):
        self.set_option_result(self.nodes_cb.currentData(), 'viewport_index')


class Viewport3dsMaxPluginWidget(plugin.PublisherCollectorMaxWidget):
    plugin_name = 'viewport'
    widget = Viewport3dsMaxWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = Viewport3dsMaxPluginWidget(api_object)
    plugin.register()
