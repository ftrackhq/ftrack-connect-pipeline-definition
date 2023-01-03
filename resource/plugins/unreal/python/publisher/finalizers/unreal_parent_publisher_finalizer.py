# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import os
from ftrack_connect_pipeline import plugin
import ftrack_api


class UnrealParentPublisherFinalizerPlugin(plugin.PublisherFinalizerPlugin):
    '''Empty/passthrough publisher finalizer plugin'''

    plugin_name = 'unreal_parent_publisher_finalizer'

    # def _run(self, event):
    #     '''
    #     Overrides the Callback function of the event
    #     :const:`~ftrack_connect_pipeline.constants.PIPELINE_RUN_PLUGIN_TOPIC`
    #     :meth:`ftrack_connect_pipeline.plugin._run`.
    #     Which runs the method passed in the given
    #     *event* ['data']['pipeline']['method'].
    #
    #     Once the base method is called, this function creates a new
    #     :class:`ftrack_api.entity.asset_version.AssetVersion` with all the
    #     required information as component, reviewable, thumbnail, etc... And
    #     commits the ftrack session.
    #
    #     Returns a dictionary with the result information of the called method.
    #
    #     *event* : Dictionary returned when the event topic
    #     :const:`~ftrack_connect_pipeline.constants.PIPELINE_RUN_PLUGIN_TOPIC` is
    #     called.
    #
    #     '''
    #     # TODO: check how to execute the _run method of the parent of this parent
    #     # super_result = super(UnrealParentPublisherFinalizerPlugin, self)._run(event)
    #     #
    #     # if super_result.get('status') != constants.SUCCESS_STATUS:
    #     #     return super_result
    #
    #     context_data = event['data']['settings']['context_data']
    #     data = event['data']['settings']['data']
    #
    #     comment = context_data['comment']
    #     status_id = context_data['status_id']
    #     asset_name = context_data['asset_name']
    #     asset_type_name = context_data['asset_type_name']
    #
    #     status = self.session.query(
    #         'Status where id is "{}"'.format(status_id)
    #     ).one()
    #     context_object = self.session.query(
    #         'select name, parent, parent.name from Context where id is "{}"'.format(
    #             context_data['parent_context_id']
    #         )
    #     ).one()
    #
    #     asset_type_entity = self.session.query(
    #         'AssetType where short is "{}"'.format(asset_type_name)
    #     ).first()
    #
    #     asset_parent_object = context_object['parent']
    #
    #     asset_entity = self.session.query(
    #         'Asset where name is "{}" and type.short is "{}" and '
    #         'parent.id is "{}"'.format(
    #             asset_name, asset_type_name, asset_parent_object['id']
    #         )
    #     ).first()
    #
    #     if not asset_entity:
    #         asset_entity = self.session.create(
    #             'Asset',
    #             {
    #                 'name': asset_name,
    #                 'type': asset_type_entity,
    #                 'parent': asset_parent_object,
    #             },
    #         )
    #
    #     rollback = False
    #     try:
    #         asset_version_entity = self.session.create(
    #             'AssetVersion',
    #             {
    #                 'asset': asset_entity,
    #                 'task': context_object,
    #                 'comment': comment,
    #                 'status': status,
    #             },
    #         )
    #
    #         if self.version_dependencies:
    #             for dependency in self.version_dependencies:
    #                 asset_version_entity['uses_versions'].append(dependency)
    #
    #         self.session.commit()
    #
    #         rollback = True  # Undo version creation from this point
    #
    #         results = {}
    #
    #         for step in data:
    #             if step['type'] == constants.COMPONENT:
    #                 component_name = step['name']
    #                 for stage in step['result']:
    #                     for plugin in stage['result']:
    #                         for component_path in plugin['result']:
    #                             publish_component_fn = (
    #                                 self.component_functions.get(
    #                                     component_name, self.create_component
    #                                 )
    #                             )
    #                             publish_component_fn(
    #                                 asset_version_entity,
    #                                 component_name,
    #                                 component_path,
    #                             )
    #                             results[component_name] = True
    #         self.session.commit()
    #         rollback = False
    #     except:
    #         # An exception occurred when creating components, return its traceback as error message
    #         tb = traceback.format_exc()
    #         super_result['status'] = constants.EXCEPTION_STATUS
    #         super_result['message'] = str(tb)
    #         return super_result
    #     finally:
    #         if rollback:
    #             self.session.reset()
    #             self.logger.warning("Rolling back asset version creation")
    #             self.session.delete(asset_version_entity)
    #             self.session.commit()
    #
    #     self.logger.debug(
    #         "publishing: {} to {} as {}".format(
    #             data, context_data, asset_entity
    #         )
    #     )
    #
    #     return_dict = {
    #         "asset_version_id": asset_version_entity['id'],
    #         "asset_id": asset_entity["id"],
    #         "component_names": list(results.keys()),
    #     }
    #     super_result['result'][self.method].update(return_dict)
    #
    #     return super_result

    def run(self, context_data=None, data=None, options=None):
        # # TODO: get assetinfo from each dependency and publish it as metadata.
        # component['metadata']['ftr_meta'] = json.dumps({
        #     'frameIn': 0,
        #     'frameOut': 150,
        #     'frameRate': 25,
        #     'height': 720,
        #     'width': 1280
        # })
        # TODO: Remove this file if we finally don't use it, and modify the definition to use the common one

        return {}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = UnrealParentPublisherFinalizerPlugin(api_object)
    plugin.register()
