import os
import stripe
from django.utils.decorators import method_decorator
from django.views import View
from dotenv import load_dotenv

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView

from payment.models import Payment
from payment.serializers import PaymentSerializer

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class PaymentViewSet(ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.all()


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
                payment = Payment.objects.get(
                    session_id=session["id"]
                )
                payment.status = Payment.Status.PAID
                payment.save(update_fields=["status"])
            except Payment.DoesNotExist:
                pass

        return HttpResponse(status=200)


class PaymentSuccessView(View):
    def get(self, request):
        return HttpResponse("Payment successful! You can close this page.")
