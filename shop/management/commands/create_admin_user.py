from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates default admin seller user if not already exists'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(email='seller@admin.com').exists():
            User.objects.create_superuser(
                email='seller@admin.com',
                password='admin123',
                full_name='Store Admin',
                contact='9800000000',
                address='Kathmandu',
            )
            self.stdout.write(self.style.SUCCESS("✔ Default admin user created."))
        else:
            self.stdout.write("⚠ Admin user already exists.")