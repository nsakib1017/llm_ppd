from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from .models import PostpartumQuestionnaire, DailyMoodCheckIn
from django.views.decorators.http import require_http_methods
import json

from .rag.pipeline import generate_ai_reply
from .rag.llm import call_featherless



from .rag.pipeline import generate_ai_reply

SESSION_KEY = "chat_messages"
LAST_SOURCES_KEY = "last_rag_sources"


def _get_messages(request):
    msgs = request.session.get(SESSION_KEY, [])
    if not isinstance(msgs, list):
        return []
    # keep only valid items
    cleaned = []
    for m in msgs:
        if isinstance(m, dict) and "role" in m and "content" in m:
            cleaned.append({"role": m["role"], "content": m["content"]})
    return cleaned


def _set_messages(request, msgs):
    request.session[SESSION_KEY] = msgs
    request.session.modified = True


@require_http_methods(["GET", "POST"])
def chat(request):
    messages = _get_messages(request)
    error = None
    sources = request.session.get(LAST_SOURCES_KEY, [])

    if request.method == "POST":
        user_text = (request.POST.get("message") or "").strip()
        if not user_text:
            return redirect("chat")

        # 1) add user turn
        messages.append({"role": "user", "content": user_text})
        _set_messages(request, messages)

        try:
            # 2) build chat history excluding system; your generate_ai_reply adds system itself
            # include everything so far (user/assistant). If you prefer, you can limit history length.
            chat_history = [m for m in messages if m["role"] in ("user", "assistant")]

            # 3) call your RAG pipeline
            reply, rag_results = generate_ai_reply(user_text=user_text, chat_history=chat_history[:-1], k=5)
            # Note: chat_history[:-1] excludes the latest user message because generate_ai_reply
            # appends the current user_text itself. (Avoid duplicating it.)

            # 4) add assistant turn
            messages.append({"role": "assistant", "content": reply})
            _set_messages(request, messages)

            # 5) store latest sources for display
            request.session[LAST_SOURCES_KEY] = rag_results
            request.session.modified = True

            return redirect("chat")

        except Exception as e:
            error = str(e)

    return render(request, "chat.html", {
        "messages": messages,
        "error": error,
        "sources": sources,   # latest RAG results (optional UI)
    })


@require_http_methods(["POST"])
def chat_clear(request):
    request.session[SESSION_KEY] = []
    request.session[LAST_SOURCES_KEY] = []
    request.session.modified = True
    return redirect("chat")

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
    from datetime import datetime, timedelta
    from django.db.models import Avg

    # Get all questionnaires
    questionnaires = PostpartumQuestionnaire.objects.all().order_by('-created_at')[:10]

    # Get all daily check-ins
    daily_checkins = DailyMoodCheckIn.objects.all().order_by('-created_at')[:30]

    # Get latest questionnaire for risk level
    latest_questionnaire = questionnaires.first() if questionnaires.exists() else None

    # Calculate average mood if data exists
    avg_mood = None
    if daily_checkins.exists():
        total_mood = sum([checkin.mood_rating for checkin in daily_checkins])
        avg_mood = round(total_mood / len(daily_checkins), 1)

    # Weekly data for charts (last 7 days)
    today = datetime.now().date()
    week_ago = today - timedelta(days=6)
    weekly_checkins = DailyMoodCheckIn.objects.filter(
        created_at__date__gte=week_ago
    ).order_by('created_at')

    weekly_chart_data = []
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    for i in range(7):
        day = week_ago + timedelta(days=i)
        day_checkins = [c for c in weekly_checkins if c.created_at.date() == day]

        if day_checkins:
            avg_mood_day = sum(c.mood_rating for c in day_checkins) / len(day_checkins)
            sleep_val = day_checkins[0].get_hours_of_sleep_display() if day_checkins else ''

            weekly_chart_data.append({
                'day': day_names[day.weekday()],
                'mood': round(avg_mood_day, 1),
                'sleep': sleep_val
            })
        else:
            weekly_chart_data.append({
                'day': day_names[day.weekday()],
                'mood': 0,
                'sleep': ''
            })

    # Monthly data (last 4 weeks)
    monthly_chart_data = []
    for week_num in range(4):
        week_start = today - timedelta(days=(week_num + 1) * 7)
        week_end = week_start + timedelta(days=6)

        week_checkins = DailyMoodCheckIn.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end
        )

        if week_checkins.exists():
            avg = week_checkins.aggregate(Avg('mood_rating'))['mood_rating__avg']
            monthly_chart_data.insert(0, {
                'week': f'Week {4-week_num}',
                'avg_mood': round(avg, 1) if avg else 0
            })
        else:
            monthly_chart_data.insert(0, {
                'week': f'Week {4-week_num}',
                'avg_mood': 0
            })

    # Today's mood
    today_checkin = DailyMoodCheckIn.objects.filter(created_at__date=today).first()
    today_mood = today_checkin.mood_rating if today_checkin else None

    # Calculate weekly average
    weekly_avg = None
    if weekly_checkins.exists():
        weekly_avg = round(sum(c.mood_rating for c in weekly_checkins) / len(weekly_checkins), 1)

    # Mood trend
    mood_trend = "No data"
    if len(weekly_chart_data) >= 2 and weekly_chart_data[-1]['mood'] > 0:
        if weekly_chart_data[-1]['mood'] > weekly_chart_data[-2]['mood']:
            mood_trend = "↑ improving"
        elif weekly_chart_data[-1]['mood'] < weekly_chart_data[-2]['mood']:
            mood_trend = "↓ declining"
        else:
            mood_trend = "→ stable"

    context = {
        'questionnaires': questionnaires,
        'daily_checkins': daily_checkins,
        'latest_questionnaire': latest_questionnaire,
        'avg_mood': avg_mood,
        'weekly_chart_data': json.dumps(weekly_chart_data),
        'monthly_chart_data': json.dumps(monthly_chart_data),
        'today_mood': today_mood,
        'weekly_avg': weekly_avg,
        'mood_trend': mood_trend
    }

    return render(request, 'history.html', context)



def daily_checkin(request):
    """Daily mood and sleep check-in"""
    if request.method == 'POST':
        try:
            # Create daily check-in instance from form data
            checkin = DailyMoodCheckIn(
                mood_rating=int(request.POST.get('mood_rating')),
                mood_description=request.POST.get('mood_description', ''),
                hours_of_sleep=request.POST.get('hours_of_sleep'),
                baby_wake_count=request.POST.get('baby_wake_count', ''),
                energy_level=request.POST.get('energy_level'),
                stress_level=request.POST.get('stress_level'),
                intrusive_thoughts=request.POST.get('intrusive_thoughts'),
                notes=request.POST.get('notes', '')
            )
            checkin.save()

            messages.success(request, 'Thank you for checking in today! Your data has been saved.')
            return redirect('history')

        except Exception as e:
            messages.error(request, f'Error submitting check-in: {str(e)}')

    return render(request, 'daily_checkin.html')
