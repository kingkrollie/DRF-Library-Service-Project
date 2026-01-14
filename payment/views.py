from django.contrib.auth import get_user_model
from rest_framework.viewsets import ReadOnlyModelViewSet

from payment.models import Payment
from payment.serializers import PaymentSerializer


class PaymentViewSet(ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    # permission_classes = Only admin or only owner of payments

    def get_queryset(self):
        return Payment.objects.all()
