import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_ppd.settings')
django.setup()

from web.pdf_generator import regenerate_all_pdfs
from web.models import DailyMoodCheckIn, PostpartumQuestionnaire

print("Manually generating PDFs with all current records...")
print("=" * 70)

# Show current counts
mood_count = DailyMoodCheckIn.objects.count()
quest_count = PostpartumQuestionnaire.objects.count()

print(f"\nCurrent database state:")
print(f"   - DailyMoodCheckIn records: {mood_count}")
print(f"   - PostpartumQuestionnaire records: {quest_count}")

print(f"\nGenerating PDFs...")
mood_pdf, quest_pdf = regenerate_all_pdfs()

print(f"\n[OK] PDFs generated successfully!")
print(f"\n   Daily Mood Check-In PDF:")
print(f"      Path: {mood_pdf}")
print(f"      Size: {os.path.getsize(mood_pdf):,} bytes")

print(f"\n   Postpartum Questionnaire PDF:")
print(f"      Path: {quest_pdf}")
print(f"      Size: {os.path.getsize(quest_pdf):,} bytes")

print("\n" + "=" * 70)
print("Done! You can now open these PDFs to view all records in JSON format.")
