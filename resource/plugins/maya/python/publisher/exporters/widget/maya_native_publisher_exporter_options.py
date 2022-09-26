# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from functools import partial

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_qt.plugin.widgets.dynamic import DynamicWidget
from ftrack_connect_pipeline_qt.ui.utility.widget import group_box

from Qt import QtWidgets, QtCore

import ftrack_api


class MayaDefaultPublisherExporterOptionsWidget(DynamicWidget):
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

        self.options_cb = {}

        super(MayaDefaultPublisherExporterOptionsWidget, self).__init__(
            parent=parent,
            session=session,
            data=data,
            name=name,
            description=description,
            options=options,
            context_id=context_id,
            asset_type_name=asset_type_name,
        )

    def build(self):
        '''build function , mostly used to create the widgets.'''

        options = {
            'constructionHistory': False,
            'channels': False,
            'preserveReferences': False,
            'shader': False,
            'constraints': False,
            'expressions': False,
            'type': [
                {
                    'label': 'mayaBinary (.mb)',
                    'value': 'mayaBinary',
                    'default': True,
                },
                {'label': 'mayaAscii (.ma)', 'value': 'mayaAscii'},
            ],
        }
        # Update current options with the given ones from definitions and store
        self.update(options)

        self.option_group = group_box.GroupBox('Maya exporter Options')
        self.option_group.setToolTip(self.description)

        self.option_layout = QtWidgets.QVBoxLayout()
        self.option_group.setLayout(self.option_layout)

        self.layout().addWidget(self.option_group)

        # Call the super build to automatically generate the options
        super(MayaDefaultPublisherExporterOptionsWidget, self).build()

    def _register_widget(self, name, widget):
        '''Register *widget* with *name* and add it to main layout.'''
        # Overriding this method in order to attach the widget to the option_layout
        widget_layout = QtWidgets.QHBoxLayout()
        widget_layout.setContentsMargins(1, 2, 1, 2)
        widget_layout.setAlignment(QtCore.Qt.AlignTop)
        label = QtWidgets.QLabel(name)

        widget_layout.addWidget(label)
        widget_layout.addWidget(widget)
        self.option_layout.addLayout(widget_layout)


class MayaDefaultPublisherExporterOptionsPluginWidget(
    plugin.MayaPublisherExporterPluginWidget
):
    plugin_name = 'maya_native_publisher_exporter'
    widget = MayaDefaultPublisherExporterOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MayaDefaultPublisherExporterOptionsPluginWidget(api_object)
    plugin.register()
