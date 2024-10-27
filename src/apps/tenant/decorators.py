from .utils import get_subdomain, get_tenant
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse_lazy


def root_only(view_func):
    forbidden_views = getattr(root_only, "forbidden_views", set())

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        subdomain = get_subdomain(request=request)
        if subdomain is not None:
            current_view_name = view_func.__name__
            if current_view_name in forbidden_views:
                raise ValueError(
                    f"This view ({current_view_name}) is only accessible from the root domain."
                )
        return view_func(request, *args, **kwargs)

    forbidden_views.add(view_func.__name__)
    setattr(root_only, "forbidden_views", forbidden_views)
    return _wrapped_view


def login_required_tenant(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse_lazy("pasal-dashboard-login")
            return redirect(f"{login_url}?next={request.path}")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def subdomain_only(view_func):
    allowed_views = getattr(subdomain_only, "allowed_views", set())

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        subdomain = get_subdomain(request=request)
        if subdomain is None:
            current_view_name = view_func.__name__
            if current_view_name not in allowed_views:
                raise ValueError(
                    f"This view ({current_view_name}) is only accessible with a subdomain."
                )
        else:
            return redirect(reversed("pasal_home"))

        return view_func(request, *args, **kwargs)

    allowed_views.add(view_func.__name__)
    setattr(subdomain_only, "allowed_views", allowed_views)
    return _wrapped_view
