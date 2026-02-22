from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DailyMoodCheckIn, PostpartumQuestionnaire
from .pdf_generator import regenerate_all_pdfs


@receiver(post_save, sender=DailyMoodCheckIn)
def update_mood_checkin_pdf(sender, instance, created, **kwargs):
    """Regenerate the complete DailyMoodCheckIn PDF when any row is added"""
    if created:
        regenerate_all_pdfs()


@receiver(post_save, sender=PostpartumQuestionnaire)
def update_questionnaire_pdf(sender, instance, created, **kwargs):
    """Regenerate the complete PostpartumQuestionnaire PDF when any row is added"""
    if created:
        regenerate_all_pdfs()
