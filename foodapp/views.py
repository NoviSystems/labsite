import datetime
import stripe
from decimal import Decimal, ROUND_UP

from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views.generic import CreateView, ListView, TemplateView
from django.views.generic.edit import DeleteView, UpdateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from foodapp import forms, models
from models import StripeCustomer

stripe.api_key = settings.STRIPE_API_KEY


class HomeView(CreateView):
    model = models.Order
    form_class = forms.OrderForm
    success_url = reverse_lazy('foodapp:home')
    template_name = 'foodapp/home.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'riceOn' in request.POST:
            models.RiceCooker.objects.all().update(is_on=True)
            return redirect(self.success_url)

        if 'riceOff' in request.POST:
            models.RiceCooker.objects.all().update(is_on=False)
            return redirect(self.success_url)

        if models.RiceCooker.objects.filter(is_on=True).exists():
            return self.get(request, error='Cannot place order, rice is currently cooking.', *args, **kwargs)

        return super(HomeView, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        form_kwargs = super(HomeView, self).get_form_kwargs()
        if 'data' in form_kwargs:
            data = form_kwargs['data'].copy()
            data['user'] = self.request.user.pk
            form_kwargs['data'] = data
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        now = datetime.datetime.now()
        orders = models.Order.objects.filter(date=datetime.date.today())

        context['last_month'] = "%02d" % (now.month - 1)
        context['year'] = now.year
        context['orders'] = orders
        context['rice_quantity'] = (orders.filter(item__description__icontains='rice').aggregate(Sum('quantity'))['quantity__sum'] or 0) * .5
        context['rice_is_on'] = models.RiceCooker.objects.filter(is_on=True).exists()
        return context


class StripeCreateView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):

    """
    TemplateView for StripeCreateView

    Create a Stripe value associated to the user
    This function sends

    Attributes:
        success_message (str) = Message upon form valid
        success_url (str) = Reverse to AccountSettingsView
        template_name_suffix (str): Generic template to be rendered
    """

    success_message = 'Stripe added successfully!'
    success_url = reverse_lazy('foodapp:stripe_card_list')
    template_name = 'foodapp/stripe_create_form.html'

    def get_context_data(self, **kwargs):

        """
        Insert objects into the context dictionary

        Context Dictionary Arguments:
            stripe: value used to display is the user already has associated Stripe data
        """

        context = super(StripeCreateView, self).get_context_data()
        try:
            StripeCustomer.objects.get(user=self.request.user)
            customerExists = True
        except ObjectDoesNotExist:
            customerExists = False
        context['customerExists'] = customerExists
        return context

    def post(self, request, *args, **kwargs):

        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.

        Use the stripe.api_key and token returned from a users CC info to create a customer
        Store the customer data as a Stripe object
        """
        customerExists = request.POST.get("customerExists")
        token = request.POST.get('stripeToken', False)
        # New Card
        if customerExists:
            customer_id = StripeCustomer.objects.get(user=self.request.user).customer_id
            customer = stripe.Customer.retrieve(customer_id)
            customer.sources.create(source=token)
            return redirect(self.success_url, request)
        # New Customer
        else:
            customer = stripe.Customer.create(source=token, )
            StripeCustomer.objects.create(user=self.request.user, customer_id=customer.id)
            return redirect(self.success_url, request)


class StripeCardDeleteView(LoginRequiredMixin, TemplateView):
    model = models.StripeCustomer
    success_url = reverse_lazy('foodapp:stripe_card_list')

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        customer_id = StripeCustomer.objects.get(user=self.request.user).customer_id
        customer = stripe.Customer.retrieve(customer_id)
        customer.sources.retrieve(args[0]).delete()
        return redirect(self.success_url, request)


class StripeCardListView(LoginRequiredMixin, TemplateView):
    template_name = 'foodapp/cards.html'

    def get_context_data(self, **kwargs):
        context = super(StripeCardListView, self).get_context_data(**kwargs)
        try:
            customer = StripeCustomer.objects.get(user=self.request.user).customer_id
        except ObjectDoesNotExist:
            return context
        cards = stripe.Customer.retrieve(customer).sources.all(object='card')
        # Needs to be way to read more than one card here. Refactor
        cardVals = []
        for data in cards.get('data'):
            cardVals += [(data['id'], data['last4'])]
        context['cards'] = cardVals
        return context


class StripeCardUpdateView(LoginRequiredMixin, CreateView):
    template_name = ''
    success_url = reverse_lazy('foodapp:stripe_card_list')

    def get_context_data(self, **kwargs):
        context = super(StripeCardUpdateView, self).get_context_data(**kwargs)
        try:
            StripeCustomer.objects.get(user=self.request.user)
            stripe = True
        except ObjectDoesNotExist:
            stripe = False
        context['stripe'] = stripe
        return context


class OrderListView(ListView):
    model = models.Order
    context_object_name = 'orders'
    template_name = 'foodapp/orders.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderListView, self).dispatch(*args, **kwargs)


class UserOrderView(OrderListView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserOrderView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        username = self.kwargs.get('username', None)

        if username is not None:
            return models.Order.objects.filter(user__username=username)

    def get_context_data(self, **kwargs):
        context = super(UserOrderView, self).get_context_data(**kwargs)
        context['title'] = 'Order History for ' + self.request.user.username + ":"
        return context


def last_month_view(request):
    now = datetime.date.today()
    last_month = (now.month - 1)
    year = now.year
    if now.month == 1:
        year = (now.year - 1)
        last_month = 12

    year = str(year)
    last_month = "%02d" % last_month
    # if request.user.is_superuser:
    #     return redirect('foodapp:super_month_orders', year, last_month)
    # else:
    return redirect('foodapp:month_orders', year, last_month)


class LeaderboardView(TemplateView):
    template_name = 'foodapp/leader.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LeaderboardView, self).dispatch(*args, **kwargs)

    def helper(self, leaderboard, items, leaderboardMax):
        helper = 1
        mvp = ""
        item_values = items.values_list('username', 'b_count')

        if len(item_values) > 0:
            mvp = item_values[0][0]

        for i in range(0, len(item_values)):
            item = item_values[i]

            if item[0] not in mvp and item[1] == item_values[0][1]:
                mvp += ", " + item[0]

            if i > 0 and item_values[i][1] == item_values[i - 1][1]:
                helper = helper - 1

            if len(leaderboard) < leaderboardMax:
                leaderboard.append((i + helper, item[0], item[1]))
            elif item[0] == str(self.request.user):
                leaderboard.pop()
                leaderboard.append((i + helper, item[0], item[1]))

        return mvp

    def annotate_user_orders(self, orders):
        return orders.annotate(b_count=Sum('orders__quantity')).order_by('-b_count')

    def get_burrito_eater_diet(self, year=None, month=None):
        if month is None and year is not None:
            return User.objects.filter(orders__item__name__iexact="Burrito", orders__date__year=year)
        elif month is not None and year is not None:
            return User.objects.filter(orders__item__name__iexact="Burrito", orders__date__year=year, orders__date__month=month)
        return User.objects.filter(orders__item__name__iexact="Burrito")

    def get_context_data(self, **kwargs):
        context = super(LeaderboardView, self).get_context_data(**kwargs)
        now = datetime.date.today()
        user = self.request.user

        last_month_date = now - datetime.timedelta(days=now.day + 1)
        last_year_date = datetime.date(int(now.year - 1), 1, 1)

        all_time_burrito_eaters_score = self.annotate_user_orders(self.get_burrito_eater_diet())
        last_year_burrito_eaters_score = self.annotate_user_orders(self.get_burrito_eater_diet(year=last_year_date.year))
        last_month_burrito_eaters_score = self.annotate_user_orders(self.get_burrito_eater_diet(year=last_month_date.year, month=last_month_date.month))
        current_month_burrito_eaters_score = self.annotate_user_orders(self.get_burrito_eater_diet(year=now.year, month=now.month))

        sorted_alltime = []
        sorted_year = []
        sorted_month = []
        sorted_current = []

        month_mvp = self.helper(sorted_month, last_month_burrito_eaters_score, 5)
        year_mvp = self.helper(sorted_year, last_year_burrito_eaters_score, 5)
        alltime_mvp = self.helper(sorted_alltime, all_time_burrito_eaters_score, 5)
        current_mvp = self.helper(sorted_current, current_month_burrito_eaters_score, 5)

        context['last_month_month'] = last_month_date.strftime('%B')
        context['current_month_month'] = now.strftime('%B')
        context['last_year'] = last_year_date.year
        context['alltime_dict'] = sorted_alltime
        context['year_dict'] = sorted_year
        context['month_dict'] = sorted_month
        context['current_dict'] = sorted_current
        context['current_user'] = str(user)
        context['month_mvp'] = month_mvp
        context['year_mvp'] = year_mvp
        context['alltime_mvp'] = alltime_mvp
        context['current_mvp'] = current_mvp

        return context


class MonthOrdersView(TemplateView):
    template_name = 'foodapp/month.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MonthOrdersView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MonthOrdersView, self).get_context_data(**kwargs)

        # Grabs year and month keywords from url
        year = self.kwargs['year']
        month = self.kwargs['month']
        now = datetime.date(int(year), int(month), 1)
        context['year'] = year
        context['month'] = now.strftime('%B')
        # Calculates the total number of burritos in a given month.
        # ASSUMES ALL MONTHLY COSTS ARE APPLIED TO BURRITOS ONLY!!!
        month_orders = models.Order.objects.filter(date__month=month, date__year=year)
        num_burritos = 0
        num_rice = 0

        for order in month_orders:
            if order.item.name.lower() == "burrito":
                num_burritos += order.quantity
            elif "rice" in order.item.description.lower():
                num_rice += order.quantity * .5

        context["num_burritos"] = num_burritos
        context["num_rice"] = num_rice

        # Creates a dictionary of user to number of burritos consumed
        user_to_orders_dict = {}
        rice_products = month_orders.filter(item__description__icontains="rice")

        for order in rice_products.filter(item__name__iexact="Burrito"):
            user_to_orders_dict[order.user.username] = [user_to_orders_dict.get(order.user.username, [0, 0])[0] + order.quantity, 0]

        for order in rice_products.exclude(item__name__iexact="Burrito"):
            if (order.user.username not in user_to_orders_dict):
                user_to_orders_dict[order.user.username] = [0, 0]
            user_to_orders_dict[order.user.username][1] = user_to_orders_dict.get(order.user.username, [0, 0])[1] + order.quantity * .5

        for username in user_to_orders_dict:
            num_burritos = user_to_orders_dict[username][0]
            num_just_rice = user_to_orders_dict[username][1]
            user_to_orders_dict[username] = (num_burritos, num_just_rice)

        context["user_to_orders_dict"] = user_to_orders_dict

        return context


class SuperMonthOrdersView(TemplateView):
    template_name = 'foodapp/super_month.html'
    form_class = forms.PaidForm
    object = models.AmountPaid

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SuperMonthOrdersView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        success_url = reverse_lazy('foodapp:last_month_view')
        if request.user.is_superuser:
            year = self.kwargs['year']
            month = self.kwargs['month']
            filtered_orders = models.Order.objects.filter(item__name__iexact="Burrito").filter(date__month=month).filter(date__year=year)

            usernames = {}
            for order in filtered_orders:
                user_used = False
                for username in usernames:
                    if order.user.username == usernames[username]:
                        user_used = True
                if not user_used:
                    usernames[order] = order.user.username
                    if request.method == 'POST':
                        form_id = 'id_' + order.user.username
                        form = request.POST.get(form_id)
                        if form:
                            new_save = models.AmountPaid(amount=form, user=order.user, date=order.date)
                            new_save.save()
        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super(SuperMonthOrdersView, self).get_context_data(**kwargs)
        # Grabs year and month keywords from url
        year = self.kwargs['year']
        month = self.kwargs['month']
        now = datetime.date(int(year), int(month), 1)
        context['year'] = year
        context['month'] = now.strftime('%B')

        # Calculates the total number of burritos in a given month.
        # ASSUMES ALL MONTHLY COSTS ARE APPLIED TO BURRITOS ONLY!!!
        month_orders = models.Order.objects.filter(date__month=month, date__year=year)
        num_burritos = 0
        for order in month_orders:
            if order.item.name.lower() == "burrito":
                num_burritos += order.quantity
        context["num_burritos"] = num_burritos

        # Sum the total MonthlyCosts objects for a given month/year. Set to zero if no objects returned.
        cost = 0
        costs = models.MonthlyCost.objects.filter(date__month=month, date__year=year)
        for item in costs:
            cost += item.cost

        cost = float(cost) / 0.9725
        context["cost"] = ("%.2f" % cost)

        # Calculates cost per burrito
        if num_burritos:
            cost_per_burrito = Decimal(cost / num_burritos).quantize(Decimal('.01'), rounding=ROUND_UP)
        else:
            cost_per_burrito = 0

        context["cost_per_burrito"] = cost_per_burrito

        # Creates a dictionary of user to number of burritos consumed
        user_to_orders_dict = {}
        for order in models.Order.objects.filter(item__name__iexact="Burrito").filter(date__month=month).filter(date__year=year):
            user_to_orders_dict[order.user.username] = user_to_orders_dict.get(order.user.username, 0) + order.quantity
        for username in user_to_orders_dict:
            money_paid = Decimal(0)
            num_burritos = user_to_orders_dict[username]
            money_owed = num_burritos * cost_per_burrito
            for paid in models.AmountPaid.objects.filter(date__month=month).filter(date__year=year):
                if paid.user.username == username:
                    money_paid += paid.amount
                    money_owed = (num_burritos * cost_per_burrito) - money_paid
            user_to_orders_dict[username] = (num_burritos, num_burritos * cost_per_burrito, money_owed, money_paid)

        context["user_to_orders_dict"] = user_to_orders_dict
        return context
