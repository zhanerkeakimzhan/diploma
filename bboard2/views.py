import logging
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from pyexpat.errors import messages
from .forms import DefenseForm, GradeForm
from .models import Students
from .models import Defense
from docxtpl import DocxTemplate
from .models import Commissions
from .models import Chairmans, Secretary
from .models import Grade
from django.contrib import auth
import io
import datetime
import locale
from datetime import date
# from .forms import GradeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, HttpResponse
from django.db.models import Avg

def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name='secretary').exists():
                return redirect('index')
            elif user.groups.filter(name='commission').exists():
                return redirect('com_main')
            else:
                return redirect('login')
        else:
            return render(request, 'login_page.html', {'error': 'Неправильное имя пользователя или пароль'})
    else:
        return render(request, 'login_page.html')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='secretary').exists())
def index(request):
    return render(request, 'index.html', {'username': auth.get_user(request).username})
# def index(request):
#     commission = get_object_or_404(Commissions, user=request.user)
#     context = {
#         'username': auth.get_user(request).username,
#         'commission': commission
#     }
#     return render(request, 'index.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='commission').exists())
def com_main(request):
    students = Students.objects.all()
    context = {
        'username': auth.get_user(request).username,
        'students': students
    }
    return render(request, 'com_main.html', context)

def logout_page(request):
    logout(request)
    return redirect('login')

# def index(request):
#     return render(request, 'index.html', {'username': auth.get_user(request).username})

def commissions(request):
    return render(request, 'commissions.html', {'username': auth.get_user(request).username})

# def com_stud_page(request, id):
#     student = get_object_or_404(Students, id=id)
#     context = {
#         'username': auth.get_user(request).username,
#         'student': student
#     }
#
#     return render(request, 'com_stud_page.html', context)

def student_page(request, id):
    student = get_object_or_404(Students, id=id)
    # student = student.id

    defenses = Defense.objects.filter(student=student)
    if defenses.exists():
        defense = defenses.first()
        if defense.is_filled:
            return redirect('student_page_second', id=id)

    defense_form = DefenseForm(request.POST or None)
    if defense_form.is_valid():
        defense = defense_form.save(commit=False)
        defense.student = student
        defense.save()
        request.session['defense_start_time'] = defense.start_time.isoformat()
        request.session['defense_end_time'] = defense.end_time.isoformat()
        messages.success(request, 'Время начала и окончания защиты успешно сохранено.')
        return redirect('student_info', id=id)
    else:
        defense_start_time = request.session.get('defense_start_time')
        defense_end_time = request.session.get('defense_end_time')
        if defense_start_time and defense_end_time:
            defense_form.initial['start_time'] = defense_start_time
            defense_form.initial['end_time'] = defense_end_time

    context = {
        'username': auth.get_user(request).username,
        'student': student,
        'defense_form': defense_form
    }



    # try:
    #     defense = Defense.objects.get(student=student)
    #     if defense.is_filled:
    #         return redirect('student_page_second', id=id)
    # except Grade.DoesNotExist:
    #     pass

    return render(request, 'student_page.html', context)

def add_time(request, id):
    student = get_object_or_404(Students, id=id)
    start_time = request.POST.get("start_time")
    end_time = request.POST.get("end_time")
    comment = request.POST.get("comment")

    add_data = Defense(student=student, start_time=start_time, end_time=end_time, coment=comment)
    add_data.save()

    add_data.is_filled = True
    add_data.save()

    # return HttpResponse(f"student: {student} <br> start_time:{start_time} <br> end_time:{end_time} <br> comment:{comment}")
    return redirect('student_page_second', id=id)

def student_page_second(request, id):
    student = get_object_or_404(Students, id=id)
    student_id = student.id
    # defense_form = DefenseForm(request.POST or None)

    defense = Defense.objects.get(student=student_id)

    start_time = defense.start_time
    end_time = defense.end_time
    comment = defense.coment

    context = {
        'username': auth.get_user(request).username,
        'student': student,
        'start_time': start_time,
        'end_time': end_time,
        'comment': comment
    }

    return render(request, 'student_page_second.html', context)

def com_stud_page(request, id):
    student = get_object_or_404(Students, id=id)
    user_profile = request.user.userprofile
    commission = get_object_or_404(Commissions, id=user_profile.commission.id)

    context = {
        'username': auth.get_user(request).username,
        'student': student
    }

    try:
        grade = Grade.objects.get(commission=commission, student=student)
        if grade.is_filled:
            return redirect('com_stud_page_second', id=id)
    except Grade.DoesNotExist:
        pass

    return render(request, 'com_stud_page.html', context)

def add_grade(request, id):
    student = get_object_or_404(Students, id=id)
    user_profile = request.user.userprofile
    commission = get_object_or_404(Commissions, id=user_profile.commission.id)
    question = request.POST.get("question")
    value = request.POST.get("value")

    add_data = Grade(commission=commission, student=student, question=question,value=value)
    add_data.save()

    add_data.is_filled = True
    add_data.save()

    request.session['grade_data'] = {
        'student': student.id,
        'commission': commission.id,
        'question': question,
        'value': value
    }
    #
    # context = {
    #     'username': auth.get_user(request).username,
    #     'student': student,
    #     'grade_data': request.session.get('grade_data')
    # }
    # return HttpResponse(f"student:{student} <br> commission:{commission} <br> question:{question} <br> value:{value}")
    # return render(request, 'com_stud_page_second.html', context)
    return redirect('com_stud_page_second', id=id)

def com_stud_page_second(request, id):
    student = get_object_or_404(Students, id=id)
    student_id = student.id

    user_profile = request.user.userprofile
    commission = get_object_or_404(Commissions, id=user_profile.commission.id)
    commission_id = commission.id

    grade_data = request.session.get('grade_data')

    grade = Grade.objects.get(commission=commission_id, student=student_id)

    question = grade.question
    value = grade.value

    context = {
        'username': auth.get_user(request).username,
        'student': student,
        'grade_data': grade_data,
        'question': question,
        'value': value
    }

    return render(request, 'com_stud_page_second.html', context)

count = 0
def download_document(request, stud_id): #решение ГАК
    global count
    count += 1
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    current_time = datetime.datetime.today()
    today = date.today()
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    student = get_object_or_404(Students, id=stud_id)
    commission1 = get_object_or_404(Commissions, id=1)
    commission2 = get_object_or_404(Commissions, id=2)
    commission3 = get_object_or_404(Commissions, id=3)
    commission4 = get_object_or_404(Commissions, id=4)
    chairman = get_object_or_404(Chairmans, id=1)
    secretary = get_object_or_404(Secretary, id=1)
    context = {
        'student': student
    }
    name = student.name
    lastname = student.lastname
    middlename = student.middlename
    speciality = student.speciality
    gradee = Grade.objects.filter(student=student).aggregate(Avg('value'))['value__avg']
    grade = round(gradee)
    defense = Defense.objects.get(student=student)


    letter_grade = ' '
    if 100 >= grade >= 95:
        letter_grade = 'A'
    elif 95 > grade >= 90:
        letter_grade = 'A-'
    elif 90 > grade >= 85:
        letter_grade = 'B+'
    elif 85 > grade >= 80:
        letter_grade = 'B'
    elif 80 > grade >= 75:
        letter_grade = 'B-'
    elif 75 > grade >= 70:
        letter_grade = 'C+'
    elif 70 > grade >= 65:
        letter_grade = 'C'
    elif 65 > grade >= 60:
        letter_grade = 'C-'
    elif 60 > grade >= 55:
        letter_grade = 'D+'
    elif 55 > grade >= 50:
        letter_grade = 'D'
    elif 50 > grade >= 25:
        letter_grade = 'FX'
    elif 25 > grade >= 0:
        letter_grade = 'F'

    firstcommision = commission1.lastname + ' ' + commission1.name + ' ' + commission1.middlename
    secondcommision = commission2.lastname + ' ' + commission2.name + ' ' + commission2.middlename
    thirdcommision = commission3.lastname + ' ' + commission3.name + ' ' + commission3.middlename
    fourthcommision = commission4.lastname + ' ' + commission4.name + ' ' + commission4.middlename

    firstchairman = chairman.lastname + ' ' + chairman.name + ' ' + chairman.middlename

    firstinitials = commission1.initials
    secondinitials = commission2.initials
    thirdinitials = commission3.initials
    fourthinitials = commission4.initials
    fifthinitials = chairman.initials
    sixthinitials = secretary.initials

    # starttimehour = student.time.hour
    # starttimeminute = student.time.minute
    # endtimehour = student.endtime.hour
    # endtimeminute = student.endtime.minute
    starttimehour = defense.start_time.hour
    starttimeminute = defense.start_time.minute
    endtimehour = defense.end_time.hour
    endtimeminute = defense.end_time.minute

    comment = defense.coment

    d1 = today.strftime("%d.%m.%Y")
    # dat = student.date.strftime("%d.%m.%Y")

    doc = DocxTemplate("bboard2/static/protocol_2.docx")

    context = {
        "number": count,
        "day": current_time.day,
        "month": current_time.strftime('%B'),
        "year": current_time.year,
        "lastname": lastname,
        "name": name,
        "middlename": middlename,
        "speciality": speciality,
        "firstcommision": firstcommision,
        "secondcommision": secondcommision,
        "thirdcommision": thirdcommision,
        "fourthcommision": fourthcommision,
        "firstchairman": firstchairman,
        "firstinitials": firstinitials,
        "secondinitials": secondinitials,
        "thirdinitials": thirdinitials,
        "fourthinitials": fourthinitials,
        "fifthinitials": fifthinitials,
        "sixthinitials":sixthinitials,
        "d1": d1,
        "starttimehour": starttimehour,
        "starttimeminute": starttimeminute,
        "endtimehour": endtimehour,
        "endtimeminute": endtimeminute,
        "grade": grade,
        "letter_grade": letter_grade,
        "comment": comment
    }

    doc.render(context)

    doc.save("{0}_{1}_Протокол_2.docx".format(name, lastname))
    doc_name = f"{name}_{lastname}_Протокол_2.docx"
    logging.debug("Document name: {}".format(doc_name))
    print(doc_name)

    # Создать HTTP-ответ, который будет содержать созданный документ
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename={doc_name}'

    with io.open(doc_name, 'rb') as file:
        document_bytes = file.read()

    response['Content-Length'] = len(document_bytes)
    response.write(document_bytes)
    return response

countsecond = 0
def download_document1(request, stud_id): #заседание ГАК
    global countsecond
    countsecond += 1
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    current_time = datetime.datetime.today()
    today = date.today()
    logging.basicConfig(filename='example2.log', level=logging.DEBUG)
    student = get_object_or_404(Students, id=stud_id)
    commission1 = get_object_or_404(Commissions, id=1)
    commission2 = get_object_or_404(Commissions, id=2)
    commission3 = get_object_or_404(Commissions, id=3)
    commission4 = get_object_or_404(Commissions, id=4)
    chairman = get_object_or_404(Chairmans, id=1)
    secretary = get_object_or_404(Secretary, id=1)
    context = {
        'student': student
    }
    name = student.name
    lastname = student.lastname
    middlename = student.middlename
    speciality = student.speciality
    diplomatitle = student.diploma_title
    advisor = student.advisor
    advisor_scientific_degree = student.advisor_scientific_degree
    gradee = Grade.objects.filter(student=student).aggregate(Avg('value'))['value__avg']
    grade = round(gradee)
    defense = Defense.objects.get(student=student)
    com1 = Grade.objects.get(commission=1, student=student).question
    com2 = Grade.objects.get(commission=2, student=student).question
    com3 = Grade.objects.get(commission=3, student=student).question
    com4 = Grade.objects.get(commission=4, student=student).question

    # com1q = com1.question

    letter_grade = ' '
    if 100 >= grade >= 95:
        letter_grade = 'A'
    elif 95 > grade >= 90:
        letter_grade = 'A-'
    elif 90 > grade >= 85:
        letter_grade = 'B+'
    elif 85 > grade >= 80:
        letter_grade = 'B'
    elif 80 > grade >= 75:
        letter_grade = 'B-'
    elif 75 > grade >= 70:
        letter_grade = 'C+'
    elif 70 > grade >= 65:
        letter_grade = 'C'
    elif 65 > grade >= 60:
        letter_grade = 'C-'
    elif 60 > grade >= 55:
        letter_grade = 'D+'
    elif 55 > grade >= 50:
        letter_grade = 'D'
    elif 50 > grade >= 25:
        letter_grade = 'FX'
    elif 25 > grade >= 0:
        letter_grade = 'F'

    firstcommision = commission1.lastname + ' ' + commission1.name + ' ' + commission1.middlename
    secondcommision = commission2.lastname + ' ' + commission2.name + ' ' + commission2.middlename
    thirdcommision = commission3.lastname + ' ' + commission3.name + ' ' + commission3.middlename
    fourthcommision = commission4.lastname + ' ' + commission4.name + ' ' + commission4.middlename

    firstchairman = chairman.lastname + ' ' + chairman.name + ' ' + chairman.middlename

    firstinitials = commission1.initials
    secondinitials = commission2.initials
    thirdinitials = commission3.initials
    fourthinitials = commission4.initials
    fifthinitials = chairman.initials
    sixthinitials = secretary.initials

    starttimehour = defense.start_time.hour
    starttimeminute = defense.start_time.minute
    endtimehour = defense.end_time.hour
    endtimeminute = defense.end_time.minute

    comment = defense.coment

    d1 = today.strftime("%d.%m.%Y")



    doc = DocxTemplate("bboard2/static/protocol_1.docx")

    context = {
        "number": countsecond,
        "day": current_time.day,
        "month": current_time.strftime('%B'),
        "year": current_time.year,
        "lastname": lastname,
        "name": name,
        "middlename": middlename,
        "speciality": speciality,
        "firstcommision": firstcommision,
        "secondcommision": secondcommision,
        "thirdcommision": thirdcommision,
        "fourthcommision": fourthcommision,
        "firstchairman": firstchairman,
        "firstinitials": firstinitials,
        "secondinitials": secondinitials,
        "thirdinitials": thirdinitials,
        "fourthinitials": fourthinitials,
        "fifthinitials": fifthinitials,
        "sixthinitials":sixthinitials,
        "starttimehour": starttimehour,
        "starttimeminute": starttimeminute,
        "endtimehour": endtimehour,
        "endtimeminute": endtimeminute,
        "grade": grade,
        "letter_grade": letter_grade,
        "advisor": advisor,
        "advisor_scientific_degree": advisor_scientific_degree,
        "diplomatitle": diplomatitle,
        "comment": comment,
        "com1": com1,
        "com2": com2,
        "com3": com3,
        "com4": com4
    }

    doc.render(context)

    doc.save("{0}_{1}_Протокол_2.docx".format(name, lastname))
    doc_name = f"{name}_{lastname}_Протокол_2.docx"
    logging.debug("Document name: {}".format(doc_name))
    print(doc_name)

    # Создать HTTP-ответ, который будет содержать созданный документ
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename={doc_name}'

    with io.open(doc_name, 'rb') as file:
        document_bytes = file.read()

    response['Content-Length'] = len(document_bytes)
    response.write(document_bytes)
    return response

def download_presentation(request, pk):
    student = get_object_or_404(Students, pk=pk)
    context = {
        'student': student
    }
    presentation = student.prez_diploma
    pre_name = presentation.name
    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = f'attachment; filename={presentation}'
    with io.open(pre_name, 'rb') as file:
        document_bytes = file.read()

    response['Content-Length'] = len(document_bytes)
    response.write(document_bytes)

    return response

# def download_presentation(request, pk):
#     student = get_object_or_404(Students, pk=pk)
#     context = {
#         'student': student
#     }
#     file = student.prez_diploma
#     response = HttpResponse(file, content_type='application/force-download')
#     response['Content-Disposition'] = 'attachment; filename="%s"' % file.name
#     return response


def edit_stud_page(request):
    return render(request, 'edit_stud_page.html', {'username': auth.get_user(request).username})

def forgot_pw(request):
    return render(request, 'forgot_pw.html')

def documents(request):
    students = Students.objects.all()
    return render(request, 'document_page.html', {'students': students})

def documents_second(request):
    students = Students.objects.all()
    return render(request, 'document_page_second.html', {'students': students, 'username': auth.get_user(request).username})

def documents_third(request):
    students = Students.objects.all()
    return render(request, 'document_page_third.html', {'students': students, 'username': auth.get_user(request).username})

def students(request):
    students = Students.objects.all()
    context = {
        'username': auth.get_user(request).username,
        'students': students
    }
    return render(request, 'students.html', context)

def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        lastname = request.POST.get('lastname')
        middlename = request.POST.get('middlename')
        birthday = request.POST.get('birthday')
        diploma_title = request.POST.get('diploma_title')
        img = request.FILES['images']

        stud = Students(
            img = img,
            name = name,
            lastname = lastname,
            middlename = middlename,
            birthday = birthday,
            diploma_title = diploma_title
        )
        stud.save()
        return redirect('students_list')
    return render(request, 'students.html')


def delete_student(request, stud_id):
    stud = Students.objects.filter(id=stud_id)

    if request.method == 'POST':
        stud.delete()
        return redirect('students_list')

    context = {
        'stud': stud,
    }
    return render('students_list', context)
#
# class GradeView(FormView):
#     template_name = 'grades.html'
#     form_class = GradeForm
#
#     def form_valid(self, form):
#         grade = form.save(commit=False)
#         grade.commission = self.request.user
#         grade.save()
#         return super().form_valid(form)
#
#
# def login_page(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             if user.is_secretary:
#                 user.groups.add(Group.objects.get(name='secretaries'))
#                 login(request, user)
#                 return redirect('index.html')
#             elif user.is_commission:
#                 user.groups.add(Group.objects.get(name='commission'))
#             login(request, user)
#             return redirect('commissions.html')
#         else:
#             return render(request, 'login_page.html', {'error': 'Неправильное имя пользователя или пароль'})
#     else:
#         return render(request, 'login_page.html')
#
# @login_required(login_url='/login/')
# def index(request):
#     if request.user.is_secretary:
#         return render(request, 'index.html', {'username': auth.get_user(request).username})
#     else:
#         return redirect('login_page.html')
#
# @login_required(login_url='/login/')
# def commissions(request):
#     if request.user.is_commission:
#         return render(request, 'commissions.html', {'username': auth.get_user(request).username})
#     else:
#         return redirect('login_page.html')
#
# def is_secretary(user):
#     return user.groups.filter(name='secretaries').exists()
#
# @user_passes_test(is_secretary)
# @login_required
# def index(request):
#     return render(request, 'index.html', {'username': auth.get_user(request).username})
#
# def is_commission(user):
#     return user.groups.filter(name='commission').exists()
#
# @user_passes_test(is_commission)
# @login_required
# def commissions(request):
#     return render(request, 'commissions.html', {'username': auth.get_user(request).username})