import ftrack_api
import os

event_paths = [
    os.path.abspath(os.path.join('ftrack-connect-pipeline-definition', 'resource', 'application_hook')),
    os.path.abspath(os.path.join('ftrack-connect-pipeline', 'resource', 'application_hook'))
]

session = ftrack_api.Session(
    plugin_paths=event_paths, auto_connect_event_hub=True
)

event = ftrack_api.event.base.Event(
    topic='ftrack.pipeline.register',
    data={
        'pipeline': {
            'type': "definition",
            'host': 'python'
        }
    }
)


result = session.event_hub.publish(
    event,
    synchronous=True,
)

print result