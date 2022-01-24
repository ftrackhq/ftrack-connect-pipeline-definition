# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline_qt.plugin.widgets import dynamic as dynamic_widget
from ftrack_connect_pipeline_qt import plugin
import ftrack_api


class DefaultValidatorWidget(dynamic_widget.DynamicWidget):
    '''Main class to represent a context widget on a publish process'''

    enable_run_plugin = False

    def __init__(
        self,
        parent=None,
        context_id=None,
        asset_type_name=None,
        session=None,
        data=None,
        name=None,
        description=None,
        options=None,
    ):
        '''initialise FileCollectorWidget with *parent*, *session*, *data*,
        *name*, *description*, *options*
        '''
        super(DefaultValidatorWidget, self).__init__(
            parent=parent,
            context_id=context_id,
            asset_type_name=asset_type_name,
            session=session,
            data=data,
            name=name,
            description=description,
            options=options,
        )


class DefaultValidatorPluginWidget(plugin.PublisherValidatorWidget):
    plugin_name = 'default.validator.widget'
    widget = DefaultValidatorWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = DefaultValidatorPluginWidget(api_object)
    plugin.register()
