# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from Qt import QtWidgets

import ftrack_api

from ftrack_connect_pipeline_qt import plugin as pluginWidget
from ftrack_connect_pipeline_qt.plugin.widgets.open_widget import (
    OpenBaseWidget,
)
from ftrack_connect_pipeline_qt.ui.utility.widget import group_box


class CommonDefaultOpenerImporterOptionsWidget(OpenBaseWidget):
    load_modes = ['Open']

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
        super(CommonDefaultOpenerImporterOptionsWidget, self).__init__(
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
        super(CommonDefaultOpenerImporterOptionsWidget, self).build()

        self.options_gb = group_box.GroupBox('')
        options_lay = QtWidgets.QVBoxLayout()
        self.some_test_option_cb = QtWidgets.QCheckBox('Some test option')

        options_lay.addWidget(self.some_test_option_cb)

        self.options_gb.setLayout(options_lay)

        self.layout().addWidget(self.options_gb)

    def post_build(self):
        super(CommonDefaultOpenerImporterOptionsWidget, self).post_build()

        self.some_test_option_cb.stateChanged.connect(
            self._on_set_some_test_option
        )

    def set_defaults(self):
        super(CommonDefaultOpenerImporterOptionsWidget, self).set_defaults()

        self.some_test_option_cb.setChecked(
            self.default_options.get('some_test_option', False)
        )
        self._on_set_some_test_option(self.some_test_option_cb.isChecked())

    def _on_load_mode_changed(self, radio_button):
        '''set the result options of value for the key.'''
        # if radio_button.text() == load_const.OPEN_MODE:
        #    self.options_gb.hide()
        # else:
        #    self.options_gb.show()
        super(
            CommonDefaultOpenerImporterOptionsWidget, self
        )._on_load_mode_changed(radio_button)

    def _on_set_some_test_option(self, checked):
        self._update_load_options('some_test_option', checked)

    def _update_load_options(self, k, v):
        self.default_options[k] = v
        self.set_option_result(self.default_options, key='load_options')


class CommonDefaultOpenerImporterPluginWidget(
    pluginWidget.OpenerImporterPluginWidget
):
    plugin_name = 'common_default_opener_importer'
    widget = CommonDefaultOpenerImporterOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CommonDefaultOpenerImporterPluginWidget(api_object)
    plugin.register()
