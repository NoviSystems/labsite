import stripe
from datetime import datetime

from celery import shared_task
from django.conf import settings
from django.core import mail
from django.template import Template, Context

from foodapp.models import RiceCooker, StripeCustomer

from django.contrib.auth.models import User

stripe.api_key = settings.STRIPE_API_KEY


notification_email_msg = Template("""
This is your friendly reminder to submit payment for your
recent Foodapp invoice {{ date }}. If
you haven't done so already, you may use the following URL,
but you must do so before it expires on {{ exp_date }}.

URL: {{ url }}
""")

reminder_email_msg = Template("""
This is your friendly reminder to submit payment for your
recent Foodapp invoice {{ date }}. If
you haven't done so already, you may use the following URL,
but you must do so before it expires on {{ exp_date }}.

URL: {{ url }}
""")


# html_email_msg = Template("""
# <html>
#     <body>
#         <br /> This is your friendly reminder to submit a work log for {{ date }}. If
#         <br /> you haven't done so already, you may use the following URL,
#         <br /> but you must do so before it expires on {{ exp_date }}.
#         <p>
#         URL: {{ url }}
#         </p>
#     </body>
# <html>
# """)


@shared_task
def reset_rice_cooker():
    cookers = RiceCooker.objects.all()
    for cooker in cookers:
        cooker.is_on = False
        cooker.save()


@shared_task
def create_invoices():
    connection = mail.get_connection(fail_silently=False)

    customers = StripeCustomer.objects.all()

    for customer in customers:
        invoice = stripe.Invoice.create(customer=customer.customer_id)

        user = customer.user

        if not invoice.closed:
            subj = "[Foodapp] Automatic invoice payment notification"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipients = [user.email]

            msg = email_msg.render(Context())
            # html_msg = html_email_msg.render(Context())

            # email = mail.EmailMultiAlternatives(subj, msg, from_email, recipients)
            # email.attach_alternative(html_msg, 'text/html')

            email.connection = connection
            email.send()


@shared_task
def send_invoice_reminder_emails():

    if settings.FOODAPP_SEND_INVOICE_REMINDERS:
        connection = mail.get_connection(fail_silently=False)

        customers = StripeCustomer.objects.all()

        for customer in customers:
            invoice = stripe.Invioce.all(customer=customer.customer_id, limit=1)
            user = customer.user

            if not invoice.closed:
                subj = "[Foodapp] Automatic invoice payment reminder"
                from_email = settings.DEFAULT_FROM_EMAIL
                recipients = [user.email]

                msg = email_msg.render(Context())
                # html_msg = html_email_msg.render(Context())

                # email = mail.EmailMultiAlternatives(subj, msg, from_email, recipients)
                # email.attach_alternative(html_msg, 'text/html')

                email.connection = connection
                email.send()

