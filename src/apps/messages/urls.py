from apps.messages import views as messages_views, ws as messages_ws
from core.urls import url
from core.regex import UUID_REGEX


patterns = (
    url(
        method='GET',
        path='/messages/',
        handler=messages_views.MessageListApiView,
        name='messages:list',
    ),

    url(
        method='POST',
        path='/messages/',
        handler=messages_views.MessageCreateApiView,
        name='messages:create',
    ),

    url(
        method='GET',
        path=f'/messages/{{message_uuid:{UUID_REGEX}}}/',
        handler=messages_views.MessageDetailApiView,
        name='messages:detail',
    ),

    url(
        method='DELETE',
        path=f'/messages/{{message_uuid:{UUID_REGEX}}}/',
        handler=messages_views.MessageDeleteView,
        name='messages:delete',
    ),

    url(
        method='PUT',
        path=f'/messages/{{message_uuid:{UUID_REGEX}}}/',
        handler=messages_views.MessageUpdateView,
        name='messages:update',
    ),

    url(
        method='GET',
        path=f'/ws/',
        handler=messages_ws.WSView,
        name='messages:chat',
    ),
)
