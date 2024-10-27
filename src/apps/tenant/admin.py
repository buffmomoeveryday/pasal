from django.contrib import admin
from .models import Tenant, Employees, StoreInformation
from apps.user.models import CustomUser



admin.site.register(Tenant)
admin.site.register(Employees)
admin.site.register(StoreInformation)

