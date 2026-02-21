from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from .models import PostpartumQuestionnaire, DailyMoodCheckIn
import json

def home(request):
    return render(request, 'home.html')

def consent(request):
    return render(request, 'consent.html')

def questionnaire(request):
    if request.method == 'POST':
        try:
            # Create questionnaire instance from form data
            q = PostpartumQuestionnaire(
                q1_interest_pleasure=int(request.POST.get('q1_interest_pleasure')),
                q2_depressed_hopeless=int(request.POST.get('q2_depressed_hopeless')),
                q3_anxious_worried=int(request.POST.get('q3_anxious_worried')),
                q4_irritable_angry=int(request.POST.get('q4_irritable_angry')),
                q5_difficulty_enjoying_motherhood=int(request.POST.get('q5_difficulty_enjoying_motherhood')),
                q6_thoughts_not_good_mother=int(request.POST.get('q6_thoughts_not_good_mother')),
                q7_thoughts_harming_self=int(request.POST.get('q7_thoughts_harming_self')),
                q8_sleep_when_baby_sleeps=int(request.POST.get('q8_sleep_when_baby_sleeps')),
                q9_worried_baby_health=int(request.POST.get('q9_worried_baby_health')),
                q10_physically_exhausted=int(request.POST.get('q10_physically_exhausted')),
                q11_relationship_partner=int(request.POST.get('q11_relationship_partner')),
                q12_emotional_support=int(request.POST.get('q12_emotional_support')),
                q13_confide_in_someone=int(request.POST.get('q13_confide_in_someone')),
                q14_depression_before_pregnancy=int(request.POST.get('q14_depression_before_pregnancy')),
                q15_depression_during_pregnancy=int(request.POST.get('q15_depression_during_pregnancy')),
                q16_family_history_mental_illness=int(request.POST.get('q16_family_history_mental_illness')),
                q17_experienced_abuse=int(request.POST.get('q17_experienced_abuse')),
                q18_unplanned_pregnancy=int(request.POST.get('q18_unplanned_pregnancy')),
                q19_delivery_complications=int(request.POST.get('q19_delivery_complications')),
                q20_baby_health_problems=int(request.POST.get('q20_baby_health_problems')),
            )
            q.save()

            # Store the ID in session for results page
            request.session['questionnaire_id'] = q.pk
            messages.success(request, 'Questionnaire submitted successfully!')
            return redirect('questionnaire_results', pk=q.pk)

        except Exception as e:
            messages.error(request, f'Error submitting questionnaire: {str(e)}')

    return render(request, 'questionnaire.html')

def questionnaire_results(request, pk):
    """Display results of questionnaire"""
    questionnaire = get_object_or_404(PostpartumQuestionnaire, pk=pk)

    # Generate recommendations based on risk level
    recommendations = []

    if questionnaire.risk_level == 'critical':
        recommendations = [
            'Please seek immediate professional help',
            'Contact 988 (Suicide & Crisis Lifeline)',
            'Reach out to your healthcare provider immediately',
            'Tell a trusted friend or family member how you\'re feeling',
            'Do not stay alone - ensure you have support nearby'
        ]
    elif questionnaire.risk_level == 'high':
        recommendations = [
            'Schedule an appointment with your healthcare provider within 1-2 days',
            'Consider reaching out to a mental health professional',
            'Talk to your partner or a trusted friend about how you\'re feeling',
            'Join a postpartum support group',
            'Ensure you\'re getting adequate sleep and nutrition'
        ]
    elif questionnaire.risk_level == 'moderate':
        recommendations = [
            'Schedule a check-in with your healthcare provider',
            'Consider talking to a therapist or counselor',
            'Connect with other new mothers for support',
            'Prioritize self-care and rest when possible',
            'Monitor your symptoms and track daily mood'
        ]
    else:
        recommendations = [
            'Continue monitoring your mental health',
            'Maintain healthy sleep habits when possible',
            'Stay connected with your support network',
            'Practice self-care regularly',
            'Don\'t hesitate to reach out if you notice changes in your mood'
        ]

    context = {
        'questionnaire': questionnaire,
        'recommendations': recommendations
    }

    return render(request, 'questionnaire_results.html', context)

def medication(request):
    return render(request, 'medication.html')

def history(request):
    """Display mood statistics and trends"""
    # Get all questionnaires
    questionnaires = PostpartumQuestionnaire.objects.all().order_by('-created_at')[:10]

    # Get all daily check-ins
    daily_checkins = DailyMoodCheckIn.objects.all().order_by('-created_at')[:30]

    # Calculate statistics
    mood_data = []
    for checkin in daily_checkins:
        mood_data.append({
            'date': checkin.created_at.strftime('%Y-%m-%d'),
            'mood': checkin.mood_rating,
            'stress': checkin.stress_level,
            'energy': checkin.energy_level
        })

    # Get latest questionnaire for risk level
    latest_questionnaire = questionnaires.first() if questionnaires.exists() else None

    # Calculate average mood if data exists
    avg_mood = None
    if daily_checkins.exists():
        total_mood = sum([checkin.mood_rating for checkin in daily_checkins])
        avg_mood = round(total_mood / len(daily_checkins), 1)

    context = {
        'questionnaires': questionnaires,
        'daily_checkins': daily_checkins,
        'mood_data_json': json.dumps(mood_data),
        'latest_questionnaire': latest_questionnaire,
        'avg_mood': avg_mood
    }

    return render(request, 'history.html', context)

def chat(request):
    return render(request, 'chat.html')
