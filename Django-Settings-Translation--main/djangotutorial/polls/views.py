from django.db.models import F
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncHour
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .models import Choice, Question, VoterIP, Category, Comment, Badge, UserBadge, Profile, Reaction, ChatMessage
from .forms import QuestionForm, ChoiceFormSet

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        query = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        
        qs = Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")
        
        if query:
            qs = qs.filter(question_text__icontains=query)
        
        if category_id:
            qs = qs.filter(category_id=category_id)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Sum
        
        # All categories for the filter
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('q', '')
        
        # Trending polls: Top 3 voted polls
        # We need to annotate each question with its total votes across choices
        context['trending_polls'] = Question.objects.annotate(
            total_votes=Sum('choice__votes')
        ).order_by('-total_votes')[:3]
        
        return context

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()
        
        # Count reactions by type
        reactions_stats = []
        for code, char in Reaction.REACTION_CHOICES:
            count = question.reactions.filter(emoji=code).count()
            user_reacted = False
            if self.request.user.is_authenticated:
                user_reacted = question.reactions.filter(user=self.request.user, emoji=code).exists()
            
            reactions_stats.append({
                'code': code,
                'char': char,
                'count': count,
                'user_reacted': user_reacted
            })
            
        context['reactions_stats'] = reactions_stats
        return context

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def poll_results_api(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choices = question.choice_set.all()
    data = {
        "labels": [c.choice_text for c in choices],
        "votes": [c.votes for c in choices],
        "total_votes": sum(c.votes for c in choices)
    }
    return JsonResponse(data)

def poll_timeline_api(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # Get vote counts grouped by hour
    timeline = question.votes.annotate(
        hour=TruncHour('vote_date')
    ).values('hour').annotate(count=Count('id')).order_by('hour')
    
    data = {
        "labels": [entry['hour'].strftime('%H:%M') for entry in timeline],
        "counts": [entry['count'] for entry in timeline]
    }
    return JsonResponse(data)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if not question.is_active:
        return render(request, "polls/detail.html", {
            "question": question,
            "error_message": "Bu anket süresi dolduğu için oylamaya kapatılmıştır.",
        })

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(request, "polls/detail.html", {
            "question": question,
            "error_message": "Bir seçenek belirtmediniz.",
        })
    else:
        ip_address = get_client_ip(request)
        if VoterIP.objects.filter(question=question, ip_address=ip_address).exists():
            return render(request, "polls/detail.html", {
                "question": question,
                "error_message": "Bu anket için daha önce oy kullandınız.",
            })
            
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        VoterIP.objects.create(question=question, ip_address=ip_address, user=request.user if request.user.is_authenticated else None)

        # Award points and badges if logged in
        if request.user.is_authenticated:
            profile = request.user.profile
            profile.points += 10 # 10 puan her oy için
            profile.save()
            
            # Badge checks
            # 1. İlk Oy Rozeti
            first_vote_badge, _ = Badge.objects.get_or_create(
                name="İlk Kıvılcım", 
                defaults={'description': "İlk oyunu kullandın!", 'icon': "🔥", 'points_threshold': 0}
            )
            UserBadge.objects.get_or_create(user=request.user, badge=first_vote_badge)
            
            # 2. Sadık Seçmen (50+ puan)
            loyal_badge, _ = Badge.objects.get_or_create(
                name="Sadık Seçmen", 
                defaults={'description': "50 puan barajını aştın!", 'icon': "🏅", 'points_threshold': 50}
            )
            if profile.points >= 50:
                UserBadge.objects.get_or_create(user=request.user, badge=loyal_badge)

        messages.success(request, "Oyunuz başarıyla kaydedildi!")
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

@login_required
def add_comment(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(question=question, user=request.user, content=content)
            messages.success(request, 'Yorumunuz eklendi.')
    return HttpResponseRedirect(reverse("polls:detail", args=(question.id,)))

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hesabınız başarıyla oluşturuldu. Şimdi giriş yapabilirsiniz.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

class LeaderboardView(generic.ListView):
    model = Profile
    template_name = "polls/leaderboard.html"
    context_object_name = "top_profiles"

    def get_queryset(self):
        return Profile.objects.order_by('-points')[:10]

@login_required
def create_poll(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST, request.FILES) # Added request.FILES
        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.pub_date = timezone.now()
            
            # Check if any choice has an image to mark it as is_image_poll
            is_image = False
            for c_form in formset:
                if c_form.cleaned_data.get('image'):
                    is_image = True
                    break
            question.is_image_poll = is_image
            question.save()
            
            choices = formset.save(commit=False)
            for choice in choices:
                choice.question = question
                choice.save()
                
            messages.success(request, 'Anketiniz başarıyla oluşturuldu.')
            return redirect('polls:index')
    else:
        form = QuestionForm()
        formset = ChoiceFormSet()
        
    return render(request, 'polls/question_form.html', {
        'form': form,
        'formset': formset,
    })

@login_required
def add_reaction(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    emoji = request.POST.get('emoji')
    if emoji:
        # Toggle reaction (one user can have multiple emojis but one of each type)
        reaction, created = Reaction.objects.get_or_create(
            question=question, user=request.user, emoji=emoji
        )
        if not created:
            reaction.delete()
    return HttpResponseRedirect(reverse("polls:detail", args=(question.id,)))

def ai_suggest_choices(request):
    question_text = request.GET.get('question', '').lower()
    
    # Mock AI Logic based on keywords
    suggestions = ["Seçenek 1", "Seçenek 2", "Seçenek 3", "Seçenek 4"]
    
    if "programlama" in question_text or "yazılım" in question_text:
        suggestions = ["Python", "JavaScript", "Rust", "Go"]
    elif "yemek" in question_text or "mutfak" in question_text:
        suggestions = ["Kebap", "Pizza", "Sushi", "Hamburger"]
    elif "spor" in question_text or "futbol" in question_text:
        suggestions = ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor"]
    elif "ülke" in question_text or "dünya" in question_text:
        suggestions = ["Türkiye", "Almanya", "ABD", "Japonya"]
    elif "film" in question_text or "sinema" in question_text:
        suggestions = ["Inception", "Interstellar", "Godfather", "Pulp Fiction"]
        
    return JsonResponse({"suggestions": suggestions})

# --- [FEATURE 8: Dynamic Social Cards] ---
import io
from PIL import Image, ImageDraw
from django.http import HttpResponse

def poll_share_image(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choices = question.choice_set.all().order_by('-votes')
    
    # Create a 1200x630 (OG standard) image
    # Using a dark "Radiant UI" background #0f172a
    img = Image.new('RGB', (1200, 630), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    # Branding logic (simplified icons/text)
    draw.text((50, 80), "MAKECHOICE - Senin Kararın, Senin Gücün", fill=(99, 102, 241))
    draw.text((50, 180), f"SORU: {question.question_text[:100]}...", fill=(255, 255, 255))
    
    # Results visualization
    y = 300
    for i, choice in enumerate(choices[:3]):
        draw.text((50, y), f"{i+1}. {choice.choice_text}: {choice.votes} Oy", fill=(255, 255, 255) if i > 0 else (244, 63, 94))
        y += 80

    # Output to response
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")

# --- [FEATURE 7: Poll Chat API] ---
def poll_chat_feed(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # Get last 50 messages
    messages = question.chat_messages.all().order_by('-created_at')[:50]
    data = [{
        'user': m.user.username,
        'message': m.message,
        'created_at': m.created_at.strftime('%H:%M')
    } for m in reversed(messages)]
    return JsonResponse({'messages': data})

@login_required
def send_chat_message(request, question_id):
    if request.method == 'POST':
        question = get_object_or_404(Question, pk=question_id)
        msg_text = request.POST.get('message')
        if msg_text:
            ChatMessage.objects.create(question=question, user=request.user, message=msg_text)
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)
