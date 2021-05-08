from django.core.management import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User, Group
from accounts.util import create_user


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        call_command("create_groups")
        u = create_user(
            "__all__",
            username="admin",
            password="admin",
            email="admin@admin.com",
            first_name='Admin',
            last_name='Administrator',
            is_staff=True,
            is_superuser=True
        )
        if u:
            self.stdout.write("Created admin user:\nUsername: 'admin'\nPassword: 'admin'")
        else:
            self.stdout.write("Failead to create admin user")
