from apps.users.dtos.profile import ProfileData
from apps.users.models import Profile, User


class ProfileService:
    """Service responsible for profile-related operations."""

    @classmethod
    def create(cls, user: User, profile_data: ProfileData) -> Profile:
        """Create a profile for the provided user."""
        payload = profile_data.model_dump(exclude_none=True, exclude_unset=True)
        profile = Profile.objects.create(user=user, **payload)

        return profile
