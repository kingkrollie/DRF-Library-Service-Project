from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "HARD", _("Hard")
        SOFT = "SOFT", _("Soft")

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=4,
        choices=Cover,
    )

    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.title}  {self.author}"


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(expected_return_date__gte=F("borrow_date")),
                name="expected_return_gte_borrow_date",
            ),
            models.CheckConstraint(
                condition=Q(actual_return_date__isnull=True) | Q(
                    actual_return_date__gte=F("borrow_date")),
                name="actual_return_null_or_gte_borrow_date",
            ),
        ]

    @property
    def total_price(self):
        days = (self.expected_return_date - self.borrow_date).days
        return days * self.book.daily_fee

    def __str__(self):
        return f"{self.user} borrowed {self.book}"
