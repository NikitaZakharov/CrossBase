import json
from typing import Optional, List, Any, Union

from pydantic import BaseModel, validator

from schemas.fields import TitleType, IdType


# Shared properties
class DataSourceBase(BaseModel):
    title: Optional[TitleType] = None
    engine_id: Optional[IdType] = None
    settings: Optional[dict] = None
    ssh_tunnel_id: Optional[IdType] = None


# Properties to receive on DataSource creation
class DataSourceCreate(DataSourceBase):
    title: TitleType
    engine_id: IdType
    settings: dict


# Properties to receive on DataSource update
class DataSourceUpdate(DataSourceBase):
    pass


# Properties shared by models stored in DB
class DataSourceInDBBase(DataSourceBase):
    id: IdType
    title: TitleType
    user_id: IdType
    engine_id: IdType
    settings: dict

    @validator('settings', pre=True)
    def decode_settings(cls, v):
        return json.loads(v)

    class Config:
        orm_mode = True


# Properties to return to client
class DataSource(DataSourceInDBBase):
    pass


# Properties properties stored in DB
class DataSourceInDB(DataSourceInDBBase):
    pass


# class QueryColumn(BaseModel):
#     name: str
#     type_code: Optional[str]


class QueryResult(BaseModel):
    data: List[List]
    columns: List[str]


class DataSourceEntity(BaseModel):
    name: str
    entity: str


class ColumnEntity(DataSourceEntity):
    type: Optional[str]
    is_nullable: Optional[bool] = False
    default: Optional[Any] = None


class ConstraintEntity(DataSourceEntity):
    is_primary_key: Optional[bool]
    is_unique: Optional[bool]
    is_check: Optional[bool]
    is_index: Optional[bool]
    foreign_key: Optional[List[str]]


class TableEntity(DataSourceEntity):
    children: Optional[List[Union[ColumnEntity, ConstraintEntity]]]
