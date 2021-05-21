# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

from functools import partial

from ftrack_connect_pipeline_houdini import plugin
from ftrack_connect_pipeline_qt.client.widgets.options.load_widget import (
    LoadBaseWidget
)
from ftrack_connect_pipeline_houdini.constants.asset import modes as load_const

from Qt import QtCore, QtWidgets
import ftrack_api

class LoadHoudiniWidget(LoadBaseWidget):
    load_modes = list(load_const.LOAD_MODES.keys())

    OPTIONS = {
        'MergeOverwriteOnConflict': {
            'type': 'checkbox',
            'label': 'Overwrite nodes on merge conflict:',
        },
    }

    def __init__(
            self, parent=None, session=None, data=None, name=None,
            description=None, options=None, context=None
    ):
        self.widgets = {}

        super(LoadHoudiniWidget, self).__init__(
            parent=parent, session=session, data=data, name=name,
            description=description, options=options, context=context
        )

    def build(self):
        super(LoadHoudiniWidget, self).build()

        for name, option in self.OPTIONS.items():
            default = None

            if option['type'] == 'checkbox':
                widget = QtWidgets.QCheckBox(option['label'])
            elif option['type'] == 'combobox':
                self.layout().addWidget(QtWidgets.QLabel(option['label']))
                widget = QtWidgets.QComboBox()
                for item in option['options']:
                    widget.addItem(item['label'])
            elif option['type'] == 'line':
                self.layout().addWidget(QtWidgets.QLabel(option['label']))
                widget = QtWidgets.QLineEdit()

            self.widgets[name] = widget
            self.layout().addWidget(widget)

    def current_index_changed(self, name, label):
        for item in self.OPTIONS[name]['options']:
            if item['label'] == label:
                self.set_option_result(item['value'], name)

    def post_build(self):
        super(LoadHoudiniWidget, self).post_build()

        for name, widget in self.widgets.items():
            option = self.OPTIONS[name]

            update_fn = partial(self.set_option_result, key=name)
            if option['type'] == 'checkbox':
                widget.stateChanged.connect(update_fn)
            elif self.OPTIONS[name]['type'] == 'combobox':
                update_fn = partial(self.current_index_changed, name)
                widget.currentIndexChanged.connect(update_fn)
            elif option['type'] == 'line':
                widget.textChanged.connect(update_fn)

    def set_defaults(self):
        super(LoadHoudiniWidget, self).set_defaults()

        for name, widget in self.widgets.items():
            option = self.OPTIONS[name]

            if name in self.default_options:
                default = self.default_options[name]
            else:
                default_option = option.get('default_option')
                default = None
                if 0 < len(default_option or ''):
                    # Replace with that option's current value
                    default = self.options[default_option]
                if len(default or '') == 0:
                    default = option.get('default')

            if option['type'] == 'checkbox':
                if default is not None:
                    widget.setChecked(default)
            elif self.OPTIONS[name]['type'] == 'combobox':
                if default is not None:
                    idx = 0
                    for item in option['options']:
                        if item['value'] == default or item['label'] == default:
                            widget.setCurrentIndex(idx)
                        idx += 1
            elif option['type'] == 'line':
                if default is not None:
                    widget.setText(default)


    def _on_load_mode_changed(self, radio_button):
        '''set the result options of value for the key.'''
        super(LoadHoudiniWidget, self)._on_load_mode_changed(radio_button)



class LoadHoudiniPluginWidget(plugin.LoaderImporterHoudiniWidget):
    plugin_name = 'load_houdini'
    widget = LoadHoudiniWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = LoadHoudiniPluginWidget(api_object)
    plugin.register()