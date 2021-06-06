import models
import schemas
from .user import user
from .base import CRUDBase


data_source = CRUDBase[models.DataSource, schemas.DataSourceCreate, schemas.DataSourceUpdate](models.DataSource)
engine = CRUDBase[models.Engine, schemas.EngineCreate, schemas.EngineUpdate](models.Engine)
ssh_tunnel = CRUDBase[models.SSHTunnel, schemas.SSHTunnelCreate, schemas.SSHTunnelUpdate](models.SSHTunnel)


__all__ = [
    'data_source',
    'engine',
    'user',
    'ssh_tunnel',
]