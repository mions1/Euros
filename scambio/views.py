from django.shortcuts import render
from collezione.views import *
from collezione.models import *
from django.db.models import Q
from django.contrib import messages

# Create your views here.
def principale(request):
    '''
    Vista principale.
    Definisce la vista principale, ovvero dove c'è la lista di tutti gli scambi ancora non completati.
    :param request:
    :return: render del template della vista se loggati, altrimenti torno al login
    '''
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        #recupero degli scambi dove è presente l'utente (come offerente o ricevente) e per i quali non c'è stata la conferma
        #di entrambe le parti
        scambi = Scambio.objects.filter( Q(offerente=user.utente) | Q(ricevente=user.utente) ).order_by('data')
        scambi = scambi.filter( Q(confermaOfferente=False) | Q(confermaRicevente=False) )
        context['scambi'] = scambi
        return render(request, 'scambio/principale.html', context)
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def archivio(request):
    '''
    Vista archivio.
    Definisce la vista dell'archivio, ovvero la lista degli scambi completati.
    :param request:
    :return: render del template dell'archivio se loggati, redirect vero il login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        scambi = Scambio.objects.filter( Q(offerente=user.utente) | Q(ricevente=user.utente) ).order_by('data')
        scambi = scambi.filter( Q(confermaOfferente=True) & Q(confermaRicevente=True) )
        context['scambi'] = scambi
        return render(request, 'scambio/archivio.html', context)
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def vota(request):
    '''
    Aggiunge il voto dato da una delle parti dello scambio all'altra ed aggiorna l'affidabilità dell'utente che ha ricevuto il voto
    :param request:
    :return: render del template dell'archivo se loggati, altrimenti torno al login
    '''
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        #recupero degli scambi completati
        scambi = Scambio.objects.filter(Q(offerente=user.utente) | Q(ricevente=user.utente)).order_by('data')
        scambi = scambi.filter(Q(confermaOfferente=True) & Q(confermaRicevente=True))
        context['scambi'] = scambi
        if request.method == 'POST':
            try:
                voto = int(request.POST['voto'][0]) #voto dato
            except KeyError:
                messages.error(request, 'Non hai selezionato nessun voto')
                return HttpResponseRedirect(reverse('scambio:archivio'))
            id = int(request.POST['voto'][1:]) #id dello scambio da votare
            scambio = scambi.get(pk=id)
            offerente = scambio.offerente.user
            #se l'utente è l'offerente allora aggiungo il voto dato dall'offerente ed aggiorno l'affidabilità del ricevente
            if user.username == offerente.username:
                scambio.votoOfferente = voto
                scambio.save()
            #viceversa di quanto detto sopra
            else:
                scambio.votoRicevente = voto
                scambio.save()

        return HttpResponseRedirect(reverse('scambio:archivio'))
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def propostaScambio(request, username):
    '''
    Richiede uno scambio lo scambio di una moneta all'utente selezionata.
    :param request:
    :param username: username dell'utente a cui chiedere lo scambio
    :return: redirect verso il catalogo dell'utente ricevente se loggati, altrimenti verso il login
    '''
    context = checkUser(request)
    if context is not None:
        if request.method == 'POST':
            user = get_object_or_404(User, username=context['user'])
            username = get_object_or_404(User, username=username)
            moneta = Moneta.objects.get(id=request.POST['moneta_id'])
            Scambio.proponiScambio(user.utente, username.utente, moneta)
            messages.info(request, 'Proposta di scambio inviata')
        return  HttpResponseRedirect(reverse('utente:catalogo', args=(username,)))
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def selezionaControfferta(request):
    '''
    Selezione della moneta da richiedere all'offerente della proposta di scambio oppure conferma scambio.
    :param request:
    :return: redirect verso la view principale se si è confermato lo scambio, render del template di selezione della moneta
    da contro offrire se si è richiesta tale operazione, redirect verso il login se non si è loggati
    '''
    context = checkUser(request)
    if context is not None:
        if request.method == 'POST':
            user = get_object_or_404(User, username=context['user'])
            scambio = get_object_or_404(Scambio, id=request.POST['scambio_id'])
            try:
                #nel caso in cui si sta confermando la precedente scelta
                conferma = request.POST['conferma']
                #setto la conferma del ricevente se l'utente è il ricevente, viceversa altrimenti
                if conferma == 'ricevente':
                    scambio.confermaRicevente = True
                else:
                    scambio.confermaOfferente = True
                scambio.save()
                return HttpResponseRedirect(reverse('scambio:principale'))
            #nel caso in cui si deve selezionare la moneta da contro offrire
            except KeyError:
                #creazione context del catalogo dell'utente con sole le monete disponibili allo scambio
                user_dettaglio = get_object_or_404(User, username=request.POST['userdettaglio_id'])
                nazionalita_select = Moneta.getNazionalita()
                valori_select = Moneta.getValori()
                valori = Moneta.getValori()
                monete = user_dettaglio.utente.moneta_set.all().filter(possiede__posseduta=True)
                context['monete'] = monete
                context['valori_select'] = valori_select
                context['nazionalita_select'] = nazionalita_select
                context['valore_min'] = min(valori)
                context['valore_max'] = max(valori)
                context['scambio'] = scambio
                return render(request, 'scambio/selezionaControfferta.html', context)
        else:
            return HttpResponseRedirect(reverse('scambio:principale'))
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def contrOffertaSelezionata(request):
    '''
    Vista dopo aver selezionato una moneta da contro offrire.
    :param request:
    :return: redirect vero la schermata principale se si è loggati, verso il login altrimenti.
    '''
    context = checkUser(request)
    if context is not None:
        if request.method == 'POST':
            user = get_object_or_404(User, username=context['user'])
            moneta = get_object_or_404(Moneta, id=request.POST['moneta_id'])
            scambio = get_object_or_404(Scambio, id=request.POST['scambio_id'])
            scambio.monetaControOfferta = moneta
            scambio.save()
            return HttpResponseRedirect(reverse('scambio:principale'))
    else:
        return HttpResponseRedirect(reverse('collezione:login'))