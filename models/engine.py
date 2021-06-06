from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Boolean

from models.base import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Engine(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    hidden = Column(Boolean, nullable=False, default=False)
