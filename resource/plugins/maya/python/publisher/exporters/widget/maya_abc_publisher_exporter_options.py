# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from functools import partial

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_qt.plugin.widgets import BaseOptionsWidget
from ftrack_connect_pipeline_qt.ui.utility.widget import group_box

from Qt import QtWidgets

import ftrack_api


class MayaAbcPublisherExporterOptionsWidget(BaseOptionsWidget):
    '''Maya Alembic publisher options user input plugin widget'''

    auto_fetch_on_init = True

    @property
    def frames_option(self):
        '''Return current frames_option'''
        _frames_option = {
            'frameStart': str(self.options.get('frameStart')),
            'frameEnd': str(self.options.get('frameEnd')),
            'alembicEval': str(self.options.get('alembicEval', '1.0')),
        }
        return _frames_option

    @property
    def bool_options(self):
        '''Return current bool_options'''
        _bool_options = {
            'alembicAnimation': self.options.get('alembicAnimation', False),
            'alembicUvwrite': self.options.get('alembicUvwrite', True),
            'alembicWorldspace': self.options.get('alembicWorldspace', False),
            'alembicWritevisibility': self.options.get(
                'alembicWritevisibility', False
            ),
        }
        return _bool_options

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
        self.options_le = {}
        self.frame_info = {}

        super(MayaAbcPublisherExporterOptionsWidget, self).__init__(
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
        for k, v in self.options_le.items():
            if v.text() == "None":
                if k in list(result.keys()):
                    self.options_le[k].setText(str(result[k]))
                else:
                    self.options_le[k].setText("0")

    def build(self):
        '''Build function , mostly used to create the widgets.'''
        super(MayaAbcPublisherExporterOptionsWidget, self).build()

        self.option_group = group_box.GroupBox('Alembic exporter Options')
        self.option_group.setToolTip(self.description)

        self.option_layout = QtWidgets.QVBoxLayout()
        self.option_group.setLayout(self.option_layout)

        self.animation_layout = QtWidgets.QVBoxLayout()
        self.frames_widget = QtWidgets.QWidget()
        self.frames_H_layout = QtWidgets.QHBoxLayout()
        self.frames_widget.setLayout(self.frames_H_layout)
        self.option_layout.addLayout(self.animation_layout)

        self.layout().addWidget(self.option_group)
        for option, default_value in sorted(self.bool_options.items()):
            option_check = QtWidgets.QCheckBox(option)
            option_check.setChecked(default_value)

            self.options_cb[option] = option_check

            if option == 'alembicAnimation':
                self.animation_layout.addWidget(option_check)
                self.animation_layout.addWidget(self.frames_widget)
            else:
                self.option_layout.addWidget(option_check)
        for option, default_value in sorted(
            self.frames_option.items(), reverse=True
        ):
            frames_V_layout = QtWidgets.QVBoxLayout()
            option_label = QtWidgets.QLabel(option)
            option_line_edit = QtWidgets.QLineEdit(default_value)
            self.options_le[option] = option_line_edit
            frames_V_layout.addWidget(option_label)
            frames_V_layout.addWidget(option_line_edit)
            self.frames_H_layout.addLayout(frames_V_layout)
            if not self.bool_options['alembicAnimation']:
                self.frames_widget.hide()

    def post_build(self):
        super(MayaAbcPublisherExporterOptionsWidget, self).post_build()

        for option, widget in self.options_cb.items():
            if option == 'alembicAnimation':
                widget.stateChanged.connect(self._on_alembic_animation_changed)
            else:
                update_fn = partial(self.set_option_result, key=option)
                widget.stateChanged.connect(update_fn)

        for option, widget in self.options_le.items():
            update_fn = partial(self.set_option_result, key=option)
            widget.textChanged.connect(update_fn)

    def _reset_default_animation_options(self):
        for k, v in self.frames_option.items():
            self.options_le[k].setText(str(v))

    def _on_alembic_animation_changed(self, value):
        '''Updates the options dictionary with provided *path* when
        textChanged of line_edit event is triggered'''
        if value:
            self.frames_widget.show()
            self._reset_default_animation_options()
            for option, widget in self.options_le.items():
                self.set_option_result(widget.text(), key=option)
        else:
            self.frames_widget.hide()
        self.set_option_result(value, key='alembicAnimation')


class MayaAbcPublisherExporterOptionsPluginWidget(
    plugin.MayaPublisherExporterPluginWidget
):
    plugin_name = 'maya_abc_publisher_exporter'
    widget = MayaAbcPublisherExporterOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MayaAbcPublisherExporterOptionsPluginWidget(api_object)
    plugin.register()
