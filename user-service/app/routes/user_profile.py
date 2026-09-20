from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user_profile import UserProfile
from app.schemas.user_profile import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse
)
from app.security.dependencies import (
    get_current_user,
    require_admin
)
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/me", response_model=UserProfileResponse)
def create_my_profile(
    profile_data: UserProfileCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    existing_profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user_id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    new_profile = UserProfile(
        user_id=user_id,
        full_name=profile_data.full_name,
        bio=profile_data.bio,
        profile_image=profile_data.profile_image
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user_id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return profile


@router.get("/admin/test")
def admin_test(
    current_user: dict = Depends(require_admin)
):
    return {
        "message": "Welcome Admin",
        "user_id": current_user.get("sub"),
        "email": current_user.get("email"),
        "role": current_user.get("role")
    }


@router.put("/me", response_model=UserProfileResponse)
def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user_id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    if profile_data.full_name is not None:
        profile.full_name = profile_data.full_name

    if profile_data.bio is not None:
        profile.bio = profile_data.bio

    if profile_data.profile_image is not None:
        profile.profile_image = profile_data.profile_image

    db.commit()
    db.refresh(profile)

    return profile