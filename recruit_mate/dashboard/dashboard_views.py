from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from interviews.models import InterviewSession
from candidates.models import Candidate
from jobs.models import JobDescription

@login_required
def dashboard_view(request):
    """Main dashboard view"""
    sessions = InterviewSession.objects.filter(user=request.user)
    
    # Calculate stats
    total_interviews = sessions.count()
    completed = sessions.filter(status='completed').count()
    in_progress = sessions.filter(status='in_progress').count()
    total_candidates = Candidate.objects.count()
    total_jobs = JobDescription.objects.filter(user=request.user).count()
    
    # Calculate average score
    completed_sessions = sessions.filter(status='completed', result__isnull=False)
    avg_score = 0
    if completed_sessions.exists():
        scores = [s.result.overall_score for s in completed_sessions]
        avg_score = sum(scores) / len(scores)
    
    completion_rate = (completed / total_interviews * 100) if total_interviews > 0 else 0
    
    # Recent sessions
    recent_sessions = sessions.order_by('-created_at')[:5]
    
    context = {
        'stats': {
            'total_interviews': total_interviews,
            'completed': completed,
            'in_progress': in_progress,
            'avg_score': round(avg_score, 1),
            'total_candidates': total_candidates,
            'total_jobs': total_jobs,
            'completion_rate': round(completion_rate, 1),
        },
        'recent_sessions': recent_sessions,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
