import datetime
from django.db import models

class Students(models.Model):
    img = models.ImageField(upload_to='images')
    name = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    middlename = models.CharField('Отчество', max_length=50)
    birthday = models.DateField('День рождения')
    diploma_title = models.CharField('Тема дипломного проекта', max_length=100)
    iin = models.CharField('ИИН', max_length=100, default=' ')
    name_eng = models.CharField('Имя на английском', max_length=100, default=' ')
    lastname_eng = models.CharField('Фамилия на английском', max_length=100, default=' ')
    middlename_eng = models.CharField('Отчество на английском', max_length=100, default=' ')
    id_card = models.CharField('№ удостоверения личности/паспорта', max_length=100, default=' ')
    speciality = models.CharField('Специальность', max_length=100, default=' ')
    diploma = models.FileField('Диплом', upload_to='uploads/', default=' ')
    prez_diploma = models.FileField('Презентация', upload_to='uploads/', default=' ')
    recen_diploma = models.FileField('Рецензия', upload_to='uploads/', default=' ')
    feedback_diploma = models.FileField('Отзыв руководителя', upload_to='uploads/', default=' ')
    antiplagiat = models.FileField('Антиплагиат', upload_to='uploads/', default=' ')
    time = models.TimeField('Время сдачи диплома', default=datetime.datetime.now().time(), null=True, blank=True)
    endtime = models.TimeField('Время окончание сдачи диплома', default=datetime.datetime.now().time(), null=True, blank=True)
    date = models.DateField('Дата сдачи диплома', default='2000-01-01', null=True, blank=True)
    advisor = models.CharField('Руководитель', max_length=100, default=' ')
    advisor_scientific_degree = models.CharField('Степень руководителя', max_length=100, default=' ')
    advisor_job = models.CharField('Место работы руководителя', max_length=100, default=' ')
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
    name_eng = models.CharField('Имя на английском', max_length=100, default=' ')
    lastname_eng = models.CharField('Фамилия на английском', max_length=100, default=' ')
    middlename_eng = models.CharField('Отчество на английском', max_length=100, default=' ')
    job = models.CharField('Место работы', max_length=100, default=' ')
    scientific_degree = models.CharField('Степень', max_length=100, default=' ')
    number = models.CharField('Номер телефона', max_length=12, default=' ')
    email = models.CharField('Почта', max_length=50, default=' ')
    initials = models.CharField('Инициалы', max_length=100, default=' ')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Commission'

class Grade(models.Model):
    commission = models.ForeignKey(Commissions, on_delete=models.CASCADE)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    value = models.IntegerField()

    def __str__(self):
        return f"{self.commission.name} - {self.student.name} - {self.value}"

class Secretary(models.Model):
    img = models.ImageField(upload_to='images')
    name = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    middlename = models.CharField('Отчество', max_length=50)
    name_eng = models.CharField('Имя на английском', max_length=100, default=' ')
    lastname_eng = models.CharField('Фамилия на английском', max_length=100, default=' ')
    middlename_eng = models.CharField('Отчество на английском', max_length=100, default=' ')
    job = models.CharField('Место работы', max_length=100, default=' ')
    number = models.CharField('Номер телефона', max_length=12, default=' ')
    email = models.CharField('Почта', max_length=50, default=' ')
    initials = models.CharField('Инициалы', max_length=100, default=' ')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Secretarie'

class Chairmans(models.Model):
    img = models.ImageField(upload_to='images')
    name = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    middlename = models.CharField('Отчество', max_length=50)
    name_eng = models.CharField('Имя на английском', max_length=100, default=' ')
    lastname_eng = models.CharField('Фамилия на английском', max_length=100, default=' ')
    middlename_eng = models.CharField('Отчество на английском', max_length=100, default=' ')
    job = models.CharField('Место работы', max_length=100, default=' ')
    scientific_degree = models.CharField('Степень', max_length=100, default=' ')
    number = models.CharField('Номер телефона', max_length=12, default=' ')
    email = models.CharField('Почта', max_length=50, default=' ')
    initials = models.CharField('Инициалы', max_length=100, default=' ')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Chairman'

# secretaries_group = Group.objects.create(name='secretaries')
# commission_group = Group.objects.create(name='commission')
#
# class CustomUser(AbstractUser):
#     is_secretary = models.BooleanField(default=False)
#     is_commission = models.BooleanField(default=False)