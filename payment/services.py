import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_API_KEY
FINE_MULTIPLAYER = 2


def create_payment_session(borrowing, is_fee: bool = False):
    total_price = int(borrowing.total_price * 100)
    if is_fee:
        days = (
            borrowing.actual_return_date - borrowing.expected_return_date
        ).days
        fee_price = (days * borrowing.book.daily_fee) * FINE_MULTIPLAYER
        total_price = int(fee_price * 100)
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
                    "unit_amount": total_price,
                },
                "quantity": 1,
            }
        ],
        success_url="http://127.0.0.1:8000/api/success/?session_id={CHECKOUT_SESSION_ID}",  # noqa
        cancel_url="http://127.0.0.1:8000/api/cancel/",
    )

    session.total_price = total_price

    return session
