from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.db.models import Q

# Create your models here.
from django.db.models import DateField


class Utente (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data_nascita = models.DateField(null=False)
    iban = models.CharField(max_length=27, null=True)
    collezionista = models.BooleanField(default=True, null=False)

    def getAffidabilita(self):
        #totale dei voti ricevuti (per calcolo media)
        totaleVoti = Scambio.objects.filter( Q(offerente=self, votoRicevente__isnull=False) |
                                             Q(ricevente=self, votoOfferente__isnull=False)).count()
        if totaleVoti == 0:
            return 0

        #somma dei voti ricevuti
        sommaVoti = 0
        voti = Scambio.objects.filter( offerente=self, votoRicevente__isnull=False ).values('votoRicevente')
        for voto in voti:
            sommaVoti += voto['votoRicevente']
        voti = Scambio.objects.filter(ricevente=self, votoOfferente__isnull=False).values('votoOfferente')
        for voto in voti:
            sommaVoti += voto['votoOfferente']

        return sommaVoti/totaleVoti

    @staticmethod
    def user_create(username, nome, cognome, data_nascita, email, password, collezionista=True, iban=None):
        user = User.objects.create_user(username=username, email=email, password=password, first_name=nome, last_name=cognome,
                                        last_login='1980-01-01', is_superuser=False, is_staff=False, is_active=True,
                                        date_joined=timezone.now())

        if (collezionista):
            group = Group.objects.get(name='collezionisti')
        else:
            group = Group.objects.get(name='venditori')
        group.user_set.add(user)
        utente = Utente.objects.create(user=user, data_nascita=data_nascita, iban=iban, collezionista=collezionista)
        utente.save()
        user.save()
        return utente

    def user_edit(self, nome="", cognome="", data_nascita="", email="", iban=""):
        if nome is not "":
            self.user.first_name = nome
        if cognome is not "":
            self.user.last_name = cognome
        if email is not "":
            self.user.email = email
        if data_nascita is not "":
            self.data_nascita = data_nascita
        if iban is not "":
            self.iban = iban
        self.save()
        return True

    def __str__(self):
        tipo = "Collezionista"
        if not self.collezionista:
            tipo = "Venditore"
        user = self.user
        return (user.first_name + " " + user.last_name + " " + tipo)

class Messaggio (models.Model):
    testo = models.CharField(max_length=200, null=True)
    letto = models.BooleanField(null=False, default=False)
    data = models.DateTimeField(null=False, default=timezone.now)
    mittente = models.ForeignKey(Utente, on_delete=models.DO_NOTHING, related_name='mittente', null=False)
    destinatario = models.ForeignKey(Utente, on_delete=models.DO_NOTHING, related_name="destinatario", null=False)

    @staticmethod
    def inviaMessaggio(mittente, destinatario, testo):
        Messaggio.objects.create(mittente=mittente, destinatario=destinatario, testo=testo)

    def __str__(self):
        return (self.testo +" " + str(self.data) +" " + self.mittente.user.first_name + " " + self.destinatario.user.first_name)

class Moneta (models.Model):
    utente = models.ManyToManyField(Utente, through="Possiede")
    valore = models.FloatField(null=False)
    nazionalita = models.CharField(max_length=30, null=False)
    foto = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = (("valore", "nazionalita"),)

    @staticmethod
    def creaMonete():
        paesi = Moneta.getNazionalita()
        valori = Moneta.getValori()

        for paese in paesi:
            for valore in valori:
                img = "collezione/img/" + paese + "/" + str(valore).replace('.', ',') + ".jpg"
                Moneta.objects.create(valore=valore, nazionalita=paese, foto=img)

    @staticmethod
    def getNazionalita():
        file_paesi = open('collezione/res/paesi.txt', 'r')
        paesi = []
        for paese in file_paesi:
            paesi.append(paese[0:paese.index('\n')])
        return paesi

    @staticmethod
    def getValori():
        file_valori = open('collezione/res/valori.txt', 'r')
        valori = []
        for valore in file_valori:
            valori.append(float(valore))
        return valori

    def editMoneta(self, utente, posseduta=False, da_scambiare=False, da_acquistare=False, prezzo=None):
        try:
            possiede = Possiede.objects.get(utente=utente, moneta=self)
            possiede.posseduta = posseduta
            possiede.da_scambiare = da_scambiare
            possiede.da_acquistare = da_acquistare
            possiede.prezzo = prezzo
            possiede.save()
        except Possiede.DoesNotExist:
            self.possiede_set.create(utente=utente, posseduta=posseduta, da_scambiare=da_scambiare, da_acquistare=da_acquistare)

    def __str__(self):
        return (str(self.valore) + " " + self.nazionalita + " ")

class Possiede(models.Model):
    utente = models.ForeignKey(Utente, on_delete=models.CASCADE, null=False)
    moneta = models.ForeignKey(Moneta, on_delete=models.CASCADE, null=False)
    posseduta = models.BooleanField(null=True, default=False)
    da_scambiare = models.BooleanField(null=True, default=False)
    da_acquistare = models.BooleanField(null=True, default=False)
    prezzo = models.FloatField(null=True, default=0.0)

    class Meta:
        unique_together=(("utente", "moneta"), )

    def __str__(self):
        return (self.utente.user.first_name + " " + str(self.moneta.nazionalita) + " " + str(self.moneta.valore) + " " +
                " " + str(self.posseduta) + " " + str(self.da_scambiare) + " " + str(self.da_acquistare) )

class Scambio (models.Model):
    data = models.DateField(null=False, default=timezone.now)
    offerente = models.ForeignKey(Utente, on_delete=models.DO_NOTHING, related_name='offerente')
    ricevente = models.ForeignKey(Utente, on_delete=models.DO_NOTHING, related_name='ricevente')
    monetaRichiesta = models.ForeignKey(Moneta, on_delete=models.DO_NOTHING, related_name='monetaRichiesta')
    monetaControOfferta = models.ForeignKey(Moneta, on_delete=models.DO_NOTHING, related_name='monetaControOfferta', null=True)
    confermaOfferente = models.BooleanField(null=True, default=False)
    confermaRicevente = models.BooleanField(null=True, default=False)
    votoOfferente = models.IntegerField(null=True, default=None)
    votoRicevente = models.IntegerField(null=True, default=None)

    @staticmethod
    def proponiScambio(offerente, ricevente, monetaRichiesta):
        return Scambio.objects.create(offerente=offerente, ricevente=ricevente, monetaRichiesta=monetaRichiesta)

    def __str__(self):
        return (str(self.data) + " " + str(self.offerente) + " " + str(self.ricevente) + " " + self.monetaRichiesta.nazionalita + " ")

class Acquisto (models.Model):
    collezionista = models.ForeignKey(Utente, on_delete=models.DO_NOTHING, related_name="acquisto_collezionista")
    venditore = models.ForeignKey(Utente, on_delete=models.DO_NOTHING, related_name="acquisto_venditore", null=True)
    moneta = models.ForeignKey(Moneta, on_delete=models.DO_NOTHING)
    prezzo = models.FloatField(null=False, default=0.0)
    data = models.DateField(null=False, default=timezone.now)
    votoCollezionista = models.IntegerField(null=True, default=None)
    votoVenditore = models.IntegerField(null=True, default=None)

    @staticmethod
    def acquista(collezionista, venditore, monetaRichiesta, prezzo):
        Acquisto.objects.create(collezionista=collezionista, venditore=venditore, moneta=monetaRichiesta, prezzo=prezzo)

    def __str__(self):
        return (self.moneta.valore +" " + self.moneta.nazionalita +" " + self.collezionista.last_name + " " + self.venditore.last_name)


