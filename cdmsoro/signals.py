from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import F
from django.conf import settings
from django.utils.crypto import get_random_string

from string import digits

from .models import (
    PermintaanResume, Validation,
    UpdatePermintaan, ManualOrder, ManualOrderSoro
)
from .tasks import (
    notify_new_request, notifi_validation_req,
    sending_notif_manual_ro
)

from masterdata.models import (
    Circuit, Order
)

from userprofile.models import Profile

@receiver(post_save, sender=PermintaanResume)
def permintaa_resume_trigerting(sender, instance, created, **kwargs):
    if created:
        Profile.objects.filter(user=instance.executor).update(
            counter = F('counter') + 1
        )

        channel = '@AAAAAEmt1lYsRQ-GBpVFzA'
        if instance.suspend.order_label == 1:
            # CDM
            channel = '@cdm_cool'

        notify_new_request(instance.id, channel, verbose_name='New resume request', creator=instance)

        
@receiver(post_save, sender=Validation)
def validation_triger(sender, instance, created, **kwargs):
    if created:
        if instance.action == 'APP':
            PermintaanResume.objects.filter(id=instance.permintaan_resume.id).update(
                validate=True, status=2
            )
        else :
            PermintaanResume.objects.filter(id=instance.permintaan_resume.id).update(
                validate=False, status=1
            )

        # if instance.action == 'APP':
        #     notifi_validation_req(instance.permintaan_resume.id, verbose_name="New Validation", creator=instance.permintaan_resume)


@receiver(post_save, sender=UpdatePermintaan)
def update_validation_triger(sender, instance, created, **kwargs):
    if created:
        PermintaanResume.objects.filter(id=instance.permintaan_resume.id).update(
            validate=False, status=3
        )
        Validation.objects.filter(permintaan_resume = instance.permintaan_resume).update(
            closed = True
        )

        channel = '@AAAAAEmt1lYsRQ-GBpVFzA'
        if instance.permintaan_resume.suspend.order_label == 1:
            # CDM
            channel = '@cdm_cool'

        notify_new_request(instance.permintaan_resume.id, channel, verbose_name='Update resume request', creator=instance.permintaan_resume)


@receiver(post_save, sender=ManualOrder)
def  create_manual_order(sender, instance, created, **kwargs):
    if created:
        PermintaanResume.objects.filter(
            manualorder = instance
        ).update(manual_bukis=True)

        channel = '@AAAAAEmt1lYsRQ-GBpVFzA'
        if instance.permintaan_resume.suspend.order_label == 1:
            # CDM
            channel = '@cdm_cool'

        sending_notif_manual_ro(instance.id, settings.TELEGRAM_KEY, '@cdm_notif')


@receiver(post_save, sender=ManualOrderSoro)
def soro_manual_signaling(sender, instance, created, **kwargs):
    if created:
        order_obj = Order()
        order_obj.order_number = 'X-' + str(instance.id)
        order_obj.circuit = instance.sid
        order_obj.closed = True
        order_obj.status = 'OCS MANUAL ORDER'
        if instance.order_type == 'SO':
            order_obj.type_order = 'SO'
        else :
            order_obj.type_order = 'RO'
        order_obj.save()

        instance.order_number = order_obj
        instance.save()