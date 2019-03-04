from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ColTarget
from masterdata.models import Customer


@receiver(post_save, sender=ColTarget)
def is_target_collect(sender, instance, created, **kwargs):
    if created:
        Customer.objects.filter(coltarget_customer=instance).update(
            is_valid=False, has_target=True
        )