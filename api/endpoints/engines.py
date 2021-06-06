from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
from api import deps
from core.utils import get_engine_conn_params_schema_cls

router = APIRouter()


@router.get('/', response_model=List[schemas.Engine])
def get_engines(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Retrieve current user data sources.
    """
    return crud.engine.get_multi(db)


@router.get('/{id}/form', response_model=schemas.EngineConnParamsForm, response_model_exclude_unset=True)
def get_engine_conn_params_form(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Get specified data source schema.
    """
    engine = crud.engine.get(db=db, id=id)
    if not engine or engine.hidden:
        raise HTTPException(status_code=404, detail="Data source not found")
    conn_params_schema_cls = get_engine_conn_params_schema_cls(engine.title)
    return schemas.EngineConnParamsForm(**conn_params_schema_cls.schema())
