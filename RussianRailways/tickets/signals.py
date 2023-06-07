from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models

@receiver(post_save, sender=models.HumanTicket)
def handle_cancelled_ticket(instance, **kwargs):
    if instance.status == 'Cancelled':
        instance.delete()