from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from .models import Candidate
from interviews.models import InterviewSession
from .models import Candidate
from dashboard.services.resume_parser import ResumeParser


@login_required
def candidate_list_view(request):
    candidates = Candidate.objects.all()
    return render(request, 'candidates/candidate_list.html', {'candidates': candidates})

@login_required
def candidates_all_view(request):
    candidate_sessions = InterviewSession.objects.filter(
        user=request.user,
        master_token__isnull=False  
    ).exclude(
        candidate_email=''
    ).select_related('result').order_by('candidate_email', '-created_at')
    
    candidates_dict = {}
    
    for session in candidate_sessions:
        email = session.candidate_email.strip().lower() 
        
        if email not in candidates_dict:
            candidates_dict[email] = {
                'name': session.candidate_name,
                'email': session.candidate_email,  
                'phone': session.candidate_phone,
                'total_interviews': 0,
                'completed_interviews': 0,
                'latest_status': session.status,
                'best_score': None,
                'sessions': []
            }
        
        candidates_dict[email]['sessions'].append(session)
        candidates_dict[email]['total_interviews'] += 1
        
        if session.status == 'completed':
            candidates_dict[email]['completed_interviews'] += 1
        
            if session.result:
                current_best = candidates_dict[email]['best_score']
                if current_best is None or session.result.overall_score > current_best:
                    candidates_dict[email]['best_score'] = session.result.overall_score
    
    candidates_data = list(candidates_dict.values())
    
    candidates_data.sort(key=lambda x: x['name'].lower() if x['name'] else '')
    
    return render(request, 'candidates/candidates_page.html', {
        'candidates': candidates_data
    })

@login_required
def candidate_profile_view(request, email):
    interviews = InterviewSession.objects.filter(
        user=request.user,
        candidate_email=email,
        master_token__isnull=False 
    ).select_related('job', 'result').prefetch_related('questions', 'answers').order_by('-created_at')
    
    if not interviews.exists():
        messages.error(request, 'Candidate not found')
        return redirect('candidates:all')
    
    first_session = interviews.first()
    candidate = {
        'name': first_session.candidate_name,
        'email': email,
        'phone': first_session.candidate_phone,
        'resume_file': first_session.candidate_resume_file,
    }
    
    total_interviews = interviews.count()
    completed_interviews = interviews.filter(status='completed').count()
    in_progress_interviews = interviews.filter(status='in_progress').count()
    
    completed_sessions = interviews.filter(status='completed', result__isnull=False)
    average_score = None
    if completed_sessions.exists():
        scores = [s.result.overall_score for s in completed_sessions]
        average_score = int(sum(scores) / len(scores))
    
    for interview in interviews:
        if interview.status == 'completed':
            technical_answers = interview.answers.filter(question__question_type='technical')
            behavioral_answers = interview.answers.filter(question__question_type='behavioral')
            
            if technical_answers.exists():
                interview.technical_score = int(technical_answers.aggregate(Avg('score'))['score__avg'])
            else:
                interview.technical_score = None
                
            if behavioral_answers.exists():
                interview.behavioral_score = int(behavioral_answers.aggregate(Avg('score'))['score__avg'])
            else:
                interview.behavioral_score = None
    
    stats = {
        'total_interviews': total_interviews,
        'completed_interviews': completed_interviews,
        'in_progress_interviews': in_progress_interviews,
        'average_score': average_score,
    }
    
    return render(request, 'candidates/candidate_profile.html', {
        'candidate': candidate,
        'interviews': interviews,
        'stats': stats,
    })

@login_required
def interview_report_view(request, pk):
    session = get_object_or_404(
        InterviewSession, 
        pk=pk, 
        user=request.user
    )
    
    result = session.result if hasattr(session, 'result') else None
    answers = session.answers.select_related('question').order_by('question__order')
    
    technical_answers = answers.filter(question__question_type='technical')
    behavioral_answers = answers.filter(question__question_type='behavioral')
    
    technical_score = None
    behavioral_score = None
    
    if technical_answers.exists():
        technical_score = int(technical_answers.aggregate(Avg('score'))['score__avg'])
    
    if behavioral_answers.exists():
        behavioral_score = int(behavioral_answers.aggregate(Avg('score'))['score__avg'])
    
    return render(request, 'candidates/interview_report.html', {
        'session': session,
        'result': result,
        'answers': answers,
        'technical_score': technical_score,
        'behavioral_score': behavioral_score,
    })

from dashboard.services import ResumeParser

@login_required
def candidate_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        resume_file = request.FILES.get('resume')
        resume_url = request.POST.get('resume_url', '')

        candidate_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'resume_file': resume_file,
            'resume_url': resume_url
        }

        if resume_file:
            parsed_data = ResumeParser.parse_resume(resume_file)
            candidate_data.update({
                'skills': parsed_data.get('skills', []),
                'experience_years': parsed_data.get('experience_years'),
                'education': parsed_data.get('education', '')
            })

        candidate = Candidate.objects.create(**candidate_data)
        messages.success(request, 'Candidate created successfully')
        return redirect('candidates:detail', pk=candidate.pk)

    return render(request, 'candidates/candidate_create.html')


@login_required
def candidate_detail_view(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    return render(request, 'candidates/candidate_detail.html', {'candidate': candidate})

@login_required
def candidate_edit_view(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    
    if request.method == 'POST':
        candidate.name = request.POST.get('name')
        candidate.email = request.POST.get('email')
        candidate.phone = request.POST.get('phone', '')
        
        resume_file = request.FILES.get('resume')
        if resume_file:
            candidate.resume_file = resume_file
            parsed_data = ResumeParser.parse_resume(resume_file)
            candidate.skills = parsed_data.get('skills', [])
            candidate.experience_years = parsed_data.get('experience_years')
            candidate.education = parsed_data.get('education', '')

        
        candidate.save()
        messages.success(request, 'Candidate updated successfully')
        return redirect('candidates:detail', pk=candidate.pk)
    
    return render(request, 'candidates/candidate_edit.html', {'candidate': candidate})

@login_required
def candidate_delete_view(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    
    if request.method == 'POST':
        candidate.delete()
        messages.success(request, 'Candidate deleted successfully')
        return redirect('candidates:list')
    
    return render(request, 'candidates/candidate_delete.html', {'candidate': candidate})
