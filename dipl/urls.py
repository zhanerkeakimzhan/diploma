from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('bboard2.urls')),
    path('admin/', admin.site.urls),
]