import datetime
from typing import Any, Union, Optional

from jose import jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = 'HS256'


def create_access_token(
    subject: Union[str, Any], expires_delta: datetime.timedelta = None
) -> str:
    expires_delta = expires_delta or datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode = {'exp': expire, 'sub': str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return decoded['sub']
    except jwt.JWTError:
        return


def generate_password_reset_token(email: str) -> str:
    delta = datetime.timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    to_encode = {'exp': exp, 'nbf': now, 'sub': email}
    encoded = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded
