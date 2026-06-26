from django.db import models

class Family(models.Model):
    name = models.CharField(max_length=100)

class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100
    )

    family = models.ForeignKey(
        Family,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )