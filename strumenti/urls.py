from django.urls import path, re_path
from . import views
from django.contrib.auth import urls

app_name = 'strumenti'

urlpatterns = [
    re_path(r'^principale/cerca$', views.cercaMonete, name='cerca'),
    re_path(r'^principale/$', views.principale, name ='principale'),
    re_path(r'^principale/acquisti$', views.acquisti, name ='acquisti'),
    re_path(r'^principale/vendite/$', views.vendite, name ='vendite'),
    re_path(r'^principale/vendite/vota/$', views.vota, name ='vota'),
    re_path(r'^principale/messaggi/$', views.messaggi, name ='messaggi'),
    re_path(r'^principale/messaggi/eliminaMessaggi/(?P<username>[a-zA-Z0-9_]+)/$', views.eliminaMessaggi, name ='eliminaMessaggi'),
    re_path(r'^principale/messaggi/(?P<username>[a-zA-Z0-9_]+)/$', views.messaggio, name ='messaggio'),
    re_path(r'^principale/messaggi/(?P<username>[a-zA-Z0-9_]+)/invia/$', views.inviaMessaggio, name ='inviaMessaggio'),
]
