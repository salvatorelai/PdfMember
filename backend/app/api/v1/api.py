from fastapi import APIRouter

from app.api.v1.endpoints import auth, documents, membership, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(membership.router, prefix="/membership", tags=["membership"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
