from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Project(models.Model):
    """Project model for organizing events"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='created_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class Event(models.Model):
    """Event model for meetings and sessions"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField()
    agenda = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    venue = models.CharField(max_length=255)
    organizer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="organized_events"
    )
    participants = models.ManyToManyField(
        User, 
        related_name="events_participated",
        blank=True
    )
    # Link to previous events for reference
    linked_events = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='related_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.project.name}"
    
    def has_conflicts(self):
        """Check if this event conflicts with other events"""
        conflicting_events = Event.objects.filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)
        
        return conflicting_events.exists()
    
    def get_conflicting_events(self):
        """Get list of conflicting events"""
        return Event.objects.filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)
    
    class Meta:
        ordering = ['-start_time']


class Decision(models.Model):
    """Decision model for event outcomes"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='decisions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.event.title}"
    
    class Meta:
        ordering = ['-created_at']


class Deliverable(models.Model):
    """Deliverable model for tasks assigned from decisions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed')
    ]
    
    decision = models.ForeignKey(
        Decision, 
        on_delete=models.CASCADE, 
        related_name='deliverables',
        null=True, 
        blank=True,
        help_text="Optional: Link to a related decision"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='assigned_deliverables'
    )
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending'
    )
    due_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.username}"
    
    @property
    def is_overdue(self):
        """Check if deliverable is overdue"""
        if self.due_date and self.status != 'completed':
            from django.utils import timezone
            return timezone.now() > self.due_date
        return False
    
    class Meta:
        ordering = ['-created_at']


class Invitation(models.Model):
    """Invitation model for event participation"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='invitations')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending'
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations'
    )
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.event.title} - {self.invitee.username} ({self.status})"
    
    class Meta:
        unique_together = ['event', 'invitee']
        ordering = ['-created_at']


class EventLink(models.Model):
    """Model to link events for reference purposes"""
    source_event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='outgoing_links'
    )
    target_event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='incoming_links'
    )
    link_type = models.CharField(
        max_length=50,
        choices=[
            ('follow_up', 'Follow Up'),
            ('reference', 'Reference'),
            ('continuation', 'Continuation'),
        ],
        default='reference'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.source_event.title} -> {self.target_event.title}"
    
    class Meta:
        unique_together = ['source_event', 'target_event']


class Notification(models.Model):
    """Notification model for user notifications"""
    
    TYPE_CHOICES = [
        ('event_invitation', 'Event Invitation'),
        ('invitation_response', 'Invitation Response'),
        ('event_update', 'Event Update'),
        ('decision_created', 'Decision Created'),
        ('deliverable_assigned', 'Deliverable Assigned'),
        ('deliverable_due', 'Deliverable Due Soon'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    
    # Related objects for context
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    decision = models.ForeignKey(Decision, on_delete=models.CASCADE, null=True, blank=True)
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, null=True, blank=True)
    invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"
    
    def get_url(self):
        """Get the URL to navigate to when notification is clicked"""
        if self.event:
            return f"/core/events/{self.event.pk}/"
        elif self.decision:
            return f"/core/decisions/{self.decision.pk}/"
        elif self.deliverable:
            return f"/core/deliverables/{self.deliverable.pk}/"
        elif self.invitation:
            return f"/core/invitations/"
        return "#"
    
    class Meta:
        ordering = ['-created_at']
