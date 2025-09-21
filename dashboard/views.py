from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta

from accounts.permissions import admin_required, management_required, project_user_required
from core.models import Project, Event, Decision, Deliverable, Invitation


@login_required
def index(request):
    """Main dashboard view that redirects based on user role"""
    if request.user.is_admin:
        return redirect('dashboard:admin_dashboard')
    elif request.user.is_management:
        return redirect('dashboard:management_dashboard')
    else:
        return redirect('dashboard:project_user_dashboard')


@admin_required
def admin_dashboard(request):
    """Admin dashboard with system-wide statistics"""
    
    # Get statistics
    total_users = request.user.__class__.objects.count()
    total_projects = Project.objects.count()
    total_events = Event.objects.count()
    total_decisions = Decision.objects.count()
    total_deliverables = Deliverable.objects.count()
    
    # Recent activity
    recent_projects = Project.objects.select_related('created_by').order_by('-created_at')[:5]
    recent_events = Event.objects.select_related('project', 'organizer').order_by('-created_at')[:5]
    
    # Upcoming events
    upcoming_events = Event.objects.filter(
        start_time__gte=timezone.now()
    ).order_by('start_time')[:5]
    
    # Overdue deliverables
    overdue_deliverables = Deliverable.objects.filter(
        due_date__lt=timezone.now(),
        status__in=['pending', 'in-progress']
    ).select_related('assigned_to', 'decision__event')[:5]
    
    # Event conflicts
    conflicting_events = []
    for event in Event.objects.filter(start_time__gte=timezone.now()):
        conflicts = event.get_conflicting_events()
        if conflicts.exists():
            conflicting_events.append({
                'event': event,
                'conflicts': conflicts
            })
    
    context = {
        'total_users': total_users,
        'total_projects': total_projects,
        'total_events': total_events,
        'total_decisions': total_decisions,
        'total_deliverables': total_deliverables,
        'recent_projects': recent_projects,
        'recent_events': recent_events,
        'upcoming_events': upcoming_events,
        'overdue_deliverables': overdue_deliverables,
        'conflicting_events': conflicting_events[:5],
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@management_required
def management_dashboard(request):
    """Management dashboard with project-specific statistics"""
    
    # Get user's projects
    user_projects = Project.objects.filter(created_by=request.user)
    
    # Get statistics for user's projects
    total_projects = user_projects.count()
    total_events = Event.objects.filter(project__in=user_projects).count()
    total_decisions = Decision.objects.filter(event__project__in=user_projects).count()
    total_deliverables = Deliverable.objects.filter(
        decision__event__project__in=user_projects
    ).count()
    
    # Recent activity in user's projects
    recent_events = Event.objects.filter(
        project__in=user_projects
    ).select_related('project', 'organizer').order_by('-created_at')[:5]
    
    # Upcoming events in user's projects
    upcoming_events = Event.objects.filter(
        project__in=user_projects,
        start_time__gte=timezone.now()
    ).order_by('start_time')[:5]
    
    # Deliverables assigned by this user (base queryset)
    assigned_deliverables_base = Deliverable.objects.filter(
        decision__event__project__in=user_projects
    ).select_related('assigned_to', 'decision__event')
    
    # Progress statistics (calculate before slicing)
    completed_deliverables = assigned_deliverables_base.filter(status='completed').count()
    pending_deliverables = assigned_deliverables_base.filter(status='pending').count()
    in_progress_deliverables = assigned_deliverables_base.filter(status='in-progress').count()
    
    # Recent deliverables for display (slice after statistics)
    assigned_deliverables = assigned_deliverables_base.order_by('-created_at')[:10]
    
    context = {
        'user_projects': user_projects,
        'total_projects': total_projects,
        'total_events': total_events,
        'total_decisions': total_decisions,
        'total_deliverables': total_deliverables,
        'recent_events': recent_events,
        'upcoming_events': upcoming_events,
        'assigned_deliverables': assigned_deliverables,
        'completed_deliverables': completed_deliverables,
        'pending_deliverables': pending_deliverables,
        'in_progress_deliverables': in_progress_deliverables,
    }
    
    return render(request, 'dashboard/management_dashboard.html', context)


@project_user_required
def project_user_dashboard(request):
    """Project user dashboard with personal tasks and invitations"""
    
    # Get user's assigned deliverables
    my_deliverables = Deliverable.objects.filter(
        assigned_to=request.user
    ).select_related('decision__event__project').order_by('-created_at')
    
    # Get user's invitations
    my_invitations = Invitation.objects.filter(
        invitee=request.user
    ).select_related('event__project', 'invited_by').order_by('-created_at')[:10]
    
    # Get events user is participating in or organized
    my_events = Event.objects.filter(
        Q(organizer=request.user) | Q(participants=request.user)
    ).distinct().select_related('project').order_by('-start_time')[:10]
    
    # Upcoming events
    upcoming_events = Event.objects.filter(
        Q(organizer=request.user) | Q(participants=request.user),
        start_time__gte=timezone.now()
    ).distinct().order_by('start_time')[:5]
    
    # Deliverable statistics
    total_deliverables = my_deliverables.count()
    completed_deliverables = my_deliverables.filter(status='completed').count()
    pending_deliverables = my_deliverables.filter(status='pending').count()
    in_progress_deliverables = my_deliverables.filter(status='in-progress').count()
    overdue_deliverables = my_deliverables.filter(
        due_date__lt=timezone.now(),
        status__in=['pending', 'in-progress']
    ).count()
    
    # Recent decisions made by user
    my_decisions = Decision.objects.filter(
        created_by=request.user
    ).select_related('event__project').order_by('-created_at')[:5]
    
    context = {
        'my_deliverables': my_deliverables,
        'my_invitations': my_invitations,
        'my_events': my_events,
        'upcoming_events': upcoming_events,
        'my_decisions': my_decisions,
        'total_deliverables': total_deliverables,
        'completed_deliverables': completed_deliverables,
        'pending_deliverables': pending_deliverables,
        'in_progress_deliverables': in_progress_deliverables,
        'overdue_deliverables': overdue_deliverables,
    }
    
    return render(request, 'dashboard/project_user_dashboard.html', context)


@login_required
def calendar_view(request):
    """Calendar view for all users (filtered by role)"""
    # Get user's accessible events based on role
    if request.user.is_admin:
        events = Event.objects.all()
        projects = Project.objects.all()
    elif request.user.is_management:
        user_projects = Project.objects.filter(created_by=request.user)
        events = Event.objects.filter(project__in=user_projects)
        projects = user_projects
    else:
        # Project users see events they're invited to, organizing, or participating in
        events = Event.objects.filter(
            Q(organizer=request.user) | 
            Q(participants=request.user) |
            Q(invitations__invitee=request.user)
        ).distinct()
        # Get projects from accessible events
        projects = Project.objects.filter(events__in=events).distinct()
    
    context = {
        'total_events': events.count(),
        'total_projects': projects.count(),
    }
    
    return render(request, 'dashboard/calendar.html', context)


@login_required
def reports_view(request):
    """Reports and analytics view"""
    from django.db.models import Count, Q
    
    # Get base data based on user role
    if request.user.is_admin:
        template = 'dashboard/admin_reports.html'
        events = Event.objects.all()
        decisions = Decision.objects.all()
        deliverables = Deliverable.objects.all()
        projects = Project.objects.all()
    elif request.user.is_management:
        template = 'dashboard/management_reports.html'
        user_projects = Project.objects.filter(created_by=request.user)
        events = Event.objects.filter(project__in=user_projects)
        decisions = Decision.objects.filter(event__project__in=user_projects)
        deliverables = Deliverable.objects.filter(decision__event__project__in=user_projects)
        projects = user_projects
    else:
        template = 'dashboard/project_user_reports.html'
        # Project users see data from events they're involved in
        events = Event.objects.filter(
            Q(organizer=request.user) | 
            Q(participants=request.user) |
            Q(invitations__invitee=request.user)
        ).distinct()
        decisions = Decision.objects.filter(event__in=events)
        deliverables = Deliverable.objects.filter(decision__event__in=events).distinct()
        projects = Project.objects.filter(events__in=events).distinct()
    
    # Calculate time periods
    now = timezone.now()
    last_month = now - timedelta(days=30)
    last_week = now - timedelta(days=7)
    
    # Calculate statistics
    context = {
        'total_projects': projects.count(),
        'total_events': events.count(),
        'total_decisions': decisions.count(),
        'total_deliverables': deliverables.count(),
        
        # Recent activity
        'recent_events': events.filter(created_at__gte=last_week).count(),
        'recent_decisions': decisions.filter(created_at__gte=last_week).count(),
        'recent_deliverables': deliverables.filter(created_at__gte=last_week).count(),
        
        # Monthly trends
        'monthly_events': events.filter(created_at__gte=last_month).count(),
        'monthly_decisions': decisions.filter(created_at__gte=last_month).count(),
        'monthly_deliverables': deliverables.filter(created_at__gte=last_month).count(),
        
        # Status breakdowns
        'deliverable_status_counts': deliverables.values('status').annotate(count=Count('id')),
        'decision_by_event_counts': decisions.values('event__title').annotate(count=Count('id'))[:10],
        
        # Recent items for display
        'latest_events': events.order_by('-created_at')[:5],
        'latest_decisions': decisions.order_by('-created_at')[:5],
        'latest_deliverables': deliverables.order_by('-created_at')[:5],
    }
    
    return render(request, template, context)


@login_required
def calendar_events_api(request):
    """API endpoint for calendar events"""
    # Get user's accessible events based on role
    if request.user.is_admin:
        events = Event.objects.all().select_related('project', 'organizer')
    elif request.user.is_management:
        user_projects = Project.objects.filter(created_by=request.user)
        events = Event.objects.filter(project__in=user_projects).select_related('project', 'organizer')
    else:
        # Project users see events they're invited to, organizing, or participating in
        events = Event.objects.filter(
            Q(organizer=request.user) | 
            Q(participants=request.user) |
            Q(invitations__invitee=request.user)
        ).distinct().select_related('project', 'organizer')
    
    # Convert events to FullCalendar format
    calendar_events = []
    for event in events:
        # Check user's relationship to the event
        is_organizer = event.organizer == request.user
        is_participant = request.user in event.participants.all()
        is_invited = event.invitations.filter(invitee=request.user).exists()
        
        # Check for conflicts
        conflicts = event.get_conflicting_events()
        has_conflict = conflicts.exists()
        
        # Determine color based on relationship
        color = '#3B82F6'  # Default blue
        if is_organizer:
            color = '#3B82F6'  # Blue for organized events
        elif is_participant:
            color = '#10B981'  # Green for participating
        elif is_invited:
            color = '#F59E0B'  # Yellow for invited
        
        calendar_events.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat() if event.end_time else None,
            'color': color,
            'description': event.description,
            'project_id': event.project.id if event.project else None,
            'project_name': event.project.name if event.project else None,
            'organizer_name': event.organizer.get_full_name() if event.organizer else None,
            'isOrganizer': is_organizer,
            'isParticipant': is_participant,
            'isInvited': is_invited,
            'hasConflict': has_conflict,
        })
    
    return JsonResponse(calendar_events, safe=False)


@login_required 
def user_projects_api(request):
    """API endpoint for user's accessible projects"""
    if request.user.is_admin:
        projects = Project.objects.all()
    elif request.user.is_management:
        projects = Project.objects.filter(created_by=request.user)
    else:
        # Project users see projects from their accessible events
        accessible_events = Event.objects.filter(
            Q(organizer=request.user) | 
            Q(participants=request.user) |
            Q(invitations__invitee=request.user)
        ).distinct()
        projects = Project.objects.filter(events__in=accessible_events).distinct()
    
    projects_data = [
        {
            'id': project.id,
            'name': project.name,
            'description': project.description
        }
        for project in projects
    ]
    
    return JsonResponse(projects_data, safe=False)
