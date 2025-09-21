from django import forms
from django.contrib.auth import get_user_model
from .models import Project, Event, Decision, Deliverable, Invitation

User = get_user_model()


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects"""
    
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter project name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'Describe the project objectives and scope'
            })
        }


class EventForm(forms.ModelForm):
    """Form for creating and editing events"""
    
    class Meta:
        model = Event
        fields = ['project', 'title', 'description', 'agenda', 'start_time', 'end_time', 'venue', 'participants', 'linked_events']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter event title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Describe the event purpose and goals'
            }),
            'agenda': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'Enter meeting agenda items'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'datetime-local'
            }),
            'venue': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter venue location'
            }),
            'participants': forms.CheckboxSelectMultiple(attrs={
                'class': 'mt-1'
            }),
            'linked_events': forms.CheckboxSelectMultiple(attrs={
                'class': 'mt-1'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Make agenda required for all users
        self.fields['agenda'].required = True
        self.fields['agenda'].help_text = "Outline the agenda items and topics to be discussed in this event"
        
        # Set up linked events field
        self.fields['linked_events'].required = False
        self.fields['linked_events'].help_text = "Select previous events that this event is related to or follows up on"
        
        if user:
            if user.is_admin:
                # Admin can see all projects and events
                self.fields['project'].queryset = Project.objects.all()
                self.fields['participants'].queryset = User.objects.all()
                linked_events_queryset = Event.objects.all().order_by('-start_time')
            elif user.is_management:
                # Management can only see their projects and events
                self.fields['project'].queryset = Project.objects.filter(created_by=user)
                self.fields['project'].required = True
                self.fields['project'].help_text = "Select the project this event belongs to"
                self.fields['participants'].queryset = User.objects.all()
                linked_events_queryset = Event.objects.filter(project__created_by=user).order_by('-start_time')
            else:
                # Project users can see projects and events they participate in
                self.fields['project'].queryset = Project.objects.filter(
                    events__participants=user
                ).distinct()
                self.fields['participants'].queryset = User.objects.all()
                linked_events_queryset = Event.objects.filter(participants=user).order_by('-start_time')
            
            # Exclude current event if editing (avoid self-reference)
            if self.instance and self.instance.pk:
                linked_events_queryset = linked_events_queryset.exclude(pk=self.instance.pk)
            
            self.fields['linked_events'].queryset = linked_events_queryset


class DecisionForm(forms.ModelForm):
    """Form for creating and editing decisions"""
    
    class Meta:
        model = Decision
        fields = ['event', 'title', 'description']
        widgets = {
            'event': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter decision title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'Describe the decision details and rationale'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_admin:
                self.fields['event'].queryset = Event.objects.all()
            elif user.is_management:
                self.fields['event'].queryset = Event.objects.filter(project__created_by=user)
            else:
                self.fields['event'].queryset = Event.objects.filter(
                    participants=user
                ).distinct()


class DeliverableForm(forms.ModelForm):
    """Form for creating and editing deliverables"""
    
    decision = forms.ModelChoiceField(
        queryset=Decision.objects.all(),
        required=False,
        empty_label="No related decision",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    
    class Meta:
        model = Deliverable
        fields = ['decision', 'title', 'description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter deliverable title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Describe the deliverable requirements'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        event_id = kwargs.pop('event_id', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_admin:
                base_decision_queryset = Decision.objects.all()
                self.fields['assigned_to'].queryset = User.objects.all()
            elif user.is_management:
                base_decision_queryset = Decision.objects.filter(
                    event__project__created_by=user
                )
                self.fields['assigned_to'].queryset = User.objects.all()
            else:
                # Project users can only see decisions from events they participate in
                base_decision_queryset = Decision.objects.filter(
                    event__participants=user
                )
                self.fields['assigned_to'].queryset = User.objects.filter(
                    is_project_user=True
                )
            
            # If event_id is provided, show decisions from that event but keep it optional
            if event_id:
                try:
                    event = Event.objects.get(pk=event_id)
                    # Filter decisions to those from the specific event, but keep the field optional
                    event_decisions = base_decision_queryset.filter(event=event)
                    self.fields['decision'].queryset = event_decisions
                    # Update the empty label to be more specific
                    self.fields['decision'].empty_label = f"No decision from {event.title}"
                except Event.DoesNotExist:
                    self.fields['decision'].queryset = base_decision_queryset
            else:
                self.fields['decision'].queryset = base_decision_queryset


class DeliverableProgressForm(forms.ModelForm):
    """Form for updating deliverable progress (used by assigned users)"""
    
    class Meta:
        model = Deliverable
        fields = ['progress', 'notes', 'status']
        widgets = {
            'progress': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'min': '0',
                'max': '100',
                'placeholder': '0-100'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Add progress notes or updates'
            }),
            'status': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            })
        }


class InvitationForm(forms.ModelForm):
    """Form for creating event invitations"""
    
    class Meta:
        model = Invitation
        fields = ['event', 'invitee', 'message']
        widgets = {
            'event': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'invitee': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'message': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Optional invitation message'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_admin:
                self.fields['event'].queryset = Event.objects.all()
            elif user.is_management:
                self.fields['event'].queryset = Event.objects.filter(
                    project__created_by=user
                )
            else:
                self.fields['event'].queryset = Event.objects.filter(
                    organizer=user
                )
            
            self.fields['invitee'].queryset = User.objects.exclude(id=user.id)


class InvitationResponseForm(forms.ModelForm):
    """Form for responding to invitations"""
    
    class Meta:
        model = Invitation
        fields = ['status']
        widgets = {
            'status': forms.RadioSelect(choices=[
                ('accepted', 'Accept'),
                ('declined', 'Decline')
            ])
        }