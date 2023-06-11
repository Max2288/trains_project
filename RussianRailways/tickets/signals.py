from django.db.models.signals import post_save
from django.dispatch import receiver
from tickets import models


@receiver(post_save, sender=models.Ticket)
def handle_cancelled_ticket(instance, **kwargs):
    if instance.status == 'Cancelled':
        instance.delete()
