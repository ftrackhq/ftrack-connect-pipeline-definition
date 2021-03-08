# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import os
import sys
import ftrack_api
import logging

NAME = 'ftrack-connect-pipeline-definition'
VERSION = '0.1.0'

logger = logging.getLogger('{}.hook'.format(NAME.replace('-','_')))


def on_application_launch(event):
    '''Handle application launch and add environment to *event*.'''
    logger.info('launching: {}'.format(NAME))

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
    os.environ['FTRACK_DEFINITION_PLUGIN_PATH'] = pipeline_plugins

    python_dependencies = os.path.join(
        plugin_base_dir, 'dependencies'
    )
    sys.path.append(python_dependencies)

    # extract version
    # from ftrack_connect_pipeline_definition import _version as integration_version

    data = {
        'integration': {
            'name': 'ftrack-connect-pipeline-definition',
            'version': '0.0.0',
            'env': {
                'PYTHONPATH.prepend': python_dependencies,
                'FTRACK_EVENT_PLUGIN_PATH':pipeline_definitions
            }
        }
    }
    return data


def register(session):
    '''Subscribe to application launch events on *registry*.'''
    if not isinstance(session, ftrack_api.session.Session):
        return

    logger.info('registering :{}'.format('ftrack.pipeline.discover'))
    session.event_hub.subscribe(
        'topic=ftrack.connect.application.discover '
        'and data.application.identifier=*',
        on_application_launch, priority=10
    )
    session.event_hub.subscribe(
        'topic=ftrack.connect.application.launch '
        'and data.application.identifier=*',
        on_application_launch, priority=10
    )
