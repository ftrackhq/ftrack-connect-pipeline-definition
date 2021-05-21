# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

from functools import partial

from ftrack_connect_pipeline_houdini import plugin
from ftrack_connect_pipeline_qt.client.widgets.options.dynamic import DynamicWidget

from Qt import QtWidgets
import ftrack_api

OPTIONS = {
    'FBXASCII': {
        'type': 'checkbox',
        'label': 'ASCII Format',
        'default': True
    },
    'FBXSDKVersion': {
        'type': 'combobox',
        'label': 'FBX SDK Version',
        'options':[
            {'label': 'FBX | FBX201600', 'value': 'FBX | FBX201600'},
            {'label': 'FBX | FBX201400', 'value': 'FBX | FBX201400'},
            {'label': 'FBX | FBX201300', 'value': 'FBX | FBX201300'},
            {'label': 'FBX | FBX201200', 'value': 'FBX | FBX201200'},
            {'label': 'FBX | FBX201100', 'value': 'FBX | FBX201100'},
            {'label': 'FBX 6.0 | FBX201000', 'value': 'FBX 6.0 | FBX201000'},
            {'label': 'FBX 6.0 | FBX200900', 'value': 'FBX 6.0 | FBX200900'},
            {'label': 'FBX 6.0 | FBX200611', 'value': 'FBX 6.0 | FBX200611'},
        ]
    },
    'FBXVertexCacheFormat': {
        'type': 'combobox',
        'label': 'Vertex Cache Format',
        'options': [
            {'label': 'Maya Compatible (MC)', 'value': 'mayaformat'},
            {'label': '3DS Max Compatible (PC2)', 'value': 'maxformat'},
        ]
    },
    'FBXExportInvisibleObjects': {
        'type': 'combobox',
        'label': 'Export Invisible Objects',
        'options': [
            {'label': 'As hidden null nodes', 'value': 'nullnodes'},
            {'label': 'As hidden full nodes', 'value': 'fullnodes'},
            {'label': 'As visible full nodes', 'value': 'visiblenodes'},
            {'label': 'Dont export', 'value': 'nonodes'},
        ]
    },
    'FBXAxisSystem': {
        'type': 'combobox',
        'label': 'Axis system',
        'options': [
            {'label': 'Y Up (Right-handed)', 'value': 'yupright'},
            {'label': 'Y Up (Left-handed)', 'value': 'yupleft'},
            {'label': 'Z Up (Right-handed)', 'value': 'zupright'},
            {'label': 'Current (Y up Right-handed)', 'value': 'currentup'},
        ]
    },
    'FBXConversionLevelOfDetail': {
        'type': 'line',
        'label': 'Conversion Level of Detail',
        'default': '1.0'
    },
    'FBXDetectConstantPointCountDynamicObjects': {
        'type': 'checkbox',
        'label': 'Detect Constant Point Count Dynamic Objects'
    },
    'FBXConvertNURBSAndBeizerSurfaceToPolygons': {
        'type': 'checkbox',
        'label': 'Convert NURBS and Beizer Surface to Polygons'
    },
    'FBXConserveMemoryAtTheExpenseOfExportTime': {
        'type': 'checkbox',
        'label': 'Conserve Memory at the Expense of Export Time'
    },
    'FBXForceBlendShapeExport': {
        'type': 'checkbox',
        'label': 'Force Blend Shape Export'
    },
    'FBXForceSkinDeformExport': {
        'type': 'checkbox',
        'label': 'Force Skin Deform Export'
    },
    'FBXExportEndEffectors': {
        'type': 'checkbox',
        'label': 'Export End Effectors',
        'default': True
    },
}

class FbxOptionsWidget(DynamicWidget):

    def __init__(
        self, parent=None, session=None, data=None, name=None,
        description=None, options=None, context=None
    ):

        self.widgets = {}

        super(FbxOptionsWidget, self).__init__(
            parent=parent,
            session=session, data=data, name=name,
            description=description, options=options,
            context=context)

    def build(self):
        '''build function , mostly used to create the widgets.'''
        super(FbxOptionsWidget, self).build()

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

    def current_index_changed(self, name, label):
        for item in self.OPTIONS[name]['options']:
            if item['label'] == label:
                self.set_option_result(item['value'], name)

    def post_build(self):
        super(FbxOptionsWidget, self).post_build()

        for name, widget in self.widgets.items():
            option = OPTIONS[name]

            if name in self.options:
                default = self.options[name]
            else:
                default_option = option.get('default_option')
                default = None
                if 0 < len(default_option or ''):
                    # Replace with that option's current value
                    default = self.options[default_option]
                if len(default or '') == 0:
                    default = option.get('default')

            update_fn = partial(self.set_option_result, key=name)
            if option['type'] == 'checkbox':
                if default is not None:
                    widget.setChecked(default)
                widget.stateChanged.connect(update_fn)
            elif OPTIONS[name]['type'] == 'combobox':
                if default is not None:
                    idx = 0
                    for item in option['options']:
                        if item['value'] == default or item['label'] == default:
                            widget.setCurrentIndex(idx)
                        idx += 1
                update_fn = partial(self.current_index_changed, name)
                widget.currentIndexChanged.connect(update_fn)
            elif option['type'] == 'line':
                if default is not None:
                    widget.setText(default)
                widget.textChanged.connect(update_fn)

class FbxOptionsPluginWidget(plugin.PublisherOutputHoudiniWidget):
    plugin_name = 'fbx_output'
    widget = FbxOptionsWidget

def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = FbxOptionsPluginWidget(api_object)
    plugin.register()