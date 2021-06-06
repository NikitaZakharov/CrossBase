from typing import Optional

from pydantic import BaseModel

from schemas.fields import TitleType, IdType, HostType, PortType, PasswordType, UsernameType


class SSHTunnelBase(BaseModel):
    title: Optional[TitleType] = None
    user_id: Optional[IdType] = None
    host: Optional[HostType] = None
    port: Optional[PortType] = None
    username: Optional[UsernameType] = None
    password: Optional[PasswordType] = None


# Properties to receive on SSHTunnel creation
class SSHTunnelCreate(BaseModel):
    title: TitleType
    host: HostType
    port: PortType
    username: UsernameType
    password: PasswordType


# Properties to receive on SSHTunnel update
class SSHTunnelUpdate(SSHTunnelBase):
    pass


# Properties shared by models stored in DB
class SSHTunnelInDBBase(SSHTunnelBase):
    id: IdType
    title: TitleType
    user_id: IdType
    host: HostType
    port: PortType
    username: UsernameType
    password: PasswordType

    class Config:
        orm_mode = True


# Properties to return to client
class SSHTunnel(SSHTunnelInDBBase):
    pass


# Properties properties stored in DB
class SSHTunnelInDB(SSHTunnelInDBBase):
    pass
