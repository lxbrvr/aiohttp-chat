from apps.users import views as users_views
from core.urls import url
from core.regex import UUID_REGEX


patterns = (
    url(
        method='GET',
        path='/users/',
        handler=users_views.UserListApiView,
        name='users:list',
    ),

    url(
        method='GET',
        path=f'/users/{{user_uuid:{UUID_REGEX}}}/',
        handler=users_views.UserDetailApiView,
        name='users:details',
    ),

    url(
        method='POST',
        path=f'/users/',
        handler=users_views.UserCreateApiView,
        name='users:create',
    ),

    url(
        method='GET',
        path='/users/me/',
        handler=users_views.CurrentUserDetailApiView,
        name='users:current',
    ),

    url(
        method='PUT',
        path='/users/me/',
        handler=users_views.CurrentUserUpdateApiView,
        name='users:update_current',
    ),

    url(
        method='PATCH',
        path='/users/me/',
        handler=users_views.CurrentUserPatchApiView,
        name='users:patch_current',
    ),

    url(
        method='POST',
        path='/access-token/',
        handler=users_views.AccessTokenCreateApiView,
        name='access_token:create',
    ),

    url(
        method='DELETE',
        path='/access-token/',
        handler=users_views.AccessTokenDestroyApiView,
        name='access_token:delete',
    ),
)
