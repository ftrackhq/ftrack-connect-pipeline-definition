# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import os
import traceback

import maya.cmds as cmds

from ftrack_connect_pipeline import utils
from ftrack_connect_pipeline_maya import plugin
import ftrack_api


def extract_load_mode_component_name(data):
    for step_result in data:
        if step_result['type'] != 'component':
            continue
        for stage_result in step_result['result']:
            if stage_result['name'] == 'importer':
                for plugin_result in stage_result['result']:
                    load_mode = plugin_result.get('options', {}).get(
                        'load_mode'
                    )
                    if load_mode:
                        return load_mode, step_result['name']
    return None


class MayaToWorkDirPlugin(plugin.LoaderFinalizerMayaPlugin):
    plugin_name = 'maya_finalize'

    def run(self, context_data=None, data=None, options=None):

        result = {}
        message = 'No work file copy needed.'

        load_mode, filename = extract_load_mode_component_name(data)

        if load_mode.lower() == 'open':

            work_path_base = os.environ.get('FTRACK_CONNECT_WORK_PATH')
            work_path = None

            context = self.session.query(
                'Context where id={}'.format(utils.get_current_context_id())
            ).one()

            structure_names = [context['project']['name']] + [
                item['name'] for item in context['link'][1:]
            ]

            # Find latest version number
            next_version_number = 1
            latest_asset_version = self.session.query(
                'AssetVersion where '
                'task.id={} and asset.name="{}" and is_latest_version=true'.format(
                    context_data['context_id'], context_data['asset_name']
                )
            ).first()
            if latest_asset_version:
                next_version_number = latest_asset_version['version'] + 1

            if work_path_base:
                # Build path down to context
                work_path = os.sep.join(
                    [work_path_base] + structure_names + ['work']
                )
            else:
                # Try to query location system (future)
                try:
                    location = self.session.pick_location()
                    work_path = location.get_filesystem_path(context)
                except:
                    self.logger.debug(traceback.format_exc())
                    # Ok, use default location
                    work_path_base = os.path.join(
                        os.path.expanduser('~'),
                        'Documents',
                        'ftrack_work_path',
                    )
                    # Build path down to context
                    work_path = os.sep.join([work_path_base] + structure_names)

            if work_path is not None:
                if not os.path.exists(work_path):
                    os.makedirs(work_path)
                if not os.path.exists(work_path):
                    return (
                        False,
                        {
                            'message': 'Could not create work directory: {}!'.format(
                                work_path
                            )
                        },
                    )
                # Make sure we do not overwrite existing work done
                work_path = os.path.join(
                    work_path, '%s_v%03d' % (filename, next_version_number)
                )
                do_load = False
                if os.path.exists(work_path):
                    # Attempt to ask user
                    try:
                        from ftrack_connect_pipeline_qt.ui.utility.widget.dialog import (
                            Dialog,
                        )

                        dlg = Dialog(
                            self.get_parent_window(),
                            title='ftrack Maya Open',
                            question='Load existing ({})?'.format(
                                os.path.basename(work_path)
                            ),
                            prompt=True,
                        )
                        if dlg.exec_():
                            do_load = True

                    except ImportError:
                        self.logger.warning(traceback.format_exc())
                if not do_load:
                    while os.path.exists(work_path):
                        self.logger.debug(
                            'Work file exists - "{}", attempting to save next version.'.format(
                                work_path
                            )
                        )
                        next_version_number += 1
                        work_path = os.path.join(
                            work_path,
                            '%s_v%03d' % (filename, next_version_number),
                        )

                    # Save Maya scene to this path
                    cmds.file(rename=work_path)
                    cmds.file(save=True)
                    message = 'Saved opened Maya scene @ "{}"'.format(
                        work_path
                    )
                    result['work_path'] = work_path
                else:
                    cmds.file(work_path, open=True, f=True)
                    message = 'Opened Maya scene @ "{}"'.format(work_path)
                    result['work_path'] = work_path

        return (result, {'message': message})


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MayaToWorkDirPlugin(api_object)
    plugin.register()
