import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_ppd.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from web.models import DailyMoodCheckIn, PostpartumQuestionnaire
from django.utils import timezone

print("Creating dummy data...")
print("-" * 60)

# Clear existing data (optional - comment out if you want to keep existing data)
print("Clearing existing data...")
DailyMoodCheckIn.objects.all().delete()
PostpartumQuestionnaire.objects.all().delete()

# Create Daily Check-ins for the past 30 days
print("\nCreating daily check-ins for the past 30 days...")

mood_descriptions = [
    "Feeling tired but hopeful",
    "A bit anxious today",
    "Happy and energetic",
    "Overwhelmed with tasks",
    "Peaceful and content",
    "Stressed but managing",
    "Grateful for support",
    "Missing sleep",
    "Feeling positive",
    "A little down",
    "",  # Some empty descriptions
    ""
]

for days_ago in range(30):
    date = timezone.now() - timedelta(days=days_ago)

    # Create 1 check-in per day
    mood_rating = random.randint(4, 9)  # Range from 4 to 9

    checkin = DailyMoodCheckIn.objects.create(
        mood_rating=mood_rating,
        mood_description=random.choice(mood_descriptions),
        hours_of_sleep=random.choice(['less_than_3', '3_4', '4_5', '5_6', 'more_than_6']),
        baby_wake_count=random.choice(['0_1', '2_3', '4_5', '6_plus', '']),
        energy_level=random.choice(['very_low', 'low', 'moderate', 'good', 'high']),
        stress_level=random.choice(['calm', 'slightly_stressed', 'moderately_stressed', 'very_stressed', 'overwhelmed']),
        intrusive_thoughts=random.choice(['no', 'no', 'no', 'mild', 'mild']),  # Mostly "no"
        notes=f"Day {days_ago} check-in" if days_ago % 5 == 0 else ""
    )

    # Set the created_at to the specific date
    checkin.created_at = date
    checkin.save()

    print(f"[OK] Created check-in for {date.strftime('%Y-%m-%d')} - Mood: {mood_rating}/10")

print(f"\nTotal daily check-ins created: {DailyMoodCheckIn.objects.count()}")

# Create some Questionnaire responses (5 over the past month)
print("\nCreating questionnaire responses...")

questionnaire_dates = [
    timezone.now() - timedelta(days=2),
    timezone.now() - timedelta(days=7),
    timezone.now() - timedelta(days=14),
    timezone.now() - timedelta(days=21),
    timezone.now() - timedelta(days=28),
]

# Sample questionnaire data sets (from low to moderate risk)
sample_responses = [
    {  # Low risk
        'q1_interest_pleasure': 0,
        'q2_depressed_hopeless': 1,
        'q3_anxious_worried': 1,
        'q4_irritable_angry': 0,
        'q5_difficulty_enjoying_motherhood': 1,
        'q6_thoughts_not_good_mother': 1,
        'q7_thoughts_harming_self': 0,
        'q8_sleep_when_baby_sleeps': 1,
        'q9_worried_baby_health': 1,
        'q10_physically_exhausted': 2,
        'q11_relationship_partner': 0,
        'q12_emotional_support': 0,
        'q13_confide_in_someone': 0,
        'q14_depression_before_pregnancy': 0,
        'q15_depression_during_pregnancy': 0,
        'q16_family_history_mental_illness': 0,
        'q17_experienced_abuse': 0,
        'q18_unplanned_pregnancy': 0,
        'q19_delivery_complications': 0,
        'q20_baby_health_problems': 0,
    },
    {  # Moderate risk
        'q1_interest_pleasure': 2,
        'q2_depressed_hopeless': 2,
        'q3_anxious_worried': 2,
        'q4_irritable_angry': 2,
        'q5_difficulty_enjoying_motherhood': 2,
        'q6_thoughts_not_good_mother': 2,
        'q7_thoughts_harming_self': 0,
        'q8_sleep_when_baby_sleeps': 2,
        'q9_worried_baby_health': 2,
        'q10_physically_exhausted': 3,
        'q11_relationship_partner': 1,
        'q12_emotional_support': 1,
        'q13_confide_in_someone': 1,
        'q14_depression_before_pregnancy': 0,
        'q15_depression_during_pregnancy': 0,
        'q16_family_history_mental_illness': 1,
        'q17_experienced_abuse': 0,
        'q18_unplanned_pregnancy': 0,
        'q19_delivery_complications': 1,
        'q20_baby_health_problems': 0,
    },
    {  # Low-Moderate
        'q1_interest_pleasure': 1,
        'q2_depressed_hopeless': 1,
        'q3_anxious_worried': 2,
        'q4_irritable_angry': 1,
        'q5_difficulty_enjoying_motherhood': 1,
        'q6_thoughts_not_good_mother': 1,
        'q7_thoughts_harming_self': 0,
        'q8_sleep_when_baby_sleeps': 2,
        'q9_worried_baby_health': 2,
        'q10_physically_exhausted': 2,
        'q11_relationship_partner': 1,
        'q12_emotional_support': 1,
        'q13_confide_in_someone': 0,
        'q14_depression_before_pregnancy': 0,
        'q15_depression_during_pregnancy': 0,
        'q16_family_history_mental_illness': 0,
        'q17_experienced_abuse': 0,
        'q18_unplanned_pregnancy': 0,
        'q19_delivery_complications': 0,
        'q20_baby_health_problems': 0,
    },
    {  # Low risk
        'q1_interest_pleasure': 0,
        'q2_depressed_hopeless': 0,
        'q3_anxious_worried': 1,
        'q4_irritable_angry': 1,
        'q5_difficulty_enjoying_motherhood': 0,
        'q6_thoughts_not_good_mother': 0,
        'q7_thoughts_harming_self': 0,
        'q8_sleep_when_baby_sleeps': 1,
        'q9_worried_baby_health': 1,
        'q10_physically_exhausted': 2,
        'q11_relationship_partner': 0,
        'q12_emotional_support': 0,
        'q13_confide_in_someone': 0,
        'q14_depression_before_pregnancy': 0,
        'q15_depression_during_pregnancy': 0,
        'q16_family_history_mental_illness': 1,
        'q17_experienced_abuse': 0,
        'q18_unplanned_pregnancy': 0,
        'q19_delivery_complications': 0,
        'q20_baby_health_problems': 0,
    },
    {  # Moderate risk
        'q1_interest_pleasure': 2,
        'q2_depressed_hopeless': 2,
        'q3_anxious_worried': 3,
        'q4_irritable_angry': 2,
        'q5_difficulty_enjoying_motherhood': 2,
        'q6_thoughts_not_good_mother': 2,
        'q7_thoughts_harming_self': 0,
        'q8_sleep_when_baby_sleeps': 3,
        'q9_worried_baby_health': 2,
        'q10_physically_exhausted': 3,
        'q11_relationship_partner': 2,
        'q12_emotional_support': 2,
        'q13_confide_in_someone': 1,
        'q14_depression_before_pregnancy': 2,
        'q15_depression_during_pregnancy': 0,
        'q16_family_history_mental_illness': 1,
        'q17_experienced_abuse': 0,
        'q18_unplanned_pregnancy': 1,
        'q19_delivery_complications': 0,
        'q20_baby_health_problems': 0,
    },
]

for i, date in enumerate(questionnaire_dates):
    responses = sample_responses[i]

    q = PostpartumQuestionnaire.objects.create(**responses)
    q.created_at = date
    q.save()

    print(f"[OK] Created questionnaire for {date.strftime('%Y-%m-%d')} - Score: {q.total_score}/48 - Risk: {q.risk_level}")

print(f"\nTotal questionnaires created: {PostpartumQuestionnaire.objects.count()}")

print("\n" + "=" * 60)
print("✅ Dummy data creation complete!")
print("=" * 60)
print("\nYou can now view the statistics at: http://127.0.0.1:8000/history/")
print("\nData Summary:")
print(f"  • {DailyMoodCheckIn.objects.count()} daily check-ins (past 30 days)")
print(f"  • {PostpartumQuestionnaire.objects.count()} questionnaire assessments")
print("\nThe charts and statistics should now display with real data!")
