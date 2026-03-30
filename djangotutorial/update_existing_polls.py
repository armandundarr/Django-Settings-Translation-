import os
import django
from django.utils import timezone
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from polls.models import Question, Category

general_category, _ = Category.objects.get_or_create(name='Genel', defaults={'color': '#3b82f6'})
sports_category, _ = Category.objects.get_or_create(name='Spor', defaults={'color': '#22c55e'})
tech_category, _ = Category.objects.get_or_create(name='Teknoloji', defaults={'color': '#a855f7'})

for q in Question.objects.all():
    if not q.category:
        if 'Dünya Kupası' in q.question_text:
            q.category = sports_category
        elif 'web geliştirme' in q.question_text.lower():
            q.category = tech_category
        else:
            q.category = general_category
        
    if not q.end_date:
        q.end_date = timezone.now() + datetime.timedelta(days=30)
    
    q.save()

print("Existing polls updated with categories and end dates!")
