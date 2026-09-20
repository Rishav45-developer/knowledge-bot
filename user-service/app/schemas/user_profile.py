from pydantic import BaseModel


class UserProfileCreate(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    profile_image: str | None = None


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    profile_image: str | None = None


class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str | None
    bio: str | None
    profile_image: str | None

    class Config:
        from_attributes = True