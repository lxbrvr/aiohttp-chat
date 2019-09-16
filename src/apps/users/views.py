from apps.users.models import UserModel
from apps.users.query_sets import UsersQS, AccessTokenQS
from apps.users.serializers import UserSerializer, AccessTokenSerializer
from core import views as core_views
from core.authentication import TokenAuthentication
from core.permissions import IsAuthenticated


class UserListApiView(core_views.ListApiView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    query_set_class = UsersQS


class UserDetailApiView(core_views.DetailApiView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    query_set_class = UsersQS
    url_param = 'user_uuid'
    lookup_field = 'uuid'


class AccessTokenCreateApiView(core_views.CreateApiView):
    query_set_class = AccessTokenQS
    serializer_class = AccessTokenSerializer


class AccessTokenDestroyApiView(core_views.DestroyApiView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    query_set_class = AccessTokenQS
    serializer_class = AccessTokenSerializer


class UserCreateApiView(core_views.CreateApiView):
    query_set_class = UsersQS
    serializer_class = UserSerializer


class CurrentUserDetailApiView(core_views.DetailApiView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    query_set_class = UsersQS

    async def get_object(self) -> UserModel:
        return (
            await
            self.query_set_class(db=self.db)
            .get_by_uuid(self.request.user.uuid)
        )


class CurrentUserUpdateApiView(core_views.UpdateApiView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    query_set_class = UsersQS

    async def get_object(self) -> UserModel:
        return (
            await
            self.query_set_class(db=self.db)
            .get_by_uuid(self.request.user.uuid)
        )


class CurrentUserPatchApiView(core_views.PatchApiView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    query_set_class = UsersQS

    async def get_object(self) -> UserModel:
        return (
            await
            self.query_set_class(db=self.db)
            .get_by_uuid(self.request.user.uuid)
        )
