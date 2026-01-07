"""
Management command to clean up expired and revoked authentication tokens.

Usage:
    python manage.py cleanup_tokens
    python manage.py cleanup_tokens --days 60  # Keep tokens for 60 days instead of default 30
"""
from django.core.management.base import BaseCommand
from accounts.models import AuthToken


class Command(BaseCommand):
    help = 'Clean up expired and revoked authentication tokens older than specified days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep expired/revoked tokens for audit purposes (default: 30)',
        )

    def handle(self, *args, **options):
        days_to_keep = options['days']
        
        self.stdout.write(f'Cleaning up tokens older than {days_to_keep} days...')
        
        deleted_count = AuthToken.cleanup_expired_tokens(days_to_keep=days_to_keep)
        
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully cleaned up {deleted_count} expired/revoked token(s)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No tokens to clean up')
            )
        
        # Display current token statistics
        total_tokens = AuthToken.objects.count()
        active_tokens = AuthToken.objects.filter(is_revoked=False).count()
        revoked_tokens = AuthToken.objects.filter(is_revoked=True).count()
        
        self.stdout.write('\nCurrent token statistics:')
        self.stdout.write(f'  Total tokens: {total_tokens}')
        self.stdout.write(f'  Active tokens: {active_tokens}')
        self.stdout.write(f'  Revoked tokens: {revoked_tokens}')
