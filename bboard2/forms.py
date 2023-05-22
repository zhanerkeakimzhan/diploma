from django import forms
from .models import Defense, Grade


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ('commission', 'student', 'value', 'question')

    def __init__(self, *args, **kwargs):
        commission_choices = kwargs.pop('commission_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['commission'].choices = commission_choices

class DefenseForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    COMMENT_CHOICES = [
        ('Выберите', ' '),
        ('Отлично', 'Отлично'),
        ('Хорошо', 'Хорошо'),
        ('Удовлетворительно', 'Удовлетворительно'),
    ]

    COMMENT_CHOICES_2 = [
        ('Выберите', ' '),
        ('Уверенно', 'Уверенно'),
        ('Правильно', 'Правильно'),
    ]

    COMMENT_CHOICES_3 = [
        ('Выберите', ' '),
        ('Высокий', 'Высокий'),
        ('Средний', 'Средний'),
        ('Низкий', 'Низкий'),
    ]

    comment = forms.ChoiceField(choices=COMMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    comment_2 = forms.ChoiceField(choices=COMMENT_CHOICES_2, widget=forms.Select(attrs={'class': 'form-control'}))
    comment_3 = forms.ChoiceField(choices=COMMENT_CHOICES_3, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Defense
        fields = ['start_time', 'end_time', 'comment', 'comment_2', 'comment_3']

