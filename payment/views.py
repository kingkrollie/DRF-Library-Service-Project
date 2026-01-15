import os

import stripe
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment.test_payment import create_checkout_session


class PaymentViewSet(ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    # permission_classes = Only admin or only owner of payments

    def get_queryset(self):
        return Payment.objects.all()


from rest_framework.views import APIView
from rest_framework.response import Response


class PayView(APIView):  #TEST TEST TEST
    def post(self, request):
        session = create_checkout_session(amount_usd=50)
        return Response({
            "checkout_url": session.url
        })



load_dotenv()
#
# stripe.api_key = os.getenv("STRIPE_WEBHOOK_SECRET")


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
                secret=os.getenv("STRIPE_WEBHOOK_SECRET")
            )
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)


        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            stripe_session_id = session["id"]

            print("PAID SESSION:", stripe_session_id)

        return HttpResponse(status=200)