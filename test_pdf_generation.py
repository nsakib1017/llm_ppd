import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_ppd.settings')
django.setup()

from web.models import DailyMoodCheckIn, PostpartumQuestionnaire
from django.utils import timezone

print("Testing PDF generation with JSON format...")
print("-" * 70)

# Show current record counts
mood_count_before = DailyMoodCheckIn.objects.count()
quest_count_before = PostpartumQuestionnaire.objects.count()

print(f"\nCurrent database state:")
print(f"   - DailyMoodCheckIn records: {mood_count_before}")
print(f"   - PostpartumQuestionnaire records: {quest_count_before}")

# Test 1: Create a DailyMoodCheckIn entry
print("\n1. Creating a new DailyMoodCheckIn entry...")
mood_checkin = DailyMoodCheckIn.objects.create(
    user_identifier="test_user_001",
    mood_rating=7,
    mood_description="Feeling better today, more energy than yesterday.",
    hours_of_sleep="5_6",
    baby_wake_count="2_3",
    energy_level="good",
    stress_level="slightly_stressed",
    intrusive_thoughts="mild",
    notes="Had a good conversation with my partner about sharing responsibilities."
)
print(f"   [OK] Created DailyMoodCheckIn with ID: {mood_checkin.id}")
print(f"   [OK] This should regenerate daily_mood_checking_all_records.pdf")
print(f"        with ALL {DailyMoodCheckIn.objects.count()} mood check-in records")

# Test 2: Create a PostpartumQuestionnaire entry
print("\n2. Creating a new PostpartumQuestionnaire entry...")
questionnaire = PostpartumQuestionnaire.objects.create(
    user_identifier="test_user_001",
    q1_interest_pleasure=1,
    q2_depressed_hopeless=2,
    q3_anxious_worried=2,
    q4_irritable_angry=1,
    q5_difficulty_enjoying_motherhood=1,
    q6_thoughts_not_good_mother=2,
    q7_thoughts_harming_self=0,
    q8_sleep_when_baby_sleeps=2,
    q9_worried_baby_health=2,
    q10_physically_exhausted=2,
    q11_relationship_partner=1,
    q12_emotional_support=1,
    q13_confide_in_someone=1,
    q14_depression_before_pregnancy=0,
    q15_depression_during_pregnancy=0,
    q16_family_history_mental_illness=0,
    q17_experienced_abuse=0,
    q18_unplanned_pregnancy=0,
    q19_delivery_complications=0,
    q20_baby_health_problems=0
)
print(f"   [OK] Created PostpartumQuestionnaire with ID: {questionnaire.id}")
print(f"   [OK] Total Score: {questionnaire.total_score}")
print(f"   [OK] Risk Level: {questionnaire.risk_level}")
print(f"   [OK] This should regenerate postpartum_questionnaire_all_records.pdf")
print(f"        with ALL {PostpartumQuestionnaire.objects.count()} questionnaire records")

# Check if PDFs were created
pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'data', 'pdfs')
print(f"\n3. Checking PDF directory: {pdf_dir}")

if os.path.exists(pdf_dir):
    # Look for the specific all_records PDFs
    expected_files = [
        'daily_mood_checking_all_records.pdf',
        'postpartum_questionnaire_all_records.pdf'
    ]

    print(f"\n   Expected PDF files:")
    for filename in expected_files:
        file_path = os.path.join(pdf_dir, filename)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            mod_time = os.path.getmtime(file_path)
            from datetime import datetime
            mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   [OK] {filename}")
            print(f"        Size: {file_size:,} bytes")
            print(f"        Last modified: {mod_time_str}")
        else:
            print(f"   [MISSING] {filename}")

    print(f"\n   All files in directory:")
    all_files = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
    for pdf_file in all_files:
        file_path = os.path.join(pdf_dir, pdf_file)
        file_size = os.path.getsize(file_path)
        print(f"     - {pdf_file} ({file_size:,} bytes)")
else:
    print(f"   [ERROR] PDF directory does not exist yet")

print("\n" + "-" * 70)
print("Test complete!")
print("\nNOTE: Each PDF now contains ALL records from its respective table in JSON format.")
print("      Every time a new record is added, the entire PDF is regenerated with all data.")
