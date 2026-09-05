from typing import Type

from django.contrib.auth import get_user_model

from apps.users.dtos.user import UserData
from apps.users.services.profile import ProfileData, ProfileService

User = get_user_model()
ProfileServiceType = Type[ProfileService]


class UserService:
    """Service responsible for user creation operations."""

    profile_service_class: ProfileServiceType = ProfileService

    @classmethod
    def register(
        cls,
        user_data: UserData,
        profile_data: ProfileData,
    ) -> User:  # type: ignore
        """Create a user together with its profile."""
        payload = user_data.model_dump()
        password = payload.pop("password")
        user = User(**payload)
        user.set_password(password)
        user.save()
        cls.profile_service_class.create(
            user=user, profile_data=profile_data or ProfileData()
        )

        return user
