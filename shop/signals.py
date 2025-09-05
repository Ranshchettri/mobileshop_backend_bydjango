from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management import call_command

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    call_command('create_admin_user')