from fastapi import APIRouter

from api.endpoints import auth, users, datasources, engines, sshtunnels


api_router = APIRouter()
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(engines.router, prefix='/engines', tags=['engines'])
api_router.include_router(datasources.router, prefix='/data-sources', tags=['data-sources'])
api_router.include_router(sshtunnels.router, prefix='/ssh-tunnels', tags=['ssh-tunnels'])
