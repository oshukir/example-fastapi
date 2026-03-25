from fastapi import APIRouter
from ..config import settings

router = APIRouter(tags=['Information'])

@router.get("/info")
def get_app_info():
    return {
        "version" : settings.APP_VERSION,
        "is_debug" : settings.DEBUG_MODE
    }