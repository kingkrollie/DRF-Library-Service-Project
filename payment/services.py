import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_API_KEY
FINE_MULTIPLAYER = 2

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
        success_url="http://127.0.0.1:8000/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://127.0.0.1:8000/cancel",
    )

    return session

def create_payment_fee_session(borrowing):
    days = (borrowing.actual_return_date - borrowing.expected_return_date).days
    fee_price = (days * borrowing.book.daily_fee) * FINE_MULTIPLAYER
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
                    "unit_amount": int(fee_price * 100),
                },
                "quantity": 1,
            }
        ],
        success_url="http://127.0.0.1:8000/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://127.0.0.1:8000/cancel",
    )
    session.fee_amount = fee_price

    return session
