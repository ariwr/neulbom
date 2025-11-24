from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.connection import get_db
from app.models import models, schema
from app.models import crud
from app.services.auth_service import get_current_active_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=schema.UserProfile)
def get_my_profile(current_user: models.User = Depends(get_current_active_user)):
    """내 프로필 조회 (나이, 지역, 등급)"""
    return current_user


@router.put("/me", response_model=schema.UserProfile)
def update_my_profile(
    profile_update: schema.UserProfileUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """내 프로필 수정"""
    updated_user = crud.update_user_profile(db, current_user.id, profile_update)
    return updated_user

