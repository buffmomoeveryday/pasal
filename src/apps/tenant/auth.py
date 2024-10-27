from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import Employees, Tenant  # Import the Employees model


class CustomTenantAuthBackend(ModelBackend):
    def authenticate(
        self, request, tenant_subdomain=None, email=None, password=None, **kwargs
    ):
        try:
            tenant = Tenant.objects.get(subdomain=tenant_subdomain)
        except Tenant.DoesNotExist:
            return None

        user_model = get_user_model()
        try:
            employee = Employees.objects.get(tenant=tenant, user__email=email)
            user = employee.user
        except Employees.DoesNotExist:
            return None

        if user.check_password(password):
            return user

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
