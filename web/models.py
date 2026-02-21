from django.db import models
from django.utils import timezone

# Create your models here.

class PostpartumQuestionnaire(models.Model):
    """Stores comprehensive postpartum depression screening responses"""
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    user_identifier = models.CharField(max_length=255, blank=True, null=True)

    # Section 1: Current Emotional State (Questions 1-7)
    q1_interest_pleasure = models.IntegerField(choices=[(0, 'Not at all'), (1, 'Several days'), (2, 'More than half the days'), (3, 'Nearly every day')])
    q2_depressed_hopeless = models.IntegerField(choices=[(0, 'Not at all'), (1, 'Several days'), (2, 'More than half the days'), (3, 'Nearly every day')])
    q3_anxious_worried = models.IntegerField(choices=[(0, 'Not at all'), (1, 'Several days'), (2, 'More than half the days'), (3, 'Nearly every day')])
    q4_irritable_angry = models.IntegerField(choices=[(0, 'Not at all'), (1, 'Several days'), (2, 'More than half the days'), (3, 'Nearly every day')])
    q5_difficulty_enjoying_motherhood = models.IntegerField(choices=[(0, 'Never'), (1, 'Sometimes'), (2, 'Often'), (3, 'Almost always')])
    q6_thoughts_not_good_mother = models.IntegerField(choices=[(0, 'Never'), (1, 'Sometimes'), (2, 'Often'), (3, 'Almost always')])
    q7_thoughts_harming_self = models.IntegerField(choices=[(0, 'Never'), (1, 'Rarely'), (2, 'Sometimes'), (3, 'Often')])

    # Section 2: Sleep & Anxiety Indicators (Questions 8-10)
    q8_sleep_when_baby_sleeps = models.IntegerField(choices=[(0, 'Easily'), (1, 'Sometimes'), (2, 'Rarely'), (3, 'Never')])
    q9_worried_baby_health = models.IntegerField(choices=[(0, 'Not at all'), (1, 'Sometimes'), (2, 'Often'), (3, 'Always')])
    q10_physically_exhausted = models.IntegerField(choices=[(0, 'No'), (1, 'Mild'), (2, 'Moderate'), (3, 'Severe')])

    # Section 3: Social Support & Relationships (Questions 11-13)
    q11_relationship_partner = models.IntegerField(choices=[(0, 'Very supportive'), (1, 'Somewhat supportive'), (2, 'Neutral'), (3, 'Strained')])
    q12_emotional_support = models.IntegerField(choices=[(0, 'Strong support'), (1, 'Moderate'), (2, 'Minimal'), (3, 'None')])
    q13_confide_in_someone = models.IntegerField(choices=[(0, 'Yes, always'), (1, 'Sometimes'), (2, 'Rarely'), (3, 'No')])

    # Section 4: Mental Health History (Questions 14-17)
    q14_depression_before_pregnancy = models.IntegerField(choices=[(0, 'No'), (2, 'Yes')])
    q15_depression_during_pregnancy = models.IntegerField(choices=[(0, 'No'), (2, 'Yes')])
    q16_family_history_mental_illness = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    q17_experienced_abuse = models.IntegerField(choices=[(0, 'No'), (2, 'Yes')])

    # Section 5: Pregnancy & Postpartum Factors (Questions 18-20)
    q18_unplanned_pregnancy = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    q19_delivery_complications = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    q20_baby_health_problems = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])

    # Calculated fields
    total_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical - Immediate Support Needed')
    ], default='low')

    class Meta:
        ordering = ['-created_at']

    def calculate_score(self):
        """Calculate total depression risk score"""
        self.total_score = (
            self.q1_interest_pleasure + self.q2_depressed_hopeless +
            self.q3_anxious_worried + self.q4_irritable_angry +
            self.q5_difficulty_enjoying_motherhood + self.q6_thoughts_not_good_mother +
            self.q7_thoughts_harming_self + self.q8_sleep_when_baby_sleeps +
            self.q9_worried_baby_health + self.q10_physically_exhausted +
            self.q11_relationship_partner + self.q12_emotional_support +
            self.q13_confide_in_someone + self.q14_depression_before_pregnancy +
            self.q15_depression_during_pregnancy + self.q16_family_history_mental_illness +
            self.q17_experienced_abuse + self.q18_unplanned_pregnancy +
            self.q19_delivery_complications + self.q20_baby_health_problems
        )

        # Determine risk level
        if self.q7_thoughts_harming_self > 0:
            self.risk_level = 'critical'
        elif self.total_score >= 20:
            self.risk_level = 'high'
        elif self.total_score >= 10:
            self.risk_level = 'moderate'
        else:
            self.risk_level = 'low'

        return self.total_score

    def save(self, *args, **kwargs):
        self.calculate_score()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Questionnaire {self.id} - Score: {self.total_score} ({self.risk_level})"


class DailyMoodCheckIn(models.Model):
    """Stores daily mood and sleep tracking data"""
    created_at = models.DateTimeField(default=timezone.now)
    user_identifier = models.CharField(max_length=255, blank=True, null=True)

    # Mood tracking
    mood_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)])
    mood_description = models.TextField(blank=True, null=True)

    # Sleep tracking
    hours_of_sleep = models.CharField(max_length=20, choices=[
        ('less_than_3', 'Less than 3'),
        ('3_4', '3-4'),
        ('4_5', '4-5'),
        ('5_6', '5-6'),
        ('more_than_6', 'More than 6')
    ])
    baby_wake_count = models.CharField(max_length=20, choices=[
        ('0_1', '0-1'),
        ('2_3', '2-3'),
        ('4_5', '4-5'),
        ('6_plus', '6+')
    ], blank=True, null=True)

    # Energy and stress
    energy_level = models.CharField(max_length=20, choices=[
        ('very_low', 'Very low'),
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('good', 'Good'),
        ('high', 'High')
    ])
    stress_level = models.CharField(max_length=20, choices=[
        ('calm', 'Calm'),
        ('slightly_stressed', 'Slightly stressed'),
        ('moderately_stressed', 'Moderately stressed'),
        ('very_stressed', 'Very stressed'),
        ('overwhelmed', 'Overwhelmed')
    ])

    # Intrusive thoughts
    intrusive_thoughts = models.CharField(max_length=20, choices=[
        ('no', 'No'),
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ])

    # Optional notes
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Daily Mood Check-Ins'

    def __str__(self):
        return f"Mood Check-In {self.created_at.strftime('%Y-%m-%d')} - Rating: {self.mood_rating}/10"
