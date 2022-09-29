# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from functools import partial

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_qt.plugin.widgets.dynamic import DynamicWidget
from ftrack_connect_pipeline_qt.ui.utility.widget import group_box

from Qt import QtWidgets, QtCore

import ftrack_api


class MayaDefaultPublisherExporterOptionsWidget(DynamicWidget):
    '''Maya native binary or ASCII publisher options user input plugin widget'''

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

    def define_options(self):
        '''Default renderable options for dynamic widget'''
        return {
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
                {
                    'label': 'mayaAscii (.ma)',
                    'value': 'mayaAscii',
                },
            ],
        }

    def build(self):
        '''build function , mostly used to create the widgets.'''

        # Update current options with the given ones from definitions and store
        self.update(self.define_options())

        self.option_group = group_box.GroupBox('Maya exporter Options')
        self.option_group.setToolTip(self.description)

        self.option_layout = QtWidgets.QVBoxLayout()
        self.option_group.setLayout(self.option_layout)

        self.layout().addWidget(self.option_group)

        # Call the super build to automatically generate the option widgets
        super(MayaDefaultPublisherExporterOptionsWidget, self).build()

    def get_parent_layout(self, name):
        '''Add widgets to group box'''
        return self.option_layout


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
