from django.db import models
from django.utils.translation import gettext_lazy as _

from library.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PN", _("Pending")
        PAID = "PD", _("Paid")

    class Type(models.TextChoices):
        PAYMENT = "PM", _("Payment")
        FINE = "FN", _("Fine")

    status = models.CharField(
        max_length=2, choices=Status, default=Status.PENDING
    )
    type = models.CharField(max_length=2, choices=Type)  # noqa: VNE003
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=255, unique=True)
    money = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
