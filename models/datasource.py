from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from models.base import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class DataSource(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(length=70), nullable=False)
    settings = Column(JSON, nullable=False)

    engine_id = Column(Integer, ForeignKey('engine.id'), nullable=False)
    engine = relationship('Engine')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    ssh_tunnel_id = Column(Integer, ForeignKey('sshtunnel.id'), nullable=True)
    ssh_tunnel = relationship('SSHTunnel')

