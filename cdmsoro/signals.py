from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import F

from .models import (
    PermintaanResume, Validation,
    UpdatePermintaan
)
from .tasks import notify_new_request, notifi_validation_req

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
        if instance.action == 'APP':
            notifi_validation_req(instance.permintaan_resume.id, verbose_name="New Validation", creator=instance.permintaan_resume)


@receiver(post_save, sender=UpdatePermintaan)
def update_validation_triger(sender, instance, created, **kwargs):
    if created:
        PermintaanResume.objects.filter(id=instance.permintaan_resume.id).update(
            validate=False
        )

        notify_new_request(instance.permintaan_resume.id, verbose_name='Update resume request', creator=instance.permintaan_resume)