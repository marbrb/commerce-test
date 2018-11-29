from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models

from . import data


class Order(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='usuario',
    )

    products = JSONField(
        verbose_name='productos',
    )

    total_value = models.IntegerField(
        verbose_name='valor total de la compra',
    )

    payment = models.OneToOneField(
        'orders.Payment',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='pago',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de creación',
    )

    def _str_(self):
        return 'Orden número {}'.format(self.id)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Orden'
        verbose_name_plural = 'Ordenes'


class Payment(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de creación',
    )

    status = models.PositiveSmallIntegerField(
        choices=data.PAYMENT_STATUS_CHOICES,
        default=data.CREATED_CHOICE,
        verbose_name='estado',
    )

    status_updated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de actualización del estado',
    )

    create_response = JSONField(
        null=True,
        verbose_name='información creacion del pago en Tpaga',
    )

    canceled_at = models.DateTimeField(
        null=True,
        verbose_name='fecha de cancelación del pago',
    )

    idempotency_token = models.CharField(
        max_length=128,
        verbose_name='token para evitar solicitudes repetidas',
        unique=True,
    )

    request_token = models.CharField(
        max_length=128,
        verbose_name='token de solicitud de pago',
    )

    @property
    def is_created(self):
        return self.status == data.CREATED_CHOICE

    @property
    def is_paid(self):
        return self.status == data.PAID_CHOICE

    @property
    def is_delivered(self):
        return self.status == data.DELIVERED_CHOICE

    @property
    def is_reversed(self):
        return self.status == data.REVERSED_CHOICE

    def _str_(self):
        return 'Solicitud de pago número {}'.format(self.id)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Solicitud de pago'
        verbose_name_plural = 'Solicitudes de pago'
