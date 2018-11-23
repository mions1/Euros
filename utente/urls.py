from django.urls import path, re_path
from . import views
from django.contrib.auth import urls

app_name = 'utente'

urlpatterns = [
    re_path(r'^(?P<username>[a-zA-Z0-9]+)/profilo/$', views.profilo, name='profilo'),
    re_path(r'^(?P<username>[a-zA-Z0-9]+)/$', views.principale, name='principale'),
    re_path(r'^(?P<username>[a-zA-Z0-9]+)/catalogo/$', views.catalogo, name='catalogo'),
    re_path(r'^(?P<username>.+)/catalogo/dettaglio/(?P<moneta_id>[0-9]+)/$', views.dettaglioMoneta, name='dettaglio_moneta'),
]
