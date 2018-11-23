from django.urls import path, re_path
from . import views
from django.contrib.auth import urls

app_name = 'scambio'

urlpatterns = [
    re_path(r'^scambio/archivio/vota/$', views.vota, name='vota'),
    re_path(r'^scambio/archivio/$', views.archivio, name='archivio'),
    re_path(r'^scambio/selezionaControfferta/contrOffertaSelezionata$', views.contrOffertaSelezionata, name='contrOffertaSelezionata'),
    re_path(r'^scambio/selezionaControfferta/$', views.selezionaControfferta, name='selezionaControfferta'),
    re_path(r'^scambio/(?P<username>[0-9a-zA-Z]+)/$', views.propostaScambio, name='propostaScambio'),
    re_path(r'^scambio/$', views.principale, name='principale'),
]
