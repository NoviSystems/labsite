import datetime
from decimal import *

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views.generic import CreateView, ListView, TemplateView, date_based
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.functional import lazy
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from models import Item, Order, RiceCooker, MonthlyCost
from forms import OrderForm

# Workaround for using reverse with success_url in class based generic views
# because direct usage of it throws an exception.
reverse_lazy = lambda name=None, *args: lazy(reverse, str)(name, args=args)


class HomepageView(CreateView):
    form_class = OrderForm
    success_url = reverse_lazy('url_todays_orders')
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
        context['rice_is_on'] = RiceCooker.objects.get(id=1).is_on
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
        context['title'] = 'Order History for ' + self.request.user.username
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
        context['rice_quantity'] = burrito_count * 0.7

        context['title'] = 'Today\'s Orders.'
        return context


#Updates all RiceCooker objects to true and redirects to homepage
def rice_on_view(request):
    RiceCooker.objects.all().update(is_on=True)
    return HttpResponseRedirect(reverse('url_homepage'))


#Updates all RiceCooker objects to false and redirects to homepage
def rice_off_view(request):
    RiceCooker.objects.all().update(is_on=False)
    return HttpResponseRedirect(reverse('url_homepage'))


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
        context['year'] = year
        context['month'] = month

        #Calculates the total number of burritos in a given month
        month_orders = Order.objects.filter(date__month=month, date__year=year)
        num_burritos = 0
        for order in month_orders:
            if order.item.name.lower() == "burrito":
                num_burritos += order.quantity
        context["num_burritos"] = num_burritos

        #Gets the Monthly Cost, if none or more than one, value is set to zero
        try:
            cost = MonthlyCost.objects.get(date__month=month, date__year=year).cost
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            cost = 0

        context["cost"] = cost

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
