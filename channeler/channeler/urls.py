# Django imports.
from django.contrib import admin
from django.urls import include, path

__author__ = 'Jason Parent'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    path('tasks/', include(('tasks.urls', 'tasks'))),
]
