from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .models import Choice, Question, VoterIP, Category, Comment

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        category_id = self.request.GET.get('category')
        qs = Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        return context

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if not question.is_active():
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
        VoterIP.objects.create(question=question, ip_address=ip_address)
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
