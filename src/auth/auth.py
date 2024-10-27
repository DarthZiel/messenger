from base64 import encode

from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy
from fastapi_users.jwt import generate_jwt

from config import TOKEN_SECRET


def get_jwt_strategy() -> JWTStrategy:

    return JWTStrategy(secret=TOKEN_SECRET, lifetime_seconds=3600)


cookie_transport = CookieTransport(cookie_name='token', cookie_max_age=3600, cookie_httponly=False)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
