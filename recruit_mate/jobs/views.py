from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobDescription
from dashboard.services import GeminiService

@login_required
def job_list_view(request):
    """List all jobs for current user"""
    jobs = JobDescription.objects.filter(user=request.user)
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

@login_required
def job_create_view(request):
    """Create new job description"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        location = request.POST.get('location', '')
        employment_type = request.POST.get('employment_type', 'full-time')
        
        # Extract skills using AI
        ai_service = GeminiService()
        skills = ai_service.extract_skills(f"{description}\n\n{requirements}")
        
        job = JobDescription.objects.create(
            user=request.user,
            title=title,
            description=description,
            requirements=requirements,
            skills=skills,
            location=location,
            employment_type=employment_type
        )
        
        messages.success(request, 'Job description created successfully')
        return redirect('jobs:detail', pk=job.pk)
    
    return render(request, 'jobs/job_create.html')

@login_required
def job_detail_view(request, pk):
    """View job description details"""
    job = get_object_or_404(JobDescription, pk=pk, user=request.user)
    return render(request, 'jobs/job_detail.html', {'job': job})

@login_required
def job_edit_view(request, pk):
    """Edit job description"""
    job = get_object_or_404(JobDescription, pk=pk, user=request.user)
    
    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.description = request.POST.get('description')
        job.requirements = request.POST.get('requirements')
        job.location = request.POST.get('location', '')
        job.employment_type = request.POST.get('employment_type', 'full-time')
        
        # Re-extract skills
        ai_service = GeminiService()
        job.skills = ai_service.extract_skills(f"{job.description}\n\n{job.requirements}")
        
        job.save()
        messages.success(request, 'Job description updated successfully')
        return redirect('jobs:detail', pk=job.pk)
    
    return render(request, 'jobs/job_edit.html', {'job': job})

@login_required
def job_delete_view(request, pk):
    """Delete job description"""
    job = get_object_or_404(JobDescription, pk=pk, user=request.user)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job description deleted successfully')
        return redirect('jobs:list')
    
    return render(request, 'jobs/job_delete.html', {'job': job})
