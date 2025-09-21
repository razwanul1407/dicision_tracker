from django.contrib import admin
from .models import Project, Event, Decision, Deliverable, Invitation, EventLink


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'start_time', 'end_time', 'organizer']
    list_filter = ['project', 'start_time', 'organizer']
    search_fields = ['title', 'description', 'agenda']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['participants', 'linked_events']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'organizer')


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'created_by', 'created_at']
    list_filter = ['event__project', 'created_at', 'created_by']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'status', 'progress', 'due_date', 'is_overdue']
    list_filter = ['status', 'assigned_to', 'due_date', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['event', 'invitee', 'status', 'invited_by', 'created_at']
    list_filter = ['status', 'event__project', 'created_at']
    search_fields = ['event__title', 'invitee__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EventLink)
class EventLinkAdmin(admin.ModelAdmin):
    list_display = ['source_event', 'target_event', 'link_type', 'created_at']
    list_filter = ['link_type', 'created_at']
    search_fields = ['source_event__title', 'target_event__title']
    readonly_fields = ['created_at']
