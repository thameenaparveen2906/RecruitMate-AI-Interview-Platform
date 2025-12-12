from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import messages
from .models import User

def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        company = request.POST.get('company', '')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                name=name,
                company=company
            )
            login(request, user)
            return redirect('dashboard:home')
    
    return render(request, 'accounts/signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('core:home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user = request.user
        
        if action == 'update_profile':
            user.name = request.POST.get('name', '')
            user.company = request.POST.get('company', '')
            user.phone = request.POST.get('phone', '')
            user.save()
            messages.success(request, 'Profile updated successfully')
        
        elif action == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not user.check_password(old_password):
                messages.error(request, 'Current password is incorrect')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters')
            else:
                user.set_password(new_password)
                user.save()
                login(request, user)
                messages.success(request, 'Password changed successfully')
    
    return render(request, 'accounts/profile.html')
