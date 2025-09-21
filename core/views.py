from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from accounts.models import CustomUser
from accounts.permissions import (
    admin_required, management_required, project_user_required,
    require_management_or_admin,
    AdminRequiredMixin, ManagementRequiredMixin, ProjectUserRequiredMixin
)
from .models import Project, Event, Decision, Deliverable, Invitation, Notification
from .forms import (
    ProjectForm, EventForm, DecisionForm, DeliverableForm, 
    DeliverableProgressForm, InvitationForm, InvitationResponseForm
)

User = get_user_model()

# ============= PROJECT VIEWS =============

@management_required
def project_list(request):
    """List all projects (admin) or user's projects (management)"""
    if request.user.is_admin:
        projects = Project.objects.all().select_related('created_by').order_by('-created_at')
    else:
        projects = Project.objects.filter(created_by=request.user).select_related('created_by').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'core/project_list.html', context)


@management_required
def project_create(request):
    """Create a new project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('core:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'core/project_form.html', {
        'form': form,
        'title': 'Create New Project'
    })


@login_required
def project_detail(request, pk):
    """Project detail view"""
    project = get_object_or_404(Project, pk=pk)
    
    # Check permissions
    if not request.user.is_admin and not request.user.is_management:
        # Project users can only view projects they participate in
        if not project.events.filter(participants=request.user).exists():
            messages.error(request, "You don't have permission to view this project.")
            return redirect('dashboard:index')
    elif request.user.is_management and project.created_by != request.user:
        messages.error(request, "You can only view your own projects.")
        return redirect('core:my_projects')
    
    events = project.events.all().select_related('organizer').order_by('-start_time')
    recent_decisions = Decision.objects.filter(event__project=project).select_related('event', 'created_by').order_by('-created_at')[:5]
    
    context = {
        'project': project,
        'events': events,
        'recent_decisions': recent_decisions,
        'can_edit': request.user.is_admin or project.created_by == request.user,
    }
    return render(request, 'core/project_detail.html', context)


@management_required
def project_edit(request, pk):
    """Edit project"""
    project = get_object_or_404(Project, pk=pk)
    
    # Check permissions
    if not request.user.is_admin and project.created_by != request.user:
        messages.error(request, "You can only edit your own projects.")
        return redirect('core:project_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated successfully!')
            return redirect('core:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'core/project_form.html', {
        'form': form,
        'title': f'Edit Project: {project.name}',
        'project': project
    })


@login_required
def my_projects(request):
    """User's projects based on role"""
    # Check permission for project users
    if request.user.is_project_user and not request.user.has_permission('can_view_projects'):
        messages.error(request, "You don't have permission to view projects.")
        return redirect('dashboard:project_user_dashboard')
    
    if request.user.is_admin:
        return redirect('core:project_list')
    elif request.user.is_management:
        projects = Project.objects.filter(created_by=request.user).order_by('-created_at')
    else:
        # Project users see projects they participate in
        projects = Project.objects.filter(
            events__participants=request.user
        ).distinct().order_by('-created_at')
    
    context = {'projects': projects}
    return render(request, 'core/my_projects.html', context)


# ============= EVENT VIEWS =============

@login_required
def event_list(request):
    """List events based on user role"""
    if request.user.is_admin:
        events = Event.objects.all()
    elif request.user.is_management:
        events = Event.objects.filter(project__created_by=request.user)
    else:
        events = Event.objects.filter(
            Q(organizer=request.user) | Q(participants=request.user)
        ).distinct()
    
    events = events.select_related('project', 'organizer').order_by('-start_time')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(project__name__icontains=search_query)
        )
    
    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'core/event_list.html', context)


@project_user_required
def event_create(request):
    """Create a new event"""
    if request.method == 'POST':
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Create invitations and notifications for participants
            for participant in event.participants.all():
                # Create invitation
                invitation, created = Invitation.objects.get_or_create(
                    event=event,
                    invitee=participant,
                    defaults={
                        'invited_by': request.user,
                        'message': f'You have been invited to participate in "{event.title}"'
                    }
                )
                
                # Create notification for the participant
                if created:  # Only create notification if invitation was newly created
                    Notification.objects.create(
                        user=participant,
                        title=f'New Event Invitation: {event.title}',
                        message=f'{request.user.get_full_name() or request.user.username} has invited you to participate in "{event.title}" on {event.start_time.strftime("%B %d, %Y at %I:%M %p")}',
                        notification_type='event_invitation',
                        event=event,
                        invitation=invitation
                    )
            
            # Check for conflicts
            if event.has_conflicts():
                conflicts = event.get_conflicting_events()
                conflict_list = ', '.join([e.title for e in conflicts[:3]])
                messages.warning(
                    request, 
                    f'Event created but conflicts detected with: {conflict_list}'
                )
            else:
                messages.success(request, f'Event "{event.title}" created successfully!')
            
            return redirect('core:event_detail', pk=event.pk)
    else:
        form = EventForm(user=request.user)
    
    return render(request, 'core/event_form.html', {
        'form': form,
        'title': 'Create New Event'
    })


@login_required
def event_detail(request, pk):
    """Event detail view"""
    event = get_object_or_404(Event, pk=pk)
    
    # Check permissions
    can_view = (
        request.user.is_admin or
        (request.user.is_management and event.project.created_by == request.user) or
        event.organizer == request.user or
        event.participants.filter(id=request.user.id).exists()
    )
    
    if not can_view:
        messages.error(request, "You don't have permission to view this event.")
        return redirect('dashboard:index')
    
    decisions = event.decisions.all().select_related('created_by').order_by('-created_at')
    conflicts = event.get_conflicting_events() if event.pk else []
    
    # Get invitation status for current user
    user_invitation = None
    if not request.user.is_admin:
        try:
            user_invitation = Invitation.objects.get(event=event, invitee=request.user)
        except Invitation.DoesNotExist:
            pass
    
    context = {
        'event': event,
        'decisions': decisions,
        'conflicts': conflicts,
        'user_invitation': user_invitation,
        'can_edit': request.user.is_admin or event.organizer == request.user or 
                   (request.user.is_management and event.project.created_by == request.user),
        'now': timezone.now(),
    }
    return render(request, 'core/event_detail.html', context)


@project_user_required
def event_edit(request, pk):
    """Edit event"""
    event = get_object_or_404(Event, pk=pk)
    
    # Check permissions
    can_edit = (
        request.user.is_admin or
        event.organizer == request.user or
        (request.user.is_management and event.project.created_by == request.user)
    )
    
    if not can_edit:
        messages.error(request, "You don't have permission to edit this event.")
        return redirect('core:event_detail', pk=pk)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('core:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event, user=request.user)
    
    return render(request, 'core/event_form.html', {
        'form': form,
        'title': f'Edit Event: {event.title}',
        'event': event
    })


@login_required
def quick_add_decisions(request, pk):
    """Quick add multiple decisions to an event"""
    event = get_object_or_404(Event, pk=pk)
    
    # Check permissions
    can_add = (
        request.user.is_admin or
        request.user.is_management or
        event.created_by == request.user
    )
    
    if not can_add:
        messages.error(request, "You don't have permission to add decisions to this event.")
        return redirect('core:event_detail', pk=pk)
    
    if request.method == 'POST':
        decision_titles = request.POST.getlist('decision_titles[]')
        decision_descriptions = request.POST.getlist('decision_descriptions[]')
        
        created_count = 0
        for i, title in enumerate(decision_titles):
            title = title.strip()
            if title:  # Only create if title is not empty
                description = decision_descriptions[i].strip() if i < len(decision_descriptions) else ''
                
                Decision.objects.create(
                    event=event,
                    title=title,
                    description=description,
                    created_by=request.user
                )
                created_count += 1
        
        if created_count > 0:
            messages.success(request, f'Successfully created {created_count} decision{"s" if created_count != 1 else ""}!')
        else:
            messages.warning(request, 'No decisions were created. Please provide at least one decision title.')
    
    return redirect('core:event_detail', pk=pk)


@login_required
def my_events(request):
    """User's events based on role"""
    # Check permission for project users
    if request.user.is_project_user and not request.user.has_permission('can_view_events'):
        messages.error(request, "You don't have permission to view events.")
        return redirect('dashboard:project_user_dashboard')
    
    if request.user.is_admin:
        return redirect('core:event_list')
    elif request.user.is_management:
        events = Event.objects.filter(project__created_by=request.user)
    else:
        events = Event.objects.filter(
            Q(organizer=request.user) | Q(participants=request.user)
        ).distinct()
    
    events = events.select_related('project', 'organizer').order_by('-start_time')
    
    context = {'events': events}
    return render(request, 'core/my_events.html', context)


# ============= DECISION VIEWS =============

@login_required
def decision_list(request):
    """List decisions based on user role"""
    if request.user.is_admin:
        decisions = Decision.objects.all()
    elif request.user.is_management:
        decisions = Decision.objects.filter(event__project__created_by=request.user)
    else:
        decisions = Decision.objects.filter(
            Q(created_by=request.user) | Q(event__participants=request.user)
        ).distinct()
    
    decisions = decisions.select_related('event__project', 'created_by').order_by('-created_at')
    
    paginator = Paginator(decisions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'core/decision_list.html', context)


@project_user_required
def decision_create(request):
    """Create a new decision"""
    if request.method == 'POST':
        form = DecisionForm(request.POST, user=request.user)
        if form.is_valid():
            decision = form.save(commit=False)
            decision.created_by = request.user
            decision.save()
            messages.success(request, f'Decision "{decision.title}" created successfully!')
            return redirect('core:decision_detail', pk=decision.pk)
    else:
        form = DecisionForm(user=request.user)
    
    return render(request, 'core/decision_form.html', {
        'form': form,
        'title': 'Create New Decision'
    })


@login_required
def decision_detail(request, pk):
    """Decision detail view"""
    decision = get_object_or_404(Decision, pk=pk)
    
    # Check permissions
    can_view = (
        request.user.is_admin or
        (request.user.is_management and decision.event.project.created_by == request.user) or
        decision.created_by == request.user or
        decision.event.participants.filter(id=request.user.id).exists()
    )
    
    if not can_view:
        messages.error(request, "You don't have permission to view this decision.")
        return redirect('dashboard:index')
    
    deliverables = decision.deliverables.all().select_related('assigned_to').order_by('-created_at')
    
    context = {
        'decision': decision,
        'deliverables': deliverables,
        'can_edit': request.user.is_admin or decision.created_by == request.user or
                   (request.user.is_management and decision.event.project.created_by == request.user),
    }
    return render(request, 'core/decision_detail.html', context)


@login_required
def decision_edit(request, pk):
    """Edit an existing decision"""
    decision = get_object_or_404(Decision, pk=pk)
    
    # Check permissions
    can_edit = (
        request.user.is_admin or 
        decision.created_by == request.user or
        (request.user.is_management and decision.event.project.created_by == request.user)
    )
    
    if not can_edit:
        messages.error(request, "You don't have permission to edit this decision.")
        return redirect('core:decision_detail', pk=pk)
    
    if request.method == 'POST':
        form = DecisionForm(request.POST, instance=decision, user=request.user)
        if form.is_valid():
            decision = form.save()
            messages.success(request, f'Decision "{decision.title}" updated successfully!')
            return redirect('core:decision_detail', pk=decision.pk)
    else:
        form = DecisionForm(instance=decision, user=request.user)
    
    return render(request, 'core/decision_form.html', {
        'form': form,
        'decision': decision,
        'title': f'Edit Decision: {decision.title}'
    })


@login_required
def my_decisions(request):
    """User's decisions"""
    # Check permission for project users
    if request.user.is_project_user and not request.user.has_permission('can_view_decisions'):
        messages.error(request, "You don't have permission to view decisions.")
        return redirect('dashboard:project_user_dashboard')
    
    decisions = Decision.objects.filter(created_by=request.user).select_related(
        'event__project'
    ).order_by('-created_at')
    
    context = {'decisions': decisions}
    return render(request, 'core/my_decisions.html', context)


# ============= DELIVERABLE VIEWS =============

@login_required
def deliverable_list(request):
    """List deliverables based on user role"""
    if request.user.is_admin:
        deliverables = Deliverable.objects.all()
    elif request.user.is_management:
        deliverables = Deliverable.objects.filter(
            decision__event__project__created_by=request.user
        )
    else:
        deliverables = Deliverable.objects.filter(assigned_to=request.user)
    
    deliverables = deliverables.select_related(
        'assigned_to', 'decision__event__project'
    ).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        deliverables = deliverables.filter(status=status_filter)
    
    paginator = Paginator(deliverables, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': Deliverable.STATUS_CHOICES,
    }
    return render(request, 'core/deliverable_list.html', context)


@management_required
def deliverable_create(request):
    """Create a new deliverable"""
    # Get event parameter if provided
    event_id = request.GET.get('event')
    initial_data = {}
    
    if request.method == 'POST':
        form = DeliverableForm(request.POST, user=request.user, event_id=event_id)
        if form.is_valid():
            deliverable = form.save()
            messages.success(request, f'Deliverable "{deliverable.title}" created successfully!')
            return redirect('core:deliverable_detail', pk=deliverable.pk)
    else:
        form = DeliverableForm(user=request.user, event_id=event_id, initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Create New Deliverable'
    }
    
    # Add event context if provided
    if event_id:
        try:
            event = Event.objects.get(pk=event_id)
            context['event'] = event
            context['title'] = f'Create Deliverable for {event.title}'
        except Event.DoesNotExist:
            pass
    
    return render(request, 'core/deliverable_form.html', context)


@login_required
def deliverable_detail(request, pk):
    """Deliverable detail view"""
    deliverable = get_object_or_404(Deliverable, pk=pk)
    
    # Check permissions
    can_view = (
        request.user.is_admin or
        deliverable.assigned_to == request.user or
        (request.user.is_management and (
            # Can view if they created the decision that led to this deliverable
            (deliverable.decision and 
             deliverable.decision.event.project.created_by == request.user) or
            # For standalone deliverables, allow management users to view all
            (not deliverable.decision)
        ))
    )
    
    if not can_view:
        messages.error(request, "You don't have permission to view this deliverable.")
        return redirect('dashboard:index')
    
    context = {
        'deliverable': deliverable,
        'can_edit': request.user.is_admin or deliverable.assigned_to == request.user or
                   (request.user.is_management and (
                       # Can edit if they created the decision that led to this deliverable
                       (deliverable.decision and
                        deliverable.decision.event.project.created_by == request.user) or
                       # For standalone deliverables, allow management users to edit all
                       (not deliverable.decision)
                   )),
    }
    return render(request, 'core/deliverable_detail.html', context)


@login_required
def deliverable_update(request, pk):
    """Update deliverable progress"""
    deliverable = get_object_or_404(Deliverable, pk=pk)
    
    # Check permissions
    can_edit = (
        request.user.is_admin or
        deliverable.assigned_to == request.user or
        (request.user.is_management and (
            # Can edit if they created the decision that led to this deliverable
            (deliverable.decision and
             deliverable.decision.event.project.created_by == request.user) or
            # For standalone deliverables, allow management users to edit all
            (not deliverable.decision)
        ))
    )
    
    if not can_edit:
        messages.error(request, "You don't have permission to edit this deliverable.")
        return redirect('core:deliverable_detail', pk=pk)
    
    # Use different form based on user role
    if deliverable.assigned_to == request.user and not request.user.is_admin:
        form_class = DeliverableProgressForm
    else:
        form_class = DeliverableForm
    
    if request.method == 'POST':
        if form_class == DeliverableProgressForm:
            form = form_class(request.POST, instance=deliverable)
        else:
            form = form_class(request.POST, instance=deliverable, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Deliverable "{deliverable.title}" updated successfully!')
            return redirect('core:deliverable_detail', pk=deliverable.pk)
    else:
        if form_class == DeliverableProgressForm:
            form = form_class(instance=deliverable)
        else:
            form = form_class(instance=deliverable, user=request.user)
    
    return render(request, 'core/deliverable_form.html', {
        'form': form,
        'title': f'Update: {deliverable.title}',
        'deliverable': deliverable
    })


@login_required
def my_deliverables(request):
    """User's assigned deliverables"""
    # Check permission for project users
    if request.user.is_project_user and not request.user.has_permission('can_manage_deliverables'):
        messages.error(request, "You don't have permission to manage deliverables.")
        return redirect('dashboard:project_user_dashboard')
    
    deliverables = Deliverable.objects.filter(
        assigned_to=request.user
    ).select_related('decision__event__project').order_by('-created_at')
    
    # Calculate counts
    pending_count = deliverables.filter(status='pending').count()
    in_progress_count = deliverables.filter(status='in_progress').count()
    completed_count = deliverables.filter(status='completed').count()
    
    # Calculate completion rate
    total_deliverables = deliverables.count()
    completion_rate = (completed_count / total_deliverables * 100) if total_deliverables > 0 else 0
    
    context = {
        'deliverables': deliverables,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'completion_rate': completion_rate,
        'today': timezone.now().date(),
    }
    return render(request, 'core/my_deliverables.html', context)


@management_required
def assigned_deliverables(request):
    """Deliverables assigned by management user"""
    if request.user.is_admin:
        deliverables = Deliverable.objects.all()
    else:
        deliverables = Deliverable.objects.filter(
            decision__event__project__created_by=request.user
        )
    
    deliverables = deliverables.select_related(
        'assigned_to', 'decision__event__project'
    ).order_by('-created_at')
    
    context = {'deliverables': deliverables}
    return render(request, 'core/assigned_deliverables.html', context)


# ============= INVITATION VIEWS =============

@management_required
def invitation_create(request):
    """Create event invitation"""
    if request.method == 'POST':
        form = InvitationForm(request.POST, user=request.user)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.invited_by = request.user
            invitation.save()
            messages.success(
                request, 
                f'Invitation sent to {invitation.invitee.get_full_name()}'
            )
            return redirect('core:event_detail', pk=invitation.event.pk)
    else:
        form = InvitationForm(user=request.user)
    
    return render(request, 'core/invitation_form.html', {
        'form': form,
        'title': 'Send Event Invitation'
    })


@login_required
def invitation_list(request):
    """List invitations based on user role"""
    if request.user.is_admin:
        invitations = Invitation.objects.all()
    elif request.user.is_management:
        invitations = Invitation.objects.filter(invited_by=request.user)
    else:
        invitations = Invitation.objects.filter(invitee=request.user)
    
    invitations = invitations.select_related(
        'event__project', 'invitee', 'invited_by'
    ).order_by('-created_at')
    
    context = {'invitations': invitations}
    return render(request, 'core/invitation_list.html', context)


@login_required
def invitation_respond(request, pk):
    """Respond to invitation"""
    invitation = get_object_or_404(Invitation, pk=pk, invitee=request.user)
    
    if request.method == 'POST':
        response = request.POST.get('response')
        if response in ['accepted', 'declined']:
            invitation.status = response
            invitation.save()
            
            # Add user to event participants if accepted
            if response == 'accepted':
                invitation.event.participants.add(request.user)
                messages.success(request, 'Invitation accepted! You have been added to the event.')
            else:
                invitation.event.participants.remove(request.user)
                messages.info(request, 'Invitation declined.')
        else:
            messages.error(request, 'Invalid response.')
        
        return redirect('core:invitation_list')
    
    # If GET request, redirect to invitation list
    return redirect('core:invitation_list')


@login_required
def my_invitations(request):
    """User's invitations"""
    invitations = Invitation.objects.filter(
        invitee=request.user
    ).select_related('event__project', 'invited_by').order_by('-created_at')
    
    context = {'invitations': invitations}
    return render(request, 'core/my_invitations.html', context)


# ============= AJAX VIEWS =============

@require_POST
@login_required
def quick_progress_update(request, pk):
    """Quick AJAX progress update"""
    deliverable = get_object_or_404(Deliverable, pk=pk)
    
    # Check permissions
    if deliverable.assigned_to != request.user and not request.user.is_admin:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        progress = int(request.POST.get('progress', 0))
        if 0 <= progress <= 100:
            deliverable.progress = progress
            if progress == 100 and deliverable.status != 'completed':
                deliverable.status = 'completed'
            elif progress > 0 and deliverable.status == 'pending':
                deliverable.status = 'in-progress'
            deliverable.save()
            
            return JsonResponse({
                'success': True,
                'progress': deliverable.progress,
                'status': deliverable.get_status_display()
            })
        else:
            return JsonResponse({'error': 'Invalid progress value'}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid progress value'}, status=400)


@require_POST
@login_required
def invitation_respond_ajax(request, pk):
    """AJAX endpoint for responding to invitations"""
    invitation = get_object_or_404(Invitation, pk=pk, invitee=request.user)
    
    response = request.POST.get('response', '').lower()
    if response not in ['accepted', 'declined']:
        return JsonResponse({'success': False, 'error': 'Invalid response'}, status=400)
    
    try:
        invitation.status = response
        invitation.save()
        
        # Add/remove user from event participants
        if response == 'accepted':
            invitation.event.participants.add(request.user)
            message = 'Invitation accepted! You have been added to the event.'
            
            # Create notification for event organizer and project creator
            organizer = invitation.event.organizer
            project_creator = invitation.event.project.created_by if invitation.event.project else None
            
            # Notify event organizer
            if organizer and organizer != request.user:
                Notification.objects.create(
                    user=organizer,
                    title=f'Invitation Accepted',
                    message=f'{request.user.get_full_name() or request.user.username} accepted the invitation to "{invitation.event.title}"',
                    notification_type='invitation_response',
                    event=invitation.event,
                    invitation=invitation
                )
            
            # Notify project creator (if different from organizer)
            if project_creator and project_creator != request.user and project_creator != organizer:
                Notification.objects.create(
                    user=project_creator,
                    title=f'Event Invitation Accepted',
                    message=f'{request.user.get_full_name() or request.user.username} accepted the invitation to "{invitation.event.title}" in project "{invitation.event.project.name}"',
                    notification_type='invitation_response',
                    event=invitation.event,
                    invitation=invitation
                )
                
        else:
            invitation.event.participants.remove(request.user)
            message = 'Invitation declined.'
            
            # Create notification for decline (optional - you can remove this if you don't want decline notifications)
            organizer = invitation.event.organizer
            if organizer and organizer != request.user:
                Notification.objects.create(
                    user=organizer,
                    title=f'Invitation Declined',
                    message=f'{request.user.get_full_name() or request.user.username} declined the invitation to "{invitation.event.title}"',
                    notification_type='invitation_response',
                    event=invitation.event,
                    invitation=invitation
                )
        
        return JsonResponse({
            'success': True,
            'message': message,
            'status': invitation.get_status_display(),
            'should_reload': True  # Signal to reload the page
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============= MANAGEMENT USER VIEWS =============

@management_required
def team_overview(request):
    """Management view for team overview"""
    # For management users, show projects they created or are involved in
    user_projects = Project.objects.filter(created_by=request.user)
    
    # Get team members from events in user's projects
    team_members = User.objects.filter(
        events_participated__project__in=user_projects
    ).distinct()
    
    # Get statistics
    total_projects = user_projects.count()
    total_members = team_members.count()
    pending_tasks = Deliverable.objects.filter(
        decision__event__project__in=user_projects,
        status__in=['pending', 'in_progress']
    ).count()
    
    context = {
        'user_projects': user_projects[:5],  # Recent 5 projects
        'team_members': team_members,
        'total_projects': total_projects,
        'total_members': total_members,
        'pending_tasks': pending_tasks,
    }
    return render(request, 'core/management/team_overview.html', context)


@management_required
def workload_distribution(request):
    """Management view for workload distribution analysis"""
    user_projects = Project.objects.filter(created_by=request.user)
    
    # Get workload data for team members
    team_workload = []
    team_members = User.objects.filter(
        events_participated__project__in=user_projects
    ).distinct()
    
    for member in team_members:
        assigned_tasks = Deliverable.objects.filter(
            assigned_to=member,
            decision__event__project__in=user_projects
        )
        pending_tasks = assigned_tasks.filter(status__in=['pending', 'in_progress']).count()
        completed_tasks = assigned_tasks.filter(status='completed').count()
        overdue_tasks = assigned_tasks.filter(
            due_date__lt=timezone.now().date(),
            status__in=['pending', 'in_progress']
        ).count()
        
        team_workload.append({
            'member': member,
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'total_tasks': assigned_tasks.count(),
            'completion_rate': (completed_tasks / assigned_tasks.count() * 100) if assigned_tasks.count() > 0 else 0,
            'workload_percentage': min(assigned_tasks.count() * 5, 100)  # Scale tasks to percentage (max 100%)
        })
    
    context = {
        'team_workload': team_workload,
        'user_projects': user_projects,
    }
    return render(request, 'core/management/workload_distribution.html', context)


# ============= PROJECT USER VIEWS =============

@login_required
def task_progress(request):
    """Project user view for personal task progress tracking"""
    # Check permission for project users
    if request.user.is_project_user and not request.user.has_permission('can_track_progress'):
        messages.error(request, "You don't have permission to track progress.")
        return redirect('dashboard:project_user_dashboard')
    
    user_deliverables = Deliverable.objects.filter(assigned_to=request.user)
    
    # Progress statistics
    total_tasks = user_deliverables.count()
    completed_tasks = user_deliverables.filter(status='completed').count()
    in_progress_tasks = user_deliverables.filter(status='in_progress').count()
    pending_tasks = user_deliverables.filter(status='pending').count()
    overdue_tasks = user_deliverables.filter(
        due_date__lt=timezone.now().date(),
        status__in=['pending', 'in_progress']
    ).count()
    
    # Progress by project
    project_progress = {}
    user_projects = Project.objects.filter(events__participants=request.user).distinct()
    for project in user_projects:
        project_tasks = user_deliverables.filter(decision__event__project=project)
        project_completed = project_tasks.filter(status='completed').count()
        project_total = project_tasks.count()
        completion_rate = (project_completed / project_total * 100) if project_total > 0 else 0
        
        project_progress[project] = {
            'total': project_total,
            'completed': project_completed,
            'completion_rate': completion_rate,
            'tasks': project_tasks[:3]  # Recent 3 tasks
        }
    
    context = {
        'user_deliverables': user_deliverables[:10],  # Recent 10 tasks
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'project_progress': project_progress,
        'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
    }
    return render(request, 'core/project_user/task_progress.html', context)


@login_required
def time_tracker(request):
    """Project user view for time tracking (placeholder for future implementation)"""
    # Check permission for project users
    if request.user.is_project_user and not request.user.has_permission('can_use_time_tracker'):
        messages.error(request, "You don't have permission to use time tracker.")
        return redirect('dashboard:project_user_dashboard')
    
    # This would integrate with a time tracking system
    # For now, we'll show a basic interface
    
    user_projects = Project.objects.filter(events__participants=request.user).distinct()
    recent_tasks = Deliverable.objects.filter(
        assigned_to=request.user,
        status__in=['in_progress', 'completed']
    ).order_by('-updated_at')[:10]
    
    context = {
        'user_projects': user_projects,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'core/project_user/time_tracker.html', context)


# ============= PERMISSION MANAGEMENT VIEWS =============

@login_required
@require_management_or_admin
def manage_user_permissions(request):
    """Manage project user permissions"""
    project_users = CustomUser.objects.filter(role='project_user').order_by('username')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        project_users = project_users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'project_users': project_users,
        'search_query': search_query,
    }
    return render(request, 'core/manage_permissions.html', context)


@login_required
@require_management_or_admin
def user_permissions_detail(request, user_id):
    """View and edit specific user permissions"""
    user = get_object_or_404(CustomUser, id=user_id, role='project_user')
    
    # Define all available permissions with descriptions
    permissions = [
        ('can_view_projects', 'View Projects', 'Can view assigned projects and project details'),
        ('can_view_events', 'View Events', 'Can view and participate in project events'),
        ('can_view_decisions', 'View Decisions', 'Can view project decisions and outcomes'),
        ('can_manage_deliverables', 'Manage Deliverables', 'Can manage assigned tasks and deliverables'),
        ('can_track_progress', 'Track Progress', 'Can track and update task progress'),
        ('can_use_time_tracker', 'Time Tracker', 'Can use time tracking features'),
        ('can_view_reports', 'View Reports', 'Can view personal productivity reports'),
        ('can_view_calendar', 'Calendar Access', 'Can access calendar view and scheduling'),
        ('can_manage_invitations', 'Manage Invitations', 'Can manage event invitations and responses'),
    ]
    
    if request.method == 'POST':
        # Update permissions based on form data
        for perm_name, _, _ in permissions:
            new_value = perm_name in request.POST
            current_value = getattr(user, perm_name, False)
            
            if new_value != current_value:
                setattr(user, perm_name, new_value)
        
        user.save()
        messages.success(request, f'Permissions updated for {user.get_full_name() or user.username}')
        return redirect('core:user_permissions_detail', user_id=user.id)
    
    # Prepare permission data for template
    user_permissions = []
    for perm_name, label, description in permissions:
        user_permissions.append({
            'name': perm_name,
            'label': label,
            'description': description,
            'enabled': getattr(user, perm_name, False)
        })
    
    context = {
        'target_user': user,
        'permissions': user_permissions,
    }
    return render(request, 'core/user_permissions_detail.html', context)


@login_required
@require_management_or_admin
def toggle_user_permission(request):
    """AJAX endpoint to toggle a specific permission"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        permission = request.POST.get('permission')
        
        try:
            user = CustomUser.objects.get(id=user_id, role='project_user')
            current_value = getattr(user, permission, False)
            setattr(user, permission, not current_value)
            user.save()
            
            return JsonResponse({
                'success': True,
                'new_value': not current_value,
                'message': f'Permission {permission} {"enabled" if not current_value else "disabled"} for {user.username}'
            })
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# ============================
# Notification Views
# ============================

@login_required
def notification_list(request):
    """List user's notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Separate unread and read notifications
    unread_notifications = notifications.filter(is_read=False)
    read_notifications = notifications.filter(is_read=True)[:20]  # Limit read notifications
    
    context = {
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications,
        'total_unread': unread_notifications.count()
    }
    return render(request, 'core/notification_list.html', context)


@login_required
def notification_count(request):
    """Get unread notification count for AJAX requests"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def mark_notification_read(request, pk):
    """Mark a specific notification as read"""
    try:
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            # Redirect to the notification's target URL
            return redirect(notification.get_url())
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        else:
            messages.error(request, 'Error marking notification as read')
            return redirect('core:notification_list')


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            messages.success(request, 'All notifications marked as read')
            return redirect('core:notification_list')
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def notification_dropdown(request):
    """Get recent notifications for dropdown"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    notification_data = []
    for notification in notifications:
        notification_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'url': notification.get_url()
        })
    
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    return JsonResponse({
        'notifications': notification_data,
        'unread_count': unread_count
    })
