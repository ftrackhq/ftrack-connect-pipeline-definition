# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from functools import partial

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_qt.plugin.widgets.dynamic import DynamicWidget
from ftrack_connect_pipeline_qt.ui.utility.widget import group_box

from Qt import QtWidgets

import ftrack_api


class MayaFbxPublisherExporterOptionsWidget(DynamicWidget):
    '''Maya FBX publisher options user input plugin widget'''

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

        super(MayaFbxPublisherExporterOptionsWidget, self).__init__(
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

        bool_options = [
            'FBXExportScaleFactor',
            'FBXExportUpAxis',
            'FBXExportFileVersion',
            'FBXExportSmoothMesh',
            'FBXExportInAscii',
            'FBXExportAnimationOnly',
            'FBXExportInstances',
            'FBXExportApplyConstantKeyReducer',
            'FBXExportBakeComplexAnimation',
            'FBXExportBakeResampleAnimation',
            'FBXExportCameras',
            'FBXExportLights',
            'FBXExportConstraints',
            'FBXExportEmbeddedTextures',
        ]

        self.option_group = group_box.GroupBox('FBX exporter Options')
        self.option_group.setToolTip(self.description)

        self.option_layout = QtWidgets.QVBoxLayout()
        self.option_group.setLayout(self.option_layout)

        self.layout().addWidget(self.option_group)
        for option in bool_options:
            option_check = QtWidgets.QCheckBox(option)
            if option in self.options:
                option_check.setChecked(bool(self.options[option]))
            self.options_cb[option] = option_check
            self.option_layout.addWidget(option_check)

    def post_build(self):
        super(MayaFbxPublisherExporterOptionsWidget, self).post_build()

        for option, widget in self.options_cb.items():
            update_fn = partial(self.set_option_result, key=option)
            widget.stateChanged.connect(update_fn)


class MayaFbxPublisherExporterOptionsPluginWidget(
    plugin.MayaPublisherExporterPluginWidget
):
    plugin_name = 'maya_fbx_publisher_exporter'
    widget = MayaFbxPublisherExporterOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MayaFbxPublisherExporterOptionsPluginWidget(api_object)
    plugin.register()
