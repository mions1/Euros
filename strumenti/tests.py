import datetime
from django.test import TestCase, Client
from django.utils import timezone
from collezione.models import *
from django.shortcuts import reverse


# Create your tests here.


test = {'username': 'test_user', 'nome': 'test_nome', 'cognome':'test_cognome',
        'data_nascita': '1999-01-01', 'email':'test@', 'password':'test_psw'}
test2 = {'username': 'test2_user', 'nome': 'test2_nome', 'cognome':'test2_cognome',
        'data_nascita': '1999-01-02', 'email':'test2@', 'password':'test2_psw'}

test_venditore = {'username': 'test_venditore_user', 'nome': 'test_venditore_nome', 'cognome':'test_venditore_cognome',
        'data_nascita': '1999-02-01', 'email':'test_venditore@', 'password':'test_venditore_psw', 'collezionista':False, 'iban':'1234'}

class LogInTest(TestCase):

    def setUp(self):
        self.credentials = {'username': test['username'], 'password': test['password']}

        #Creo un utente di testing
        Group.objects.create(name='collezionisti')
        Utente.user_create(**test)

    def test_login(self):
        # effettuo login
        c = Client()
        response = self.client.post('/collezione/login/', self.credentials, follow=True )

        # Restituisce true se l'utente si è loggato correttamente, false altrimenti
        self.assertTrue(response.context['user'].is_active)

class UtenteMethodTests(TestCase):

    def test_user_create(self):
        Group.objects.create(name='collezionisti')
        Utente.user_create(**test)
        utente = User.objects.get(username=test['username']).utente
        self.assertTrue(utente.user.username == test['username'])

    def test_user_edit(self):
        Group.objects.create(name='collezionisti')
        Utente.user_create(**test)
        utente = User.objects.get(username=test['username']).utente
        utente.user_edit(nome='test_edit')
        self.assertTrue(utente.user.first_name == 'test_edit' and utente.user.last_name == test['cognome'])

    def test_getAffidabilita_with_one_vote(self):
        Group.objects.create(name='collezionisti')
        Utente.user_create(**test)
        Utente.user_create(**test2)
        utente = User.objects.get(username=test['username']).utente
        utente2 = User.objects.get(username=test2['username']).utente
        Moneta.objects.create(valore=1, nazionalita='Italia')
        moneta = Moneta.objects.get(valore=1)

        self.assertTrue(utente.getAffidabilita() == 0)

        scambio = Scambio.proponiScambio(utente, utente2, moneta)

        scambio.votoRicevente = 5
        scambio.votoOfferente = 3
        scambio.save()

        affidabilitaUtente = utente.getAffidabilita()
        affidabilitaUtente2 = utente2.getAffidabilita()

        self.assertTrue(affidabilitaUtente == 5)
        self.assertTrue(affidabilitaUtente2 == 3)

    def test_getAffidabilita_with_more_vote(self):
        Group.objects.create(name='collezionisti')
        Utente.user_create(**test)
        Utente.user_create(**test2)
        utente = User.objects.get(username=test['username']).utente
        utente2 = User.objects.get(username=test2['username']).utente
        Moneta.objects.create(valore=1, nazionalita='Italia')
        moneta = Moneta.objects.get(valore=1)

        self.assertTrue(utente.getAffidabilita() == 0)

        scambio1 = Scambio.proponiScambio(utente, utente2, moneta)
        scambio2 = Scambio.proponiScambio(utente, utente2, moneta)

        scambio1.votoRicevente = 5
        scambio1.votoOfferente = 3
        scambio1.save()

        scambio2.votoRicevente = 2
        scambio2.votoOfferente = 3

        scambio2.save()

        affidabilitaUtente = utente.getAffidabilita()
        affidabilitaUtente2 = utente2.getAffidabilita()

        self.assertTrue(affidabilitaUtente == 3.5)
        self.assertTrue(affidabilitaUtente2 == 3)

    def test_user_create_collezionista(self):
        Group.objects.create(name='collezionisti')
        Utente.user_create('username', 'nome', 'cognome', '1995-12-01', 'email@', 'password', True )
        utente = User.objects.get(username='username', utente__collezionista=True)
        self.assertTrue(utente.username == 'username')

    def test_user_create_venditore(self):
        Group.objects.create(name='venditori')
        Utente.user_create('username', 'nome', 'cognome', '1995-12-01', 'email@', 'password', False, 'iban')
        utente = User.objects.get(username='username', utente__collezionista=False)
        self.assertTrue(utente.username == 'username')

    def test_user_edit_with_no_edit(self):
        Group.objects.create(name='collezionisti')
        Utente.user_create(**test)
        utente = User.objects.get(username=test['username'])
        utente.utente.user_edit()
        self.assertTrue(utente.username == test['username'])
        self.assertTrue(utente.first_name == test['nome'],)
        self.assertTrue(utente.last_name == test['cognome'])

    def test_user_edit_with_full_edit(self):
        Group.objects.create(name='collezionisti')
        Utente.user_create(**test)
        utente = User.objects.get(username=test['username'])
        utente.utente.user_edit(nome='nuovo', cognome='nuovo')
        self.assertTrue(utente.username == test['username'])
        self.assertTrue(utente.first_name == 'nuovo')
        self.assertTrue(utente.last_name == 'nuovo')

class StrumentiViewTests(TestCase):

    def test_principale_view_with_no_login(self):
        response = self.client.get(reverse('strumenti:principale'))
        #302 perchè redirezione verso il login
        self.assertTrue(response.status_code == 302)
        self.assertTrue('login' in response.url)

    def test_principale_view_for_collezionista(self):
        Group.objects.create(name='collezionisti')
        Utente.user_create(**test)
        c = Client()
        response = self.client.post('/collezione/login/',
                                    {'username': test['username'], 'password': test['password']}, follow=True )
        response = self.client.get(reverse('strumenti:principale'))

        self.assertTrue(response.status_code == 200)
        self.assertTrue('Scambi' in str(response.content))

    def test_principale_view_for_venditore(self):
        Group.objects.create(name='venditori')
        Utente.user_create(**test_venditore)
        c = Client()
        response = self.client.post('/collezione/login/',
                                    {'username': test_venditore['username'], 'password': test_venditore['password']}, follow=True)
        response = self.client.get(reverse('strumenti:principale'))

        self.assertTrue(response.status_code == 200)
        self.assertTrue('Vendite' in str(response.content))

    def test_messaggi_view_with_no_messages(self):
        Group.objects.create(name='collezionisti')
        Utente.user_create(**test)
        c = Client()
        response = self.client.post('/collezione/login/',
                                    {'username': test['username'], 'password': test['password']}, follow=True)
        response = self.client.get(reverse('strumenti:messaggi'))

        self.assertTrue(response.status_code == 200)
        self.assertTrue('Nessun messaggio' in str(response.content))

    def test_messaggi_view_with_messages(self):
        Group.objects.create(name='collezionisti')
        test_utente = Utente.user_create(**test)
        test2_utente = Utente.user_create(**test2)
        c = Client()
        Messaggio.inviaMessaggio(test_utente,test2_utente,"ciao")
        response = self.client.post('/collezione/login/',
                                    {'username': test['username'], 'password': test['password']}, follow=True)
        response = self.client.get(reverse('strumenti:messaggi'))

        self.assertTrue(response.status_code == 200)
        self.assertTrue(test2['username'].capitalize() in str(response.content))

    def test_acquisti_view_with_no_acquisti(self):
        Group.objects.create(name='collezionisti')
        Utente.user_create(**test)
        c = Client()
        response = self.client.post('/collezione/login/',
                                    {'username': test['username'], 'password': test['password']}, follow=True)
        response = self.client.get(reverse('strumenti:acquisti'))

        self.assertTrue(response.status_code == 200)
        self.assertTrue('Nessun acquisto' in str(response.content))

    def test_acquisti_view_with_acquisti(self):
        Group.objects.create(name='collezionisti')
        Group.objects.create(name='venditori')
        test_utente = Utente.user_create(**test)
        venditore = Utente.user_create(**test_venditore)
        c = Client()
        Moneta.objects.create(valore=1, nazionalita='Italia')
        moneta = Moneta.objects.get(valore=1)
        Acquisto.objects.create(collezionista=test_utente, venditore=venditore, moneta=moneta, prezzo=1)
        response = self.client.post('/collezione/login/',
                                    {'username': test['username'], 'password': test['password']}, follow=True)
        response = self.client.get(reverse('strumenti:acquisti'))

        self.assertTrue(response.status_code == 200)
        self.assertTrue("Italia" in str(response.content))

    def test_vendite_view_with_collezionista(self):
        Group.objects.create(name='collezionisti')
        test_utente = Utente.user_create(**test)
        c = Client()
        response = self.client.post('/collezione/login/',
                                    {'username': test['username'], 'password': test['password']}, follow=True)
        response = self.client.get(reverse('strumenti:vendite'))

        #redirect verso strumenti:principale
        self.assertTrue(response.status_code == 302)
        self.assertTrue('principale' in response.url)

    def test_vendite_view_with_no_vendita(self):
        Group.objects.create(name='venditori')
        venditore = Utente.user_create(**test_venditore)
        c = Client()
        response = self.client.post('/collezione/login/',
                                    {'username': test_venditore['username'], 'password': test_venditore['password']}, follow=True)
        response = self.client.get(reverse('strumenti:vendite'))

        #redirect verso strumenti:principale
        self.assertTrue(response.status_code == 200)
        self.assertTrue("Nessuna vendita" in str(response.content))

    def test_vendite_view_with_vendita(self):
        Group.objects.create(name='collezionisti')
        Group.objects.create(name='venditori')
        test_utente = Utente.user_create(**test)
        venditore = Utente.user_create(**test_venditore)
        c = Client()
        Moneta.objects.create(valore=1, nazionalita='Italia')
        moneta = Moneta.objects.get(valore=1)
        Acquisto.objects.create(collezionista=test_utente, venditore=venditore, moneta=moneta, prezzo=1)
        c = Client()
        response = self.client.post('/collezione/login/',
                                    {'username': test_venditore['username'], 'password': test_venditore['password']}, follow=True)
        response = self.client.get(reverse('strumenti:vendite'))

        #redirect verso strumenti:principale
        self.assertTrue(response.status_code == 200)
        self.assertTrue("Italia" in str(response.content))
