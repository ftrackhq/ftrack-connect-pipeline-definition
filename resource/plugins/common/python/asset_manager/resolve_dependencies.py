# :coding: utf-8
# :copyright: Copyright (c) 2022 ftrack
import re

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

    def get_linked_contexts_recursive(self, entity):
        '''Add context if it has assets property that can be resolved. Follow
        links/go upstream to recursively add further related contexts.'''
        result = []
        if entity is None:
            return result
        if 'assets' in entity:
            # Can only add context that has assets
            result.append(entity)
        # Any explicit links?
        if entity.get('incoming_links') is not None:
            for entity_link in entity.get('incoming_links'):
                self.conditional_add_contexts(
                    result,
                    self.get_linked_contexts_recursive(entity_link['from']),
                )
        # A version?
        if entity.entity_type == 'AssetVersion':
            self.conditional_add_contexts(
                result, self.get_linked_contexts_recursive(entity['task'])
            )
        # A task or asset?
        elif 'parent' in entity:
            self.conditional_add_contexts(
                result, self.get_linked_contexts_recursive(entity['parent'])
            )
        # Look at parent project as a lst thing
        elif 'project' in entity:
            self.conditional_add_contexts(
                result, self.get_linked_contexts_recursive(entity['project'])
            )
        return result

    def conditional_add_latest_version(
        self, versions, ctx, asset, asset_type_option
    ):
        '''Filter context *ctx* and *asset* against *asset_type_option*, if they pass,
        add latest version to *versions*'''
        # We have a matching asset type, check any filters
        if 'task_names_include' in asset_type_option.get('filters', {}):
            matches_all = True
            for expression in asset_type_option['filters'][
                'task_names_include'
            ]:
                if not re.match(expression, ctx['name'].lower()):
                    matches_all = False
                    break
            if not matches_all:
                return
        if 'task_names_exclude' in asset_type_option.get('filters', {}):
            matches_any = False
            for expression in asset_type_option['filters'][
                'task_names_exclude'
            ]:
                if re.match(expression, ctx['name'].lower()):
                    matches_any = True
                    break
            if matches_any:
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
                return
        # All good so far, resolve latest version
        latest_version = None
        for v in self.session.query(
            'AssetVersion where asset.id={}'.format(asset['id'])
        ):
            if v['is_latest_version']:
                latest_version = v
                break
        if latest_version and (True or not latest_version in versions):
            versions.append(latest_version)

    def resolve_dependencies(self, contexts, options):
        '''Generic dependency resolve, locates latest versions from *context*,
        based on task type resolvable asset types supplied *options* and filters.'''
        versions = []
        for ctx in contexts:
            if ctx['assets'] is not None:
                for asset in ctx['assets']:
                    for asset_type_option in options.get('asset_types', []):
                        if (
                            asset_type_option['asset_type'] == '*'
                            or asset['type']['name'].lower()
                            == asset_type_option['asset_type'].lower()
                        ):
                            self.conditional_add_latest_version(
                                versions, ctx, asset, asset_type_option
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

    def run(self, context_data=None, data=None, options=None):
        # Load and check supplied context
        context_id = data['context_id']
        context = self.session.query(
            'Context where id={}'.format(context_id)
        ).one()
        if context.entity_type != 'Task':
            return (
                False,
                {'message': 'Asset resolve can only be performed on tasks!'},
            )

        # Fetch all linked asset containers (contexts: shots, asset builds, sequences and so on)
        linked_contexts = self.get_linked_contexts_recursive(context)

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
                    [],
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
                False,
                {
                    'message': 'Do not know how to resolve task type: '
                    '"{}"'.format(context['type']['name'])
                },
            )


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = AssetDependencyResolverPlugin(api_object)
    plugin.register()
