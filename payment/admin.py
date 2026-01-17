from django.contrib import admin

from payment.models import Payment


class PaymentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Payment, PaymentAdmin)
