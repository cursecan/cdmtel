from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import F
from django.conf import settings

from .models import (
    PermintaanResume, Validation,
    UpdatePermintaan, ManualOrder
)
from .tasks import (
    notify_new_request, notifi_validation_req,
    sending_notif_manual_ro
)

from userprofile.models import Profile

@receiver(post_save, sender=PermintaanResume)
def permintaa_resume_trigerting(sender, instance, created, **kwargs):
    if created:
        Profile.objects.filter(user=instance.executor).update(
            counter = F('counter') + 1
        )

        notify_new_request(instance.id, verbose_name='New resume request', creator=instance)

        
@receiver(post_save, sender=Validation)
def validation_triger(sender, instance, created, **kwargs):
    if created:
        PermintaanResume.objects.filter(id=instance.permintaan_resume.id).update(
            validate=True
        )
        # if instance.action == 'APP':
        #     notifi_validation_req(instance.permintaan_resume.id, verbose_name="New Validation", creator=instance.permintaan_resume)


@receiver(post_save, sender=UpdatePermintaan)
def update_validation_triger(sender, instance, created, **kwargs):
    if created:
        PermintaanResume.objects.filter(id=instance.permintaan_resume.id).update(
            validate=False
        )

        notify_new_request(instance.permintaan_resume.id, verbose_name='Update resume request', creator=instance.permintaan_resume)


@receiver(post_save, sender=ManualOrder)
def  create_manual_order(sender, instance, created, **kwargs):
    if created:
        PermintaanResume.objects.filter(
            manualorder = instance
        ).update(manual_bukis=True)

        sending_notif_manual_ro(instance.id, settings.TELEGRAM_KEY, settings.REMOT_TELEHOST)
