from django import forms
from django.forms import inlineformset_factory
from .models import Question, Choice

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'category', 'end_date']
        widgets = {
            'question_text': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Soru metnini girin...',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local',
            }),
        }

ChoiceFormSet = inlineformset_factory(
    Question, 
    Choice, 
    fields=['choice_text', 'image'], 
    extra=3, 
    can_delete=False,
    widgets={
        'choice_text': forms.TextInput(attrs={
            'class': 'form-input choice-field',
            'placeholder': 'Seçenek metni...',
        }),
        'image': forms.ClearableFileInput(attrs={
            'class': 'form-input',
            'style': 'margin-top: 0.5rem;',
        }),
    }
)
