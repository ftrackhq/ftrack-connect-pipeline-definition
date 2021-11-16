# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

from functools import partial

import ftrack_api

def is_valid_version_status(status):
    return not status['name'].lower() in ['omitted']

def get_latest_version(asset, session):
    top_version = None
    for version in session.query('AssetVersion where asset.id {}'.format(asset['id'])):
        if is_valid_version_status(version['status']):
            if top_version is None or top_version['version']<version['version']:
                top_version = version
    return top_version

def get_linked_contexts_recursive(entity):
    def conditional_add_context(contexts, context):
        if not context['id'] in [ctx['idx'] for ctx in contexts]:
            contexts.append(context)
    result = []
    # Can only add context that has assets
    if 'assets' in entity:
        conditional_add_context(result, entity)
    for entity_link in entity.get('incoming_links'):
        result.append(get_linked_contexts_recursive(entity_link['from']))
    if entity.entity_type == 'AssetVersion':
        result.extend(get_linked_contexts_recursive(entity['task']))
    elif 'parent' in entity:
        result.extend(get_linked_contexts_recursive(entity['parent']))
    return result

def resolve_all_asset_dependencies(all_contexts, asset_type_resolvers, session):

    def conditional_add_version(versions, version):
        if not version['id'] in [ver['idx'] for ver in versions]:
            versions.append(version)

    result = []

    for context in all_contexts:
        for asset in session.query('Asset where parent.id {}'.format(context['id'])):
            if asset['type']['name'] in asset_type_resolvers:
                conditional_add_version(result, partial(asset_type_resolvers[asset['type']['name']], asset, session))

    return result

def resolve_compositing_dependencies(task, session):
    def get_compositing_asset_dependencies(asset, session):
        if asset['name'].lower().startswith('precomp'):
            return get_latest_version(asset, asset, session)

    ASSET_TYPE_RESOLVERS = {
        'Compositing': get_compositing_asset_dependencies,
        'Image Sequence': get_latest_version,
    }
    return resolve_all_asset_dependencies(get_linked_contexts_recursive(task), ASSET_TYPE_RESOLVERS, session)


resolvers = {
    'Compositing':resolve_compositing_dependencies
}

def resolve_asset_dependencies(event, session):
    '''Modify the application environment to include  our location plugin.'''
    context_id = event['data']['context']['id']

    task = session.query('TypedContext where id is {}'.format(context_id)).first()
    return {
        'versions':partial(resolvers[task['type']['name']], session, task)
    }

def register(session, **kw):
    '''Register plugin to api_object.'''

    # Location will be available from actions
    session.event_hub.subscribe(
        'topic=ftrack.pipeline.resolve.dependencies.asset',
        partial(resolve_asset_dependencies, session)
    )

