from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import (
    Order, Circuit
)

@receiver(post_save, sender=Order)
def generate_circuit_status(sender, instance, created, **kwargs):
    if created:
        circuit_obj = Circuit.objects.filter(id=instance.circuit.id)
        if instance.type_order == instance.SUSPEND:
            circuit_obj.update(is_active=False)
        else :
            circuit_obj.update(is_active=True)