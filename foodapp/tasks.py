import stripe

from celery import shared_task
from django.conf import settings
from django.core import mail
from django.template import Template, Context

from foodapp.models import RiceCooker, StripeCustomer

stripe.api_key = settings.STRIPE_API_KEY


notification_email_msg = Template("""
This is your friendly reminder to submit payment for your
recent Foodapp invoice for a total of {{ total_cost }}.  Please
navigate to the following link in order to view and pay this
invoice.

{% url 'foodapp:stripe_invoice_create' %}

If you fail to pay this invoice, the items will be rolled into
the next invoice.
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

    if settings.FOODAPP_SEND_INVOICE_REMINDERS:
        for customer in customers:
            # Calculate total cost
            all_invoice_items = stripe.InvoiceItem.all(customer=customer.customer_id)

            total_cost = 0
            for data in all_invoice_items.get('data'):
                if data['invoice'] is None:
                    total_cost += int(data['amount'])

            total_cost = '$%.2f' % (total_cost / 100.00)

            # Send email
            user = customer.user
            subj = "[Foodapp] Payment required - you have unpaid items on Foodapp"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipients = [user.email]

            msg = notification_email_msg.render(Context({"total_cost": total_cost}))
            email = mail.EmailMessage(subj, msg, from_email, recipients)

            # html_msg = html_email_msg.render(Context())
            # email = mail.EmailMultiAlternatives(subj, msg, from_email, recipients)
            # email.attach_alternative(html_msg, 'text/html')

            email.connection = connection
            email.send()

