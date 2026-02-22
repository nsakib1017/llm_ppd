import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from django.conf import settings
from django.core.serializers import serialize


def get_pdf_directory():
    """Ensure the PDF directory exists and return its path"""
    pdf_dir = os.path.join(settings.BASE_DIR, 'web', 'data', 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    return pdf_dir


def model_to_dict(instance):
    """Convert a model instance to a dictionary with formatted datetime"""
    data = {}
    for field in instance._meta.fields:
        field_name = field.name
        field_value = getattr(instance, field_name)

        # Convert datetime to ISO format string
        if isinstance(field_value, datetime):
            data[field_name] = field_value.isoformat()
        else:
            data[field_name] = field_value

    return data


def generate_table_pdf(model_class, filename, title):
    """Generate a single PDF for all rows in a table with JSON formatting"""
    pdf_dir = get_pdf_directory()
    filepath = os.path.join(pdf_dir, filename)

    # Get all records from the table
    all_records = model_class.objects.all().order_by('-created_at')

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )

    # Style for JSON code
    json_style = ParagraphStyle(
        'JSONStyle',
        parent=styles['Code'],
        fontSize=8,
        leftIndent=10,
        rightIndent=10,
        spaceAfter=15,
        wordWrap='LTR'
    )

    # Title
    story.append(Paragraph(title, title_style))
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    story.append(Paragraph(f"Generated: {timestamp}", styles['Normal']))
    story.append(Paragraph(f"Total Records: {all_records.count()}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Add each record as JSON
    for idx, record in enumerate(all_records, 1):
        # Convert record to dictionary
        record_dict = model_to_dict(record)

        # Format as pretty JSON
        json_str = json.dumps(record_dict, indent=2, ensure_ascii=False)

        # Add record header
        header_text = f"Record {idx} (ID: {record.id})"
        story.append(Paragraph(header_text, styles['Heading3']))

        # Add JSON as preformatted text
        json_para = Preformatted(json_str, json_style)
        story.append(json_para)
        story.append(Spacer(1, 0.2*inch))

    # Build PDF
    doc.build(story)
    return filepath


def regenerate_all_pdfs():
    """Regenerate both table PDFs with all current data"""
    from .models import DailyMoodCheckIn, PostpartumQuestionnaire

    # Generate DailyMoodCheckIn PDF
    mood_pdf = generate_table_pdf(
        DailyMoodCheckIn,
        'daily_mood_checking_all_records.pdf',
        'Daily Mood Check-In - All Records'
    )

    # Generate PostpartumQuestionnaire PDF
    questionnaire_pdf = generate_table_pdf(
        PostpartumQuestionnaire,
        'postpartum_questionnaire_all_records.pdf',
        'Postpartum Questionnaire - All Records'
    )

    return mood_pdf, questionnaire_pdf
