from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from core.settings import BASE_URL

from apps.tenant.models import Tenant
from apps.tenant.utils import get_tenant, get_host_name, get_subdomain
from apps.ecommerce.models import Customer


class CheckIfTenantExists:
    """it checks if the tenant exists,
    it only makes the database call
    if the subdomain exists otherwise it
    entirely skips the call and redirects
    the user to the project url"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        subdomain = get_subdomain(request=request)
        if subdomain is not None:
            tenant = Tenant.objects.filter(subdomain=subdomain).first()
            if not tenant:
                return redirect(BASE_URL)

        response = self.get_response(request)
        return response


class TenantMiddleware(MiddlewareMixin):
    """adds the tenant middleware
    for every subdomain request"""

    def process_request(self, request):
        tenant_identifier = get_tenant(request)
        tenant = Tenant.objects.filter(name=tenant_identifier).first()
        request.tenant = tenant or None


class CustomerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        if "customer_id" in request.session:
            try:
                customer_id = request.session["customer_id"]
                request.customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                # Handle the case where the customer doesn't exist (possibly deleted)
                request.customer = None
        else:
            request.customer = None

        # Call the next middleware or view
        response = self.get_response(request)

        # Process the response
        return response
