# Generated by Django 2.1.3 on 2018-11-29 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='request_token',
            field=models.CharField(max_length=128, null=True, verbose_name='token de solicitud de pago'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(10, 'creada'), (20, 'pagada'), (30, 'pago fallido'), (40, 'entregada'), (50, 'entrega fallida'), (60, 'pago reversado'), (60, 'devolución fallida')], default=10, null=True, verbose_name='estado'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status_updated_at',
            field=models.DateTimeField(null=True, verbose_name='fecha de actualización del estado'),
        ),
    ]