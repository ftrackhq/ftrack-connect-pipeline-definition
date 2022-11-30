# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack
import unreal

import ftrack_api

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_qt.plugin.widget.dynamic import DynamicWidget
from ftrack_connect_pipeline_unreal.constants.asset import modes as load_const


class UnrealRigLoaderImporterOptionsWidget(DynamicWidget):
    '''Unreal rig loader plugin widget user input plugin widget.'''

    load_modes = list(load_const.LOAD_MODES.keys())

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
        super(UnrealRigLoaderImporterOptionsWidget, self).__init__(
            parent=parent,
            session=session,
            data=data,
            name=name,
            description=description,
            options=options,
            context_id=context_id,
            asset_type_name=asset_type_name,
        )

    def define_options(self):
        '''Default renderable options for dynamic widget'''
        result = {
            'UpdateExistingAsset': True,
            'Skeleton': [],
            'CreatePhysicsAsset': True,
            'ImportMaterial': True,
        }
        # Load existing skeletons
        assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()
        skeletons = assetRegistry.get_assets_by_class('Skeleton')
        for skeleton in skeletons:
            result['Skeleton'].append({'value': str(skeleton.asset_name)})
        return result

    def get_options_group_name(self):
        '''Override'''
        return 'Rig loader Options'

    def build(self):
        '''build function , mostly used to create the widgets.'''

        self.update(self.define_options())

        super(UnrealRigLoaderImporterOptionsWidget, self).build()


class UnrealRigLoaderImporterOptionsPluginWidget(
    plugin.UnrealLoaderImporterPluginWidget
):
    plugin_name = 'unreal_rig_loader_importer'
    widget = UnrealRigLoaderImporterOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealRigLoaderImporterOptionsPluginWidget(api_object)
    plugin.register()
