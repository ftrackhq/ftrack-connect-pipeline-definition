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
        os.path.join(lookup_dir, 'publisher'), host
    )

    result_data = {
        'schemas': schemas,
        'publishers': publishers,
        'loaders': loaders,
        'packages': packages
    }

    for schema in schemas:
        # validate schema
        for entry in [
            (constants.LOADER_SCHEMA, 'loaders'),
            (constants.PUBLISHER_SCHEMA, 'publishers'),
            (constants.PACKAGE_SCHEMA, 'packages')
        ]:
            if schema['title'] == entry[0]:
                for loader in result_data[entry[1]]:
                    if not _validate(schema, loader):
                        result_data[entry[1]].pop(loader)

    # validate package
    valid_packages = [str(package['name']) for package in packages]
    for entry in ['loaders', 'publishers']:

        # check package name in definitions
        for definition in result_data[entry]:
            if str(definition['package']) not in valid_packages:
                logger.error(
                    '{} {}:{} use unknown package : {} , packages: {}'.format(
                        entry, definition['host'], definition['name'],
                        definition['package'], valid_packages)
                    )
                # pop definition
                result_data[entry].remove(definition)

    # validate package vs definitions components
    for package in packages:
        package_component_names = [component['name'] for component in package['components']]
        for entry in ['loaders', 'publishers']:
            for definition in result_data[entry]:
                if definition['package'] != package['name']:
                    # this is not the package you are looking for....
                    continue

                definition_components = [component['name'] for component in definition['components']]
                component_diff = set(package_component_names).difference(definition_components)
                match = not len(component_diff)
                if not match:
                    logger.error(
                        '{} {}:{} package {} components are not matching : required component: {}'.format(
                            entry, definition['host'], definition['name'],
                            definition['package'], component_diff)
                    )
                    result_data[entry].remove(definition)

    # log final discovery result
    for key, value in result_data.items():
        logger.info('discovered : {} : {}'.format(key, len(value)))

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
