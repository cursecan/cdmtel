from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Q, F

from .models import (
    Order, Circuit, CancelOrder
)
from cdmsoro.models import PermintaanResume

@receiver(post_save, sender=Order)
def generate_circuit_status(sender, instance, created, **kwargs):
    if created:
        circuit_obj = Circuit.objects.filter(id=instance.circuit.id)
        if instance.type_order == instance.SUSPEND:
            circuit_obj.update(is_active=False)
        else :
            circuit_obj.update(is_active=True)


@receiver(post_save, sender=CancelOrder)
def generate_cancel_triger(sender, instance, created, **kwargs):
    if created:
        order_obj = Order.objects.filter(order_number=instance.order_num)
        if order_obj.exists():
            order_obj.update(is_cancel=True, closed=True, status='ABANDONED')
            
            Circuit.objects.filter(order__order_number=instance.order_num).update(
                is_active =  True
            )

