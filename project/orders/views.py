from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView



class CustomLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'admin/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


# class NewOrderFormView(TemplateView):
#     pass
