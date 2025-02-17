from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Profile

from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        user = instance
        Profile.objects.create(
            user = user,
            username = user.username,
            email = user.email,
            name = user.first_name
        )
        subject = 'Welcome to DevSearch'
        message = 'We are glad you are here!'
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )
        
@receiver(post_save, sender=Profile)
def update_user(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user
    if created == False:
        user.first_name = profile.name
        user.username = profile.username
        user.save()

@receiver(post_delete, sender=Profile)
def delete_user(sender, instance, **kwargs):
    user = User.objects.get(id=instance.user.id)
    user.delete()