import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from polls.models import Question

if Question.objects.count() == 0:
    q = Question(question_text='IP Sinirlamasi Test Anketi', pub_date=timezone.now())
    q.save()
    q.choice_set.create(choice_text='Calisiyor', votes=0)
    q.choice_set.create(choice_text='Calismiyor', votes=0)
    print("Test anketi olusturuldu.")
else:
    print("Anket zaten var.")
