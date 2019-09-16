import typing as t
import abc

import jwt
from aiohttp import hdrs
from aiohttp.web_request import Request

from apps.users.models import UserModel
from apps.users.query_sets import UsersQS
from conf import settings


class BaseAuthentication(metaclass=abc.ABCMeta):
    """
    The base authentication interface for using in ApiView.
    """

    @abc.abstractmethod
    async def authenticate(self, request: Request):
        """
        Tries authenticates the client from request.
        """

        pass


class TokenAuthentication(BaseAuthentication):
    """
    Authentication class for authentication with authorization header.
    For example, the header might look like:
        Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJI
    """

    async def authenticate(self, request: Request) -> t.Optional[UserModel]:
        header_values = request.headers.get(hdrs.AUTHORIZATION, '').split()

        if len(header_values) != 2:
            return

        token = header_values[1]
        token_data = self.validate_api_token(token)

        if not token_data:
            return

        user_uuid = token_data['user_id']

        return await UsersQS(db=request.app.mongo).get_by_uuid(user_uuid)

    def validate_api_token(self, token: str) -> t.Optional[t.Dict[str, t.Any]]:
        if not token:
            return

        try:
            payload = jwt.decode(
                jwt=token,
                key=settings.SECRET_KEY,
                options={'verify_exp': True},
            )
        except jwt.exceptions.InvalidTokenError:
            return

        if not payload.get('user_id'):
            return

        return payload
