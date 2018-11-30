from secrets import token_hex

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import TemplateView

from .forms import ProductForm
from .models import Order
from .models import Payment
from .models import Product
from .utils import confirm_delivery
from .utils import create_payment_at_tpaga
from .utils import get_client_ip
from .utils import update_payment_status


class CustomLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'admin/login.html'


class NewOrderFormView(LoginRequiredMixin, FormView):
    template_name = 'index.html'
    form_class = ProductForm

    def form_valid(self, form):
        quantity = int(form.cleaned_data.get('quantity'))
        product = Product.objects.first()
        value = product.price * quantity
        products_json = {
            product.name: quantity
        }

        token = token_hex(16)
        while Payment.objects.filter(idempotency_token=token).exists():
            token = token_hex(16)

        payment = Payment.objects.create(
            idempotency_token=token,
        )

        order = Order.objects.create(
            user=self.request.user,
            products=products_json,
            total_value=value,
            payment=payment,
        )

        request_ip = get_client_ip(self.request)

        success, url = create_payment_at_tpaga(order, request_ip)
        if not success:
            return self.form_invalid(form)

        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.first()

        return context


class CompleteOrderTemplateView(TemplateView):
    template_name = 'success.html'

    def get_object(self, **kwargs):
        object = get_object_or_404(
            Order,
            pk=kwargs.get('pk', 0)
        )

        return object

    def get(self, request, *args, **kwargs):
        order = self.get_object(**kwargs)
        update_payment_status(payment=order.payment)

        if order.payment.is_paid:
            confirm_delivery(payment=order.payment)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object(**kwargs)

        context.update({
            'order': order
        })

        return context
