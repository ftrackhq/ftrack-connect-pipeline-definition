# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

from functools import partial

import unreal as ue

from ftrack_connect_pipeline_unreal_engine import plugin
from ftrack_connect_pipeline_qt.client.widgets.options.load_widget import (
    LoadBaseWidget
)
from ftrack_connect_pipeline_unreal_engine.constants.asset import modes as load_const

from Qt import QtCore, QtWidgets
import ftrack_api

# Common
class LoadUnrealWidget(LoadBaseWidget):
    load_modes = list(load_const.LOAD_MODES.keys())

    def __init__(
            self, parent=None, session=None, data=None, name=None,
            description=None, options=None, context_id=None, asset_type=None
    ):
        self.widgets = {}

        super(LoadUnrealWidget, self).__init__(
            parent=parent, session=session, data=data, name=name,
            description=description, options=options, context_id=context_id, asset_type=asset_type
        )

    def build(self):
        super(LoadUnrealWidget, self).build()

        for name, option in self.config.items():
            if option['type'] == 'checkbox':
                widget = QtWidgets.QCheckBox(option['label'])
            elif option['type'] == 'combobox':
                self.layout().addWidget(QtWidgets.QLabel(option['label']))
                widget = QtWidgets.QComboBox()
                if name == 'ChooseSkeleton':
                    # Load existing skeletons
                    option['options'] = []
                    assetRegistry = ue.AssetRegistryHelpers.get_asset_registry()
                    skeletons = assetRegistry.get_assets_by_class('Skeleton')
                    for skeleton in skeletons:
                        option['options'].append({
                            'label': str(skeleton.asset_name),
                            'value': str(skeleton.asset_name)})
                for item in option['options']:
                    widget.addItem(item['label'])
            elif option['type'] == 'line':
                self.layout().addWidget(QtWidgets.QLabel(option['label']))
                widget = QtWidgets.QLineEdit()

            self.widgets[name] = widget
            self.layout().addWidget(widget)

    def current_index_changed(self, name, idx):
        option = self.config[name]
        self.set_option_result(option['options'][idx]['value'],
                               name)

    def post_build(self):
        super(LoadUnrealWidget, self).post_build()

        for name, widget in self.widgets.items():
            option = self.config[name]

            update_fn = partial(self.set_option_result, key=name)
            if option['type'] == 'checkbox':
                widget.stateChanged.connect(update_fn)
            elif self.config[name]['type'] == 'combobox':
                combobox_name = str(name)
                update_fn = partial(self.current_index_changed, name)
                widget.currentIndexChanged.connect(update_fn)
            elif option['type'] == 'line':
                widget.textChanged.connect(update_fn)

    def set_defaults(self):
        super(LoadUnrealWidget, self).set_defaults()

        for name, widget in self.widgets.items():
            option = self.config[name]

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
                self.set_option_result(
                    default if not default is None else False, name)
                if default is not None:
                    widget.setChecked(default)
            elif option['type'] == 'combobox':
                if default is not None:
                    idx = 0
                    for item in option['options']:
                        if item['value'] == default or item['label'] == default:
                            widget.setCurrentIndex(idx)
                        idx += 1
                else:
                    self.set_option_result(option['options'][0]['value'], name)
            elif option['type'] == 'line':
                if default is not None:
                    widget.setText(default)
                else:
                    self.set_option_result('', name)


    def _on_load_mode_changed(self, radio_button):
        '''set the result options of value for the key.'''
        super(LoadUnrealWidget, self)._on_load_mode_changed(radio_button)

# Rig
class LoadUnrealRigWidget(LoadUnrealWidget):
    config = {
        'UpdateExistingAsset': {
            'type': 'checkbox',
            'label': 'Update existing assets:',
            'default': True
        },
        'ChooseSkeleton': {
            'type': 'combobox',
            'label': 'Choose skeleton',
            'options': [
            ]
        },
        'CreatePhysicsAsset': {
            'type': 'checkbox',
            'label': 'Create Physics Asset:',
            'default': True
        },
        'ImportMaterial': {
            'type': 'checkbox',
            'label': 'Import Material:',
            'default': True
        },
    }

class LoadUnrealRigPluginWidget(plugin.LoaderImporterUnrealWidget):
    plugin_name = 'load_rig_unreal'
    widget = LoadUnrealRigWidget

# Animation
class LoadUnrealAnimationWidget(LoadUnrealWidget):
    config = {
        'UpdateExistingAsset': {
            'type': 'checkbox',
            'label': 'Update existing assets:',
            'default': True
        },
        'ChooseSkeleton': {
            'type': 'combobox',
            'label': 'Choose skeleton',
            'options': [
            ]
        },
        'UseCustomRange': {
            'type': 'checkbox',
            'label': 'Use custom animation range:',
        },
        'AnimRangeMin': {
            'type': 'line',
            'label': 'Custom animation range start:',
            'default': '1'
        },
        'AnimRangeMax': {
            'type': 'line',
            'label': 'Custom animation range end:',
            'default': '100'
        }
    }

class LoadUnrealAnimationPluginWidget(plugin.LoaderImporterUnrealWidget):
    plugin_name = 'load_animation_unreal'
    widget = LoadUnrealAnimationWidget

# Geometry
class LoadUnrealGeometryWidget(LoadUnrealWidget):
    config = {
        'UpdateExistingAsset': {
            'type': 'checkbox',
            'label': 'Update existing assets:',
            'default': True
        },
        'ImportMaterial': {
            'type': 'checkbox',
            'label': 'Import material:',
            'default': True
        }
    }

class LoadUnrealGeometryPluginWidget(plugin.LoaderImporterUnrealWidget):
    plugin_name = 'load_geometry_unreal'
    widget = LoadUnrealGeometryWidget

# Image sequence
class LoadUnrealImageSequenceWidget(LoadUnrealWidget):
    config = {
        'OverrideExisting': {
            'type': 'checkbox',
            'label': 'Override existing assets:',
            'default': True
        }
    }

class LoadUnrealImageSequencePluginWidget(plugin.LoaderImporterUnrealWidget):
    plugin_name = 'load_image_sequence_unreal'
    widget = LoadUnrealImageSequenceWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    load_unreal_rig = LoadUnrealRigPluginWidget(api_object)
    load_unreal_rig.register()

    load_unreal_anim = LoadUnrealAnimationPluginWidget(api_object)
    load_unreal_anim.register()

    load_unreal_geo = LoadUnrealGeometryPluginWidget(api_object)
    load_unreal_geo.register()

    load_unreal_img = LoadUnrealImageSequencePluginWidget(api_object)
    load_unreal_img.register()
