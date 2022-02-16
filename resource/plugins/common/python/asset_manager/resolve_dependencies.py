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

    def get_linked_contexts_recursive(self, entity, processed_entities, log_indent=1):
        '''Add context if it has assets property that can be resolved. Follow
        links/go upstream to recursively add further related contexts.'''
        result = []
        if entity is None or entity['id'] in processed_entities:
            return result
        processed_entities.append(entity['id']) # Prevent cycles
        self.logger.debug('(Resolver) {}Processing: {}()'.format(
            ' '*(2*log_indent), entity['name'], entity['id']))
        if 'assets' in entity:
            # Can only add context that has assets
            self.logger.debug('(Resolver) {} Considering for resolve'.format(' ' * (2 * log_indent)))
            result.append(entity)
        # Any explicit links?
        if entity.get('incoming_links') is not None:
            for entity_link in entity.get('incoming_links'):
                self.logger.debug('(Resolver) {}traveling via incoming link from: {}'.format(
                    ' ' * (2 * log_indent), entity_link['from']))
                self.conditional_add_contexts(
                    result,
                    self.get_linked_contexts_recursive(entity_link['from'], processed_entities, log_indent+1),
                )
        # A version?
        if entity.entity_type == 'AssetVersion':
            self.logger.debug('(Resolver) {}going to version'.format(' ' * (2 * log_indent)))
            self.conditional_add_contexts(
                result, self.get_linked_contexts_recursive(entity['task'], processed_entities, log_indent+1)
            )
        # A task or asset?
        elif 'parent' in entity and entity['parent'] is not None:
            self.logger.debug('(Resolver) {}going to parent'.format(' ' * (2 * log_indent)))
            self.conditional_add_contexts(
                result, self.get_linked_contexts_recursive(entity['parent'], processed_entities, log_indent+1)
            )
        # Look at parent project as a last thing
        elif 'project' in entity:
            self.logger.debug('(Resolver) {}going to parent'.format(' ' * (2 * log_indent)))
            self.conditional_add_contexts(
                result, self.get_linked_contexts_recursive(entity['project'], processed_entities, log_indent+1)
            )
        return result

    def conditional_add_latest_version(
        self, versions, context, asset, asset_type_option
    ):
        '''Filter context *ctx* and *asset* against *asset_type_option*, if they pass,
        add latest version to *versions*'''
        # We have a matching asset type, find latest version
        latest_version = self.session.query('AssetVersion where asset.id={} and is_latest_version is true'.format(asset['id'])).first()
        if latest_version:
            self.logger.debug('(Resolver) Got latest version %s_%s_v%03d, filtering and adding.' % (
                context['name'], latest_version['asset']['name'], latest_version['version']))
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
                        '(Resolver)    Task name include filter mismatch: {} '.format(context['name']))
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
                        '(Resolver)    Task name exclude filter mismatch: {} '.format(context['name']))
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
                        '(Resolver)    Asset name include filter mismatch: {} '.format(asset['name']))
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
                        '(Resolver)    Asset name exclude filter mismatch: {} '.format(asset['name']))
                    return
            # Add a dictionary, allowing further metadata to be passed with resolve at
            # a later stage
            versions.append({'entity':latest_version})
        else:
            self.logger.debug('(Resolver) No latest version on {}_{}.'.format(context['name'], asset['name']))

    def resolve_dependencies(self, contexts, options):
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
                                context['name'], asset['type']['name'], asset_type_option['asset_type']))
                    else:
                        asset_type_matches = True
                        break
                if asset_type_matches:
                    self.conditional_add_latest_version(
                        versions, context, asset, asset_type_option
                    )

        return versions

    # Task type specific resolvers

    def resolve_texture_dependencies(self, contexts, options):
        '''Find latest texture dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further texture specific resolves/checks on result here
        return versions

    def resolve_vehicle_dependencies(self, contexts, options):
        '''Find latest vehicle dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further vehicle specific resolves/checks on result here
        return versions

    def resolve_conform_dependencies(self, contexts, options):
        '''Find latest conform dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further conform specific resolves/checks on result here
        return versions

    def resolve_environment_dependencies(self, contexts, options):
        '''Find latest environment dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further environment specific resolves/checks on result here
        return versions

    def resolve_matte_painting_dependencies(self, contexts, options):
        '''Find latest matte_painting dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further matte painting specific resolves/checks on result here
        return versions

    def resolve_prop_dependencies(self, contexts, options):
        '''Find latest prop dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further prop specific resolves/checks on result here
        return versions

    def resolve_character_dependencies(self, contexts, options):
        '''Find latest character dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further character specific resolves/checks on result here
        return versions

    def resolve_editing_dependencies(self, contexts, options):
        '''Find latest editing dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further editing specific resolves/checks on result here
        return versions

    def resolve_production_dependencies(self, contexts, options):
        '''Find latest production dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further production specific resolves/checks on result here
        return versions

    def resolve_modeling_dependencies(self, contexts, options):
        '''Find latest modeling dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further modeling specific resolves/checks on result here
        return versions

    def resolve_previz_dependencies(self, contexts, options):
        '''Find latest previz dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further previz specific resolves/checks on result here
        return versions

    def resolve_tracking_dependencies(self, contexts, options):
        '''Find latest tracking dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further tracking specific resolves/checks on result here
        return versions

    def resolve_rigging_dependencies(self, contexts, options):
        '''Find latest rigging dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further rigging specific resolves/checks on result here
        return versions

    def resolve_animation_dependencies(self, contexts, options):
        '''Find latest animation dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further animation specific resolves/checks on result here
        return versions

    def resolve_fx_dependencies(self, contexts, options):
        '''Find latest fx dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further fx specific resolves/checks on result here
        return versions

    def resolve_lighting_dependencies(self, contexts, options):
        '''Find latest lighting dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further lighting specific resolves/checks on result here
        return versions

    def resolve_rotoscoping_dependencies(self, contexts, options):
        '''Find latest rotoscoping dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further rotoscoping specific resolves/checks on result here
        return versions

    def resolve_compositing_dependencies(self, contexts, options):
        '''Find latest compositing dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further compositing specific resolves/checks on result here
        return versions

    def resolve_deliverable_dependencies(self, contexts, options):
        '''Find latest deliverable dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further deliverable specific resolves/checks on result here
        return versions

    def resolve_layout_dependencies(self, contexts, options):
        '''Find latest layout dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further layout specific resolves/checks on result here
        return versions

    def resolve_rendering_dependencies(self, contexts, options):
        '''Find latest rendering dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further rendering specific resolves/checks on result here
        return versions

    def resolve_concept_art_dependencies(self, contexts, options):
        '''Find latest concept art dependency versions *contexts*, based on task type resolvable
        asset types supplied *options*'''
        versions = self.resolve_dependencies(contexts, options)
        # Perform further concept art specific resolves/checks on result here
        return versions

    def resolve_task_dependencies(self, context, options):
        try:
            # Fetch all linked asset containers (contexts: shots, asset builds, sequences and so on)
            linked_contexts = self.get_linked_contexts_recursive(context, [])

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
                        linked_contexts, resolver_options
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
