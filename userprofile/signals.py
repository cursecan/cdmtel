from django.dispatch import receiver
from django.db.models.signals import post_save


from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def generate_initial_profile(sender, instance, created, **kwargs):
    if created:
        profile_obj = Profile.objects.create(user=instance)
        profile_obj.superior = profile_obj
        profile_obj.save()