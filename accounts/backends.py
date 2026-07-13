from django.contrib.auth.backends import ModelBackend
from .models import CustomUser


class EmailOrUsernameBackend(ModelBackend):
    """Allow login with either username or email address."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        # Try email first, fall back to username
        try:
            user = CustomUser.objects.get(email__iexact=username)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(username__iexact=username)
            except CustomUser.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
