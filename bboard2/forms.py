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
        ('Таңдаңыз', ' '),
        ('Өте жақсы', 'Өте жақсы'),
        ('Жақсы', 'Жақсы'),
        ('Қанағаттанарлық', 'Қанағаттанарлық'),
        ('Нашар', 'Нашар'),
    ]

    COMMENT_CHOICES_2 = [
        ('Таңдаңыз', ' '),
        ('Сенімді әрі дұрыс', 'Сенімді әрі дұрыс'),
        ('Дұрыс', 'Дұрыс'),
        ('Сенімсіз, бірақ дұрыс', 'Сенімсіз, бірақ дұрыс'),
        ('Жауап бере алмады', 'Жауап бере алмады'),

    ]

    COMMENT_CHOICES_3 = [
        ('Таңдаңыз', ' '),
        ('Жоғары', 'Жоғары'),
        ('Орташа', 'Орташа'),
        ('Төмен', 'Төмен'),
    ]

    comment = forms.ChoiceField(choices=COMMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    comment_2 = forms.ChoiceField(choices=COMMENT_CHOICES_2, widget=forms.Select(attrs={'class': 'form-control'}))
    comment_3 = forms.ChoiceField(choices=COMMENT_CHOICES_3, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Defense
        fields = ['start_time', 'end_time', 'comment', 'comment_2', 'comment_3']

