from celery import shared_task
from .services.telegram_client import send_telegram_message
from library.models import Borrowing


@shared_task
def notify_new_borrowing(borrowing_id):
    borrowing = Borrowing.objects.get(id=borrowing_id)
    message = (
        f"📚 New Borrowing Created!\n"
        f"User: {borrowing.user.email}\n"
        f"Book: {borrowing.book.title}\n"
        f"Borrow Date: {borrowing.borrow_date}\n"
        f"Expected Return: {borrowing.expected_return_date}"
    )
    send_telegram_message(message)
