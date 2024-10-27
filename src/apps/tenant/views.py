from django.shortcuts import render

from .models import Employees
from .utils import get_tenant


def our_team(request):
    tenant = get_tenant(request=request)
    employees = Employees.objects.filter(tenant=tenant)

    context = {
        "tenant": tenant,
        "employees": employees,
    }

    return render(
        request=request,
        template_name="our_team.html",
        context=context,
    )
