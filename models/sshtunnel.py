from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from models.base import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class SSHTunnel(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False, default=22)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
