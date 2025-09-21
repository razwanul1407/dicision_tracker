from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from core.models import Project, Event, Decision, Deliverable, Invitation, Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Clear all application data while preserving user accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This command will delete ALL application data while preserving user accounts.\n'
                    'Run with --confirm to proceed.\n'
                    'Example: python manage.py clear_data --confirm'
                )
            )
            return

        self.stdout.write('Starting database cleanup...')
        
        with transaction.atomic():
            # Get counts before deletion for reporting
            initial_counts = {
                'notifications': Notification.objects.count(),
                'invitations': Invitation.objects.count(),
                'deliverables': Deliverable.objects.count(),
                'decisions': Decision.objects.count(),
                'events': Event.objects.count(),
                'projects': Project.objects.count(),
                'users': User.objects.count(),
            }
            
            self.stdout.write(f'Initial data counts:')
            for model, count in initial_counts.items():
                self.stdout.write(f'  {model.capitalize()}: {count}')
            
            # Delete application data in correct order (respecting foreign keys)
            self.stdout.write('\nDeleting application data...')
            
            # Delete notifications first (they reference other models)
            deleted_notifications = Notification.objects.all().delete()[0]
            self.stdout.write(f'  Deleted {deleted_notifications} notifications')
            
            # Delete invitations (they reference events)
            deleted_invitations = Invitation.objects.all().delete()[0]
            self.stdout.write(f'  Deleted {deleted_invitations} invitations')
            
            # Delete deliverables (they reference decisions)
            deleted_deliverables = Deliverable.objects.all().delete()[0]
            self.stdout.write(f'  Deleted {deleted_deliverables} deliverables')
            
            # Delete decisions (they reference events)
            deleted_decisions = Decision.objects.all().delete()[0]
            self.stdout.write(f'  Deleted {deleted_decisions} decisions')
            
            # Delete events (they reference projects)
            deleted_events = Event.objects.all().delete()[0]
            self.stdout.write(f'  Deleted {deleted_events} events')
            
            # Delete projects
            deleted_projects = Project.objects.all().delete()[0]
            self.stdout.write(f'  Deleted {deleted_projects} projects')
            
            # Verify users are preserved
            remaining_users = User.objects.count()
            self.stdout.write(f'\nUsers preserved: {remaining_users}')
            
            # Show user details
            self.stdout.write('\nRemaining users:')
            for user in User.objects.all():
                role = 'Admin' if user.is_admin else 'Management' if user.is_management else 'Project User'
                self.stdout.write(f'  - {user.username} ({user.email}) - {role}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nDatabase cleanup completed successfully!'
                    f'\nRemoved all application data while preserving {remaining_users} user accounts.'
                )
            )