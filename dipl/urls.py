from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, re_path, include
from bboard2 import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', include('bboard2.urls')),
    # path('bboard2', include('bboard2.urls')),
    path('admin/', admin.site.urls),
    # path('i18n/', include('django.conf.urls.i18n')),
]

#
# urlpatterns += i18n_patterns(
#     path('bboard2', include('bboard2.urls')),
#
# )