from django.db import models
from apps.accounts.models import User

class Transaction(models.Model):

    TYPE_CHOICES = [
        ("income","Receita"),
        ("expense","Despesa")
    ]

    PAYMENT_CHOICES = [
        ("pix","Pix"),
        ("credit","Crédito"),
        ("debit","Débito")
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    description = models.CharField(
        max_length=200
    )

    value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES
    )

    category = models.CharField(
        max_length=100
    )

    date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )