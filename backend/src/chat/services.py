from fastapi_users import jwt
from config import TOKEN_SECRET


def validate_token(token: str):
    ALGORITHM = "HS256"  # Используем алгоритм HS256
    try:
        payload = jwt.decode(token, TOKEN_SECRET, algorithms=[ALGORITHM])
        return payload  # Возвращаем полезную нагрузку токена, если он валиден
    except jwt.PyJWTError as e:
        print(f"Token validation error: {str(e)}")
        return None  # Возвращаем None, если токен недействителен
