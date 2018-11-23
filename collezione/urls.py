from django.urls import path, re_path
from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth import urls

app_name = 'collezione'

urlpatterns = [
    re_path(r'^$', LoginView.as_view(), name ='login'),
    re_path(r'^login/$', LoginView.as_view(), name ='login'),
    re_path(r'^registrazione/$', views.RegistrazioneView.as_view(), name ='registrazione'),
    re_path(r'^registrazione/reg$', views.registrazione, name ='signupReg'),
    re_path(r'^homepage/$', views.homepage, name='homepage'),
    re_path(r'^homepage/editprofile/$', views.ModificaProfiloView.as_view(), name='editprofile'),
    re_path(r'^homepage/modificaProfilo/$', views.modificaProfilo, name='modificaProfilo'),
    re_path(r'^homepage/profilo/$', views.profilo, name='profilo'),
    re_path(r'^homepage/catalogo/$', views.catalogo, name='catalogo'),
    re_path(r'^homepage/catalogo/dettaglio/(?P<moneta_id>[0-9]+)/$', views.dettaglioMoneta, name='dettaglio_moneta'),
    re_path(r'^homepage/catalogo/dettaglio/imposta_dettaglio_moneta/$', views.impostaDettaglioMoneta, name='imposta_dettaglio_moneta'),
    re_path(r'^homepage/utenti/$', views.utenti, name='utenti'),
    ]
