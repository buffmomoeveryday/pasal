from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.user.models import CustomUser


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=255)
    stripe_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class TenantAwareQuerySet(models.QuerySet):
    def filter_by_tenant(self, tenant):
        return self.filter(tenant=tenant)


class TenantAwareManager(models.Manager):
    def get_queryset(self):
        base_queryset = super().get_queryset()
        if hasattr(self.model, "tenant") and hasattr(self.model.tenant, "identifier"):
            return base_queryset.filter_by_tenant(self.model.tenant)
        return base_queryset


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)


class Employees(TenantAwareModel):
    user = models.OneToOneField(
        to=CustomUser, on_delete=models.CASCADE, related_name="employee"
    )
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.tenant.name}"


class StoreInformation(TenantAwareModel):
    email = models.EmailField(null=True, blank=True, default="null@null.com")
    about_us = models.TextField(default="null")
    contact = models.TextField(default="null")
    address = models.CharField(max_length=233, default="null")
    logo = models.ImageField(default="null")
    favicon = models.ImageField(null=True, blank=True, default="null")

    def __str__(self):
        return f"{self.tenant.name}'s Information"


@receiver(post_save, sender=Tenant)
def create_store_information(sender, instance, created, **kwargs):
    if created:
        StoreInformation.objects.create(tenant=instance)
