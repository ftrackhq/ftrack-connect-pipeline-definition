# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from functools import partial

from ftrack_connect_unreal_engine import plugin
from ftrack_connect_pipeline_qt.client.widgets.options.load_widget import (
    LoadBaseWidget
)
from ftrack_connect_unreal_engine.constants.asset import modes as load_const

from Qt import QtCore, QtWidgets
import ftrack_api

OPTIONS = {
    'MergeOverwriteOnConflict': {
        'type': 'checkbox',
        'label': 'Overwrite nodes on merge conflict:',
    },
}


class LoadUnrealWidget(LoadBaseWidget):
    load_modes = load_const.LOAD_MODES.keys()

    def __init__(
            self, parent=None, session=None, data=None, name=None,
            description=None, options=None, context=None
    ):
        self.widgets = {}

        super(LoadUnrealWidget, self).__init__(
            parent=parent, session=session, data=data, name=name,
            description=description, options=options, context=context
        )


    def build(self):
        super(LoadUnrealWidget, self).build()

        for name, option in OPTIONS.items():
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

    def post_build(self):
        super(LoadUnrealWidget, self).post_build()

        for name, widget in self.widgets.items():
            option = OPTIONS[name]

            update_fn = partial(self.set_option_result, key=name)
            if option['type'] == 'checkbox':
                widget.stateChanged.connect(update_fn)
            elif OPTIONS[name]['type'] == 'combobox':
                def currentIndexChanged(label):
                    for item in option['options']:
                        if item['label'] == label:
                            self.set_option_result(item['value'], name)
                widget.currentIndexChanged.connect(currentIndexChanged)
            elif option['type'] == 'line':
                widget.textChanged.connect(update_fn)

    def set_defaults(self):
        super(LoadUnrealWidget, self).set_defaults()

        for name, widget in self.widgets.items():
            option = OPTIONS[name]

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
            elif OPTIONS[name]['type'] == 'combobox':
                if default is not None:
                    idx = 0
                    for item in option['options']:
                        if item['value'] == default or item['label'] == default:
                            widget.setCurrentIndex(idx)
                        idx += 1
                def currentIndexChanged(label):
                    for item in option['options']:
                        if item['label'] == label:
                            self.set_option_result(item['value'], name)
            elif option['type'] == 'line':
                if default is not None:
                    widget.setText(default)


    def _on_load_mode_changed(self, radio_button):
        '''set the result options of value for the key.'''
        super(LoadUnrealWidget, self)._on_load_mode_changed(radio_button)



class LoadUnrealPluginWidget(plugin.LoaderImporterUnrealWidget):
    plugin_name = 'load_unreal'
    widget = LoadUnrealWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = LoadUnrealPluginWidget(api_object)
    plugin.register()
