from celery import shared_task
from django.utils.timezone import now

from .services.telegram_client import send_telegram_message
from library.models import Borrowing


@shared_task
def notify_new_borrowing(borrowing_id):
    borrowing = Borrowing.objects.get(id=borrowing_id)
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
        expected_return_date__lte=today, actual_return_date__isnull=True
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
