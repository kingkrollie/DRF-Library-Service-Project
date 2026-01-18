from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money",
        )
        read_only_fields = (
            "id",
            "status",
            "money",
            "session_url",
            "borrowing",
        )
