# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import tempfile

import unreal

from ftrack_connect_pipeline_houdini import plugin
import ftrack_api


class OutputHoudiniAlembicPlugin(plugin.PublisherOutputHoudiniPlugin):

    plugin_name = 'alembic_output'

    def fetch(self, context=None, data=None, options=None):
        '''Fetch start and end frames from the scene'''
        r = hou.playbar.frameRange()
        frame_info = {
            "frameStart": r[0],
            "frameEnd": r[1]
        }
        return frame_info

    def extract_options(self, options):
        r = hou.playbar.frameRange()
        return {
            'ABCAnimation' : bool(options.get('ABCAnimation', True)),
            'ABCFrameRangeStart': float(options.get('ABCFrameRangeStart', r[0])),
            'ABCFrameRangeEnd': float(options.get('ABCFrameRangeEnd', r[1])),
            'ABCFrameRangeBy': float(options.get('ABCFrameRangeBy', '1.0')),
        }

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

        bcam = self.bakeCamAnim(cam,
                                [options['frameStart'],
                                 options['frameEnd']])

        # Create Rop Net
        ropNet = objPath.createNode('ropnet')

        abcRopnet = ropNet.createNode('alembic')

        if iAObj.options.get('alembicAnimation'):
            # Check Alembic for animation option
            abcRopnet.parm('trange').set(1)
            for i, x in enumerate(
                    ['frameStart', 'frameEnd', 'alembicEval']):
                abcRopnet.parm('f%d' % (i + 1)).deleteAllKeyframes()
                abcRopnet.parm('f%d' % (i + 1)).set(iAObj.options[x])
        else:
            abcRopnet.parm('trange').set(0)

        abcRopnet.parm('filename').set(new_file_path)
        abcRopnet.parm('root').set(bcam.parent().path())
        abcRopnet.parm('objects').set(bcam.path())
        abcRopnet.parm('format').set('hdf5')
        abcRopnet.render()
        ropNet.destroy()

        return {component_name: new_file_path}


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    ma_plugin = OutputHoudiniAlembicPlugin(api_object)
    ma_plugin.register()
