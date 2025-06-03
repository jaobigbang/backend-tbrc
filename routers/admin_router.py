# routers/admin_router.py
from fastapi import APIRouter, Depends
from utils.dependencies import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard")
def admin_dashboard(current_admin=Depends(get_current_admin_user)):
    return {"message": f"Welcome Admin {current_admin['sub']}!"}

@router.get("/status")
def status_dashboard(current_admin=Depends(get_current_admin_user)):
    return {"message": f"Welcome Admin {current_admin['sub']}!"}
