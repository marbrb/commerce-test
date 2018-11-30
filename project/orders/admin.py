import json

from django.contrib import admin
from django.contrib import messages
from django.urls import path
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from .models import Order
from .models import Payment
from .models import Product
from .utils import reverse_payment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def _payment(self, obj):
        if obj.payment:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse('admin:orders_payment_change', args=[obj.payment.id]),
                str(obj.payment),
            ))

        return '-'

    _payment.short_description = 'Datos del pago'
    _payment.allow_tags = True


    list_display = (
        'id',
        'user',
        'total_value',
        'created_at',
    )

    list_filter = (
        'created_at',
    )

    search_fields = (
        'id',
        'user__first_name',
        'user__last_name',
        'user__email',
    )

    fields = (
        '_payment',
        'user',
        'products',
        'total_value',
    )

    readonly_fields = fields


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def _order(self, obj):
        if obj.order:
            return mark_safe('<a href="{}">{}</a>'.format(
                reverse('admin:orders_order_change', args=[obj.order.id]),
                str(obj.order),
            ))

        return '-'

    _order.short_description = 'Datos del pago'
    _order.allow_tags = True

    def create_response_json(self, obj):
        if not obj.create_response:
            return '-'

        return json.dumps(obj.create_response, sort_keys=True, indent=2)

    list_display = (
        'id',
        'created_at',
        'status',
    )

    search_fields = (
        'id',
        'idempotency_token'
    )

    fields = (
        '_order',
        'created_at',
        'status',
        'status_updated_at',
        'canceled_at',
        'idempotency_token',
        'create_response_json',
        'request_token',
    )

    readonly_fields = fields

    def _reverse_payment(self, request, object_id):

        payment = get_object_or_404(
            Payment,
            pk=object_id,
        )


        if not (payment.is_paid or payment.is_delivered):
            messages.error(request, msg)

            return redirect(
                'admin:orders_payment_change', object_id
            )

        reverse_payment(payment=payment)

        if payment.is_reversed:
            messages.success(request, 'El pago fue reversado.')

        else:
            messages.error(request, 'No se puede reversar el pago.')

        return redirect(
            'admin:orders_payment_change', object_id
        )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {'buttons': []}

        payment = get_object_or_404(
            Payment,
            pk=object_id,
        )

        if payment.is_paid or payment.is_delivered:
            extra_context['buttons'] = [{
                'url': 'reembolso',
                'textname': 'Revertir pago',
                'confirm': '¿Confirma que desea revertir el pago?',
            }]


        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context
        )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                '<path:object_id>/change/reembolso/',
                self.admin_site.admin_view(self._reverse_payment),
                name='revert_payment'
            )
        ]
        return my_urls + urls


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return not Product.objects.exists()

    list_display = (
        'id',
        'name',
        'price',
    )

    search_fields = (
        'id',
        'name',
        'description'
    )
