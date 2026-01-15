import os
from dotenv import load_dotenv
import stripe

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_checkout_session(amount_usd: int):   #TEST TEST TEST
    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Test payment",
                    },
                    "unit_amount": amount_usd * 100,  # cents
                },
                "quantity": 1,
            }
        ],
        success_url="http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://localhost:8000/cancel",
    )
    return session
