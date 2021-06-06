from typing import Optional, List, Dict

from pydantic import BaseModel

from schemas.fields import TitleType, IdType


# Shared properties
class EngineBase(BaseModel):
    title: Optional[TitleType] = None
    hidden: Optional[bool] = None


class EngineCreate(EngineBase):
    title: Optional[TitleType] = None
    hidden: Optional[bool] = None


class EngineUpdate(EngineBase):
    pass


# Properties shared by models stored in DB
class EngineInDBBase(EngineBase):
    id: IdType
    title: TitleType
    hidden: bool

    class Config:
        orm_mode = True


# Properties to return to client
class Engine(EngineInDBBase):
    pass


# Properties properties stored in DB
class EngineInDB(EngineInDBBase):
    pass


class FormField(BaseModel):
    title: str
    type: str
    minimum: Optional[int]
    maximum: Optional[int]
    minLength: Optional[int]
    maxLength: Optional[int]


class EngineConnParamsForm(BaseModel):
    properties: Dict[str, FormField]
    required: List[str]
