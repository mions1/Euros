from django.shortcuts import render
from collezione.views import *
from collezione.models import *
from django.db.models import Q
from django.contrib import messages

# Create your views here.

def principale(request):
    '''
    View principale degli strumenti (messaggistica, scambi etc).
    :param request:
    :return: render del template principale se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        #recupero conteggio messaggi e scambi per segnalarli nella gui
        messaggi_count = user.utente.destinatario.filter(letto=False).count()
        scambi_ricevuti = user.utente.ricevente.filter(confermaRicevente=False)
        scambi_inviati = user.utente.offerente.filter(monetaControOfferta__isnull=False, confermaOfferente=False)
        scambi_count = scambi_ricevuti.count() + scambi_inviati.count()
        context ['messaggi_count'] = messaggi_count
        context ['scambi_count'] = scambi_count
        return render(request, 'strumenti/principale.html', context)
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def messaggi(request):
    '''
    View della lista delle conversazioni.
    :param request:
    :return: render del template messaggi se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        #recupero dei messaggi dove l'utente è mittente oppure destinatario e distinguerli in modo da avere una lista di
        #utenti con la quale l'utente ha avuto delle conversazioni
        messaggi = Messaggio.objects.filter( Q(destinatario=user.utente) | Q(mittente=user.utente) ).distinct('destinatario__user__username', 'mittente__user__username')
        interlocutori = []
        for messaggio in messaggi:
            if messaggio.mittente.user.username != user.username:
                if messaggio.mittente.user.username not in interlocutori:
                    interlocutori.append(messaggio.mittente.user.username)
            else:
                if messaggio.destinatario.user.username not in interlocutori:
                    interlocutori.append(messaggio.destinatario.user.username)
        if interlocutori == []:
            interlocutori = None
        context['messaggi'] = messaggi
        context['interlocutori'] = interlocutori
        return render(request, 'strumenti/messaggi.html', context)
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def messaggio(request, username):
    '''
    View di una conversazione
    :param request:
    :param username: user con il quale l'utente ha avuto la conversazione
    :return: render del template messaggio se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        user_messaggio = get_object_or_404(User, username=username)
        #recupero della conversazione tra l'utente e l'altro user
        messaggi = Messaggio.objects.filter( (Q(destinatario=user.utente) & Q(mittente=user_messaggio.utente))
                                             | (Q(destinatario=user_messaggio.utente) & Q(mittente=user.utente)) )
        messaggi.update(letto=True)
        context['messaggi'] = messaggi
        context['user_messaggio'] = user_messaggio
        return render(request, 'strumenti/messaggio.html', context)
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def acquisti(request):
    '''
    View della lista degli acquisti effettuati (nel caso si è, quindi, un collezionista)
    :param request:
    :return: render del template acquisti se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        acquisti = Acquisto.objects.filter( collezionista=user.utente ).order_by('data')
        context['acquisti'] = acquisti
        return render(request, 'strumenti/acquisti.html', context)
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def vendite(request):
    '''
    View della lista delle vendite (nel caso si è, quindi, un venditore)
    :param request:
    :return: render del template vendite se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        if (user.utente.collezionista):
            return HttpResponseRedirect(reverse('strumenti:principale'))
        vendite = Acquisto.objects.filter( venditore=user.utente ).order_by('data')
        context['vendite'] = vendite
        return render(request, 'strumenti/vendite.html', context)
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def cercaMonete(request):
    '''
    View per cercare monete da comprare o da scambiare
    :param request:
    :return: render del template cerca se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        nazionalita_select = Moneta.getNazionalita()
        valori_select = Moneta.getValori()
        nazione = request.POST.get('nazionalita', default=".+")
        valore = request.POST.get('valore',default=".+")
        scambio = request.POST.get('scambio', default="off")
        acquisto = request.POST.get('acquisto', default="off")
        non_possedute = request.POST.get('possedute', default="off")
        da_acquistare = request.POST.get('da_acquistare', default="off")
        if request.method != 'POST':
            scambio = "on"
            acquisto = "on"
            non_possedute = "on"
            da_acquistare = "on"

        if str(valore).endswith('0'):
            valore = valore[0]

        possiede_utente = user.utente.possiede_set.filter(posseduta=True)
        possiede_utente_da_acquistare = user.utente.possiede_set.filter(da_acquistare=True)
        possiede = Possiede.objects.filter( ~Q(utente = user.utente) & ( (Q(posseduta=True) & Q(da_scambiare=True)) | Q(prezzo__gt = 0.0) ) )\
            .order_by('utente__user__username', 'moneta__nazionalita', 'moneta__valore')
        possiede = possiede.filter( moneta__nazionalita__regex = '^' + nazione + '$',
                                moneta__valore__regex = '^' + valore + '$')

        if scambio == 'off':
            possiede = possiede.filter( utente__collezionista=False )
        if acquisto == 'off':
            possiede = possiede.filter( ~Q(utente__collezionista=False) )

        monete_utente = Moneta.objects.filter(pk__in=possiede_utente.values('moneta'))
        monete_utente_da_acquistare = Moneta.objects.filter(pk__in=possiede_utente_da_acquistare.values('moneta'))
        monete = Moneta.objects.filter(pk__in=possiede.values('moneta'))
        if non_possedute != 'off':
            possiede = possiede.filter( ~Q(moneta__in=monete_utente))
        if da_acquistare != 'off':
            possiede = possiede.filter( moneta__in=monete_utente_da_acquistare)

        context['possiede'] = possiede
        context['valori_select'] = valori_select
        context['nazionalita_select'] = nazionalita_select

        return render(request, 'strumenti/cerca.html', context)
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def vota(request):
    '''
    Metodo per inserire la votazione effettuata da un collezionista/venditore all'altra parte.
    :param request:
    :return: render del template acquisti se l'utente è un collezionista
    render del template vendite se l'utente è un venditore
    redirect al login se non si è loggati
    '''
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        if request.method == 'POST':
            try:
                voto = int(request.POST['voto'][0])
            except KeyError:
                messages.error(request, 'Non hai selezionato nessun voto')
                if user.utente.collezionista:
                    vendite = Acquisto.objects.filter(collezionista=user.utente).order_by('data')
                    context['acquisti'] = vendite
                    return render(request, 'strumenti/acquisti.html', context)
                else:
                    vendite = Acquisto.objects.filter(venditore=user.utente).order_by('data')
                    context['vendite'] = vendite
                    return render(request, 'strumenti/vendite.html', context)
            id = int(request.POST['voto'][1:])
            acquisto = Acquisto.objects.get(pk=id)
            collezionista = acquisto.collezionista.user
            #Se l'utente è un collezionista allora inserisce il voto collezionista e setta l'affidabilità del venditore
            if user.username == collezionista.username:
                vendite = Acquisto.objects.filter(collezionista=user.utente).order_by('data')
                acquisto.votoCollezionista = voto
                acquisto.save()
            #Viceversa di quanto sopra
            else:
                vendite = Acquisto.objects.filter(venditore=user.utente).order_by('data')
                acquisto.votoVenditore = voto
                acquisto.save()
                context['vendite'] = vendite
                return render(request, 'strumenti/vendite.html', context)
        context['acquisti'] = vendite
        return render(request, 'strumenti/acquisti.html', context)
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def inviaMessaggio(request, username):
    '''
    Invio di un messaggio.
    Ci si arriva tramite il bottone 'Invia' nel template messaggio
    :param request:
    :param username: user al quale inviare il messaggio
    :return: render del template messaggio se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        user_messaggio = get_object_or_404(User, username=username)
        if request.method == 'POST':
            testo = request.POST['testo']
            Messaggio.inviaMessaggio(mittente=user.utente, destinatario=user_messaggio.utente, testo=testo)

        messaggi = Messaggio.objects.filter( (Q(destinatario=user.utente) & Q(mittente=user_messaggio.utente))
                                            | (Q(destinatario=user_messaggio.utente) & Q(mittente=user.utente)))
        context['messaggi'] = messaggi
        context['user_messaggio'] = user_messaggio
        return render(request, 'strumenti/messaggio.html', context)
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def eliminaMessaggi(request, username):
    context = checkUser(request)
    if context is not None:
        user = get_object_or_404(User, username=context['user'])
        user_messaggio = get_object_or_404(User, username=username)
        messaggi = Messaggio.objects.filter( (Q(destinatario=user.utente) & Q(mittente=user_messaggio.utente))
                                             | (Q(destinatario=user_messaggio.utente) & Q(mittente=user.utente)) )
        messaggi.delete()
        context['messaggi'] = messaggi
        context['user_messaggio'] = user_messaggio
        return HttpResponseRedirect(reverse('strumenti:messaggi'))
    else:
        return HttpResponseRedirect(reverse('collezione:login'))
