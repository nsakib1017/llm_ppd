# Quick Start Guide - Automatic PDF Generation

## What Was Implemented

Your Django application now automatically generates PDFs with all database records in JSON format whenever new entries are added to:
- `web_dailymoodchecking` table
- `web_postpartumuestionnaire` table

## Generated PDF Files

Location: `web/data/pdfs/`

- **`daily_mood_checking_all_records.pdf`** - Contains ALL mood check-in records
- **`postpartum_questionnaire_all_records.pdf`** - Contains ALL questionnaire records

## How It Works

1. When you add a new row to either table (via web form, Django admin, or code)
2. A Django signal is triggered automatically
3. Both PDFs are regenerated with ALL current records in JSON format
4. PDFs are saved to `web/data/pdfs/` directory

## Testing

### View Current PDFs
The PDFs are already generated with your existing data. Open them from:
```
web/data/pdfs/daily_mood_checking_all_records.pdf
web/data/pdfs/postpartum_questionnaire_all_records.pdf
```

### Add a New Entry and Watch It Update
```bash
python test_pdf_generation.py
```
This will:
- Create new test entries
- Automatically trigger PDF regeneration
- Show you the updated file sizes and timestamps

### Manually Regenerate PDFs
```bash
python manual_generate_pdfs.py
```

## What Each PDF Contains

Each PDF shows:
1. **Header**: Title, generation timestamp, total record count
2. **All Records**: Each record formatted as JSON with:
   - Record number and ID
   - All fields from that database row
   - ISO-formatted datetime stamps

### Example from PDF:
```
Daily Mood Check-In - All Records
Generated: 2026-02-22 02:28:24
Total Records: 33

Record 1 (ID: 37)
{
  "id": 37,
  "created_at": "2026-02-22T02:28:24.123456",
  "user_identifier": "test_user_001",
  "mood_rating": 7,
  "mood_description": "Feeling better today...",
  "hours_of_sleep": "5_6",
  ...
}

Record 2 (ID: 36)
{
  ...
}
```

## Files Added/Modified

### New Files:
- `web/signals.py` - Django signal handlers
- `web/pdf_generator.py` - PDF generation logic
- `test_pdf_generation.py` - Test script
- `manual_generate_pdfs.py` - Manual PDF generation utility

### Modified Files:
- `web/apps.py` - Registers signals on startup
- `requirements.txt` - Added reportlab dependency

## No Action Required

The system is fully automatic. Just use your application normally:
- Submit forms through the web interface
- Add records via Django admin
- Create records programmatically

The PDFs will update automatically with every new entry!
