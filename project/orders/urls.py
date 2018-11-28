from django.urls import path

# from .views import OrderFormView
from .views import CustomLoginView

urlpatterns = [
    # url(
    #     r'^$',
    #     NewOrderFormView.as_view(),
    #     name='new_order',
    # ),

    path(
        r'ingresar/',
        CustomLoginView.as_view(),
        name='login',
    ),
]
