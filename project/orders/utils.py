import requests
from base64 import b64encode

from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from . import data


def headers():
    credentials = '{}:{}'.format(settings.TPAGA_USER, settings.TPAGA_PASS)
    b64_credentials = b64encode(bytes(credentials)).decode("utf-8")

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Cache-Control': 'no-cache',
        'Authorization': 'Basic {api_key}'.format(
            rest_api_key=encoded_credentials()
        )
    }

    return headers

def create_payment_at_tpaga(order, request_ip):
    tpaga_payment_url = ''
    expire_date = order.payment.created_at + timezone.timedelta(hours=1)
    products_list = [{
        'name': '{} - Cant. {}'.format(k, v)
    } for k, v in order.products.items()]

    data = {
        "cost": order.total_value,
        "expires_at": expire_date.isoformat() ,
        "idempotency_token": order.payment.idempotency_token,
        "order_id": order.id,
        "purchase_description": 'Compra en PythonShirts',
        "purchase_details_url": settings.BASE_URL + reverse('orders:complete_order'),
        "purchase_items": products_list,
        "terminal_id": 1,
        "user_ip_address": request_ip,
    }

    try:
        response = requests.post(
            '{}{}'.format(
                settings.TPAGA_API_URL,
                settings.TPAGA_CREATE_PAYMENT_URL,
            ),
            data=json.dumps(data),
            headers=headers(),
            timeout=20,
        )

        if response.status_code == 201:
            data = response.json()
            order.payment.status = data.CREATED_CHOICE
            order.payment.status_updated_at = timezone.now()
            order.payment.create_response = data
            order.payment.request_token = data.get('token', '')
            order.payment.save()

            return True, data.get('tpaga_payment_url', '')

    except requests.exceptions.Timeout:
        order.payment.create_response = {
            'error': 'timeout',
        }

    return False, '/'

def update_payment_status(payment):
    status_url = settings.TPAGA_PAYMENT_STATUS_URL.format(
        payment.request_token
    )

    try:
        response = requests.get(
            '{}{}'.format(
                settings.TPAGA_API_URL,
                status_url,
            ),
            headers=headers(),
            timeout=20,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'paid':
                payment.status = data.PAID_CHOICE

            elif data.get('status') == 'delivered':
                payment.status = data.DELIVERED_CHOICE

            elif data.get('status') == 'failed':
                payment.status = data.FAILED_PAYMENT_CHOICE

    except requests.exceptions.Timeout:
        payment.status = data.FAILED_PAYMENT_CHOICE

    payment.status_updated_at = timezone.now()
    payment.save()


def confirm_delivery(payment):
    data = {
        "payment_request_token": payment.request_token,
    }

    try:
        response = requests.post(
            '{}{}'.format(
                settings.TPAGA_API_URL,
                settings.TPAGA_CONFIRM_DELIVERY_URL,
            ),
            data=json.dumps(data),
            headers=headers(),
            timeout=20,
        )

        data = response.json()

        if response.status_code == 200 and data.get('status') == 'delivered':
            payment.status = data.DELIVERED_CHOICE
            payment.status_updated_at = timezone.now()
            payment.save()
            return True

        else:
            payment.status = data.FAILED_DELIVERY_CHOICE

    except requests.exceptions.Timeout:
        payment.status = data.FAILED_DELIVERY_CHOICE

    payment.status_updated_at = timezone.now()
    payment.save()

    return False

def reverse_payment(payment):
        data = {
            "payment_request_token": payment.request_token,
        }

        try:
            response = requests.post(
                '{}{}'.format(
                    settings.TPAGA_API_URL,
                    settings.TPAGA_REFUND_URL,
                ),
                data=json.dumps(data),
                headers=headers(),
                timeout=20,
            )

            data = response.json()

            if response.ok and data.get('status') == 'reverted':
                payment.status = data.REVERSED_CHOICE
                payment.status_updated_at = timezone.now()
                payment.save()
                return True

            else:
                payment.status = data.FAILED_REVERSED_CHOICE

        except requests.exceptions.Timeout:
            payment.status = data.FAILED_REVERSED_CHOICE

        payment.status_updated_at = timezone.now()
        payment.save()

        return False
