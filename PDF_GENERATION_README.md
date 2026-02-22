# Automatic PDF Generation for Database Tables

This implementation automatically generates PDF reports with **all records in JSON format** whenever new entries are added to the `DailyMoodCheckIn` and `PostpartumQuestionnaire` tables in your SQLite database.

## How It Works

The system uses **Django signals** to detect when new rows are added to the database tables and automatically regenerates comprehensive PDFs containing **all records** from each table.

### Components

1. **`web/signals.py`**
   - Defines signal receivers that listen for new database entries
   - Triggers complete PDF regeneration when new rows are created
   - Uses Django's `post_save` signal with `created=True` to detect only new entries

2. **`web/pdf_generator.py`**
   - Contains PDF generation logic using ReportLab library
   - `regenerate_all_pdfs()` - Main function that regenerates both PDFs
   - `generate_table_pdf()` - Creates a single PDF with all rows from a table
   - `model_to_dict()` - Converts database records to JSON-serializable dictionaries
   - Each row is formatted as pretty-printed JSON in the PDF

3. **`web/apps.py`**
   - Modified to register signals when Django starts
   - Ensures signal handlers are connected on application startup

## PDF Output

Generated PDFs are automatically saved to: `web/data/pdfs/`

### File Names (Fixed, Not Timestamped)

- **Daily Mood Check-Ins**: `daily_mood_checking_all_records.pdf`
- **Questionnaires**: `postpartum_questionnaire_all_records.pdf`

Each time a new record is added to either table, the corresponding PDF is **completely regenerated** with all current records.

### PDF Contents

Each PDF contains:
- **Header**: Title, generation timestamp, and total record count
- **All Records**: Every record from the table formatted as JSON
  - Each record has a header with its sequential number and ID
  - Full record data in pretty-printed JSON format (2-space indentation)
  - Records are ordered by creation date (newest first)

#### Example JSON Format in PDF:

```json
Record 1 (ID: 37)
{
  "id": 37,
  "created_at": "2026-02-22T02:28:24.123456",
  "user_identifier": "test_user_001",
  "mood_rating": 7,
  "mood_description": "Feeling better today...",
  "hours_of_sleep": "5_6",
  "baby_wake_count": "2_3",
  "energy_level": "good",
  "stress_level": "slightly_stressed",
  "intrusive_thoughts": "mild",
  "notes": "Had a good conversation..."
}
```

## Installation

The required package has already been added to `requirements.txt`:

```bash
pip install reportlab==4.2.5
```

## Testing

Run the test script to verify PDF generation:

```bash
python test_pdf_generation.py
```

This will:
1. Show current record counts in both tables
2. Create test entries in both tables
3. Automatically regenerate PDFs via signals
4. Display information about the generated PDFs including file sizes and modification times

## Usage

No manual intervention is required. PDFs are regenerated automatically whenever:

1. A new entry is created in the database via Django ORM:
   ```python
   # This will automatically trigger PDF regeneration with ALL records
   DailyMoodCheckIn.objects.create(
       user_identifier="user123",
       mood_rating=7,
       hours_of_sleep="5_6",
       # ... other fields
   )
   ```

2. A new entry is created through Django admin interface

3. A new entry is created through your web forms

## File Locations

```
llm_ppd/
├── web/
│   ├── signals.py              # Signal receivers
│   ├── pdf_generator.py        # PDF generation logic
│   ├── apps.py                 # Signal registration
│   ├── models.py               # Database models
│   └── data/
│       └── pdfs/               # Generated PDFs stored here
│           ├── daily_mood_checking_all_records.pdf
│           └── postpartum_questionnaire_all_records.pdf
├── test_pdf_generation.py      # Test script
└── requirements.txt            # Dependencies
```

## Key Differences from Per-Record PDFs

This implementation differs from typical per-record PDF generation:

- **One PDF per table** (not one per record)
- **Contains all records** in JSON format
- **Regenerated completely** each time a new record is added
- **Fixed filenames** that get overwritten with updated data
- **JSON format** for easy parsing and data portability
- **Includes all fields** from each database row

## Notes

- PDFs are regenerated only when **new** entries are created (not for updates to existing entries)
- The PDF directory (`web/data/pdfs/`) is automatically created if it doesn't exist
- The entire PDF is regenerated each time, ensuring it always contains the complete current dataset
- Both PDFs are regenerated whenever a record is added to either table
- All datetime fields are formatted in ISO 8601 format for consistency
