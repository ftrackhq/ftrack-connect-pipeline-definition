# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from functools import partial

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_qt.plugin.widgets.dynamic import DynamicWidget

from Qt import QtWidgets

import ftrack_api


class MayaOptionsWidget(DynamicWidget):
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

        super(MayaOptionsWidget, self).__init__(
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
        super(MayaOptionsWidget, self).build()

        options = [
            'history',
            'channels',
            'preserve_reference',
            'shader',
            'constraints',
            'expressions',
        ]
        self.option_group = QtWidgets.QGroupBox('Maya Output Options')
        self.option_group.setToolTip(self.description)

        self.option_layout = QtWidgets.QVBoxLayout()
        self.option_group.setLayout(self.option_layout)

        self.file_type_combo = QtWidgets.QComboBox()
        self.file_type_combo.addItem('mayaBinary (.mb)')
        self.file_type_combo.addItem('mayaAscii (.ma)')
        self.option_layout.addWidget(self.file_type_combo)

        for option in options:
            option_check = QtWidgets.QCheckBox(option)

            self.options_cb[option] = option_check
            self.option_layout.addWidget(option_check)

        self.layout().addWidget(self.option_group)

    def post_build(self):
        super(MayaOptionsWidget, self).post_build()

        for option, widget in self.options_cb.items():
            update_fn = partial(self.set_option_result, key=option)
            widget.stateChanged.connect(update_fn)

        self.file_type_combo.currentIndexChanged.connect(
            self._on_file_type_set
        )

    def _on_file_type_set(self, index):
        value = self.file_type_combo.currentText()
        self.set_option_result(value.split(' ')[0], 'file_type')


class MayaOptionsPluginWidget(plugin.PublisherOutputMayaWidget):
    plugin_name = 'maya_options'
    widget = MayaOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MayaOptionsPluginWidget(api_object)
    plugin.register()
