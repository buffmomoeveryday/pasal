from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.ecommerce.models import Customer


@receiver(pre_save, sender=Customer)
def send_welcome_email(sender, instance, **kwargs):
    pass
