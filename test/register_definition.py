import ftrack_api
import os
from pprint import pformat
event_paths = [
    os.path.abspath(os.path.join('resource', 'application_hook'))
]

session = ftrack_api.Session(
    plugin_paths=event_paths
)

event = ftrack_api.event.base.Event(
    topic='ftrack.pipeline.register',
    data={
        'pipeline': {
            'type': "definition"
        }
    }
)


result = session.event_hub.publish(
    event,
    synchronous=True,
)

print 'RESULTS', pformat(result[0]), len(result[0])