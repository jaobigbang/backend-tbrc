from fastapi import APIRouter
from .core_router import router as core_router
from .protein_web_router import router as protein_web_router

router = APIRouter()

# Combine routers here
router.include_router(core_router)
router.include_router(protein_web_router)