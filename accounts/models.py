from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PasswordResetCode(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    code = models.CharField(
        max_length=100,
        unique=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    used = models.BooleanField(
        default=False,
    )

    def __str__(self) -> str:
        return f"{self.user.email} - {self.code}"

    def is_expired(self) -> bool:
        expiration_time = (
            self.created_at +
            timezone.timedelta(minutes=15)
        )

        return timezone.now() > expiration_time