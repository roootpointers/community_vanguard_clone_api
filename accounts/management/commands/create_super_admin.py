from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Creates a super admin user'

    def add_arguments(self, parser):
        # Making arguments optional and setting default values
        parser.add_argument('--username', type=str, default='admin', help='Admin username (default: admin)')
        parser.add_argument('--email', type=str, default='admin@example.com',
                            help='Admin email (default: admin@example.com)')
        parser.add_argument('--password', type=str, default='admin', help='Admin password (default: admin)')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        email = kwargs['email']
        password = kwargs['password']

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Super admin {username} was created successfully!'))
        else:
            self.stdout.write(self.style.WARNING(f'User {username} already exists.'))