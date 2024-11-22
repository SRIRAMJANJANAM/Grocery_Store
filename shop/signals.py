# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Customer

@receiver(post_save, sender=User)
def create_customer_for_user(sender, instance, created, **kwargs):
    # Create a Customer only if the User is newly created and doesn't already have one
    if created:
        Customer.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def create_customer_for_user(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)