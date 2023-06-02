from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from bboard2 import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('index/', views.index, name='index'),
    path('com_main/', views.com_main, name='com_main'),
    path('chair_main/', views.chair_main, name='chair_main'),
    path('forgot/', views.forgot_pw, name='forgot'),
    path('student/<int:id>/', views.student_page, name='student_page'),
    path('student_second/<int:id>/', views.student_page_second, name='student_page_second'),
    path('com_student/<int:id>/', views.com_stud_page, name='com_stud_page'),
    path('chair_student/<int:id>/', views.chair_stud_page, name='chair_stud_page'),
    path('com_student_second/<int:id>/', views.com_stud_page_second, name='com_stud_page_second'),
    path('chair_student_second/<int:id>/', views.chair_stud_page_second, name='chair_stud_page_second'),
    path('add_grade/<int:id>/', views.add_grade, name='add_grade'),
    path('add_grade_chair/<int:id>/', views.add_grade_chair, name='add_grade_chair'),
    path('update_grade/<int:grade_id>/', views.update_grade, name='update_grade'),
    path('add_time/<int:id>/', views.add_time, name='add_time'),
    path('edit_stud/', views.edit_stud_page, name='edit_stud'),
    path('students/', views.students, name='students_list'),
    path('commissions/', views.commissions, name='commissions_list'),
    path('com_list/', views.com_list, name='com_list'),
    path('com_page/<int:id>/', views.com_page, name='com_page'),
    path('chair_page/<int:id>/', views.chair_page, name='chair_page'),
    path('download/<int:stud_id>/', views.download_document, name='download_document'),
    path('download1/<int:stud_id>/', views.download_document1, name='download_document1'),
    path('download3/', views.download_document3, name='download_document3'),
    path('download_presentation/<int:pk>/', views.download_presentation, name='download_presentation'),
    path('download_diploma/<int:pk>/', views.download_diploma, name='download_diploma'),
    path('download_recen/<int:pk>/', views.download_recen, name='download_recen'),
    path('download_feedback/<int:pk>/', views.download_feedback, name='download_feedback'),
    path('download_antiplagiat/<int:pk>/', views.download_antiplagiat, name='download_antiplagiat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)