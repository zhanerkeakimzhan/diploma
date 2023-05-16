from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from bboard2 import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('index/', views.index, name='index'),
    path('com_main/', views.com_main, name='com_main'),
    path('forgot/', views.forgot_pw, name='forgot'),
    path('documents/', views.documents, name='documents'),
    path('student/<int:id>/', views.student_page, name='student_page'),
    path('com_student/<int:id>/', views.com_stud_page, name='com_stud_page'),
    path('com_student_second/<int:id>/', views.com_stud_page_second, name='com_stud_page_second'),
    path('add_grade/<int:id>/', views.add_grade, name='add_grade'),
    path('edit_stud/', views.edit_stud_page, name='edit_stud'),
    path('students/', views.students, name='students_list'),
    path('commissions/', views.commissions, name='commissions_list'),
    path('documents/', views.documents, name='documents_list'),
    path('documentssecond/', views.documents_second, name='documents_list_second'),
    path('documentsthird/', views.documents_third, name='documents_list_third'),
    path('add/', views.add_student, name='add_students'),
    path('delete/<int:stud_id>/', views.delete_student, name='delete_student'),
    path('download/<int:stud_id>/', views.download_document, name='download_document'),
    path('download1/<int:stud_id>/', views.download_document1, name='download_document1'),
    path('download_presentation/<int:pk>/', views.download_presentation, name='download_presentation')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)