from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Customer

from django_htmx.http import HttpResponseClientRedirect


def login_customer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        
        if "customer_id" not in request.session:
            if request.htmx:
                # to make sure that if the request if htmx it doesn't behave abnormally
                return HttpResponseClientRedirect(reverse_lazy("login-customer"))

            return redirect(reverse_lazy("login-customer"))
            
        customer_id = request.session["customer_id"]
        try:
            request.customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return HttpResponseClientRedirect(reverse_lazy("login-customer"))
        return view_func(request, *args, **kwargs)

    return _wrapped_view
