# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import os
import ftrack_api
import ftrack_connect.application

import logging

logger = logging.getLogger('ftrack_connect_pipeline_definition.discover')

plugin_base_dir = os.path.normpath(
    os.path.join(
        os.path.abspath(
            os.path.dirname(__file__)
        ),
        '..'
    )
)

pipeline_definitions = os.path.join(
    plugin_base_dir, 'resource', 'definitions'
)

pipeline_plugins = os.path.join(
    plugin_base_dir, 'resource', 'plugins'
)

python_dependencies = os.path.join(
    plugin_base_dir, 'dependencies'
)


def on_discover_pipeline(event):
    '''Handle application launch and add environment to *event*.'''

    # Add pipeline dependencies to pythonpath.
    ftrack_connect.application.appendPath(
        python_dependencies,
        'PYTHONPATH',
        event['data']['options']['env']
    )

    # Add base plugins to events path.
    ftrack_connect.application.appendPath(
        pipeline_definitions,
        'FTRACK_EVENT_PLUGIN_PATH',
        event['data']['options']['env']
    )

    # Add base plugins to events path.
    ftrack_connect.application.appendPath(
        pipeline_plugins,
        'FTRACK_DEFINITION_PLUGIN_PATH',
        event['data']['options']['env']
    )
    # return event['data']['options']

    ######################
    data = {
        'integration': {
            "name": 'ftrack-connect-pipeline-definition',
            'version': '0.0.0'
        },
        'env': {
            'PYTHONPATH.prepend': python_dependencies,
            'FTRACK_EVENT_PLUGIN_PATH': pipeline_definitions,
            'FTRACK_DEFINITION_PLUGIN_PATH': pipeline_plugins
        }
    }
    return data

    ######################


def register(session):
    '''Subscribe to application launch events on *registry*.'''
    if not isinstance(session, ftrack_api.session.Session):
        return

    session.event_hub.subscribe(
        'topic=ftrack.connect.application.launch',
        on_discover_pipeline, priority=10
    )
