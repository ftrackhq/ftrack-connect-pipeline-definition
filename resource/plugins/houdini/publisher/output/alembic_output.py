# :coding: utf-8
# :copyright: Copyright (c) 2014-2021 ftrack

import tempfile

import hou

from ftrack_connect_pipeline_houdini import plugin
import ftrack_api


class OutputHoudiniAlembicPlugin(plugin.PublisherOutputHoudiniPlugin):

    plugin_name = 'alembic_output'

    def fetch(self, context=None, data=None, options=None):
        '''Fetch start and end frames from the scene'''
        r = hou.playbar.frameRange()
        frame_info = {
            'frameStart': r[0],
            'frameEnd': r[1]
        }
        return frame_info

    def extract_options(self, options):
        r = hou.playbar.frameRange()
        return {
            'ABCAnimation' : bool(options.get('ABCAnimation', True)),
            'ABCFrameRangeStart': float(
                options.get('ABCFrameRangeStart', r[0])),
            'ABCFrameRangeEnd': float(options.get('ABCFrameRangeEnd', r[1])),
            'ABCFrameRangeBy': float(options.get('ABCFrameRangeBy', '1.0')),
        }

    def bakeCamAnim(self, node, frameRange):
        ''' Bake camera to World Space '''
        if 'cam' in node.type().name():
            bkNd = hou.node('/obj').createNode(
                'cam', '%s_bake' % node.name())

            for x in ['resx', 'resy']:
                bkNd.parm(x).set(node.parm(x).eval())

        for frame in range(int(frameRange[0]), (int(frameRange[1]) + 1)):
            time = (frame - 1) / hou.fps()
            tsrMtx = node.worldTransformAtTime(time).explode()

            for parm in tsrMtx:
                if 'shear' not in parm:
                    for x, p in enumerate(bkNd.parmTuple(parm[0])):
                        p.setKeyframe(hou.Keyframe(tsrMtx[parm][x], time))

        return bkNd

    def run(self, context=None, data=None, options=None):

        component_name = options['component_name']
        new_file_path = tempfile.NamedTemporaryFile(
            delete=False,
            suffix='.abc'
        ).name

        options = self.extract_options(options)

        self.logger.debug(
            'Calling output options: data {}. options {}'.format(
                data, options
            )
        )

        root_obj = hou.node('/obj')

        collected_objects = []
        for collector in data:
            collected_objects.extend(collector['result'])
        object_paths = ' '.join(collected_objects)
        objects = [hou.node(obj_path) for obj_path in collected_objects]

        if context['asset_type'] == 'cam':
            bcam = self.bakeCamAnim(objects[0],
                                    [options['ABCFrameRangeStart'],
                                     options['ABCFrameRangeEnd']])
            objects = [bcam]
            objects = [bcam.path()]

        # Create Rop Net
        rop_net = root_obj.createNode('ropnet')

        abc_ropnet = rop_net.createNode('alembic')

        if options.get('ABCAnimation'):
            # Check Alembic for animation option
            abc_ropnet.parm('trange').set(1)
            for i, x in enumerate(['ABCFrameRangeStart', 'ABCFrameRangeEnd',
                                   'ABCFrameRangeBy']):
                abc_ropnet.parm('f%d' % (i + 1)).deleteAllKeyframes()
                abc_ropnet.parm('f%d' % (i + 1)).set(options[x])
        else:
            abc_ropnet.parm('trange').set(0)

        abc_ropnet.parm('filename').set(new_file_path)
        abc_ropnet.parm('root').set(objects[0].parent().path())
        abc_ropnet.parm('objects').set(object_paths)
        abc_ropnet.parm('format').set('hdf5')
        abc_ropnet.render()
        rop_net.destroy()

        return [new_file_path]

def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    ma_plugin = OutputHoudiniAlembicPlugin(api_object)
    ma_plugin.register()
