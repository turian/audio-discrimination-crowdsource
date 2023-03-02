from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from .models import AnnotatorProfile

user = get_user_model()


@receiver(user_signed_up)
def create_user_profile(request, user, *args, **kwargs):
    """This function received a created signal from allauth whenever
    a new user signed up, then the receiver decorator triggers this
    function to create a user profile by extracting the email address
    of user from all auth"""
    user_mail = user.email
    profile = AnnotatorProfile.objects.create(user=user, email=user_mail)
    profile.save()
