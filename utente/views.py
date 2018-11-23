from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from collezione.models import *
from collezione.views import checkUser, getStatics
from django.contrib import messages

# Create your views here.
def principale(request, username):
    '''
    View principale, la homepage di un altro utente.
    :param request:
    :param username: utente selezionato
    :return: render del template principale se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user_dettaglio = get_object_or_404(User, username=username)
        context['user_dettaglio'] = user_dettaglio
        return render(request, 'utente/principale.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def catalogo(request, username):
    '''
    Catalogo dell'utente selezionato.
    Sono mostrate solo le monete che possiede.
    :param request:
    :param username: utente selezionato
    :return: render del template catalogo se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = context['user']
        user_dettaglio = get_object_or_404(User, username=username) #user selezionato
        context['user_dettaglio'] = user_dettaglio
        #valori per le select dei filtri
        nazionalita_select = Moneta.getNazionalita()
        valori_select = Moneta.getValori()
        #recupero monete possedute e filtrate secondo i filtri di ricerca inseriti dall'utente
        monete = user_dettaglio.utente.moneta_set.all().filter(possiede__posseduta=True)
        if request.method == 'POST':
            nazionalita = request.POST['select_nazionalita']
            valore = request.POST['select_valore']
            da_scambiare = request.POST.get('select_da_scambiare', 'false')
            #Serve per poter filtrare anche i 1.0€ e 2.0€, altrimenti non funziona
            if str(valore).endswith('0'):
                valore = valore[0]

            monete = user_dettaglio.utente.moneta_set.filter(possiede__da_scambiare__regex='^' + da_scambiare + '$',
                                              nazionalita__regex='^' + nazionalita + '$',
                                              valore__regex='^' + valore + '$').order_by('nazionalita', 'valore')
        context['monete'] = monete
        context['possedute'] = user.utente.moneta_set.all().filter(possiede__posseduta=True)
        context['valori_select'] = valori_select
        context['nazionalita_select'] = nazionalita_select
        return render(request, 'utente/catalogo.html', context=context)
    else:
        return HttpResponseRedirect(reverse('login'))

def dettaglioMoneta(request, username, moneta_id):
    '''
    View del dettaglio di una moneta.
    :param request:
    :param username: user avente tale moneta
    :return: render del template dettaglio_moneta se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user_dettaglio = User.objects.get(username=username)
        #recupero moneta richiesta
        moneta = Moneta.objects.get(pk=int(moneta_id))
        try:
            possiede = moneta.possiede_set.get(utente__user=context['user'])
        except Possiede.DoesNotExist:
            Possiede.objects.create(utente=context['user'].utente, moneta=moneta)
        possiede_dettaglio = moneta.possiede_set.get(utente__user=user_dettaglio)
        context['possiede'] = possiede
        context['possiede_dettaglio'] = possiede_dettaglio
        context['moneta'] = moneta
        context['user_dettaglio'] = user_dettaglio
        return render(request, 'utente/dettaglio_moneta.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def profilo(request, username):
    '''
    Profilo dell'utente selezionato.
    :param request:
    :param username: utente selezionato
    :return: render del template profilo se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    statics = []
    if context is not None:
        user_dettaglio = User.objects.get(username=username)
        context['user_to_show'] = user_dettaglio
        statics = getStatics(user_dettaglio)
        for key,item in statics.items():
            context[key] = item
        return render(request, 'collezione/profilo.html', context=context)
    return HttpResponseRedirect(reverse('login'))