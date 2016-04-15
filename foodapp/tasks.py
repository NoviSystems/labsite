import stripe

from celery import shared_task
from django.conf import settings
from foodapp.models import RiceCooker, StripeCustomer

from django.contrib.auth.models import User

stripe.api_key = settings.STRIPE_API_KEY


@shared_task
def reset_rice_cooker():
    cookers = RiceCooker.objects.all()
    for cooker in cookers:
        cooker.is_on = False
        cooker.save()


@shared_task
def create_invoices():
    customers = StripeCustomer.objects.all()

    for customer in customers:
        invoice = stripe.Invoice.create(
            customer=customer.customer_id
        )

        # create page
        # send email

@shared_task
def send_invoice_reminder_emails():
    customers = StripeCustomer.objects.all()

    for customer in customers:
        invoice = stripe.Invioce.all(customer=customer.customer_id, limit=1)

        if not invoice.closed:
            pass
            # send emails