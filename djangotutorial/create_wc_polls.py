import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from polls.models import Question

# Poll 1: World Cup Winner
teams = [
    "Arjantin", "Avustralya", "Avusturya", "Belçika", "Brezilya", "Cezayir", 
    "Ekvador", "Fas", "Fildişi Sahili", "Fransa", "Gana", "Güney Afrika", 
    "Güney Kore", "Haiti", "Hırvatistan", "Hollanda", "İngiltere", "İran", 
    "İspanya", "İsviçre", "İtalya / Bosna (Playoff)", "Japonya", "Kanada", 
    "Katar", "Kolombiya", "Meksika", "Mısır", "Norveç", "Özbekistan", 
    "Panama", "Paraguay", "Portekiz", "Suudi Arabistan", "Senegal", 
    "Tunus", "Türkiye / Kosova (Playoff)", "Uruguay", "ABD", "Yeni Zelanda"
]

q1 = Question(question_text='2026 Dünya Kupası\'nı kim kazanır?', pub_date=timezone.now())
q1.save()

for team in sorted(teams):
    q1.choice_set.create(choice_text=team, votes=0)


# Poll 2: World Cup Top Scorer
players = [
    "Kylian Mbappé (Fransa)",
    "Erling Haaland (Norveç)",
    "Harry Kane (İngiltere)",
    "Vinícius Júnior (Brezilya)",
    "Lionel Messi (Arjantin)",
    "Cristiano Ronaldo (Portekiz)",
    "Jude Bellingham (İngiltere)",
    "Jamal Musiala (Almanya)",
    "Lautaro Martínez (Arjantin)",
    "Cody Gakpo (Hollanda)",
    "Christian Pulisic (ABD)"
]

q2 = Question(question_text='2026 Dünya Kupası\'nda en fazla golü kim atar (Gol Kralı)?', pub_date=timezone.now())
q2.save()

for player in players:
    q2.choice_set.create(choice_text=player, votes=0)

print("Dünya Kupası anketleri başarıyla oluşturuldu!")
