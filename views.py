import datetime
from decimal import *

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views.generic import CreateView, ListView, TemplateView
from django.http import HttpResponseRedirect
from django.utils.functional import lazy
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import redirect

from models import Item, Order, RiceCooker, MonthlyCost, AmountPaid
from forms import OrderForm, PaidForm

# Workaround for using reverse with success_url in class based generic views
# because direct usage of it throws an exception.
reverse_lazy = lambda name=None, *args: lazy(reverse, str)(name, args=args)


class HomepageView(CreateView):
    form_class = OrderForm
    success_url = reverse_lazy('url_homepage')
    template_name = 'foodapp/homepage.html'
    object = Order

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomepageView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            item_pk = request.POST.get('item', None)

            if item_pk is not None:
                item = Item.objects.get(pk=item_pk)
            else:
                raise AttributeError('Could not locate item with pk %s' % item_pk)

            if item and item.once_a_day:
                order = None

                try:
                    order = Order.objects.filter(user=request.user).get(item__pk=item_pk, date=datetime.date.today)
                    return self.render_to_response(self.get_context_data(form=form, error='This item has already been ordered.'))
                except Order.DoesNotExist:
                    obj.user = request.user
                    obj.save()
                    return HttpResponseRedirect(self.success_url)
            else:
                obj.user = request.user
                obj.save()
                return HttpResponseRedirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)

        now = datetime.datetime.now()
        context['last_month'] = "%02d" % (now.month - 1)
        context['year'] = now.year
        context['rice_is_on'] = RiceCooker.objects.all()[0].is_on;
        return context


class OrderListView(ListView):
    model = Order
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
            return Order.objects.filter(user__username=username)

    def get_context_data(self, **kwargs):
        context = super(UserOrderView, self).get_context_data(**kwargs)
        context['title'] = 'Order History for ' + self.request.user.username + ":"
        return context


class TodaysOrdersView(OrderListView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TodaysOrdersView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TodaysOrdersView, self).get_context_data(**kwargs)
        orders = Order.objects.filter(date=datetime.date.today)
        context['orders'] = orders

        # The following piece of code is a hackish way to find the # of cups of rice needed
        burrito_count = 0
        for order in orders:
            if order.item.name.strip().lower().find('burrito') > -1:
                burrito_count = burrito_count + order.quantity
        context['rice_quantity'] = burrito_count * 0.5

        context['title'] = 'Today\'s Orders:'
        return context


#Updates all RiceCooker objects to true and redirects to homepage
def rice_on_view(request):
    RiceCooker.objects.all().update(is_on=True)
    return HttpResponseRedirect(reverse('url_homepage'))


#Updates all RiceCooker objects to false and redirects to homepage
def rice_off_view(request):
    RiceCooker.objects.all().update(is_on=False)
    return HttpResponseRedirect(reverse('url_homepage'))


def last_month_view(request):
    now = datetime.date.today()
    #FIX THIS BACK
    last_month = (now.month-1)
    year = now.year
    if now.month == 1:
        year = (now.year - 1)
        last_month = 12

    year = str(year)
    last_month = "%02d" % last_month
    if request.user.is_superuser:
        return redirect('url_super_month_orders', year, last_month)
    else:
        return redirect('url_month_orders', year, last_month)

class MonthOrdersView(TemplateView):
    template_name = 'foodapp/month.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MonthOrdersView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MonthOrdersView, self).get_context_data(**kwargs)

        #Grabs year and month keywords from url
        year = self.kwargs['year']
        month = self.kwargs['month']
        now = datetime.date(int(year), int(month), 1)
        context['year'] = year
        context['month'] = now.strftime('%B')

        #Calculates the total number of burritos in a given month.
        #ASSUMES ALL MONTHLY COSTS ARE APPLIED TO BURRITOS ONLY!!!
        month_orders = Order.objects.filter(date__month=month, date__year=year)
        num_burritos = 0
        for order in month_orders:
            if order.item.name.lower() == "burrito":
                num_burritos += order.quantity
        context["num_burritos"] = num_burritos

        #Sum the total MonthlyCosts objects for a given month/year. Set to zero if no objects returned.
        cost = 0
        costs = MonthlyCost.objects.filter(date__month=month, date__year=year)
        for item in costs:
            cost += item.cost

        cost = float(cost)/0.9725
        context["cost"] = ("%.2f" % cost)

        #Calculates cost per burrito
        if num_burritos:
            cost_per_burrito = Decimal(cost/num_burritos).quantize(Decimal('.01'), rounding=ROUND_UP)
        else:
            cost_per_burrito = 0

        context["cost_per_burrito"] = cost_per_burrito

        #Creates a dictionary of user to number of burritos consumed
        user_to_orders_dict = {}
        for order in Order.objects.filter(item__name__iexact="Burrito").filter(date__month=month).filter(date__year=year):
            user_to_orders_dict[order.user.username] = user_to_orders_dict.get(order.user.username, 0) + order.quantity

        for username in user_to_orders_dict:
            num_burritos = user_to_orders_dict[username]
            user_to_orders_dict[username] = (num_burritos, num_burritos*cost_per_burrito)

        context["user_to_orders_dict"] = user_to_orders_dict

        return context

class SuperMonthOrdersView(TemplateView):
    template_name = 'foodapp/super_month.html'
    form_class = PaidForm
    object = AmountPaid
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SuperMonthOrdersView, self).dispatch(*args, **kwargs)
    def post(self, request, *args, **kwargs):
        success_url = reverse_lazy('url_last_month_view')
	if request.user.is_superuser:
	    year = self.kwargs['year']
            month = self.kwargs['month']
            filtered_orders = Order.objects.filter(item__name__iexact="Burrito").filter(date__month=month).filter(date__year=year)
         
            usernames = {}
	    for order in filtered_orders:
                user_used = False
                for username in usernames:
                    if order.user.username == usernames[username]:
                        user_used = True
		if not user_used:
                    usernames[order] = order.user.username
    	            if request.method == 'POST':
	                form_id = 'id_'+order.user.username
		        form = request.POST.get(form_id)
		        if form:
		            new_save = AmountPaid(amount=form, user=order.user, date=order.date)
		            new_save.save()	
        return HttpResponseRedirect(success_url)
	    
    def get_context_data(self, **kwargs):
        context = super(SuperMonthOrdersView, self).get_context_data(**kwargs)
        #Grabs year and month keywords from url
        year = self.kwargs['year']
        month = self.kwargs['month']
        now = datetime.date(int(year), int(month), 1)
        context['year'] = year
        context['month'] = now.strftime('%B')

        #Calculates the total number of burritos in a given month.
        #ASSUMES ALL MONTHLY COSTS ARE APPLIED TO BURRITOS ONLY!!!
        month_orders = Order.objects.filter(date__month=month, date__year=year)
        num_burritos = 0
        for order in month_orders:
            if order.item.name.lower() == "burrito":
                num_burritos += order.quantity
        context["num_burritos"] = num_burritos

        #Sum the total MonthlyCosts objects for a given month/year. Set to zero if no objects returned.
        cost = 0
        costs = MonthlyCost.objects.filter(date__month=month, date__year=year)
        for item in costs:
            cost += item.cost

        cost = float(cost)/0.9725
        context["cost"] = ("%.2f" %  cost)

        #Calculates cost per burrito
        if num_burritos:
            cost_per_burrito = Decimal(cost/num_burritos).quantize(Decimal('.01'), rounding=ROUND_UP)
        else:
            cost_per_burrito = 0

        context["cost_per_burrito"] = cost_per_burrito
	
        #Creates a dictionary of user to number of burritos consumed
        user_to_orders_dict = {}
        for order in Order.objects.filter(item__name__iexact="Burrito").filter(date__month=month).filter(date__year=year):
            user_to_orders_dict[order.user.username] = user_to_orders_dict.get(order.user.username, 0) + order.quantity
        for username in user_to_orders_dict:
	    money_paid = Decimal(0)
            num_burritos = user_to_orders_dict[username]
	    money_owed = num_burritos*cost_per_burrito
            for paid in AmountPaid.objects.filter(date__month=month).filter(date__year=year):   
                if paid.user.username == username:
                    money_paid += paid.amount
                    money_owed = (num_burritos*cost_per_burrito) - money_paid
            user_to_orders_dict[username] = (num_burritos, num_burritos*cost_per_burrito, money_owed, money_paid)

        context["user_to_orders_dict"] = user_to_orders_dict
	return context
