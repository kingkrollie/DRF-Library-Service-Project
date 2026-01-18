import os
import stripe
from django.conf import settings
from django.utils.decorators import method_decorator

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView

from library.permissions import IsOwnerOrStaff
from payment.models import Payment
from payment.serializers import PaymentSerializer

from notifications.tasks import notify_payment_success

stripe.api_key = settings.STRIPE_API_KEY


class PaymentViewSet(ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrStaff)

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Payment.objects.select_related(
                "borrowing",
                "borrowing__user",
                "borrowing__book",
            )

        return Payment.objects.select_related(
            "borrowing",
            "borrowing__user",
            "borrowing__book",
        ).filter(borrowing__user=user)


def payment_success(request):
    session_id = request.GET.get("session_id")

    return HttpResponse(
        f"✅ Payment successful! Session ID: {session_id}"
    )


def payment_cancel(request):
    return HttpResponse("❌ Payment was cancelled.")


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=os.getenv("STRIPE_WEBHOOK_SECRET"),
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            try:
                payment = Payment.objects.get(session_id=session["id"])
                payment.status = Payment.Status.PAID
                payment.save(update_fields=["status"])
                notify_payment_success.delay(payment.id)
            except Payment.DoesNotExist:
                pass

        return HttpResponse(status=200)
