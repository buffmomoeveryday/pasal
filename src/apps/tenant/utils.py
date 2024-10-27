from core.settings import BASE_URL
from .models import Tenant
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings


def get_host_name(request):
    try:
        if hasattr(request, "get_host") and callable(getattr(request, "get_host")):
            return request.get_host().split(":")[0].lower()
    except Exception as e:
        print(f"Exception occurred in get_host_name: {e}")
    return None


def get_subdomain(request):
    hostname = get_host_name(request=request)
    if hostname is None:
        return None

    parts = hostname.split(".")
    if len(parts) < 2:
        return None
    subdomain = parts[0]
    return subdomain


def get_tenant(request):
    hostname = get_host_name(request=request)
    if hostname is None:
        return None
    subdomain = get_subdomain(request=request)
    try:
        return Tenant.objects.filter(subdomain=subdomain).first()
    except Tenant.DoesNotExist:
        return None
    except Exception as e:
        return None


def redirect_after_login(request):
    nxt = request.GET.get("next", None)
    if nxt is None:
        return redirect(settings.TENANT_LOGIN_REDIRECT)
    elif not url_has_allowed_host_and_scheme(
        url=nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(settings.TENANT_LOGIN_REDIRECT)
    else:
        return redirect(nxt)
