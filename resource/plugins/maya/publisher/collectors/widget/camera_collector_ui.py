# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from functools import partial

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_qt.client.widgets.options import BaseOptionsWidget

from Qt import QtWidgets

import ftrack_api


class CameraCollectorWidget(BaseOptionsWidget):
    auto_fetch_on_init = True

    def __init__(
        self, parent=None, session=None, data=None, name=None,
        description=None, options=None, context=None
    ):

        self.maya_cameras = []
        super(CameraCollectorWidget, self).__init__(
            parent=parent,
            session=session, data=data, name=name,
            description=description, options=options,
            context=context)

    def on_fetch_callback(self, result):
        ''' This function is called by the _set_internal_run_result function of
        the BaseOptionsWidget'''
        self.maya_cameras = result
        if self.maya_cameras:
            self.cameras.setDisabled(False)
        else:
            self.cameras.setDisabled(True)
        self.cameras.clear()
        self.cameras.addItems(result)

    def build(self):
        '''build function , mostly used to create the widgets.'''
        super(CameraCollectorWidget, self).build()
        self.cameras = QtWidgets.QComboBox()
        self.cameras.setToolTip(self.description)
        self.layout().addWidget(self.cameras)

        if self.options.get('camera_name'):
            self.maya_cameras.append(self.options.get('camera_name'))

        if not self.maya_cameras:
            self.cameras.setDisabled(True)
            self.cameras.addItem('No Suitable Cameras found.')
        else:
            self.cameras.addItems(self.maya_cameras)

    def post_build(self):
        super(CameraCollectorWidget, self).post_build()
        update_fn = partial(self.set_option_result, key='camera_name')

        self.cameras.editTextChanged.connect(update_fn)
        if self.maya_cameras:
            self.set_option_result(self.maya_cameras[0], key='camera_name')


class CameraCollectorPluginWidget(plugin.PublisherCollectorMayaWidget):
    plugin_name = 'camera'
    widget = CameraCollectorWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = CameraCollectorPluginWidget(api_object)
    plugin.register()
