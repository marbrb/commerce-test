import json

from django.contrib import admin

from .models import Order
from .models import Payment
from .models import Product


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

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
        'user',
        'products',
        'total_value',
        'payment',
    )

    readonly_fields = fields

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

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
        'created_at',
        'status',
        'status_updated_at',
        'canceled_at',
        'idempotency_token',
        'create_response_json',
        'request_token',
    )

    readonly_fields = fields


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
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
