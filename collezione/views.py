from django.views import generic
from django.db.models import Q
from collezione.forms import *
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from collezione.models import *
from django.contrib import messages
from django.db import IntegrityError

# Create your views here.
class RegistrazioneView(generic.FormView):
    '''
    Classe per la vista del form registrazione utente.
    '''
    template_name = "collezione/registrazione.html"
    form_class = RegistrazioneForm
    success_url = "collezione:signupReg"

class ModificaProfiloView(generic.FormView):
    '''
    Classe per la vista del form modifica profilo.
    '''
    template_name = "collezione/modificaProfilo.html"
    form_class = EditProfileForm
    success_url = "collezione:editprofile"

def homepage(request):
    '''
    View per la homepage.
    Questa view definisce la homepage dell'utente collezionista, acceduta subito dopo aver effettuato il login.
    :param request:
    :return: render della homepage nel caso in cui si è loggati con un utente collezionista;
    redirect verso la homepage nell'app vendita nel caso in cui si è loggati come venditori;
    redirect verso il login nel caso in cui si accede a questa views senza aver effettuato il login
    '''
    context = checkUser(request)
    if context is not None:
        user = context['user']
        #verifico se ci sono messaggi non letti oppure scambi ancora da vedere in modo che venga notificato nel caso
        messaggi_non_letti = user.utente.destinatario.filter(letto=False)
        scambi_ricevuti = user.utente.ricevente.filter(confermaRicevente=False)
        scambi_inviati = user.utente.offerente.filter(monetaControOfferta__isnull=False, confermaOfferente=False)
        notifiche_count = messaggi_non_letti.count() + scambi_ricevuti.count() + scambi_inviati.count()
        context ['notifiche_count'] = notifiche_count
        context ['messaggi_count'] = messaggi_non_letti.count()
        context ['scambi_count'] = scambi_ricevuti.count() + scambi_inviati.count()
        if user.utente.collezionista:
            ultimi_scambi = Scambio.objects.filter(confermaRicevente=True, confermaOfferente=True).\
                order_by('data').reverse()[:6]
            ultimi_acquisti = Acquisto.objects.all().order_by('data').reverse()[:6]
            context['scambi'] = ultimi_scambi
            context['acquisti'] = ultimi_acquisti
            return render(request, 'collezione/homepage.html', context)
        return HttpResponseRedirect(reverse('vendita:homepage'))
    return HttpResponseRedirect(reverse('login'))

def modificaProfilo(request):
    '''
    View per la modifica del profilo.
    Questa view effettua i cambiamenti del profilo richiesti nella finestra definita dal form della modifica del pofilo.
    :param request:
    :return: redirect verso il template della modifica
    '''
    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        iban = ""
        #l'iban sarà definito solo nel caso in cui l'utente sia un venditore
        try:
            iban = request.POST['iban']
        except (KeyError):
            iban = ""
        if user.utente.user_edit(request.POST['nome'], request.POST['cognome'],
                                       request.POST['data_nascita'], request.POST['email'], iban):
            messages.info(request,"Changed Ok!")
        else:
            messages.error(request, "Error!")

        return HttpResponseRedirect(reverse('collezione:editprofile'))

def profilo(request):
    '''
    View del profilo utente.
    Questa view definisce la vista del template del profilo utente, con i suoi dati ed alcune statistiche ad esso riferite.
    :param request:
    :return: render del template del profilo nel caso in cui l'utente è connesso, redirect verso il login altrimenti.
    '''
    context = checkUser(request)
    statics = []
    if context is not None:
        #recupero delle statistiche da mostrare
        context['user_to_show'] = context['user']
        statics = getStatics(context['user'])
        for key,item in statics.items():
            context[key] = item
        return render(request, 'collezione/profilo.html', context)
    return HttpResponseRedirect(reverse('login'))

def registrazione(request):
    '''
    View per la registrazione.
    Questa view effettua la registrazione dell'utente prendendo i dati dal form della registrazione.
    :param request:
    :return: redirect verso il login
    '''

    errore = False;
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        username = request.POST['username']
        nome = request.POST['nome']
        cognome = request.POST['cognome']
        data = request.POST['data_nascita']
        collezionista = request.POST['tipo']

        if "@" not in email:
            messages.error(request, 'Email non valida')
            errore = True
        for c in username:
            if not c.isalnum():
                messages.error(request, 'Username può contenere solo caratteri o numeri')
                errore = True
                break;
        for c in nome:
            if not c.isalpha():
                messages.error(request, 'Nome può contenere solo caratteri o numeri')
                errore = True
                break;
        for c in cognome:
            if not c.isalpha():
                if c != "'":
                    messages.error(request, 'Cognome può contenere solo caratteri o numeri o apostrofi')
                    errore = True
                    break;

        #l'iban è definito se ci si registra come venditore
        try:
            iban = request.POST['iban']
        except KeyError:
            iban = None
        if iban == '':
            iban = None

        if iban is not None:
            for c in iban:
                if not c.isalnum():
                    messages.error(request, 'Iban può contenere solo caratteri o numeri')
                    errore = True
                    break;

        if User.objects.all().filter(username=username).count() == 1:
            messages.error(request, 'Username già esistente')
            errore = True

        if User.objects.all().filter(email=email).count() == 1:
            messages.error(request, 'Email già esistente')
            errore = True

        if not errore:
            try:
                Utente.user_create(username,nome,cognome,data,email,password,collezionista,iban)
            except IntegrityError:
                messages.error(request, 'Impossibile procedere alla registrazione')
                return HttpResponseRedirect(reverse('collezione:registrazione'))
        else:
            return HttpResponseRedirect(reverse('collezione:registrazione'))
    return HttpResponseRedirect(reverse('login'))

def catalogo(request):
    '''
    View del catalogo delle monete.
    Questa view definisce il catalogo, cioè la lista delle monete esistenti.
    :param request:
    :return: il render del template del catalogo se l'utente è loggato, altrimenti torna al login
    '''
    context = checkUser(request)
    if context is not None:
        user = context['user']
        nazionalita_select = Moneta.getNazionalita()
        valori_select = Moneta.getValori() #valori delle monete (0.1€, etc) per creare la selectbox
        monete = Moneta.objects.all().order_by('nazionalita', 'valore') #recupero monete dal db
        possedute = user.utente.moneta_set.all().filter(possiede__posseduta=True) #recupero le monete possedute dall'utente
        #nel caso in cui l'utente ha richiesto dei filtri
        if request.method == 'POST':
            nazionalita = request.POST['select_nazionalita'] #recupero la nazionalita del filtro
            valore = request.POST['select_valore'] #recupero il valore del filtro
            posseduta = request.POST['select_posseduta'] #recupero il filtro posseduta

            #Serve per poter filtrare anche i 1.0€ e 2.0€, altrimenti non funziona
            if str(valore).endswith('0'):
                valore = valore[0]

            #recupero delle monete con i filtri richiesti
            monete = Moneta.objects.filter(
                nazionalita__regex='^' + nazionalita + '$',
                valore__regex='^' + valore + '$').order_by('nazionalita','valore')
            if posseduta == "1":
                monete = possedute
            elif posseduta == "0":
                monete = monete.difference(possedute).order_by('nazionalita', 'valore')

        context['monete'] = monete
        context['valori_select'] = valori_select
        context['nazionalita_select'] = nazionalita_select
        context['possedute'] = possedute
        return render(request, 'collezione/catalogo.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def dettaglioMoneta(request, moneta_id):
    '''
    View per la vista del dettaglio della moneta.
    Definisco la vista del dettaglio della moneta richiesta.
    :param request:
    :return: render del template del dettaglio della moneta se loggato, redirect verso il login altrimenti
    '''
    context = checkUser(request)
    if context is not None:
        user = context['user']
        #moneta richiesta
        moneta = Moneta.objects.get(pk=int(moneta_id))
        try:
            #creo il record nella relazione possiede se non esiste già con questa moneta
            possiede = moneta.possiede_set.get(utente__user=user)
        except Possiede.DoesNotExist:
            moneta.possiede_set.create(utente=user.utente, posseduta=False, da_scambiare=False,
                                     da_acquistare=False)
            possiede = moneta.possiede_set.get(utente__user=user)

        context['possiede'] = possiede
        context['moneta'] = moneta
        return render(request, 'collezione/dettaglio_moneta.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def impostaDettaglioMoneta(request):
    '''
    Imposto i dettagli della moneta richiesti dall'utente (posseduta, da_scambiare, da_acquistare).
    :param request:
    :return: render del dettaglio della moneta se loggato
    redirect verso la homepage se loggato ma sono arrivato a questa view tramite accesso diretto
    redirect vero il login se non loggato
    '''
    context = checkUser(request)
    if context is not None:
        user = context['user']
        if request.method == 'POST':
            #recupero moneta e le checkbox
            moneta_id = request.POST['moneta_id']
            posseduta = request.POST.get('posseduta', False)
            da_scambiare = request.POST.get('da_scambiare', False)
            da_acquistare = request.POST.get('da_acquistare', False)
            moneta = Moneta.objects.get(pk=int(moneta_id))
            moneta.editMoneta(user.utente, posseduta, da_scambiare, da_acquistare)
            possiede = moneta.possiede_set.get(utente__user=user)
            context['possiede'] = possiede
            context['moneta'] = moneta

            return render(request, 'collezione/dettaglio_moneta.html', context)
        else:
            return HttpResponseRedirect(reverse('collezione:homepage'))
    else:
        return HttpResponseRedirect(reverse('login'))

def utenti(request):
    '''
    Vista per la lista degli utenti registrati
    :param request:
    :return:
    '''
    context = checkUser(request)
    if context is not None:
        user = context['user']
        #recupero di tutti gli utenti (ad esclusione dell'utente loggato)
        users = User.objects.all().filter(~Q(username=user.username),is_staff=False,is_superuser=False,is_active=True,)
        if request.method == 'POST':
            tipo = request.POST['select_tipo']
            #prendo solo gli utenti del tipo richiesto
            users = users.filter(utente__collezionista__regex='^' + tipo + "$")
        context['users'] = users
        return render(request, 'collezione/utenti.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def getStatics(user):
    '''
    Recupero delle statistiche da mostrare in Profilo.
    :param user:
    :return: dizionario di statistiche
    '''
    statics = {}
    moneta_set = user.utente.possiede_set.filter(posseduta=True)
    patrimonio = 0.0
    for moneta in moneta_set:
        patrimonio += float(moneta.moneta.valore)
    scambi = Scambio.objects.filter( Q(offerente=user.utente) | Q(ricevente=user.utente))
    acquisti = Acquisto.objects.filter( Q(collezionista=user.utente))
    affidabilita = user.utente.getAffidabilita()
    statics = {'monete_possedute': moneta_set,
               'patrimonio': patrimonio,
               'scambi_effettuati': scambi,
               'acquisti_effettuati': acquisti,
               'affidabilita': affidabilita,
            }
    return statics

def checkUser (request):
    '''
    Controllo se l'utente esiste (quindi, se si è loggati).
    Questo metodo è utilizzato all'interno di ogni views in modo che, nel caso si tentasse un accesso diretto ad un
    url prima di aver effettuato il login, questo ti faccia tornare al login
    :param request:
    :return: nel caso si è loggati resistuisco il context contenente l'utente, altrimenti none
    '''
    username = request.user
    try:
        user = User.objects.get(username=username)
    except (User.DoesNotExist, Utente.DoesNotExist):
        return None
    else:
        context = {'user': user,}
        return context
