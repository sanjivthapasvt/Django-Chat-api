# chat_room/middleware.py
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from jwt import InvalidTokenError

User = get_user_model()

@database_sync_to_async
def get_user(validated_token):
    jwt_auth = JWTAuthentication()
    try:
        user = jwt_auth.get_user(validated_token)
        return user
    except Exception:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        if token is not None:
            try:
                validated_token = JWTAuthentication().get_validated_token(token)
                scope["user"] = await get_user(validated_token)
            except InvalidTokenError:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
