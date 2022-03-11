# :coding: utf-8
# :copyright: Copyright (c) 2022 ftrack
import re
import sys

import ftrack_api
from ftrack_connect_pipeline import plugin


class AssetDependencyResolverPlugin(plugin.AssetManagerResolvePlugin):
    plugin_name = 'resolve_dependencies'

    def conditional_add_contexts(self, result, contexts):
        '''Add to list of linked contexts, if not already there'''
        result_context_ids = [ctx['id'] for ctx in result]
        for ctx in contexts:
            if not ctx['id'] in result_context_ids:
                result.append(ctx)

    def get_linked_contexts_recursive(
        self, entity, processed_entities, add_context=True
    ):
        '''Add context if it has assets property that can be resolved. Follow
        links/go upstream to recursively add further related contexts.'''
        result = []
        if entity is None or entity['id'] in processed_entities:
            return result
        processed_entities.append(entity['id'])  # Prevent cycles

        # Find out entity type
        next_entity_type = context = asset = version_nr = None
        if entity.entity_type == 'AssetVersion':
            next_entity_type = 'task'
            context = entity['task']
            asset = entity['asset']
            version_nr = entity['version']
        elif entity.entity_type == 'Asset':
            next_entity_type = 'parent'
            context = entity['parent']
            asset = entity
        elif 'parent' in entity and entity['parent'] is not None:
            next_entity_type = 'parent'
            context = entity
        elif 'project' in entity:
            next_entity_type = 'project'

        if context:
            link = [ctx['name'] for ctx in context['link']]
        else:
            link = [entity['full_name']]
        if asset:
            link.append(asset['name'])
        if version_nr:
            link.append('v{}'.format(version_nr))
        indent = ' ' * 3 * len(link)  # Make logs easy to read

        self.logger.debug(
            '(Resolver) {}Processing: {}({})'.format(
                indent, '/'.join(link), entity['id']
            )
        )
        if 'assets' in entity and add_context is True:
            # Can only add context that has assets
            self.logger.debug(
                '(Resolver) {}Considering for resolve'.format(indent)
            )
            result.append(entity)
        # Any explicit links? Make sure to fetch updated data from backend
        if 'incoming_links' in entity:
            self.session.populate(entity, 'incoming_links')
            if entity['incoming_links'] is not None:
                for entity_link in entity.get('incoming_links'):
                    self.logger.debug(
                        '(Resolver) {}Traveling via incoming link from: {}'.format(
                            indent, entity_link['from']
                        )
                    )
                    self.conditional_add_contexts(
                        result,
                        self.get_linked_contexts_recursive(
                            entity_link['from'], processed_entities
                        ),
                    )
        if next_entity_type:
            self.logger.debug(
                '(Resolver) {}Traveling to: {}'.format(
                    indent, next_entity_type
                )
            )
            self.session.populate(entity, next_entity_type)
            self.conditional_add_contexts(
                result,
                self.get_linked_contexts_recursive(
                    entity[next_entity_type], processed_entities
                ),
            )
        return result

    def str_version(self, context, asset_version):
        return '%s_%s_v%03d' % (
            context['name'],
            asset_version['asset']['name'],
            asset_version['version'],
        )

    def conditional_add_latest_version(
        self,
        versions,
        context,
        asset,
        asset_type_option,
        status_names_include,
        status_names_exclude,
    ):
        '''Filter context *ctx* and *asset* against *asset_type_option*, if they pass,
        add latest version to *versions*'''
        # We have a matching asset type, find latest version
        no_status_include_constraints = len(
            status_names_include or []
        ) == 0 or (
            len(status_names_include) == 1 and status_names_include[0] == '.*'
        )
        no_status_exclude_constraints = len(
            status_names_exclude or []
        ) == 0 or (
            len(status_names_exclude) == 1 and status_names_exclude[0] == '.^'
        )
        latest_version = None
        if no_status_include_constraints and no_status_exclude_constraints:
            # No version status constraints
            latest_version = self.session.query(
                'AssetVersion where asset.id={} and is_latest_version is true'.format(
                    asset['id']
                )
            ).first()
        elif (
            no_status_include_constraints
            and len(status_names_exclude) == 1
            and status_names_exclude[0] == '^Omitted$'
        ):
            # Framework default, treat this special to save performance
            latest_version = self.session.query(
                'AssetVersion where asset.id={} and status.name != "Omitted" '
                'order by version desc'.format(asset['id'])
            ).first()
        else:
            # Find latest version by iterating versions and check statuses
            for version in self.session.query(
                'AssetVersion where asset.id={} '
                'order by version desc'.format(asset['id'])
            ):
                if len(status_names_include or []) > 0:
                    include = False
                    for status_name_include in status_names_include:
                        if re.match(
                            status_name_include, version['status']['name']
                        ):
                            include = True
                            break
                    if not include:
                        self.logger.debug(
                            '(Resolver) Not considering version {} - does not include status(es): {}.'.format(
                                self.str_version(context, version),
                                status_names_include,
                            )
                        )
                        continue
                if len(status_names_exclude or []) > 0:
                    exclude = False
                    for status_name_exclude in status_names_exclude:
                        if not re.match(
                            status_name_exclude, version['status']['name']
                        ):
                            exclude = True
                            break
                    if exclude:
                        self.logger.debug(
                            '(Resolver) Not considering version {} - matches exclude status(es): {}.'.format(
                                self.str_version(context, version),
                                status_name_exclude,
                            )
                        )
                        continue
                latest_version = version
                break

        if latest_version:
            self.logger.debug(
                '(Resolver) Got latest version {}, filtering and adding.'.format(
                    self.str_version(context, latest_version)
                )
            )
            if 'task_names_include' in asset_type_option.get('filters', {}):
                matches_all = True
                for expression in asset_type_option['filters'][
                    'task_names_include'
                ]:
                    if not re.match(expression, context['name'].lower()):
                        matches_all = False
                        break
                if not matches_all:
                    self.logger.debug(
                        '(Resolver)    Task name include filter mismatch: {} '.format(
                            context['name']
                        )
                    )
                    return
            if 'task_names_exclude' in asset_type_option.get('filters', {}):
                matches_any = False
                for expression in asset_type_option['filters'][
                    'task_names_exclude'
                ]:
                    if re.match(expression, context['name'].lower()):
                        matches_any = True
                        break
                if matches_any:
                    self.logger.debug(
                        '(Resolver)    Task name exclude filter mismatch: {} '.format(
                            context['name']
                        )
                    )
                    return
            if 'asset_names_include' in asset_type_option.get('filters', {}):
                matches_all = True
                for expression in asset_type_option['filters'][
                    'asset_names_include'
                ]:
                    if not re.match(expression, asset['name'].lower()):
                        matches_all = False
                        break
                if not matches_all:
                    self.logger.debug(
                        '(Resolver)    Asset name include filter mismatch: {} '.format(
                            asset['name']
                        )
                    )
                    return
            if 'asset_names_exclude' in asset_type_option.get('filters', {}):
                matches_any = False
                for expression in asset_type_option['filters'][
                    'asset_names_exclude'
                ]:
                    if re.match(expression, asset['name'].lower()):
                        matches_any = True
                        break
                if matches_any:
                    self.logger.debug(
                        '(Resolver)    Asset name exclude filter mismatch: {} '.format(
                            asset['name']
                        )
                    )
                    return
            # Add a dictionary, allowing further metadata to be passed with resolve at
            # a later stage
            versions.append({'entity': latest_version})
        else:
            self.logger.debug(
                '(Resolver) No latest version on {}_{}.'.format(
                    context['name'], asset['name']
                )
            )

    def resolve_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Generic dependency resolve, locates latest versions from *context*,
        based on task type resolvable asset types supplied *options* and filters.'''
        versions = []
        for context in contexts:
            for asset in context.get('assets'):
                asset_type_matches = False
                for asset_type_option in options.get('asset_types', []):
                    if (
                        asset_type_option['asset_type'] != '*'
                        and asset['type']['name'].lower()
                        != asset_type_option['asset_type'].lower()
                    ):
                        self.logger.debug(
                            '(Resolver) {} Asset type mismatch: {}>{}.'.format(
                                context['name'],
                                asset['type']['name'],
                                asset_type_option['asset_type'],
                            )
                        )
                    else:
                        asset_type_matches = True
                        break
                if asset_type_matches:
                    self.conditional_add_latest_version(
                        versions,
                        context,
                        asset,
                        asset_type_option,
                        status_names_include,
                        status_names_exclude,
                    )

        return versions

    # Task type specific resolvers

    def resolve_texture_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest texture dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further texture specific resolves/checks on result here
        return versions

    def resolve_vehicle_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest vehicle dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further vehicle specific resolves/checks on result here
        return versions

    def resolve_conform_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest conform dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further conform specific resolves/checks on result here
        return versions

    def resolve_environment_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest environment dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further environment specific resolves/checks on result here
        return versions

    def resolve_matte_painting_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest matte_painting dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further matte painting specific resolves/checks on result here
        return versions

    def resolve_prop_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest prop dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further prop specific resolves/checks on result here
        return versions

    def resolve_character_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest character dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further character specific resolves/checks on result here
        return versions

    def resolve_editing_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest editing dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further editing specific resolves/checks on result here
        return versions

    def resolve_production_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest production dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further production specific resolves/checks on result here
        return versions

    def resolve_modeling_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest modeling dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further modeling specific resolves/checks on result here
        return versions

    def resolve_previz_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest previz dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further previz specific resolves/checks on result here
        return versions

    def resolve_tracking_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest tracking dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further tracking specific resolves/checks on result here
        return versions

    def resolve_rigging_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest rigging dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further rigging specific resolves/checks on result here
        return versions

    def resolve_animation_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest animation dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further animation specific resolves/checks on result here
        return versions

    def resolve_fx_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest fx dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further fx specific resolves/checks on result here
        return versions

    def resolve_lighting_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest lighting dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further lighting specific resolves/checks on result here
        return versions

    def resolve_rotoscoping_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest rotoscoping dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further rotoscoping specific resolves/checks on result here
        return versions

    def resolve_compositing_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest compositing dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further compositing specific resolves/checks on result here
        return versions

    def resolve_deliverable_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest deliverable dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further deliverable specific resolves/checks on result here
        return versions

    def resolve_layout_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest layout dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further layout specific resolves/checks on result here
        return versions

    def resolve_rendering_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest rendering dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further rendering specific resolves/checks on result here
        return versions

    def resolve_concept_art_dependencies(
        self, contexts, options, status_names_include, status_names_exclude
    ):
        '''Find latest concept art dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(
            contexts, options, status_names_include, status_names_exclude
        )
        # Perform further concept art specific resolves/checks on result here
        return versions

    def resolve_task_dependencies(self, context, options):
        try:
            # Fetch all linked asset containers (contexts: shots, asset builds, sequences and so on)
            linked_contexts = self.get_linked_contexts_recursive(
                context, [], add_context=False
            )  # Do not include deps on target context

            # Define task type resolver mappings
            TASK_TYPE_RESOLVERS = {
                'texture': self.resolve_texture_dependencies,
                'conform': self.resolve_conform_dependencies,
                'environment': self.resolve_environment_dependencies,
                'matte painting': self.resolve_matte_painting_dependencies,
                'prop': self.resolve_prop_dependencies,
                'character': self.resolve_character_dependencies,
                'editing': self.resolve_editing_dependencies,
                'production': self.resolve_production_dependencies,
                'modeling': self.resolve_modeling_dependencies,
                'previz': self.resolve_previz_dependencies,
                'tracking': self.resolve_tracking_dependencies,
                'rigging': self.resolve_rigging_dependencies,
                'animation': self.resolve_animation_dependencies,
                'fx': self.resolve_fx_dependencies,
                'lighting': self.resolve_lighting_dependencies,
                'rotoscoping': self.resolve_rotoscoping_dependencies,
                'compositing': self.resolve_compositing_dependencies,
                'deliverable': self.resolve_deliverable_dependencies,
                'layout': self.resolve_layout_dependencies,
                'rendering': self.resolve_rendering_dependencies,
                'concept art': self.resolve_concept_art_dependencies,
                '*': self.resolve_dependencies,
            }

            # Extract task type resolver options from schema
            resolver_options = options['task_types'].get(
                context['type']['name'].lower()
            )
            if resolver_options is None:
                # Options for this resolver not defined, any generic?
                resolver_options = options['task_types'].get('*')
                if resolver_options is None:
                    return (
                        {},
                        {
                            'message': 'No asset types defined to resolve for '
                            '"{}" task type!'.format(context['type']['name'])
                        },
                    )

            resolver_name = context['type']['name'].lower()
            if not resolver_name in TASK_TYPE_RESOLVERS:
                resolver_name = '*'

            if resolver_name in TASK_TYPE_RESOLVERS:
                return {
                    'versions': TASK_TYPE_RESOLVERS[resolver_name.lower()](
                        linked_contexts,
                        resolver_options,
                        options.get('status_names_include'),
                        options.get('status_names_exclude'),
                    )
                }
            else:
                return (
                    {},
                    {
                        'message': 'Do not know how to resolve task type: '
                        '"{}"'.format(context['type']['name'])
                    },
                )
        except:
            import traceback

            sys.stderr.write(traceback.format_exc())
            raise

    def run(self, context_data=None, data=None, options=None):
        # Load and check supplied context
        # return ({}, {'message': 'SIMULATED FAILURE'})

        context_id = data['context_id']
        context = self.session.query(
            'Context where id={}'.format(context_id)
        ).first()
        if context is None:
            return (
                {},
                {
                    'message': 'The context {} is now known to ftrack!'.format(
                        context_id
                    )
                },
            )
        elif context.entity_type != 'Task':
            return (
                {},
                {
                    'message': 'Asset resolve can only be performed on tasks, not {}!'.format(
                        context_id
                    )
                },
            )

        return self.resolve_task_dependencies(context, options)


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = AssetDependencyResolverPlugin(api_object)
    plugin.register()
