from celery import shared_task
from django.utils.timezone import now

from payment.models import Payment
from library.models import Borrowing
from .services.telegram_client import send_telegram_message


@shared_task
def notify_new_borrowing(borrowing_id):
    borrowing = Borrowing.objects.select_related("user", "book").get(id=borrowing_id)
    message = (
        f"📚 New Borrowing Created!\n"
        f"👤 User: {borrowing.user.email}\n"
        f"📖 Book: {borrowing.book.title}\n"
        f"📅 Borrow Date: {borrowing.borrow_date}\n"
        f"📅 Expected Return: {borrowing.expected_return_date}"
    )
    send_telegram_message(message)


@shared_task
def notify_overdue_borrowings():
    today = now().date()

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True
    ).select_related("user", "book")

    messages = [
        (
            "📚 Borrowing overdue!\n"
            f"👤 User: {borrowing.user.email}\n"
            f"📖 Book: {borrowing.book.title}\n"
            f"📅 Expected return date: {borrowing.expected_return_date}"
        )
        for borrowing in overdue_borrowings
    ]

    if not messages:
        send_telegram_message("✅ No borrowings overdue today!")
        return

    for msg in messages:
        send_telegram_message(msg)


@shared_task
def notify_payment_success(payment_id):
    payment = Payment.objects.select_related(
        "borrowing__user",
        "borrowing__book"
    ).get(id=payment_id)

    actual_money = payment.money / 100
    if payment.type == "FN":
        message = (
            f"🚩Fine payment🚩\n"
            f"💳 Payment Successful!\n"
            f"👤 User: {payment.borrowing.user.email}\n"
            f"📖 Book: {payment.borrowing.book.title}\n"
            f"💰 Amount: ${actual_money}"
        )
    else:
        message = (
            f"💳 Payment Successful!\n"
            f"👤 User: {payment.borrowing.user.email}\n"
            f"📖 Book: {payment.borrowing.book.title}\n"
            f"💰 Amount: ${actual_money}"
        )

    send_telegram_message(message)
