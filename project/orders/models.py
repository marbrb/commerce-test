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

    status = models.PositiveSmallIntegerField(
        choices=data.ORDER_STATUS_CHOICES,
        default=data.CREATED_CHOICE,
        verbose_name='estado',
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


class Payment(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='fecha de creación',
    )

    status = models.CharField(
        max_length=128,
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
