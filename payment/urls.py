from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet, StripeWebhookView

app_name = "payment"

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("", include(router.urls)),
    path("stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
