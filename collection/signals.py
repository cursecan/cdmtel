from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    ColTarget, Saldo, Validation, Approval
)
from masterdata.models import Customer


@receiver(post_save, sender=ColTarget)
def is_target_collect(sender, instance, created, **kwargs):
    # if created:
    Validation.objects.filter(
        customer__coltarget_customer=instance
    ).update(closed=True)
    
    Customer.objects.filter(coltarget_customer=instance).update(
        status = 1
        # has_target=True, has_validate=False, has_approve=False
    )
    ColTarget.objects.filter(id=instance.id).update(
        is_valid = False
    )


@receiver(post_save, sender=Saldo)
def update_current_saldo(sender, instance, created, **kwargs):
    if created:
        Customer.objects.filter(
            customer_saldo = instance
        ).update(cur_saldo=instance.amount)


@receiver(post_save, sender=Validation)
def validation_triger(sender, instance, created, **kwargs):
    if created:  
        if instance.validate == 'AP':      
            Customer.objects.filter(bjt_cust_validate=instance).update(
                # has_validate=True
                status = 2
            )
        else :
            Customer.objects.filter(bjt_cust_validate=instance).update(
                # has_target=False, has_validate=False, has_approve=False
                status = 3
            )
            instance.closed = True
            instance.save()


@receiver(post_save, sender=Approval)
def approval_triger(sender, instance, created, **kwargs):
    if created:
        Validation.objects.filter(
            approval = instance
        ).update(closed=True)

        cust_obj = Customer.objects.get(
            bjt_cust_validate__approval=instance
        )

        coltarget_obj = cust_obj.coltarget_customer.all()

        if instance.approve:
            coltarget_obj.update(is_valid=True)
            cust_obj.status = 4
            cust_obj.save()
        else :
            cust_obj.has_validate=False
            cust_obj.status = 1
            cust_obj.save()
            # coltarget_obj.update(is_valid=False)

        cust_obj.save()
