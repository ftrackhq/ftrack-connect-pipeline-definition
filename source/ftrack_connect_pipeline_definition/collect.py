# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import json
import fnmatch
import os
import logging
from jsonschema import validate as _validate_jsonschema

from ftrack_connect_pipeline import constants

logger = logging.getLogger(__name__)


def collect_and_filter_definitions(lookup_dir, host):
    logger.debug('filter by host: {}'.format(host))

    schemas = _collect_json(
        os.path.join(lookup_dir, 'schema')
    )

    packages = _collect_json(
        os.path.join(lookup_dir, 'package')
    )

    loaders = _collect_json(
        os.path.join(lookup_dir, 'loader'), host
    )

    publishers = _collect_json(
        os.path.join(lookup_dir, 'publisher'),host
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
                if _validate(schema, loader):
                    result_data['loaders'].append(loader)

        elif schema['title'] == constants.PUBLISHER_SCHEMA:
            for publisher in publishers:
                if _validate(schema, publisher):
                    result_data['publishers'].append(publisher)

        elif schema['title'] == constants.PACKAGE_SCHEMA:
            for package in packages:
                if _validate(schema, package):
                    result_data['packages'].append(package)

    for key, value in result_data.items():
        logger.info('discovered : {}: {}'.format(key, len(value)))

    return result_data


def _collect_json(source_path, filter_host=None):
    '''
    Return a json encoded list of all the json files discovered in the given
    *source_path*.
    '''
    logger.debug('looking for dernitions in : {}'.format(source_path))

    json_files = []
    for root, dirnames, filenames in os.walk(source_path):
        for filename in fnmatch.filter(filenames, '*.json'):
            json_files.append(os.path.join(root, filename))

    loaded_jsons = []
    for json_file in json_files:
        data_store = None
        with open(json_file, 'r') as _file:
            try:
                data_store = json.load(_file)
            except Exception as error:
                logger.warning(
                    "{0} could not be registered, reason: {1}".format(
                        _file, str(error)
                    )
                )

        if filter_host:
            if data_store.get('host') != filter_host:
                logger.debug('filtering out host: {}'.format(
                    data_store.get('host')
                ))
                continue

        if data_store:
            loaded_jsons.append(data_store)

    return loaded_jsons


def _validate(schema, definition):
    '''Validate all the given definitions with the given schema'''
    try:
        _validate_jsonschema(instance=definition, schema=schema)
    except Exception as error:
        logger.error(error)
        return False

    return True
