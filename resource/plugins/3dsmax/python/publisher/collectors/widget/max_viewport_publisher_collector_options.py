# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
from functools import partial

from ftrack_connect_pipeline_3dsmax import plugin
from ftrack_connect_pipeline_qt.plugin.widget import BaseOptionsWidget

from Qt import QtWidgets

import ftrack_api


class MaxViewportPublisherCollectorOptionsWidget(BaseOptionsWidget):
    '''Max viewport collector widget plugin'''

    # Run fetch function on widget initialization
    auto_fetch_on_init = True

    def __init__(
        self,
        parent=None,
        session=None,
        data=None,
        name=None,
        description=None,
        options=None,
        context_id=None,
        asset_type_name=None,
    ):

        self.viewports = []
        super(MaxViewportPublisherCollectorOptionsWidget, self).__init__(
            parent=parent,
            session=session,
            data=data,
            name=name,
            description=description,
            options=options,
            context_id=context_id,
            asset_type_name=asset_type_name,
        )

    def on_fetch_callback(self, result):
        '''This function is called by the _set_internal_run_result function of
        the BaseOptionsWidget'''
        self.logger('@@@ on_fetch_callback({})'.format(result))
        self.viewports = result
        if self.viewports:
            self.viewports_cb.setDisabled(False)
        else:
            self.viewports_cb.setDisabled(True)
        self.viewports_cb.clear()
        for item in self.viewports:
            self.viewports_cb.addItem(item[0], item[1])

    def build(self):
        '''build function , mostly used to create the widgets.'''
        self.logger('@@@ build()'.format())
        super(MaxViewportPublisherCollectorOptionsWidget, self).build()
        self.viewports_cb = QtWidgets.QComboBox()
        self.viewports_cb.setToolTip(self.description)
        self.layout().addWidget(self.viewports_cb)

        if self.options.get('viewport_name'):
            self.viewports.append(self.options.get('viewport_name'))

        if not self.viewports:
            self.viewports_cb.setDisabled(True)
            self.viewports_cb.addItem('No suitable viewports found.')
        else:
            self.viewports_cb.addItems(self.viewports)

    def post_build(self):
        super(MaxViewportPublisherCollectorOptionsWidget, self).post_build()
        update_fn = partial(self.set_option_result, key='viewport_name')

        self.viewports_cb.currentTextChanged.connect(update_fn)
        if self.viewports:
            self.set_option_result(
                self.viewports_cb.currentText(), key='viewport_name'
            )

    def report_input(self):
        '''(Override) Amount of collected objects has changed, notify parent(s)'''
        message = ''
        status = False
        num_objects = 1 if self.viewports_cb.isEnabled() else 0
        if num_objects > 0:
            message = '{} viewport{} selected'.format(
                num_objects, 's' if num_objects > 1 else ''
            )
            status = True
        self.inputChanged.emit(
            {
                'status': status,
                'message': message,
            }
        )


class MaxViewportPublisherCollectorPluginWidget(
    plugin.MaxPublisherCollectorPluginWidget
):
    plugin_name = 'max_viewport_publisher_collector'
    widget = MaxViewportPublisherCollectorOptionsWidget


def register(api_object, **kw):
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return
    plugin = MaxViewportPublisherCollectorPluginWidget(api_object)
    plugin.register()
