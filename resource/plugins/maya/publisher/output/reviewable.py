# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import tempfile
import glob

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api

class OutputMayaReviewablePlugin(plugin.PublisherOutputMayaPlugin):
    plugin_name = 'reviewable'

    def run(self, context=None, data=None, options=None):
        component_name = options['component_name']
        camera_name = options.get('camera_name', 'persp')

        current_panel = cmds.getPanel(wf=True)
        panel_type = cmds.getPanel(to=current_panel)  # scriptedPanel
        if panel_type != 'modelPanel':
            visible_panels = cmds.getPanel(vis=True)
            for _panel in visible_panels:
                if cmds.getPanel(to=_panel) == 'modelPanel':
                    current_panel = _panel
                    break
                else:
                    current_panel = None

        previous_camera = 'persp'
        if current_panel:
            previous_camera = cmds.modelPanel(current_panel, q=True, camera=True)

        cmds.lookThru(camera_name)

        res_w = int(cmds.getAttr('defaultResolution.width'))
        res_h = int(cmds.getAttr('defaultResolution.height'))

        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame = cmds.playbackOptions(q=True, max=True)

        prev_selection = cmds.ls(sl=True)
        cmds.select(cl=True)

        filename = tempfile.NamedTemporaryFile().name

        cmds.playblast(
            format='movie',
            sequenceTime=0,
            clearCache=1,
            viewer=0,
            offScreen=True,
            showOrnaments=0,
            frame=range(int(start_frame), int(end_frame + 1)),
            filename=filename,
            fp=4,
            percent=100,
            quality=70,
            w=res_w,
            h=res_h
        )

        if len(prev_selection):
            cmds.select(prev_selection)

        cmds.lookThru(previous_camera)

        temp_files = glob.glob(filename + '.*')
        #TODO:
        # find a better way to find the extension of the playblast file.
        full_path = temp_files[0]

        return {component_name: full_path}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = OutputMayaReviewablePlugin(api_object)
    plugin.register()
