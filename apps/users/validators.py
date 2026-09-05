from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    """Enforces length, character variety, and special character requirements."""

    def __init__(self, min_length=12):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must contain at least %(min_length)d characters."),
                code="password_too_short_complex",
                params={"min_length": self.min_length},
            )
        if not any(c.islower() for c in password) or not any(
            c.isupper() for c in password
        ):
            raise ValidationError(
                _("Password must mix upper and lower case characters."),
                code="password_missing_case",
            )
        if not any(not c.isalnum() for c in password):
            raise ValidationError(
                _("Password must include at least one special character."),
                code="password_missing_special",
            )

    def get_help_text(self):
        return _(
            "Use at least %(min_length)d characters with upper case, lower case, and a special character."
        ) % {"min_length": self.min_length}
