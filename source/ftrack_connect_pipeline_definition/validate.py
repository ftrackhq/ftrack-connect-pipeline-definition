from ftrack_connect_pipeline import constants
import copy
from jsonschema import validate as _validate_jsonschema
import logging

logger = logging.getLogger(__name__)


def _validate_schema(schema, definition):
    '''Validate all the given definitions with the given schema'''
    try:
        _validate_jsonschema(instance=definition, schema=schema)
    except Exception as error:
        logger.error(error)
        return False

    return True


def validate_schema(data):
    copy_data = copy.deepcopy(data)
    # validate schema
    for schema in data['schemas']:
        for entry in [
            (constants.LOADER_SCHEMA, 'loaders'),
            (constants.PUBLISHER_SCHEMA, 'publishers'),
            (constants.PACKAGE_SCHEMA, 'packages')
        ]:
            if schema['title'] == entry[0]:
                for loader in data[entry[1]]:
                    if not _validate_schema(schema, loader):
                        copy_data[entry[1]].pop(loader)
    return copy_data


def validate_asset_types(data, session):
    # validate package asset types:
    copy_data = copy.deepcopy(data)
    valid_assets_types = [
        type['short'] for type in session.query('AssetType').all()
    ]

    for package in data['packages']:
        if package['asset_type'] not in valid_assets_types:
            logger.error(
                'Package {} does use a non existing'
                ' asset type: {}'.format(
                    package['name'], package['asset_type']
                    )
            )
            copy_data['packages'].remove(package)

    return copy_data


def validate_package_type(data):
    # validate package
    copy_data = copy.deepcopy(data)
    valid_packages = [str(package['name']) for package in data['packages']]
    for entry in ['loaders', 'publishers']:

        # check package name in definitions
        for definition in data[entry]:
            if str(definition.get('package')) not in valid_packages:
                logger.error(
                    '{} {}:{} use unknown package : {} , packages: {}'.format(
                        entry, definition['host'], definition['name'],
                        definition.get('package'), valid_packages)
                    )
                # pop definition
                copy_data[entry].remove(definition)

    return copy_data


def validate_definition_components(data):
    copy_data = copy.deepcopy(data)
    # validate package vs definitions components
    for package in data['packages']:
        package_component_names = [
            component['name'] for component in package['components']
            if not component.get('optional', False)
        ]
        for entry in ['loaders', 'publishers']:
            for definition in data[entry]:
                if definition['package'] != package['name']:
                    # this is not the package you are looking for....
                    continue

                definition_components_names = [
                    component['name'] for component in definition['components']
                ]

                for name in package_component_names:
                    if name not in definition_components_names:
                        logger.error(
                            '{} {}:{} package {} components'
                            ' are not matching : required component: {}'.format(
                                entry, definition['host'], definition['name'],
                                definition['package'], package_component_names)
                        )
                        copy_data[entry].remove(definition)
                        break

    # reverse lookup for definitions components in packages
    for entry in ['loaders', 'publishers']:
        for definition in copy_data[entry]:
            definition_components_names = [
                component['name'] for component in definition['components']
            ]
            for package in data['packages']:
                if definition['package'] != package['name']:
                    # this is not the package you are looking for....
                    continue

                package_component_names = [
                    component['name'] for component in package['components']
                ]

                component_diff = set(
                    definition_components_names
                ).difference(
                    set(package_component_names)
                )
                if len(component_diff) != 0:
                    logger.error(
                        '{} {}:{} package {} components'
                        ' are not matching : required component: {}'.format(
                            entry, definition['host'], definition['name'],
                            definition['package'], package_component_names)
                    )
                    copy_data[entry].remove(definition)

    return copy_data