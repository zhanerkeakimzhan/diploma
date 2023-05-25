import datetime
import self as self
from django.db import models
from django.contrib.auth.models import User

class Students(models.Model):
    img = models.ImageField(upload_to='images')
    name = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    middlename = models.CharField('Отчество', max_length=50)
    birthday = models.DateField('День рождения')
    diploma_title = models.CharField('Тема дипломного проекта', max_length=100)
    iin = models.CharField('ИИН', max_length=100, default='')
    name_eng = models.CharField('Имя на английском', max_length=100, default='')
    lastname_eng = models.CharField('Фамилия на английском', max_length=100, default='')
    middlename_eng = models.CharField('Отчество на английском', max_length=100, default='')
    id_card = models.CharField('№ удостоверения личности/паспорта', max_length=100, default='')
    speciality = models.CharField('Специальность', max_length=100, default='')
    diploma = models.FileField('Диплом', upload_to='uploads/', default='')
    prez_diploma = models.FileField('Презентация', upload_to='uploads/', default='')
    recen_diploma = models.FileField('Рецензия', upload_to='uploads/', default='')
    feedback_diploma = models.FileField('Отзыв руководителя', upload_to='uploads/', default='')
    antiplagiat = models.FileField('Антиплагиат', upload_to='uploads/', default='')
    date = models.DateField('Дата сдачи диплома', default='2000-01-01', null=True, blank=True)
    advisor = models.CharField('Руководитель', max_length=100, default='')
    advisor_scientific_degree = models.CharField('Степень руководителя', max_length=100, default='')
    advisor_job = models.CharField('Место работы руководителя', max_length=100, default='')
    advisor_initials = models.CharField('Руководитель инициалы', max_length=100, default='')
    gpa = models.CharField('GPA', max_length=10, default='')
    # opinion = models.CharField('Особые мнение членов комиссии', )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Student'

class Commissions(models.Model):
    img = models.ImageField(upload_to='images')
    name = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    middlename = models.CharField('Отчество', max_length=50)
    name_eng = models.CharField('Имя на английском', max_length=100)
    lastname_eng = models.CharField('Фамилия на английском', max_length=100)
    middlename_eng = models.CharField('Отчество на английском', max_length=100)
    job = models.CharField('Место работы', max_length=100)
    scientific_degree = models.CharField('Степень', max_length=100)
    number = models.CharField('Номер телефона', max_length=12)
    email = models.CharField('Почта', max_length=50)
    initials = models.CharField('Инициалы', max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Commission'



class Secretary(models.Model):
    img = models.ImageField(upload_to='images')
    name = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    middlename = models.CharField('Отчество', max_length=50)
    name_eng = models.CharField('Имя на английском', max_length=100, default='')
    lastname_eng = models.CharField('Фамилия на английском', max_length=100, default='')
    middlename_eng = models.CharField('Отчество на английском', max_length=100, default='')
    job = models.CharField('Место работы', max_length=100, default='')
    number = models.CharField('Номер телефона', max_length=12, default='')
    email = models.CharField('Почта', max_length=50, default='')
    initials = models.CharField('Инициалы', max_length=100, default='')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Secretarie'

class Chairmans(models.Model):
    img = models.ImageField(upload_to='images')
    name = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    middlename = models.CharField('Отчество', max_length=50)
    name_eng = models.CharField('Имя на английском', max_length=100, default='')
    lastname_eng = models.CharField('Фамилия на английском', max_length=100, default='')
    middlename_eng = models.CharField('Отчество на английском', max_length=100, default='')
    job = models.CharField('Место работы', max_length=100, default='')
    scientific_degree = models.CharField('Степень', max_length=100, default='')
    number = models.CharField('Номер телефона', max_length=12, default='')
    email = models.CharField('Почта', max_length=50, default='')
    initials = models.CharField('Инициалы', max_length=100, default='')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Chairman'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    commission = models.ForeignKey(Commissions, on_delete=models.CASCADE, null=True, blank=True)
    chairman = models.ForeignKey(Chairmans, on_delete=models.CASCADE, null=True, blank=True)

class Grade(models.Model):
    commission = models.ForeignKey(Commissions, on_delete=models.CASCADE, null=True, blank=True)
    chairman = models.ForeignKey(Chairmans, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    value = models.IntegerField()
    question = models.CharField(max_length=100, default='')
    is_filled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.commission.name} - {self.student.name} - {self.value}"

class Defense(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    coment = models.CharField(default='', max_length=500) #Особые мнения комиссии
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    is_filled = models.BooleanField(default=False)
    page_number = models.CharField()
    picture_number = models.CharField()
    text_input = models.CharField() #отзыв рук
    text_input_1 = models.CharField() #заключение эксперта
    score = models.CharField() #оценка рецензента
    text_area = models.CharField() #Неофициальные отзывы
    comment_2 = models.CharField() #Общая характеристика ответов
    comment_3 = models.CharField() #Уровень знаний