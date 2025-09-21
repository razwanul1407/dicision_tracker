from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
import json

from .forms import CustomUserCreationForm, UserProfileForm, UserRoleUpdateForm
from .permissions import admin_required, AdminRequiredMixin

User = get_user_model()


class CustomLoginView(LoginView):
    """Custom login view"""
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard:index')


@never_cache
@csrf_protect
def custom_logout_view(request):
    """Custom logout view that handles both GET and POST requests"""
    if request.method == 'POST' or request.method == 'GET':
        # Log out the user
        logout(request)
        
        # Create response with redirect
        response = redirect('accounts:login')
        
        # Clear all relevant cookies
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')
        
        # Clear any custom cookies if they exist
        for cookie_name in request.COOKIES:
            if cookie_name not in ['sessionid', 'csrftoken']:
                response.delete_cookie(cookie_name)
        
        # Add success message
        messages.success(request, 'You have been logged out successfully.')
        
        return response
    
    # If somehow we get here with other methods, redirect to login
    return redirect('accounts:login')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.first_name}.')
            return redirect('dashboard:index')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@admin_required
def user_management(request):
    """Admin view for managing users with enhanced filtering and search"""
    users_list = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Role filtering
    role_filter = request.GET.get('role')
    if role_filter:
        users_list = users_list.filter(role=role_filter)
    
    # Pagination
    paginator = Paginator(users_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_users = User.objects.count()
    admin_count = User.objects.filter(role='admin').count()
    management_count = User.objects.filter(role='management').count()
    project_user_count = User.objects.filter(role='project_user').count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'total_users': total_users,
        'admin_count': admin_count,
        'management_count': management_count,
        'project_user_count': project_user_count,
    }
    return render(request, 'accounts/user_management.html', context)


class UserCreateView(AdminRequiredMixin, CreateView):
    """Admin view for creating users"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/user_create.html'
    success_url = reverse_lazy('accounts:user_management')
    
    def form_valid(self, form):
        messages.success(self.request, f'User "{form.instance.username}" created successfully!')
        return super().form_valid(form)


class UserRoleUpdateView(AdminRequiredMixin, UpdateView):
    """Admin view for updating user roles"""
    model = User
    form_class = UserRoleUpdateForm
    template_name = 'accounts/user_role_update.html'
    success_url = reverse_lazy('accounts:user_management')
    
    def form_valid(self, form):
        old_role = self.object.role
        new_role = form.cleaned_data['role']
        messages.success(
            self.request, 
            f'User role updated from {self.object.get_role_display()} to {dict(User.USER_ROLES)[new_role]}!'
        )
        return super().form_valid(form)


class UserDetailView(AdminRequiredMixin, DetailView):
    """Admin view for user details"""
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_obj'


@admin_required
def system_settings(request):
    """Admin view for system-wide settings"""
    if request.method == 'POST':
        # Handle settings form submission
        messages.success(request, 'System settings updated successfully!')
        return redirect('accounts:system_settings')
    
    return render(request, 'accounts/system_settings.html')


@admin_required
@require_POST
def toggle_user_status(request, user_id):
    """AJAX view to toggle user active status"""
    try:
        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body)
        activate = data.get('activate', False)
        
        user.is_active = activate
        user.save()
        
        status = 'activated' if activate else 'deactivated'
        return JsonResponse({
            'success': True,
            'message': f'User {user.username} has been {status}.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
