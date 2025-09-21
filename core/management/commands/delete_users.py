from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Delete specific user accounts by username'

    def add_arguments(self, parser):
        parser.add_argument(
            'usernames',
            nargs='+',
            type=str,
            help='Usernames to delete'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete the users',
        )

    def handle(self, *args, **options):
        usernames = options['usernames']
        
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    f'This command will delete the following users: {", ".join(usernames)}\n'
                    'Run with --confirm to proceed.\n'
                    f'Example: python manage.py delete_users {" ".join(usernames)} --confirm'
                )
            )
            return

        self.stdout.write(f'Deleting users: {", ".join(usernames)}')
        
        deleted_count = 0
        for username in usernames:
            try:
                user = User.objects.get(username=username)
                user_info = f'{user.username} ({user.email})'
                user.delete()
                self.stdout.write(f'  ✓ Deleted: {user_info}')
                deleted_count += 1
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ✗ User not found: {username}')
                )
        
        # Show remaining users
        remaining_users = User.objects.count()
        self.stdout.write(f'\nRemaining users: {remaining_users}')
        
        self.stdout.write('\nCurrent user accounts:')
        for user in User.objects.all():
            role = 'Admin' if user.is_admin else 'Management' if user.is_management else 'Project User'
            self.stdout.write(f'  - {user.username} ({user.email}) - {role}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDeleted {deleted_count} user(s) successfully!'
            )
        )