import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_ppd.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client
from django.urls import reverse

# Create a test client
client = Client()

print("Testing Django views...")
print("-" * 50)

# Test homepage
try:
    response = client.get('/')
    print(f"[OK] Homepage (/) - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  Content length: {len(response.content)} bytes")
except Exception as e:
    print(f"[ERROR] Homepage (/) - Error: {e}")

# Test all pages
pages = [
    ('home', '/home/'),
    ('questioneer', '/questioneer/'),
    ('daily_meds', '/daily-meds/'),
    ('mood_statistics', '/mood-statistics/'),
    ('materna_ai', '/materna-ai/'),
]

for name, url in pages:
    try:
        response = client.get(url)
        print(f"[OK] {name} ({url}) - Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {name} ({url}) - Error: {e}")

print("-" * 50)
print("Testing complete!")
