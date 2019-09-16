from apps.messages.models import MessageModel
from apps.messages.permissions import IsMessageOwner
from apps.messages.query_sets import MessagesQS
from apps.messages.serializers import MessageSerializer
from core.serialization.typings import SerializedData
from apps.messages.ws import WSCHatChanel

from core import views as core_views
from core.authentication import TokenAuthentication
from core.db.models import Model
from core.permissions import IsAuthenticated


class MessageListApiView(core_views.ListApiView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    query_set_class = MessagesQS


class MessageDetailApiView(core_views.DetailApiView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    query_set_class = MessagesQS
    url_param = 'message_uuid'
    lookup_field = 'uuid'


class MessageCreateApiView(core_views.CreateApiView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    query_set_class = MessagesQS

    async def post_serialize(self, data: SerializedData) -> SerializedData:
        await WSCHatChanel(self.request).add_message(data)
        return data


class MessageDeleteView(core_views.DestroyApiView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsMessageOwner]
    query_set_class = MessagesQS
    url_param = 'message_uuid'
    lookup_field = 'uuid'

    async def destroy(self, model: MessageModel) -> None:
        await super().destroy(model)
        await WSCHatChanel(self.request).delete_message({'id': model.uuid})


class MessageUpdateView(core_views.UpdateApiView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsMessageOwner]
    serializer_class = MessageSerializer
    query_set_class = MessagesQS
    url_param = 'message_uuid'
    lookup_field = 'uuid'

    async def post_serialize(self, data: SerializedData) -> SerializedData:
        await WSCHatChanel(self.request).update_message(data)
        return data
