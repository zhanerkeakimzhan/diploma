import logging
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from pyexpat.errors import messages
from .forms import DefenseForm
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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
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
            elif user.groups.filter(name='chairman').exists():
                return redirect('chair_main')
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


@login_required
@user_passes_test(lambda u: u.groups.filter(name='commission').exists())
def com_main(request):
    date_query = request.GET.get('date', datetime.date.today())  # Получение значения фильтрации по дате

    studentss = Students.objects.all()

    if date_query:
        # Фильтрация студентов по дате сдачи
        studentss = studentss.filter(date=date_query)

    context = {
        'username': auth.get_user(request).username,
        'students': studentss,
        'date_query': date_query  # Передача значения фильтрации по дате в контекст
    }
    return render(request, 'com_main.html', context)


def chair_main(request):
    query = request.GET.get('date', datetime.date.today())  # Получение значения фильтрации по дате

    students = Students.objects.all()

    if query:
        # Фильтрация студентов по дате сдачи
        students = students.filter(date=query)

    context = {
        'username': auth.get_user(request).username,
        'students': students,
        'date_query': query  # Передача значения фильтрации по дате в контекст
    }

    return render(request, 'chairman_main.html', context)


student_ids = []


def students(request):
    query = request.GET.get('date', datetime.date.today())  # Получение значения фильтрации по дате

    studentss = Students.objects.all()

    if query:
        # Фильтрация студентов по дате сдачи
        studentss = studentss.filter(date=query)

    context = {
        'username': auth.get_user(request).username,
        'students': studentss,
        'date_query': query  # Передача значения фильтрации по дате в контекст
    }

    global student_ids
    student_ids = [student.id for student in studentss]

    # Отправка значения фильтрации по дате обратно на страницу
    # чтобы сохранить введенную дату в поле поиска
    context['date_query'] = query

    # return HttpResponse(f"айдишки: {student_ids}")
    return render(request, 'students.html', context)


def logout_page(request):
    logout(request)
    return redirect('login')


def commissions(request):
    return render(request, 'commissions.html', {'username': auth.get_user(request).username})


def student_page(request, id):
    student = get_object_or_404(Students, id=id)

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

    return render(request, 'student_page.html', context)


def add_time(request, id):
    student = get_object_or_404(Students, id=id)
    start_time = request.POST.get("start_time")
    end_time = request.POST.get("end_time")
    comment = request.POST.get("comment")
    page_number = request.POST.get("page_number")
    picture_number = request.POST.get("picture_number")
    text_input = request.POST.get("text_input")
    text_input_1 = request.POST.get("text_input_1")
    score = request.POST.get("score")
    text_area = request.POST.get("text_area")
    comment_2 = request.POST.get("comment_2")
    comment_3 = request.POST.get("comment_3")

    add_data = Defense(student=student, start_time=start_time, end_time=end_time, coment=comment,
                       page_number=page_number, picture_number=picture_number, text_input=text_input,
                       text_input_1=text_input_1, score=score, text_area=text_area, comment_2=comment_2,
                       comment_3=comment_3)
    add_data.save()

    add_data.is_filled = True
    add_data.save()

    # return HttpResponse(f"student: {student} <br> start_time:{start_time} <br> end_time:{end_time} <br> comment:{comment}"
    #                     f"<br> page_number:{page_number} <br> picture_number:{picture_number} <br> text_input:{text_input} "
    #                     f"<br> text_input_1:{text_input_1} <br> score:{score} <br> text_area:{text_area} "
    #                     f"<br> comment_2:{comment_2} <br> comment_3:{comment_3} ")
    return redirect('student_page_second', id=id)


def student_page_second(request, id):
    student = get_object_or_404(Students, id=id)
    student_id = student.id

    defense = Defense.objects.get(student=student_id)

    start_time = defense.start_time
    end_time = defense.end_time
    comment = defense.coment
    page_number = defense.page_number
    picture_number = defense.picture_number
    text_input = defense.text_input
    text_input_1 = defense.text_input_1
    score = defense.score
    text_area = defense.text_area
    comment_2 = defense.comment_2
    comment_3 = defense.comment_3

    context = {
        'username': auth.get_user(request).username,
        'student': student,
        'start_time': start_time,
        'end_time': end_time,
        'comment': comment,
        'page_number': page_number,
        'picture_number': picture_number,
        'text_input': text_input,
        'text_input_1': text_input_1,
        'score': score,
        'text_area': text_area,
        'comment_2': comment_2,
        'comment_3': comment_3
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


def chair_stud_page(request, id):
    student = get_object_or_404(Students, id=id)
    user_profile = request.user.userprofile
    chairman = get_object_or_404(Chairmans, id=user_profile.chairman.id)

    context = {
        'username': auth.get_user(request).username,
        'student': student
    }

    try:
        grade = Grade.objects.get(chairman=chairman, student=student)
        if grade.is_filled:
            return redirect('chair_stud_page_second', id=id)
    except Grade.DoesNotExist:
        pass

    return render(request, 'chair_stud_page.html', context)


def add_grade(request, id):
    student = get_object_or_404(Students, id=id)
    user_profile = request.user.userprofile
    commission = get_object_or_404(Commissions, id=user_profile.commission.id)
    question = request.POST.get("question")
    value = request.POST.get("value")

    add_data = Grade(commission=commission, student=student, question=question, value=value)
    add_data.save()

    add_data.is_filled = True
    add_data.save()

    request.session['grade_data'] = {
        'student': student.id,
        'commission': commission.id,
        'question': question,
        'value': value
    }

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


def add_grade_chair(request, id):
    student = get_object_or_404(Students, id=id)
    user_profile = request.user.userprofile
    chairman = get_object_or_404(Chairmans, id=user_profile.chairman.id)
    question = request.POST.get("question")
    value = request.POST.get("value")

    add_data = Grade(chairman=chairman, student=student, question=question, value=value)
    add_data.save()

    add_data.is_filled = True
    add_data.save()

    return redirect('chair_stud_page_second', id=id)


def chair_stud_page_second(request, id):
    student = get_object_or_404(Students, id=id)
    student_id = student.id

    user_profile = request.user.userprofile
    chairman = get_object_or_404(Chairmans, id=user_profile.chairman.id)
    chairman_id = chairman.id

    grade_data = request.session.get('grade_data')

    grade = Grade.objects.get(chairman=chairman_id, student=student_id)

    question = grade.question
    value = grade.value

    context = {
        'username': auth.get_user(request).username,
        'student': student,
        'grade_data': grade_data,
        'question': question,
        'value': value,
        'grade': grade,
    }

    return render(request, 'chair_stud_page_second.html', context)


def update_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    value = request.POST.get("value")

    grade.value = value
    grade.save()

    return redirect('chair_stud_page_second', id=grade.student.id)


count = 0


def download_document(request, stud_id):  # решение ГАК
    global count
    count += 1
    locale.setlocale(locale.LC_ALL, 'kk_KZ.UTF-8')
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

    fc = commission1.scientific_degree
    sc = commission2.scientific_degree
    thc = commission3.scientific_degree
    foc = commission4.scientific_degree

    fch = chairman.scientific_degree

    starttimehour = defense.start_time.hour
    starttimeminute = defense.start_time.minute
    endtimehour = defense.end_time.hour
    endtimeminute = defense.end_time.minute
    diploma_title = student.diploma_title

    comment = defense.coment

    d1 = today.strftime("%d.%m.%Y")

    doc = DocxTemplate("bboard2/static/protocol_2_kz.docx")

    context = {
        'student': student,
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
        "sixthinitials": sixthinitials,
        "d1": d1,
        "starttimehour": starttimehour,
        "starttimeminute": starttimeminute,
        "endtimehour": endtimehour,
        "endtimeminute": endtimeminute,
        "grade": grade,
        "letter_grade": letter_grade,
        "comment": comment,
        "diploma_title": diploma_title,
        "fc": fc,
        "sc": sc,
        "thc": thc,
        "foc": foc,
        "fch": fch,
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


def download_document1(request, stud_id):  # заседание ГАК протокол 1
    global countsecond
    countsecond += 1
    locale.setlocale(locale.LC_ALL, 'kk_KZ.UTF-8')
    current_time = datetime.datetime.today()
    logging.basicConfig(filename='example2.log', level=logging.DEBUG)
    student = get_object_or_404(Students, id=stud_id)
    commission1 = get_object_or_404(Commissions, id=1)
    commission2 = get_object_or_404(Commissions, id=2)
    commission3 = get_object_or_404(Commissions, id=3)
    commission4 = get_object_or_404(Commissions, id=4)
    chairman = get_object_or_404(Chairmans, id=1)
    secretary = get_object_or_404(Secretary, id=1)

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
    chair = Grade.objects.get(chairman=1, student=student).question

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

    fc = commission1.scientific_degree
    sc = commission2.scientific_degree
    thc = commission3.scientific_degree
    foc = commission4.scientific_degree

    fch = chairman.scientific_degree

    starttimehour = defense.start_time.hour
    starttimeminute = defense.start_time.minute
    endtimehour = defense.end_time.hour
    endtimeminute = defense.end_time.minute

    comment = defense.coment
    page_number = defense.page_number
    picture_number = defense.picture_number
    text_input = defense.text_input  # отзыв рук
    text_input_1 = defense.text_input_1  # заключение эксперта
    score = defense.score
    text_area = defense.text_area
    comment_2 = defense.comment_2
    comment_3 = defense.comment_3

    doc = DocxTemplate("bboard2/static/protocol_1_kz.docx")

    context = {
        'student': student,
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
        "sixthinitials": sixthinitials,
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
        "com4": com4,
        "chair": chair,
        "page_number": page_number,
        "picture_number": picture_number,
        "text_input": text_input,  # отзыв рук
        "text_input_1": text_input_1,  # заключение эксперта
        "score": score,  # оценка рецензента
        "text_area": text_area,  # Неофициальные отзывы
        "comment_2": comment_2,  # Общая характеристика ответов
        "comment_3": comment_3,  # Уровень знаний
        "fc": fc,
        "sc": sc,
        "thc": thc,
        "foc": foc,
        "fch": fch,
    }

    doc.render(context)

    doc.save("{0}_{1}_Протокол_1.docx".format(name, lastname))
    doc_name = f"{name}_{lastname}_Протокол_1.docx"
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


def download_document3(request):  # ведомость
    doc = DocxTemplate("bboard2/static/statement_kz.docx")
    commission1 = get_object_or_404(Commissions, id=1)
    commission2 = get_object_or_404(Commissions, id=2)
    commission3 = get_object_or_404(Commissions, id=3)
    commission4 = get_object_or_404(Commissions, id=4)
    chairman = get_object_or_404(Chairmans, id=1)
    secretary = get_object_or_404(Secretary, id=1)
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

    global student_ids

    studentss = []

    countthird = 0

    for student_id in student_ids:
        student = get_object_or_404(Students, id=student_id)
        countthird += 1

        gradee = Grade.objects.filter(student=student).aggregate(Avg('value'))['value__avg']
        grade = round(gradee)

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

        if 100 >= grade >= 90:
            tgrade = 5
        elif 89 >= grade >= 75:
            tgrade = 4
        elif 74 >= grade >= 50:
            tgrade = 3
        else:
            tgrade = 2

        defense = Defense.objects.get(student=student)
        agrade = defense.text_input
        rgrade = defense.score

        com1 = Grade.objects.get(commission=1, student=student).value
        com2 = Grade.objects.get(commission=2, student=student).value
        com3 = Grade.objects.get(commission=3, student=student).value
        com4 = Grade.objects.get(commission=4, student=student).value
        chair1 = Grade.objects.get(chairman=1, student=student).value

        studentss.append({
            'name': student.name,
            'lastname': student.lastname,
            'middlename': student.middlename,
            "grade": grade,
            "letter_grade": letter_grade,
            "agrade": agrade,
            "rgrade": rgrade,
            "com1": com1,
            "com2": com2,
            "com3": com3,
            "com4": com4,
            "chair1": chair1,
            "tgrade": tgrade,
            "countthird": countthird,
        })

    locale.setlocale(locale.LC_ALL, 'kk_KZ.UTF-8')
    current_time = datetime.datetime.today()

    context = {
        'studentss': studentss,
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
        "sixthinitials": sixthinitials,
        "day": current_time.day,
        "month": current_time.strftime('%B'),
        "year": current_time.year,
    }

    doc.render(context)

    doc.save("ведомость.docx")
    doc_name = "ведомость.docx"

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
    presentation = student.prez_diploma
    file_path = presentation.path

    with open(file_path, 'rb') as file:
        document_bytes = file.read()

    response = HttpResponse(document_bytes, content_type='application/force-download')
    response['Content-Disposition'] = f'attachment; filename={presentation.name}'
    response['Content-Length'] = len(document_bytes)

    return response


def download_diploma(request, pk):
    student = get_object_or_404(Students, pk=pk)
    diplomaa = student.diploma
    file_path = diplomaa.path

    with open(file_path, 'rb') as file:
        document_bytes = file.read()

    response = HttpResponse(document_bytes,
                            content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{diplomaa.name}"'
    response['Content-Length'] = len(document_bytes)

    return response


def download_recen(request, pk):
    student = get_object_or_404(Students, pk=pk)
    recen = student.recen_diploma
    file_path = recen.path

    with open(file_path, 'rb') as file:
        document_bytes = file.read()

    response = HttpResponse(document_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{recen.name}"'
    response['Content-Length'] = len(document_bytes)

    return response


def download_feedback(request, pk):
    student = get_object_or_404(Students, pk=pk)
    feedback = student.feedback_diploma
    file_path = feedback.path

    with open(file_path, 'rb') as file:
        document_bytes = file.read()

    response = HttpResponse(document_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{feedback.name}"'
    response['Content-Length'] = len(document_bytes)

    return response


def download_antiplagiat(request, pk):
    student = get_object_or_404(Students, pk=pk)
    antiplagiat = student.antiplagiat
    file_path = antiplagiat.path

    with open(file_path, 'rb') as file:
        document_bytes = file.read()

    response = HttpResponse(document_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{antiplagiat.name}"'
    response['Content-Length'] = len(document_bytes)

    return response


def edit_stud_page(request):
    return render(request, 'edit_stud_page.html', {'username': auth.get_user(request).username})


def forgot_pw(request):
    return render(request, 'forgot_pw.html')


def com_list(request):
    commissionss = Commissions.objects.all()
    chairmans = Chairmans.objects.all()
    context = {
        'username': auth.get_user(request).username,
        'commissions': commissionss,
        'chairmans': chairmans
    }
    return render(request, 'com_list.html', context)


def com_page(request, id):
    commission = get_object_or_404(Commissions, id=id)

    context = {
        'username': auth.get_user(request).username,
        'commission': commission,
    }

    return render(request, 'com_page.html', context)


def chair_page(request, id):
    chairman = get_object_or_404(Chairmans, id=id)

    context = {
        'username': auth.get_user(request).username,
        'chairman': chairman,
    }

    return render(request, 'chair_page.html', context)