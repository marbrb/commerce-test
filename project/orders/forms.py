from django import forms

from .models import Product


class ProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        required=True,
    )
