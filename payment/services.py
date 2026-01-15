import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_API_KEY

def create_payment_session(borrowing):
    total_price = borrowing.total_price

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Borrowing #{borrowing.id}",
                    },
                    "unit_amount": int(total_price * 100),
                },
                "quantity": 1,
            }
        ],
        success_url="http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://localhost:8000/cancel",
    )

    return session
