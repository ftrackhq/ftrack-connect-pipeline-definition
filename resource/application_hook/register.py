# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import ftrack_api
from ftrack_connect_pipeline import constants
import os
from ftrack_connect_pipeline_definition import collect


def collect_and_filter_definitions(event):
    host = event['data']['pipeline']['host']

    current_dir = os.path.dirname(__file__)

    schemas = collect.collect_json(
        os.path.join(current_dir, 'schema')
    )

    packages = collect.collect_json(
        os.path.join(current_dir, 'package')
    )

    loaders = collect.collect_json(
        os.path.join(current_dir, 'loader'), host
    )

    publishers = collect.collect_json(
        os.path.join(current_dir, 'publisher'),host
    )

    result_data = {
        'schemas': schemas,
        'publishers': [],
        'loaders': [],
        'packages': []

    }

    for schema in schemas:
        if schema['title'] == constants.LOADER_SCHEMA:
            for loader in loaders:
                if collect.validate(schema, loader):
                    result_data['loaders'].append(loader)

        elif schema['title'] == constants.PUBLISHER_SCHEMA:
            for publisher in publishers:
                if collect.validate(schema, publisher):
                    result_data['publishers'].append(publisher)

        elif schema['title'] == constants.PACKAGE_SCHEMA:
            for package in packages:
                if collect.validate(schema, package):
                    result_data['packages'].append(package)

    return result_data


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that _register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    api_object.event_hub.subscribe(
        'topic={} and data.pipeline.type=definition'.format(
            constants.PIPELINE_REGISTER_TOPIC
        ),
        collect_and_filter_definitions
    )
