# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from ftrack_connect_pipeline_unreal import plugin
from ftrack_connect_pipeline_qt.plugin.widget.base_collector_widget import (
    BaseCollectorWidget,
)

import ftrack_api


class UnrealDependenciesPublisherCollectorOptionsWidget(BaseCollectorWidget):
    '''Unreal dependencies user selection template plugin widget'''

    # Run fetch function on widget initialization
    auto_fetch_on_init = True

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
        super(
            UnrealDependenciesPublisherCollectorOptionsWidget, self
        ).__init__(
            parent=parent,
            session=session,
            data=data,
            name=name,
            description=description,
            options=options,
            context_id=context_id,
            asset_type_name=asset_type_name,
        )

    def report_input(self):
        '''(Override) Amount of collected objects has changed, notify parent(s)'''
        message = ''
        status = False
        # TODO: Remove the +1 when QT supports summarize of multiple collectors
        num_objects = len(self.options.get('collected_objects') or []) + 1
        if num_objects > 0:
            message = '{} asset{} selected'.format(
                num_objects, 's' if num_objects > 1 else ''
            )
            status = True
        self.inputChanged.emit(
            {
                'status': status,
                'message': message,
            }
        )


class UnrealDependenciesPublisherCollectorPluginWidget(
    plugin.UnrealPublisherCollectorPluginWidget
):
    plugin_name = 'unreal_dependencies_publisher_collector'
    widget = UnrealDependenciesPublisherCollectorOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealDependenciesPublisherCollectorPluginWidget(api_object)
    plugin.register()
