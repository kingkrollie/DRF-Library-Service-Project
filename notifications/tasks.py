import logging

from celery import shared_task
from django.utils.timezone import now

from library.models import Borrowing
from payment.models import Payment
from .services.telegram_client import send_telegram_message

logger = logging.getLogger(__name__)


@shared_task
def notify_new_borrowing(borrowing_id):
    try:
        borrowing = Borrowing.objects.select_related(
            "user",
            "book"
        ).get(id=borrowing_id)

        message = (
            f"📚 New Borrowing Created!\n"
            f"👤 User: {borrowing.user.email}\n"
            f"📖 Book: {borrowing.book.title}\n"
            f"📅 Borrow Date: {borrowing.borrow_date}\n"
            f"📅 Expected Return: {borrowing.expected_return_date}"
        )

        send_telegram_message(message)

    except Borrowing.DoesNotExist:
        logger.warning(
            "Borrowing with id=%s does not exist. Skipping notification.",
            borrowing_id
        )

    except Exception as exc:
        logger.exception(
            "Failed to send telegram notification for borrowing id=%s: %s",
            borrowing_id,
            exc
        )


@shared_task
def notify_overdue_borrowings():
    today = now().date()

    try:
        overdue_borrowings = Borrowing.objects.filter(
            expected_return_date__lte=today,
            actual_return_date__isnull=True
        ).select_related("user", "book")

        if not overdue_borrowings.exists():
            send_telegram_message("✅ No borrowings overdue today!")
            return

        for borrowing in overdue_borrowings:
            message = (
                "📚 Borrowing overdue!\n"
                f"👤 User: {borrowing.user.email}\n"
                f"📖 Book: {borrowing.book.title}\n"
                f"📅 Expected return date: {borrowing.expected_return_date}"
            )
            send_telegram_message(message)

    except Exception as exc:
        logger.exception("Failed to process overdue borrowings: %s", exc)


@shared_task
def notify_payment_success(payment_id):
    try:
        payment = Payment.objects.select_related(
            "borrowing__user",
            "borrowing__book"
        ).get(id=payment_id)

        actual_money = payment.money / 100

        message_prefix = "🚩Fine payment🚩\n" if payment.type == "FN" else ""

        message = (
            f"{message_prefix}"
            f"💳 Payment Successful!\n"
            f"👤 User: {payment.borrowing.user.email}\n"
            f"📖 Book: {payment.borrowing.book.title}\n"
            f"💰 Amount: ${actual_money}"
        )

        send_telegram_message(message)

    except Payment.DoesNotExist:
        logger.warning(
            "Payment with id=%s does not exist. Skipping notification.",
            payment_id
        )

    except Exception as exc:
        logger.exception(
            "Failed to send payment notification for payment id=%s: %s",
            payment_id,
            exc
        )
