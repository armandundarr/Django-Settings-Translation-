import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from polls.models import Question

q = Question(question_text='2026 yılında favori web geliştirme aracınız hangisi?', pub_date=timezone.now())
q.save()
q.choice_set.create(choice_text='Django', votes=0)
q.choice_set.create(choice_text='Next.js / React', votes=0)
q.choice_set.create(choice_text='Vue / Nuxt', votes=0)
q.choice_set.create(choice_text='SvelteKit', votes=0)

print("Yeni anket başarıyla oluşturuldu!")
