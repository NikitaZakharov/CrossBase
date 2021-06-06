import json
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import crud
import models
import schemas
from core.utils import (
    get_datasource_conn,
    get_engine_introspection_cls,
    get_engine_error_cls,
    get_engine_conn_params_schema_cls,
    get_ssh_tunnel_error_cls,
)
from core.redis import make_cache_key, cache
from api import deps


router = APIRouter()


@router.get('/', response_model=List[schemas.DataSource])
def get_data_sources(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve current user data sources.
    """
    return crud.data_source.get_multi_by_user(db, user_id=current_user.id)


@router.post('/', response_model=schemas.DataSource)
def create_data_source(
    *,
    db: Session = Depends(deps.get_db),
    data_source_in: schemas.DataSourceCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new data source for current user.
    """
    if not crud.engine.get(db=db, id=data_source_in.engine_id):
        raise HTTPException(status_code=404, detail='Engine not found')

    if data_source_in.ssh_tunnel_id:
        ssh_tunnel = crud.ssh_tunnel.get(db=db, id=data_source_in.ssh_tunnel_id)
        if not ssh_tunnel or ssh_tunnel.user_id != current_user.id:
            raise HTTPException(status_code=404, detail='SSH tunnel not found')

    return crud.data_source.create_with_user(db=db, obj_in=data_source_in, user_id=current_user.id)


@router.put('/{id}', response_model=schemas.DataSource)
def update_data_source(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    data_source_in: schemas.DataSourceUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a data source.
    """
    data_source = crud.data_source.get(db=db, id=id)
    if not data_source or data_source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail='Data source not found')

    if data_source_in.ssh_tunnel_id and data_source.ssh_tunnel_id != data_source_in.ssh_tunnel_id:
        ssh_tunnel = crud.ssh_tunnel.get(db=db, id=data_source_in.ssh_tunnel_id)
        if not ssh_tunnel or ssh_tunnel.user_id != current_user.id:
            raise HTTPException(status_code=404, detail='SSH tunnel not found')

    if data_source_in.engine_id and data_source.engine_id != data_source_in.engine_id:
        if not crud.engine.get(db=db, id=data_source_in.engine_id):
            raise HTTPException(status_code=404, detail='Engine not found')

    if data_source_in.settings:
        conn_params_schema_cls = get_engine_conn_params_schema_cls(data_source.engine.title)
        conn_params_schema_cls(**data_source_in.settings)

    return crud.data_source.update(db=db, db_obj=data_source, obj_in=data_source_in)


@router.get('/{id}', response_model=schemas.DataSource)
def read_data_source(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get data source by ID.
    """
    data_source = crud.data_source.get(db=db, id=id)
    if not data_source or data_source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail='Data source not found')
    return data_source


@router.delete('/{id}', response_model=schemas.DataSource)
def delete_data_source(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete data source.
    """
    data_source = crud.data_source.get(db=db, id=id)
    if not data_source or data_source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Data source not found")
    return crud.data_source.remove(db=db, id=id)


@router.post('/{id}/query', response_model=schemas.QueryResult, responses={'400': {'model': schemas.Msg}})
def execute_query(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    query: str = Body(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Execute query for specified data source.
    """
    data_source = crud.data_source.get(db=db, id=id)
    if not data_source or data_source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Data source not found")

    conn = None
    try:
        with get_datasource_conn(data_source) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                if cursor.description is None:
                    data = [(cursor.statusmessage, )]
                    columns = ['status', ]
                else:
                    data = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]
                return {'data': data, 'columns': columns}
    # client exceptions should be returned to client
    except (get_engine_error_cls(data_source.engine.title), get_ssh_tunnel_error_cls()) as e:
        return JSONResponse(status_code=400, content={'msg': str(e)})
    finally:
        if conn is not None:
            conn.close()


@router.get('/{id}/schema', response_model=List[schemas.TableEntity], responses={'400': {'model': schemas.Msg}})
async def get_data_source_schema(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    from_cache: bool = False,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get specified data source schema.
    """
    data_source = crud.data_source.get(db=db, id=id)
    if not data_source or data_source.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Data source not found")

    if from_cache:
        cache_key = make_cache_key(datasourceschema=id)
        if (schema := await cache.get(cache_key, decoder=json.loads)) is not None:
            return schema

    conn = None

    try:
        with get_datasource_conn(data_source) as conn:
            introspection_cls = get_engine_introspection_cls(data_source.engine.title)
            introspection = introspection_cls(conn)
            schema = introspection.get_structure()
            cache_key = make_cache_key(datasourceschema=id)
            await cache.set(cache_key, schema, encoder=json.dumps)
            return schema
    # client exceptions should be returned to client
    except (get_engine_error_cls(data_source.engine.title), get_ssh_tunnel_error_cls()) as e:
        return JSONResponse(status_code=400, content={'msg': str(e)})
    finally:
        if conn is not None:
            conn.close()
