# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import ftrack_api

from ftrack_connect_pipeline_maya import plugin
from ftrack_connect_pipeline_qt.plugin.widget.dynamic import DynamicWidget
from ftrack_connect_pipeline_3dsmax.utils import (
    max_alembic_commands as abc_utils,
)


class MaxAbcLoaderExporterOptionsWidget(DynamicWidget):
    '''Max FBX publisher options user input plugin widget'''

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

        super(MaxAbcLoaderExporterOptionsWidget, self).__init__(
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
        return abc_utils.abc_default_import_options

    def get_options_group_name(self):
        '''Override'''
        return 'Alembic exporter Options'

    def build(self):
        '''build function , mostly used to create the widgets.'''

        self.update(self.define_options())

        super(MaxAbcLoaderExporterOptionsWidget, self).build()


class MaxAbcLoaderExporterOptionsPluginWidget(
    plugin.MaxLoaderExporterPluginWidget
):
    plugin_name = 'maya_abc_loader_importer'
    widget = MaxAbcLoaderExporterOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MaxAbcLoaderExporterOptionsPluginWidget(api_object)
    plugin.register()
