from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with a super admin user'

    def handle(self, *args, **options):
        # Check if admin already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write(
                self.style.WARNING('Super admin already exists!')
            )
            return

        # Create super admin
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@humanoidai.com',
            password='admin123',
            first_name='Super',
            last_name='Admin',
            role='admin'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created super admin: {admin.username}')
        )
        self.stdout.write(
            self.style.SUCCESS('Username: admin')
        )
        self.stdout.write(
            self.style.SUCCESS('Password: admin123')
        )
        self.stdout.write(
            self.style.WARNING('Please change the password in production!')
        )
