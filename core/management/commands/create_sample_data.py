from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from core.models import Project, Event, Decision, Deliverable, Invitation

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing the Event Decision Tracker'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create sample users
        admin_user, created = User.objects.get_or_create(
            username='admin_user',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('password123')
            admin_user.save()
            self.stdout.write(f'Created admin user: {admin_user.username}')

        management_user, created = User.objects.get_or_create(
            username='manager1',
            defaults={
                'email': 'manager1@example.com',
                'first_name': 'John',
                'last_name': 'Manager',
                'role': 'management'
            }
        )
        if created:
            management_user.set_password('password123')
            management_user.save()
            self.stdout.write(f'Created management user: {management_user.username}')

        project_user1, created = User.objects.get_or_create(
            username='projectuser1',
            defaults={
                'email': 'projectuser1@example.com',
                'first_name': 'Alice',
                'last_name': 'Worker',
                'role': 'project_user'
            }
        )
        if created:
            project_user1.set_password('password123')
            project_user1.save()
            self.stdout.write(f'Created project user: {project_user1.username}')

        project_user2, created = User.objects.get_or_create(
            username='projectuser2',
            defaults={
                'email': 'projectuser2@example.com',
                'first_name': 'Bob',
                'last_name': 'Developer',
                'role': 'project_user'
            }
        )
        if created:
            project_user2.set_password('password123')
            project_user2.save()
            self.stdout.write(f'Created project user: {project_user2.username}')

        # Create sample projects
        project1, created = Project.objects.get_or_create(
            name='Website Redesign Project',
            defaults={
                'description': 'Complete redesign of the company website with modern UI/UX',
                'created_by': management_user
            }
        )
        if created:
            self.stdout.write(f'Created project: {project1.name}')

        project2, created = Project.objects.get_or_create(
            name='Mobile App Development',
            defaults={
                'description': 'Development of iOS and Android mobile applications',
                'created_by': management_user
            }
        )
        if created:
            self.stdout.write(f'Created project: {project2.name}')

        # Create sample events
        now = timezone.now()
        
        event1, created = Event.objects.get_or_create(
            title='Project Kickoff Meeting',
            defaults={
                'project': project1,
                'description': 'Initial meeting to discuss project scope and requirements',
                'agenda': '1. Project overview\n2. Team introductions\n3. Timeline discussion\n4. Resource allocation',
                'start_time': now + timedelta(days=1, hours=9),
                'end_time': now + timedelta(days=1, hours=11),
                'venue': 'Conference Room A',
                'organizer': management_user
            }
        )
        if created:
            event1.participants.add(project_user1, project_user2)
            self.stdout.write(f'Created event: {event1.title}')

        event2, created = Event.objects.get_or_create(
            title='Design Review Session',
            defaults={
                'project': project1,
                'description': 'Review of initial design mockups and wireframes',
                'agenda': '1. Present wireframes\n2. Discuss user flow\n3. Color scheme review\n4. Feedback collection',
                'start_time': now + timedelta(days=7, hours=14),
                'end_time': now + timedelta(days=7, hours=16),
                'venue': 'Design Studio',
                'organizer': management_user
            }
        )
        if created:
            event2.participants.add(project_user1)
            self.stdout.write(f'Created event: {event2.title}')

        # Create sample decisions
        decision1, created = Decision.objects.get_or_create(
            title='Technology Stack Selection',
            defaults={
                'event': event1,
                'description': 'Decided to use React for frontend and Django for backend',
                'created_by': management_user
            }
        )
        if created:
            self.stdout.write(f'Created decision: {decision1.title}')

        decision2, created = Decision.objects.get_or_create(
            title='Project Timeline Approval',
            defaults={
                'event': event1,
                'description': 'Approved 3-month timeline with weekly milestone reviews',
                'created_by': management_user
            }
        )
        if created:
            self.stdout.write(f'Created decision: {decision2.title}')

        # Create sample deliverables
        deliverable1, created = Deliverable.objects.get_or_create(
            title='Setup Development Environment',
            defaults={
                'decision': decision1,
                'description': 'Install and configure React and Django development environments',
                'assigned_to': project_user1,
                'progress': 80,
                'status': 'in-progress',
                'due_date': now + timedelta(days=3)
            }
        )
        if created:
            self.stdout.write(f'Created deliverable: {deliverable1.title}')

        deliverable2, created = Deliverable.objects.get_or_create(
            title='Create Project Repository',
            defaults={
                'decision': decision1,
                'description': 'Setup Git repository with initial project structure',
                'assigned_to': project_user2,
                'progress': 100,
                'status': 'completed',
                'due_date': now + timedelta(days=2)
            }
        )
        if created:
            self.stdout.write(f'Created deliverable: {deliverable2.title}')

        deliverable3, created = Deliverable.objects.get_or_create(
            title='Weekly Progress Reports',
            defaults={
                'decision': decision2,
                'description': 'Prepare and submit weekly progress reports',
                'assigned_to': project_user1,
                'progress': 0,
                'status': 'pending',
                'due_date': now + timedelta(days=7)
            }
        )
        if created:
            self.stdout.write(f'Created deliverable: {deliverable3.title}')

        # Create sample invitations
        invitation1, created = Invitation.objects.get_or_create(
            event=event2,
            invitee=project_user2,
            defaults={
                'invited_by': management_user,
                'status': 'pending',
                'message': 'Please join us for the design review session. Your input will be valuable.'
            }
        )
        if created:
            self.stdout.write(f'Created invitation for {invitation1.invitee.username}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('\nSample login credentials:')
        self.stdout.write(f'Admin: admin_user / password123')
        self.stdout.write(f'Manager: manager1 / password123')
        self.stdout.write(f'Project User 1: projectuser1 / password123')
        self.stdout.write(f'Project User 2: projectuser2 / password123')