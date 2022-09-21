# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import tempfile
import glob
import platform

import maya.cmds as cmds

from ftrack_connect_pipeline_maya import plugin
import ftrack_api


class MayaTurntablePublisherExporterPlugin(plugin.MayaPublisherExporterPlugin):
    ''' Maya turntable reviewable publisher plugin'''

    plugin_name = 'maya_turntable_publisher_exporter'

    def run(self, context_data=None, data=None, options=None):
        '''Render a turntable out of the camera and selected objects provided in *data*'''
        camera_name = data[0]['result'][0] 
        collected_objects = data[1]['result']
        selected_object = collected_objects[0].split('|')[1]


        self.logger.debug(f'turntable - camera {camera_name}')
        self.logger.debug(f'turntable - collected_objects {collected_objects}')
        self.logger.debug(f'turntable - objects {selected_object}')

        res_w = int(cmds.getAttr('defaultResolution.width'))
        res_h = int(cmds.getAttr('defaultResolution.height'))

        sframe = cmds.playbackOptions(q=True, min=True)
        eframe = cmds.playbackOptions(q=True, max=True)

        # Ensure 50 frames are always set as minimum.
        if eframe-sframe < 50:
            eframe = sframe + 50 

        locator_to_delete = self.setup_turntable(selected_object, sframe, eframe)
        reviwable_path = self.run_reviewable(camera_name, sframe, eframe, res_w, res_h)

        self.logger.info(
            f'Running turntable with frame range: {sframe}-{eframe}, from camera: {camera_name}'
        )
        cmds.delete(locator_to_delete)
        return reviwable_path


    def setup_turntable(self, object, sframe, eframe):
        bb_vertices = cmds.exactWorldBoundingBox(object)
        x_loc = (bb_vertices[0]+bb_vertices[3])/2
        y_loc = bb_vertices[1]
        z_loc = (bb_vertices[2]+bb_vertices[5])/2

        object_locator = cmds.spaceLocator(
            absolute=True, 
            position=[x_loc, y_loc, z_loc],
            name="object_locator"
        )

        cmds.setAttr(f'{object_locator[0]}.visibility', False)
        cmds.xform(object_locator, centerPivots = True)
        cmds.setKeyframe(object_locator, attribute="rotateY", value=0, time=sframe)
        cmds.setKeyframe(object_locator, attribute="rotateY", value=360, time=int(eframe)+1)
        cmds.keyTangent(object_locator, attribute="rotateY", index=(0, 1),
                        inTangentType="linear", outTangentType="linear")
        cmds.orientConstraint(object_locator, object)
        return object_locator

    def run_reviewable(self, camera_name, sframe, eframe, res_w, res_h):
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
            previous_camera = cmds.modelPanel(
                current_panel, q=True, camera=True
            )

        cmds.lookThru(camera_name)

        res_w = int(cmds.getAttr('defaultResolution.width'))
        res_h = int(cmds.getAttr('defaultResolution.height'))

        prev_selection = cmds.ls(sl=True)
        cmds.select(cl=True)

        filename = tempfile.NamedTemporaryFile().name

        playblast_data = dict(
            format='movie',
            sequenceTime=0,
            clearCache=1,
            viewer=0,
            offScreen=True,
            showOrnaments=0,
            frame=range(int(sframe), int(eframe + 1)),
            filename=filename,
            fp=4,
            percent=100,
            quality=70,
            w=res_w,
            h=res_h,
        )

        if 'linux' in platform.platform().lower():
            playblast_data['format']='qt'
            playblast_data['compression'] = 'raw'

        cmds.playblast(
            **playblast_data
        )

        if len(prev_selection):
            cmds.select(prev_selection)

        cmds.lookThru(previous_camera)

        temp_files = glob.glob(filename + '.*')
        # TODO:
        # find a better way to find the extension of the playblast file.
        full_path = temp_files[0]

        return [full_path]


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MayaTurntablePublisherExporterPlugin(api_object)
    plugin.register()
