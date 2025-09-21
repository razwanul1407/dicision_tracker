#!/usr/bin/env python
"""
Script to set up sample users with different permissions for testing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dicision_tracker.settings')
django.setup()

from accounts.models import CustomUser

def create_test_users():
    """Create test users with different permission configurations"""
    
    # Create management user
    if not CustomUser.objects.filter(username='manager').exists():
        manager = CustomUser.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='password123',
            role='management',
            first_name='Manager',
            last_name='User'
        )
        print(f"✅ Created management user: {manager.username}")
    
    # Create project users with different permissions
    project_users = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'permissions': {
                'can_view_projects': True,
                'can_view_events': True,
                'can_view_decisions': False,  # Limited access
                'can_manage_deliverables': True,
                'can_track_progress': True,
                'can_use_time_tracker': False,  # No time tracking
                'can_view_reports': False,  # No reports
                'can_view_calendar': True,
                'can_manage_invitations': True,
            }
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'permissions': {
                'can_view_projects': True,
                'can_view_events': True,
                'can_view_decisions': True,  # Full access
                'can_manage_deliverables': True,
                'can_track_progress': True,
                'can_use_time_tracker': True,  # Has time tracking
                'can_view_reports': True,  # Has reports
                'can_view_calendar': True,
                'can_manage_invitations': True,
            }
        },
        {
            'username': 'bob_wilson',
            'email': 'bob@example.com',
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'permissions': {
                'can_view_projects': False,  # Very limited access
                'can_view_events': True,
                'can_view_decisions': False,
                'can_manage_deliverables': True,
                'can_track_progress': False,
                'can_use_time_tracker': False,
                'can_view_reports': False,
                'can_view_calendar': True,
                'can_manage_invitations': False,
            }
        }
    ]
    
    for user_data in project_users:
        username = user_data['username']
        permissions = user_data.pop('permissions')
        
        if not CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.create_user(
                password='password123',
                role='project_user',
                **user_data
            )
            
            # Set permissions
            for perm_name, perm_value in permissions.items():
                setattr(user, perm_name, perm_value)
            user.save()
            
            print(f"✅ Created project user: {user.username} with custom permissions")
            
            # Show permission summary
            enabled_permissions = [perm for perm, enabled in permissions.items() if enabled]
            print(f"   Enabled permissions: {', '.join(enabled_permissions)}")
        else:
            print(f"⚠️  User {username} already exists")

def show_user_permissions():
    """Display current user permissions"""
    print("\n" + "="*60)
    print("CURRENT USER PERMISSIONS")
    print("="*60)
    
    project_users = CustomUser.objects.filter(role='project_user')
    
    for user in project_users:
        print(f"\n👤 {user.get_full_name()} ({user.username})")
        print("-" * 40)
        
        permissions = [
            ('can_view_projects', 'View Projects'),
            ('can_view_events', 'View Events'),
            ('can_view_decisions', 'View Decisions'),
            ('can_manage_deliverables', 'Manage Deliverables'),
            ('can_track_progress', 'Track Progress'),
            ('can_use_time_tracker', 'Use Time Tracker'),
            ('can_view_reports', 'View Reports'),
            ('can_view_calendar', 'Calendar Access'),
            ('can_manage_invitations', 'Manage Invitations'),
        ]
        
        for perm_name, perm_label in permissions:
            status = "✅" if getattr(user, perm_name, False) else "❌"
            print(f"  {status} {perm_label}")

if __name__ == '__main__':
    print("Setting up test users with different permissions...")
    create_test_users()
    show_user_permissions()
    print("\n🎉 Test users created successfully!")
    print("\nLogin credentials:")
    print("  Manager: manager / password123")
    print("  Project Users: john_doe, jane_smith, bob_wilson / password123")
    print("\nTest the permission system at: http://127.0.0.1:8000/")