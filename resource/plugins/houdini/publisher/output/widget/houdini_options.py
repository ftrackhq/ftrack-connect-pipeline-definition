# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from functools import partial

from ftrack_connect_pipeline_houdini import plugin
from ftrack_connect_pipeline_qt.client.widgets.options.dynamic import DynamicWidget

from Qt import QtWidgets

import ftrack_api

class HoudiniOptionsWidget(DynamicWidget):

    def __init__(
        self, parent=None, session=None, data=None, name=None,
        description=None, options=None, context=None
    ):

        self.options_cb = {}

        super(HoudiniOptionsWidget, self).__init__(
            parent=parent,
            session=session, data=data, name=name,
            description=description, options=options,
            context=context)

    def build(self):
        '''build function , mostly used to create the widgets.'''
        super(HoudiniOptionsWidget, self).build()

        options = [
        ]
        self.option_group = QtWidgets.QGroupBox('Houdini Output Options')
        self.option_group.setToolTip(self.description)

        self.option_layout = QtWidgets.QVBoxLayout()
        self.option_group.setLayout(self.option_layout)

        self.layout().addWidget(self.option_group)
        for option in options:
            option_check = QtWidgets.QCheckBox(option)

            self.options_cb[option] = option_check
            self.option_layout.addWidget(option_check)


    def post_build(self):
        super(HoudiniOptionsWidget, self).post_build()

        for option, widget in self.options_cb.items():
            update_fn = partial(self.set_option_result, key=option)
            widget.stateChanged.connect(update_fn)



class HoudiniOptionsPluginWidget(plugin.PublisherOutputHoudiniWidget):
    plugin_name = 'houdini_options'
    widget = HoudiniOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = HoudiniOptionsPluginWidget(api_object)
    plugin.register()
