#!/usr/bin/env python
"""
Test Data Population Script for Decision Tracker
This script creates comprehensive test data including:
- Projects with different creators
- Events with participants (current and future dates)
- Decisions for events
- Deliverables assigned to participants
- Invitations and notifications
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dicision_tracker.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Project, Event, Decision, Deliverable, Invitation, Notification
from accounts.models import CustomUser

User = get_user_model()

def create_users():
    """Create test users with different roles"""
    print("Creating test users...")
    
    users = []
    
    # Admin user
    admin_user, created = User.objects.get_or_create(
        username='admin_user',
        defaults={
            'email': 'admin@decisiontracker.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_active': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    users.append(admin_user)
    
    # Management users
    management_users_data = [
        ('john_manager', 'john.manager@company.com', 'John', 'Manager'),
        ('sarah_lead', 'sarah.lead@company.com', 'Sarah', 'Wilson'),
        ('mike_director', 'mike.director@company.com', 'Mike', 'Director'),
    ]
    
    for username, email, first_name, last_name in management_users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': 'management',
                'is_active': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
        users.append(user)
    
    # Project users
    project_users_data = [
        ('alice_dev', 'alice.dev@company.com', 'Alice', 'Johnson'),
        ('bob_designer', 'bob.designer@company.com', 'Bob', 'Smith'),
        ('carol_qa', 'carol.qa@company.com', 'Carol', 'Brown'),
        ('david_analyst', 'david.analyst@company.com', 'David', 'Davis'),
        ('emma_writer', 'emma.writer@company.com', 'Emma', 'Taylor'),
        ('frank_tester', 'frank.tester@company.com', 'Frank', 'Miller'),
    ]
    
    for username, email, first_name, last_name in project_users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': 'project_user',
                'is_active': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
        users.append(user)
    
    print(f"Created {len(users)} users")
    return users

def create_projects(management_users):
    """Create test projects"""
    print("Creating test projects...")
    
    projects_data = [
        {
            'name': 'Mobile App Development',
            'description': 'Development of a new mobile application for customer engagement. This project includes UI/UX design, backend development, testing, and deployment phases.',
        },
        {
            'name': 'Website Redesign Project',
            'description': 'Complete redesign of the company website to improve user experience and modernize the brand image. Includes new content strategy and SEO optimization.',
        },
        {
            'name': 'Data Analytics Platform',
            'description': 'Building an internal analytics platform to track business metrics and generate automated reports for management decision making.',
        },
        {
            'name': 'Security Audit Implementation',
            'description': 'Comprehensive security audit and implementation of recommended security measures across all systems and applications.',
        },
    ]
    
    projects = []
    for i, project_data in enumerate(projects_data):
        project, created = Project.objects.get_or_create(
            name=project_data['name'],
            defaults={
                'description': project_data['description'],
                'created_by': management_users[i % len(management_users)],
            }
        )
        projects.append(project)
    
    print(f"Created {len(projects)} projects")
    return projects

def create_events_with_participants(projects, management_users, project_users):
    """Create events with participants"""
    print("Creating events with participants...")
    
    events_data = [
        # Current and past events
        {
            'title': 'Project Kickoff Meeting',
            'description': 'Initial meeting to discuss project goals, timeline, and team assignments.',
            'start_time': timezone.now() - timedelta(days=25, hours=2),
            'end_time': timezone.now() - timedelta(days=25, hours=1),
            'venue': 'in_person',
            'days_offset': -25,
        },
        {
            'title': 'Sprint Planning Session',
            'description': 'Planning session for the first development sprint. Define user stories and estimate effort.',
            'start_time': timezone.now() - timedelta(days=20, hours=3),
            'end_time': timezone.now() - timedelta(days=20, hours=1),
            'venue': 'virtual',
            'days_offset': -20,
        },
        {
            'title': 'Design Review Meeting',
            'description': 'Review and approve the initial design mockups and user interface concepts.',
            'start_time': timezone.now() - timedelta(days=15, hours=2),
            'end_time': timezone.now() - timedelta(days=15, hours=1),
            'venue': 'in_person',
            'days_offset': -15,
        },
        {
            'title': 'Weekly Team Standup',
            'description': 'Regular weekly standup to discuss progress, blockers, and upcoming tasks.',
            'start_time': timezone.now() - timedelta(days=7, hours=1),
            'end_time': timezone.now() - timedelta(days=7, minutes=30),
            'venue': 'virtual',
            'days_offset': -7,
        },
        {
            'title': 'Stakeholder Demo',
            'description': 'Demonstration of current progress to key stakeholders and gathering feedback.',
            'start_time': timezone.now() - timedelta(days=3, hours=2),
            'end_time': timezone.now() - timedelta(days=3, hours=1),
            'venue': 'hybrid',
            'days_offset': -3,
        },
        # Current events (today)
        {
            'title': 'Emergency Bug Triage',
            'description': 'Urgent meeting to address critical bugs found in the production system.',
            'start_time': timezone.now() + timedelta(hours=2),
            'end_time': timezone.now() + timedelta(hours=3),
            'venue': 'virtual',
            'days_offset': 0,
        },
        # Future events
        {
            'title': 'Architecture Planning Session',
            'description': 'Deep dive into technical architecture decisions and system design.',
            'start_time': timezone.now() + timedelta(days=3, hours=2),
            'end_time': timezone.now() + timedelta(days=3, hours=4),
            'venue': 'in_person',
            'days_offset': 3,
        },
        {
            'title': 'User Testing Feedback Review',
            'description': 'Review results from user testing sessions and plan improvements.',
            'start_time': timezone.now() + timedelta(days=7, hours=3),
            'end_time': timezone.now() + timedelta(days=7, hours=4),
            'venue': 'hybrid',
            'days_offset': 7,
        },
        {
            'title': 'Security Implementation Review',
            'description': 'Review progress on security measures implementation and plan next steps.',
            'start_time': timezone.now() + timedelta(days=10, hours=2),
            'end_time': timezone.now() + timedelta(days=10, hours=3),
            'location': 'Secure Meeting Room',
            'venue': 'in_person',
            'days_offset': 10,
        },
        {
            'title': 'Final Project Review',
            'description': 'Comprehensive review of project deliverables and preparation for launch.',
            'start_time': timezone.now() + timedelta(days=14, hours=4),
            'end_time': timezone.now() + timedelta(days=14, hours=6),
            'venue': 'hybrid',
            'days_offset': 14,
        },
        {
            'title': 'Post-Launch Retrospective',
            'description': 'Team retrospective to discuss what went well and areas for improvement.',
            'start_time': timezone.now() + timedelta(days=21, hours=2),
            'end_time': timezone.now() + timedelta(days=21, hours=3),
            'venue': 'in_person',
            'days_offset': 21,
        },
    ]
    
    events = []
    all_users = management_users + project_users
    
    for i, event_data in enumerate(events_data):
        project = projects[i % len(projects)]
        organizer = management_users[i % len(management_users)]
        
        event, created = Event.objects.get_or_create(
            title=event_data['title'],
            project=project,
            defaults={
                'description': event_data['description'],
                'agenda': f"Agenda for {event_data['title']}:\n1. Opening and introductions\n2. Main discussion\n3. Decision making\n4. Next steps\n5. Closing",
                'start_time': event_data['start_time'],
                'end_time': event_data['end_time'],
                'venue': event_data['venue'],
                'organizer': organizer,
            }
        )
        
        if created:
            # Add participants (3-6 random users)
            num_participants = random.randint(3, 6)
            participants = random.sample(all_users, min(num_participants, len(all_users)))
            event.participants.set(participants)
            
            print(f"Created event: {event.title} with {len(participants)} participants")
        
        events.append(event)
    
    print(f"Created {len(events)} events")
    return events

def create_decisions_and_deliverables(events, management_users, project_users):
    """Create decisions for events and assign deliverables"""
    print("Creating decisions and deliverables...")
    
    decisions_data = [
        {
            'title': 'Technology Stack Decision',
            'description': 'Decided to use React Native for mobile development to ensure cross-platform compatibility.',
        },
        {
            'title': 'Design System Standards',
            'description': 'Established comprehensive design system with color palette, typography, and component guidelines.',
        },
        {
            'title': 'Testing Framework Selection',
            'description': 'Selected Jest and Cypress for unit and integration testing respectively.',
        },
        {
            'title': 'Deployment Strategy',
            'description': 'Agreed on CI/CD pipeline using GitHub Actions with staging and production environments.',
        },
        {
            'title': 'Security Requirements',
            'description': 'Defined security requirements including authentication, data encryption, and access controls.',
        },
        {
            'title': 'Performance Benchmarks',
            'description': 'Set performance targets: page load < 2s, API response < 500ms.',
        },
    ]
    
    deliverables_templates = [
        {
            'title': 'API Documentation',
            'description': 'Complete API documentation with examples and authentication details.',
            'status': 'in-progress',
            'progress': 75,
        },
        {
            'title': 'Database Schema Design',
            'description': 'Design and implement the database schema for the application.',
            'status': 'completed',
            'progress': 100,
        },
        {
            'title': 'User Interface Mockups',
            'description': 'Create detailed UI mockups for all application screens.',
            'status': 'in-progress',
            'progress': 60,
        },
        {
            'title': 'User Authentication System',
            'description': 'Implement secure user authentication with JWT tokens.',
            'status': 'in-progress',
            'progress': 80,
        },
        {
            'title': 'Unit Test Suite',
            'description': 'Develop comprehensive unit tests achieving 90%+ code coverage.',
            'status': 'pending',
            'progress': 25,
        },
        {
            'title': 'Performance Testing',
            'description': 'Conduct load testing and performance optimization.',
            'status': 'pending',
            'progress': 10,
        },
        {
            'title': 'Security Audit Report',
            'description': 'Complete security vulnerability assessment and remediation plan.',
            'status': 'in-progress',
            'progress': 40,
        },
        {
            'title': 'Deployment Scripts',
            'description': 'Create automated deployment scripts for staging and production.',
            'status': 'pending',
            'progress': 30,
        },
    ]
    
    decisions = []
    deliverables = []
    
    # Create decisions for events
    for i, event in enumerate(events[:len(decisions_data)]):
        decision_data = decisions_data[i]
        creator = management_users[i % len(management_users)]
        
        decision, created = Decision.objects.get_or_create(
            title=decision_data['title'],
            event=event,
            defaults={
                'description': decision_data['description'],
                'created_by': creator,
            }
        )
        decisions.append(decision)
        
        if created:
            print(f"Created decision: {decision.title}")
            
            # Create 1-3 deliverables for each decision
            num_deliverables = random.randint(1, 3)
            for j in range(num_deliverables):
                if deliverables_templates:
                    deliverable_data = deliverables_templates.pop(0)
                    assigned_user = random.choice(project_users)
                    
                    deliverable = Deliverable.objects.create(
                        title=deliverable_data['title'],
                        description=deliverable_data['description'],
                        status=deliverable_data['status'],
                        progress=deliverable_data['progress'],
                        decision=decision,
                        assigned_to=assigned_user,
                    )
                    deliverables.append(deliverable)
                    print(f"  - Created deliverable: {deliverable.title} (assigned to {assigned_user.get_full_name()})")
    
    print(f"Created {len(decisions)} decisions and {len(deliverables)} deliverables")
    return decisions, deliverables

def create_invitations_and_notifications(events, all_users):
    """Create invitations and notifications"""
    print("Creating invitations and notifications...")
    
    invitations = []
    notifications = []
    
    for event in events:
        # Create invitations for some users who are not yet participants
        non_participants = [user for user in all_users if user not in event.participants.all() and user != event.organizer]
        
        if non_participants:
            # Invite 1-3 additional users
            num_invites = min(random.randint(1, 3), len(non_participants))
            invitees = random.sample(non_participants, num_invites)
            
            for invitee in invitees:
                invitation, created = Invitation.objects.get_or_create(
                    event=event,
                    invitee=invitee,
                    defaults={
                        'invited_by': event.organizer,
                        'message': f'You are invited to participate in "{event.title}". Your expertise would be valuable for this event.',
                        'status': random.choice(['pending', 'accepted', 'declined']),
                    }
                )
                
                if created:
                    invitations.append(invitation)
                    
                    # Create notification for the invitation
                    notification = Notification.objects.create(
                        user=invitee,
                        title=f'Event Invitation: {event.title}',
                        message=f'{event.organizer.get_full_name()} invited you to "{event.title}" scheduled for {event.start_time.strftime("%B %d, %Y at %I:%M %p")}',
                        notification_type='event_invitation',
                        event=event,
                        invitation=invitation,
                        is_read=random.choice([True, False]),
                    )
                    notifications.append(notification)
    
    # Create some system notifications
    system_notifications = [
        {
            'title': 'Welcome to Decision Tracker',
            'message': 'Welcome to the Decision Tracker system! You can now participate in events, manage deliverables, and track project progress.',
            'type': 'system',
        },
        {
            'title': 'New Feature: Real-time Notifications',
            'message': 'We\'ve added real-time notifications to keep you updated on important events and decisions.',
            'type': 'system',
        },
        {
            'title': 'System Maintenance Scheduled',
            'message': 'System maintenance is scheduled for this weekend. Please save your work and expect brief downtime.',
            'type': 'system',
        },
    ]
    
    for user in all_users[:len(system_notifications)]:
        notification_data = system_notifications[all_users.index(user) % len(system_notifications)]
        notification = Notification.objects.create(
            user=user,
            title=notification_data['title'],
            message=notification_data['message'],
            notification_type=notification_data['type'],
            is_read=random.choice([True, False]),
        )
        notifications.append(notification)
    
    print(f"Created {len(invitations)} invitations and {len(notifications)} notifications")
    return invitations, notifications

def main():
    """Main function to populate test data"""
    print("🚀 Starting test data population for Decision Tracker...")
    print("=" * 60)
    
    try:
        # Create users
        users = create_users()
        management_users = [u for u in users if u.is_management or u.is_admin]
        project_users = [u for u in users if u.is_project_user]
        
        print(f"Management users: {len(management_users)}")
        print(f"Project users: {len(project_users)}")
        print("-" * 60)
        
        # Create projects
        projects = create_projects(management_users)
        print("-" * 60)
        
        # Create events with participants
        events = create_events_with_participants(projects, management_users, project_users)
        print("-" * 60)
        
        # Create decisions and deliverables
        decisions, deliverables = create_decisions_and_deliverables(events, management_users, project_users)
        print("-" * 60)
        
        # Create invitations and notifications
        invitations, notifications = create_invitations_and_notifications(events, users)
        print("-" * 60)
        
        # Print summary
        print("✅ Test data population completed successfully!")
        print("📊 Summary:")
        print(f"   👥 Users: {len(users)} (Admin: {len([u for u in users if u.is_admin])}, Management: {len([u for u in users if u.is_management])}, Project: {len([u for u in users if u.is_project_user])})")
        print(f"   📁 Projects: {len(projects)}")
        print(f"   📅 Events: {len(events)}")
        print(f"   ⚖️  Decisions: {len(decisions)}")
        print(f"   📋 Deliverables: {len(deliverables)}")
        print(f"   📧 Invitations: {len(invitations)}")
        print(f"   🔔 Notifications: {len(notifications)}")
        print("\n🔑 Login Credentials:")
        print("   Admin: admin_user / admin123")
        print("   Management: john_manager / password123")
        print("   Project User: alice_dev / password123")
        print("\n🌐 You can now test the system with realistic data!")
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()