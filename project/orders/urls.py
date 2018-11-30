from django.urls import path

from .views import CompleteOrderTemplateView
from .views import CustomLoginView
from .views import NewOrderFormView

urlpatterns = [
    path(
        r'',
        NewOrderFormView.as_view(),
        name='new_order',
    ),

    path(
        'orden/<int:pk>/hecho/',
        CompleteOrderTemplateView.as_view(),
        name='complete_order',
    ),

    path(
        'ingresar/',
        CustomLoginView.as_view(),
        name='login',
    ),
]
