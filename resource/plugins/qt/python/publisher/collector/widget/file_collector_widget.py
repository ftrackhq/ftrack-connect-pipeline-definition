# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from functools import partial

from ftrack_connect_pipeline_qt import plugin
from ftrack_connect_pipeline_qt.plugin.widgets import BaseOptionsWidget

from Qt import QtWidgets, QtCore

import ftrack_api


class FileCollectorWidget(BaseOptionsWidget):
    '''Main class to represent a context widget on a publish process'''
    #We are enabling the run button for this single widget
    enable_run_plugin = True

    def __init__(
            self, parent=None, context_id=None, asset_type_name=None, session=None,
            data=None, name=None, description=None, options=None
    ):
        '''initialise FileCollectorWidget with *parent*, *session*, *data*,
        *name*, *description*, *options*
        '''
        super(FileCollectorWidget, self).__init__(
            parent=parent, context_id=context_id, asset_type_name=asset_type_name, session=session,
            data=data, name=name, description=description, options=options
        )
        #We add a new button to fetch the data, we could also override the run_
        # build bunction or simply add a new button whatever we want, calling
        # the self.on_run_plugin() function
        self.fetch_build()

    def build(self):
        '''build function widgets.'''
        super(FileCollectorWidget, self).build()

        current_path = self.options.get('path')

        widget_layout = QtWidgets.QHBoxLayout()
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.setAlignment(QtCore.Qt.AlignTop)

        label = QtWidgets.QLabel('path')
        self.line_edit = QtWidgets.QLineEdit(current_path)
        self.browser_button = QtWidgets.QPushButton('BROWSE')
        self.browser_button.setObjectName('borderless')

        widget_layout.addWidget(label)
        widget_layout.addWidget(self.line_edit)
        widget_layout.addWidget(self.browser_button)
        self.layout().addLayout(widget_layout)

        self.file_selector = QtWidgets.QFileDialog()
        self.file_selector.setFileMode(QtWidgets.QFileDialog.ExistingFile)


    def post_build(self):
        '''hook events'''
        super(FileCollectorWidget, self).post_build()
        self.browser_button.clicked.connect(self._show_file_dialog)
        self.file_selector.fileSelected.connect(self._on_select_file)
        self.line_edit.textChanged.connect(self._on_path_changed)

    def fetch_build(self):
        '''post build function , mostly used connect widgets events.'''
        self.fetch_plugin_button = QtWidgets.QPushButton('FETCH')
        self.fetch_plugin_button.setObjectName('borderless')
        self.fetch_plugin_button.clicked.connect(
            partial(self.on_run_plugin, 'fetch')
        )
        self.layout().addWidget(self.fetch_plugin_button)

    def on_fetch_callback(self, result):
        ''' This function is called by the _set_internal_run_result function of
        the BaseOptionsWidget'''
        self.line_edit.clear()
        self.line_edit.setText(result)

    def _show_file_dialog(self):
        ''' Shows the file dialog'''
        self.file_selector.show()

    def _on_select_file(self, path):
        '''Updates the text with provided *path* when
        fileSelected of file_selector event is triggered'''
        self.line_edit.clear()
        self.line_edit.setText(path)

    def _on_path_changed(self, path):
        '''Updates the options dictionary with provided *path* when
        textChanged of line_edit event is triggered'''
        self.set_option_result(path, key='path')


class CollectorWidget(plugin.PublisherCollectorWidget):
    plugin_name = 'file_collector.widget'
    widget = FileCollectorWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CollectorWidget(api_object)
    plugin.register()
