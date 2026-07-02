import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, queue="emails")
def send_order_confirmation_email(self, order_id):

    try:
        from django.conf import settings
        from django.core.mail import send_mail

        from .models import Order

        logger.info(f"starting email task for order {order_id}")

        order = (
            Order.objects.select_related("user")
            .prefetch_related("items")
            .get(id=order_id)
        )

        logger.info(f"Order found: {order.order_number}")

        send_mail(
            subject=f"Order #{order.order_number} Confirmed!",
            message=f"Your order #{order.order_number} has been confirmed",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=False,
        )

        logger.info("email sent successfully")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
