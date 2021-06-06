from pydantic import BaseModel, constr

from schemas.fields import HostType, PortType, UsernameType, PasswordType


class ConnectionParams(BaseModel):
    host: HostType
    port: PortType
    user: UsernameType
    password: PasswordType
    database: constr(min_length=1)
