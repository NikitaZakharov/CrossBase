from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import as_declarative, declared_attr

from models.base import Base

if TYPE_CHECKING:
    from .datasource import Item  # noqa: F401


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False, default='')
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    @declared_attr
    def __tablename__(cls) -> str:
        return 'users'
