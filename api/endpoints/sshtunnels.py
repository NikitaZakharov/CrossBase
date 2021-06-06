from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import models
import schemas
from api import deps


router = APIRouter()


@router.get('/', response_model=List[schemas.SSHTunnel])
def get_ssh_tunnels(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve current user SSH tunnels.
    """
    return crud.ssh_tunnel.get_multi_by_user(db, user_id=current_user.id)


@router.post('/', response_model=schemas.SSHTunnel)
def create_ssh_tunnel(
    *,
    db: Session = Depends(deps.get_db),
    ssh_tunnel_in: schemas.SSHTunnelCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new SSH tunnel for current user.
    """
    return crud.ssh_tunnel.create_with_user(db=db, obj_in=ssh_tunnel_in, user_id=current_user.id)


@router.put('/{id}', response_model=schemas.SSHTunnel)
def update_ssh_tunnel(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    ssh_tunnel_in: schemas.SSHTunnelUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update SSH tunnel.
    """
    ssh_tunnel = crud.ssh_tunnel.get(db=db, id=id)
    if not ssh_tunnel or ssh_tunnel.user_id != current_user.id:
        raise HTTPException(status_code=404, detail='SSH tunnel not found')
    return crud.ssh_tunnel.update(db=db, db_obj=ssh_tunnel, obj_in=ssh_tunnel_in)


@router.get('/{id}', response_model=schemas.SSHTunnel)
def read_ssh_tunnel(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get SSH tunnel by ID.
    """
    ssh_tunnel = crud.ssh_tunnel.get(db=db, id=id)
    if not ssh_tunnel or ssh_tunnel.user_id != current_user.id:
        raise HTTPException(status_code=404, detail='SSH tunnel not found')
    return ssh_tunnel


@router.delete('/{id}', response_model=schemas.SSHTunnel)
def delete_ssh_tunnel(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete SSH tunnel.
    """
    ssh_tunnel = crud.ssh_tunnel.get(db=db, id=id)
    if not ssh_tunnel or ssh_tunnel.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="SSH tunnel not found")
    return crud.ssh_tunnel.remove(db=db, id=id)
