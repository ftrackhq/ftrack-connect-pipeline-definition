# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import os
import sys
import ftrack_api
import logging
import functools

NAME = 'ftrack-connect-pipeline-definition'

logger = logging.getLogger('{}.hook'.format(NAME.replace('-', '_')))

plugin_base_dir = os.path.normpath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
)
python_dependencies = os.path.join(plugin_base_dir, 'dependencies')
sys.path.append(python_dependencies)


def on_discover_pipeline_definition(session, event):
    from ftrack_connect_pipeline_definition import (
        __version__ as integration_version,
    )

    data = {
        'integration': {
            'name': 'ftrack-connect-pipeline-definition',
            'version': integration_version,
        }
    }

    return data


def on_launch_pipeline_definition(session, event):
    '''Handle application launch and add environment to *event*.'''
    definition_base_data = on_discover_pipeline_definition(session, event)

    pipeline_definitions = os.path.join(
        plugin_base_dir, 'resource', 'definitions'
    )
    pipeline_plugins = os.path.join(plugin_base_dir, 'resource', 'plugins')
    os.environ['FTRACK_DEFINITION_PLUGIN_PATH'] = pipeline_plugins

    definition_base_data['integration']['env'] = {
        'PYTHONPATH.prepend': python_dependencies,
        'FTRACK_EVENT_PLUGIN_PATH': pipeline_definitions,
        'FTRACK_DEFINITION_PLUGIN_PATH': pipeline_plugins,
    }
    return definition_base_data


def register(session):
    '''Subscribe to application launch events on *registry*.'''
    if not isinstance(session, ftrack_api.session.Session):
        return

    handle_discovery_event = functools.partial(
        on_discover_pipeline_definition, session
    )

    session.event_hub.subscribe(
        'topic=ftrack.connect.application.discover '
        'and data.application.identifier=*',
        handle_discovery_event,
        priority=10,
    )

    handle_launch_event = functools.partial(
        on_launch_pipeline_definition, session
    )

    session.event_hub.subscribe(
        'topic=ftrack.connect.application.launch '
        'and data.application.identifier=*',
        handle_launch_event,
        priority=10,
    )
