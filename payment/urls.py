from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payment.views import (
    PaymentViewSet,
    StripeWebhookView,
    payment_success,
    payment_cancel,
)

app_name = "payment"

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"
    ),
    path("success/", payment_success, name="payment-success"),
    path("cancel/", payment_cancel, name="payment-cancel"),
]
