from django.urls import path, re_path
from . import views
from django.contrib.auth import urls

app_name = 'vendita'

urlpatterns = [
    re_path(r'^catalogo_utente/dettaglio/confermaAcquisto/(?P<username>[0-9a-zA-Z]+)/$', views.confermaAcquisto, name='confermaAcquisto'),
    re_path(r'^catalogo_utente/dettaglio/acquista/(?P<username>[0-9a-zA-Z]+)/$', views.acquista, name='acquista'),
    re_path(r'^catalogo/dettaglio/imposta/$', views.impostaDettaglioMoneta, name='imposta_dettaglio_moneta'),
    re_path(r'^catalogo/dettaglio/(?P<moneta_id>[0-9]+)/$', views.dettaglioMoneta, name='dettaglio_moneta'),
    re_path(r'^catalogo/$', views.catalogo, name='catalogo'),
    re_path(r'^homepage/$', views.homepage, name='homepage'),
    ]