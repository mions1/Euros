from django.shortcuts import render, HttpResponseRedirect, reverse, get_object_or_404
from collezione.views import checkUser
from collezione.models import *
from django.contrib import messages

# Create your views here.
def homepage(request):
    '''
    View della homepage dell'utente venditore.
    :param request:
    :return: render del template homepage se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None and not context['user'].utente.collezionista:
        ultime_vendite = Acquisto.objects.filter(venditore=context['user'].utente).order_by('data').reverse()[:10]
        totale = 0.0
        for vendita in ultime_vendite:
            totale += vendita.prezzo
        context['vendite'] = ultime_vendite
        context['totale'] = totale
        return render(request, 'vendita/homepage.html', context)
    return HttpResponseRedirect(reverse('login'))

def catalogo(request):
    '''
    View del catalogo del venditore.
    :param request:
    :return: render del template catalogo se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = context['user']
        nazionalita_select = Moneta.getNazionalita()
        valori_select = Moneta.getValori()
        valori = Moneta.getValori()
        monete = Moneta.objects.all().order_by('nazionalita', 'valore')
        possedute = user.utente.moneta_set.all().filter(possiede__posseduta=True)
        if request.method == 'POST':
            nazionalita = request.POST['select_nazionalita']
            valore = request.POST['select_valore']
            posseduta = request.POST['select_posseduta']
            if valore != '.+':
                valori = [float(valore)]

            monete = Moneta.objects.filter(
                nazionalita__regex='^' + nazionalita + '$',
                valore__regex='^' + valore + '$').order_by('nazionalita','valore')
            if posseduta == "1":
                monete = possedute

        context['monete'] = monete
        context['valori_select'] = valori_select
        context['nazionalita_select'] = nazionalita_select
        context['valore_min'] = min(valori)
        context['valore_max'] = max(valori)
        context['possedute'] = possedute
        return render(request, 'vendita/catalogo.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def dettaglioMoneta(request, moneta_id):
    '''
    View del dettaglio di una moneta.
    :param request:
    :return: render del template dettaglio_moneta se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = context['user']
        moneta = Moneta.objects.get(pk=int(moneta_id))
        try:
            possiede = moneta.possiede_set.get(utente__user=user)
        except Possiede.DoesNotExist:
            moneta.possiede_set.create(utente=user.utente, posseduta=False, da_scambiare=False,
                                       da_acquistare=False)
            possiede = moneta.possiede_set.get(utente__user=user)

        context['possiede'] = possiede
        context['moneta'] = moneta
        return render(request, 'vendita/dettaglio_moneta.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def impostaDettaglioMoneta(request):
    '''
    Settaggio di eventuali variazioni della moneta (prezzo, posseduta, etc)
    :param request:
    :return: render del template dettaglio_moneta,
    se ci si arriva tramite url diretto redirect verso la homepage,
    redirect al login se non loggati
    '''
    context = checkUser(request)
    if context is not None:
        user = context['user']
        if request.method == 'POST':
            moneta_id = request.POST['moneta_id']
            posseduta = request.POST.get('posseduta', False)
            prezzo = request.POST.get('prezzo', 0.0)
            if (str(prezzo) == ''):
                prezzo = 0.0
            moneta = Moneta.objects.get(pk=int(moneta_id))
            moneta.editMoneta(user.utente, posseduta, prezzo=prezzo)

            return HttpResponseRedirect(reverse('vendita:dettaglio_moneta', args=((moneta_id),)))
        else:
            return HttpResponseRedirect(reverse('vendita:homepage'))
    else:
        return HttpResponseRedirect(reverse('login'))

def confermaAcquisto(request, username):
    '''
    View per l'acquisto di una moneta, pagina di inserimento dati carta
    :param request:
    :param username: venditore
    :return: render del template utente:catalogo se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        if request.method == 'POST':
            user = get_object_or_404(User, username=context['user'])
            username = get_object_or_404(User, username=username)
            prezzo = request.POST['prezzo']
            moneta = Moneta.objects.get(id=request.POST['moneta_id'])
            context['user_dettaglio'] = username
            context['prezzo'] = prezzo
            context['moneta'] = moneta
        return render(request, 'vendita/acquisto.html', context)
    else:
        return HttpResponseRedirect(reverse('collezione:login'))

def acquista(request, username):
    '''
    View per l'acquisto di una moneta.
    :param request:
    :param username: venditore
    :return: render del template utente:catalogo se loggati, redirect al login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        if request.method == 'POST':
            user = get_object_or_404(User, username=context['user'])
            username = get_object_or_404(User, username=username)
            moneta = Moneta.objects.get(id=request.POST['moneta_id'])
            prezzo = request.POST.get('prezzo', 0.0)
            carta = request.POST['carta']
            print(carta)
            errore = False
            for c in carta:
                if not c.isdigit():
                    messages.error(request, 'Numero carta di credito non valido')
                    errore = True
                    break
            if not errore:
                messages.info(request, 'Acquisto effettuato')
                Acquisto.acquista(user.utente, username.utente, moneta, prezzo)
                moneta.editMoneta(user.utente, True)

        return HttpResponseRedirect(reverse('utente:catalogo', args=(username,)))
    else:
        return HttpResponseRedirect(reverse('collezione:login'))