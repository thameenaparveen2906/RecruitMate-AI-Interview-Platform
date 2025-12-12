from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import InterviewSession, InterviewQuestion, InterviewAnswer, InterviewResult
from jobs.models import JobDescription
from candidates.models import Candidate
from dashboard.services import GeminiService, ResumeParser

@login_required
def interview_list_view(request):
    """List all interviews (completed sessions with candidates)"""
    filter_status = request.GET.get('filter', 'all')
    
    sessions = InterviewSession.objects.filter(user=request.user).exclude(status='pending')
    
    if filter_status == 'completed':
        sessions = sessions.filter(status='completed')
    elif filter_status == 'in_progress':
        sessions = sessions.filter(status='in_progress')
    
    return render(request, 'interviews/interviews_page.html', {
        'sessions': sessions,
        'total_count': sessions.count(),
        'filter': filter_status
    })

@login_required
def interview_links_view(request):
    """List all interview links"""
    from django.db.models import Count, Q
    
    # Get only master sessions (ones without candidate info)
    sessions = InterviewSession.objects.filter(
        user=request.user,
        candidate_name='',
        candidate_email='',
        master_token__isnull=True  # Master sessions don't have a master_token
    ).prefetch_related('questions').annotate(
        candidate_sessions_count=Count(
            'id',
            filter=Q(
                user=request.user,
                candidate_name__isnull=False
            )
        )
    )
    
    # For each session, get the count of candidate sessions linked to this master
    for session in sessions:
        session.candidate_sessions = InterviewSession.objects.filter(
            master_token=session.token,
            user=request.user
        )
    
    return render(request, 'interviews/interview_links.html', {'sessions': sessions})

@login_required
def interview_create_view(request):
    """Create new interview session"""
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        candidate_id = request.POST.get('candidate_id')
        num_questions = int(request.POST.get('num_questions', 10))
        difficulty_level = request.POST.get('difficulty_level', 'mixed')
        
        job = get_object_or_404(JobDescription, pk=job_id, user=request.user)
        
        # Candidate is optional - can be None for public interview links
        candidate = None
        if candidate_id:
            candidate = get_object_or_404(Candidate, pk=candidate_id)
        
        # Create session
        session = InterviewSession.objects.create(
            user=request.user,
            job=job,
            candidate=candidate,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # Process custom mandatory questions first
        custom_question_ids = request.POST.getlist('custom_question_id')
        custom_questions_count = 0
        
        for q_id in custom_question_ids:
            question_text = request.POST.get(f'custom_question_text_{q_id}')
            question_type = request.POST.get(f'custom_question_type_{q_id}', 'technical')
            question_difficulty = request.POST.get(f'custom_question_difficulty_{q_id}', 'medium')
            
            if question_text:
                InterviewQuestion.objects.create(
                    session=session,
                    question_text=question_text,
                    question_type=question_type,
                    difficulty=question_difficulty,
                    expected_key_points=[],
                    order=custom_questions_count + 1,
                    is_mandatory=True,
                    is_custom=True
                )
                custom_questions_count += 1
        
        # Adjust AI-generated questions count
        ai_questions_count = num_questions - custom_questions_count
        
        if ai_questions_count > 0:
            # Generate questions using Gemini AI
            ai_service = GeminiService()
            resume_parser = ResumeParser()
            
            # Parse resume if candidate is selected and has a resume
            resume_text = "General candidate profile - will be filled when candidate registers"
            if candidate:
                if candidate.resume_file:
                    # Parse the uploaded resume file
                    parsed_resume = resume_parser.parse_resume(candidate.resume_file)
                    resume_text = f"""
Candidate: {candidate.name}
Email: {candidate.email}
Phone: {candidate.phone or 'Not provided'}
Experience: {parsed_resume.get('experience_years', 'Not specified')} years
Skills: {', '.join(parsed_resume.get('skills', candidate.skills))}

Resume Content:
{parsed_resume.get('full_text', 'Resume content not available')}
"""
                else:
                    # Fallback to basic candidate info
                    resume_text = f"""
Candidate: {candidate.name}
Email: {candidate.email}
Phone: {candidate.phone or 'Not provided'}
Skills: {', '.join(candidate.skills)}
Experience: {candidate.experience_years or 'Not specified'} years
"""
            
            # Add difficulty level to the prompt
            difficulty_instruction = ""
            if difficulty_level == 'easy':
                difficulty_instruction = "Generate EASY level questions suitable for entry-level candidates."
            elif difficulty_level == 'medium':
                difficulty_instruction = "Generate MEDIUM level questions suitable for intermediate candidates."
            elif difficulty_level == 'hard':
                difficulty_instruction = "Generate HARD level questions suitable for advanced candidates."
            else:
                difficulty_instruction = "Generate a MIX of easy, medium, and hard questions."
            
            job_context = f"""
Job Title: {job.title}

Job Description:
{job.description}

Requirements:
{job.requirements}

Difficulty Level: {difficulty_instruction}
"""
            
            questions_data = ai_service.generate_questions(
                job_context,
                resume_text,
                ai_questions_count
            )
            
            # Save AI-generated questions
            for idx, q_data in enumerate(questions_data):
                # Override difficulty if specific level selected
                if difficulty_level != 'mixed':
                    q_difficulty = difficulty_level
                else:
                    q_difficulty = q_data.get('difficulty', 'medium')
                
                InterviewQuestion.objects.create(
                    session=session,
                    question_text=q_data.get('question', ''),
                    question_type=q_data.get('type', 'technical'),
                    difficulty=q_difficulty,
                    expected_key_points=q_data.get('expected_key_points', []),
                    order=custom_questions_count + idx + 1,
                    is_mandatory=False,
                    is_custom=False
                )
        
        messages.success(request, 'Interview link created successfully! Share the link with candidates.')
        return redirect('interviews:detail', pk=session.pk)
    
    jobs = JobDescription.objects.filter(user=request.user, is_active=True)
    candidates = Candidate.objects.all()
    return render(request, 'interviews/interview_create.html', {
        'jobs': jobs,
        'candidates': candidates
    })

@login_required
def interview_detail_view(request, pk):
    """View interview session details"""
    session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
    
    questions = session.questions.all()
    answers = session.answers.all()
    
    return render(request, 'interviews/interview_detail.html', {
        'session': session,
        'questions': questions,
        'answers': answers
    })

@login_required
def interview_toggle_status_view(request, pk):
    """Toggle interview link active/inactive status"""
    if request.method == 'POST':
        session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
        action = request.POST.get('action')
        
        if action == 'deactivate':
            session.status = 'abandoned'
            session.save()
            messages.success(request, 'Interview link deactivated')
        elif action == 'activate':
            session.status = 'pending'
            session.save()
            messages.success(request, 'Interview link activated')
    
    return redirect('interviews:links')

@login_required
def interview_delete_view(request, pk):
    """Delete interview link"""
    if request.method == 'POST':
        session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
        session.delete()
        messages.success(request, 'Interview link deleted successfully')
    
    return redirect('interviews:links')

@login_required
def interview_edit_view(request, pk):
    """Edit interview link settings"""
    session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
    
    if request.method == 'POST':
        num_questions = request.POST.get('num_questions')
        duration = request.POST.get('duration')
        difficulty = request.POST.get('difficulty')
        
        # Update session settings (you can add these fields to the model if needed)
        # For now, just show success message
        messages.success(request, 'Interview link updated successfully')
        return redirect('interviews:links')
    
    return redirect('interviews:links')

@login_required
def interview_candidates_view(request, pk):
    """View all candidates who took this interview"""
    session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
    
    # Get all candidate sessions linked to this master session
    candidate_sessions = InterviewSession.objects.filter(
        master_token=session.token,
        user=request.user
    ).select_related('result').order_by('-started_at')
    
    # Calculate stats
    total_candidates = candidate_sessions.count()
    completed_count = candidate_sessions.filter(status='completed').count()
    in_progress_count = candidate_sessions.filter(status='in_progress').count()
    abandoned_count = candidate_sessions.filter(status='abandoned').count()
    
    return render(request, 'interviews/interview_candidates.html', {
        'session': session,
        'candidates': candidate_sessions,
        'total_candidates': total_candidates,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'abandoned_count': abandoned_count
    })

def interview_take_view(request, token):
    """Candidate takes interview (public view)"""
    # Get the master session (the interview link)
    master_session = get_object_or_404(InterviewSession, token=token)

    # Check if expired or deactivated
    if timezone.now() > master_session.expires_at or master_session.status == 'abandoned':
        return render(request, 'interviews/interview_expired.html')

    # Check if candidate info is in session
    candidate_session_id = request.session.get(f'candidate_session_{token}')

    if candidate_session_id:
        # Get existing candidate session
        try:
            session = InterviewSession.objects.get(pk=candidate_session_id)
        except InterviewSession.DoesNotExist:
            del request.session[f'candidate_session_{token}']
            return redirect('interviews:take', token=token)
    else:
        # Show registration form
        if request.method == 'POST' and 'candidate_name' in request.POST:

            # Resume must be uploaded
            resume_file = request.FILES.get('candidate_resume_file')
            if not resume_file:
                return render(request, 'interviews/interview_register.html', {
                    'session': master_session,
                    'error': 'Please upload your resume to continue.'
                })

            # Create candidate session
            import uuid
            session = InterviewSession.objects.create(
                user=master_session.user,
                job=master_session.job,
                token=uuid.uuid4(),
                candidate_name=request.POST.get('candidate_name'),
                candidate_email=request.POST.get('candidate_email'),
                candidate_phone=request.POST.get('candidate_phone'),
                candidate_resume_file=resume_file,
                status='in_progress',
                started_at=timezone.now(),
                expires_at=master_session.expires_at,
                master_token=master_session.token
            )

            # Parse resume (only for storing in DB or reporting)
            resume_parser = ResumeParser()
            parsed_resume = resume_parser.parse_resume(resume_file)

            # --- FIX APPLIED HERE ---
            # Copy original master questions WITHOUT regenerating

            master_questions = master_session.questions.all()

            # First copy custom/mandatory questions
            custom_count = 0
            custom_questions = master_questions.filter(is_custom=True, is_mandatory=True)

            for q in custom_questions:
                InterviewQuestion.objects.create(
                    session=session,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    difficulty=q.difficulty,
                    expected_key_points=q.expected_key_points,
                    order=custom_count + 1,
                    is_mandatory=True,
                    is_custom=True
                )
                custom_count += 1

            # Then copy AI-generated questions EXACTLY as they were created
            ai_questions = master_questions.filter(is_custom=False)

            for q in ai_questions:
                InterviewQuestion.objects.create(
                    session=session,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    difficulty=q.difficulty,
                    expected_key_points=q.expected_key_points,
                    order=custom_count + q.order,
                    is_mandatory=False,
                    is_custom=False
                )

            # --------------------------------------

            # Save session ID
            request.session[f'candidate_session_{token}'] = session.pk
            return redirect('interviews:take', token=token)

        else:
            return render(request, 'interviews/interview_register.html', {
                'session': master_session
            })

    # If completed
    if session.status == 'completed':
        return render(request, 'interviews/interview_completed.html', {'session': session})

    questions = session.questions.all()
    answered_questions = session.answers.values_list('question_id', flat=True)

    # Next unanswered question
    next_question = questions.exclude(id__in=answered_questions).first()

    if request.method == 'POST' and next_question and 'answer' in request.POST:
        answer_text = request.POST.get('answer')

        # Evaluate with AI
        ai_service = GeminiService()
        evaluation = ai_service.evaluate_answer(
            next_question.question_text,
            answer_text,
            next_question.expected_key_points
        )

        # Save answer
        InterviewAnswer.objects.create(
            session=session,
            question=next_question,
            answer_text=answer_text,
            score=evaluation.get('score', 0),
            feedback=evaluation.get('feedback', ''),
            strengths=evaluation.get('strengths', []),
            improvements=evaluation.get('improvements', [])
        )

        # If finished
        if session.answers.count() >= questions.count():
            answers_data = [
                {
                    'question': a.question.question_text,
                    'answer': a.answer_text,
                    'score': a.score,
                    'feedback': a.feedback
                }
                for a in session.answers.all()
            ]

            avg_score = sum(a.score for a in session.answers.all()) / session.answers.count()

            report = ai_service.generate_report({
                'candidate_name': session.candidate_name or 'Anonymous',
                'position': session.job.title,
                'total_questions': questions.count(),
                'average_score': avg_score,
                'answers': answers_data
            })

            # Save final result
            InterviewResult.objects.create(
                session=session,
                overall_score=report.get('overall_score', int(avg_score)),
                summary=report.get('summary', ''),
                strengths=report.get('strengths', []),
                weaknesses=report.get('weaknesses', []),
                recommendation=report.get('recommendation', 'maybe'),
                detailed_feedback=report.get('detailed_feedback', '')
            )

            session.status = 'completed'
            session.completed_at = timezone.now()
            session.save()

            return redirect('interviews:take', token=token)

        return redirect('interviews:take', token=token)

    return render(request, 'interviews/interview_take.html', {
        'session': session,
        'question': next_question,
        'progress': {
            'answered': session.answers.count(),
            'total': questions.count()
        }
    })

@login_required
def interview_results_view(request, pk):
    """View interview results"""
    session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
    
    if session.status != 'completed':
        messages.warning(request, 'Interview not yet completed')
        return redirect('interviews:detail', pk=pk)
    
    result = session.result
    answers = session.answers.all()
    
    return render(request, 'interviews/interview_results.html', {
        'session': session,
        'result': result,
        'answers': answers
    })

