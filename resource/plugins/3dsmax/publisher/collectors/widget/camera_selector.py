# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import ftrack_api

from functools import partial

from ftrack_connect_pipeline_3dsmax import plugin
from ftrack_connect_pipeline_qt.client.widgets.options import BaseOptionsWidget

from Qt import QtWidgets


class Camera3dsMaxWidget(BaseOptionsWidget):
    # Run fetch function on widget initialization
    auto_fetch_on_init = True

    def __init__(
            self, parent=None, session=None, data=None, name=None,
            description=None, options=None, context=None
    ):
        self.cameras = []

        super(Camera3dsMaxWidget, self).__init__(
            parent=parent, session=session, data=data, name=name,
            description=description, options=options, context=context
        )

    def on_fetch_callback(self, result):
        ''' This function is called by the _set_internal_run_result function of
        the BaseOptionsWidget'''
        self.cameras = result
        if self.cameras:
            self.cameras_cb.setDisabled(False)
        else:
            self.cameras_cb.setDisabled(True)
        self.cameras_cb.clear()
        self.cameras_cb.addItems(self.cameras)
        self.set_option_result(self.cameras[0], key='camera_name')

    def build(self):
        super(Camera3dsMaxWidget, self).build()
        self.cameras_cb = QtWidgets.QComboBox()
        self.layout().addWidget(self.cameras_cb)

        if self.options.get('camera_name'):
            self.cameras.append(self.options.get('camera_name'))

        if not self.cameras:
            self.cameras_cb.setDisabled(True)
            self.cameras_cb.addItem('No Suitable Cameras found.')
        else:
            self.cameras_cb.addItems(self.cameras)

    def post_build(self):
        super(Camera3dsMaxWidget, self).post_build()
        update_fn = partial(self.set_option_result, key='camera_name')
        self.cameras_cb.editTextChanged.connect(update_fn)
        if self.cameras:
            self.set_option_result(self.cameras[0], key='camera_name')


class Camera3dsMaxPluginWidget(plugin.PublisherCollectorMaxWidget):
    plugin_name = 'camera'
    widget = Camera3dsMaxWidget

def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = Camera3dsMaxPluginWidget(api_object)
    plugin.register()
