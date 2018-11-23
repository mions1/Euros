from django import forms
from django.utils import timezone
from collezione.models import *

class EditProfileForm(forms.Form):
    email = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    nome = forms.CharField(required=False)
    cognome = forms.CharField(required=False)
    data_nascita = forms.DateField(label='Data di nascita (yyyy-mm-dd)', widget=forms.DateInput(format="%Y-%m-%d"), required=False)

class RegistrazioneForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    username = forms.CharField()
    nome = forms.CharField()
    cognome = forms.CharField()
    data_nascita = forms.DateField(label='Data di nascita (yyyy-mm-dd)', widget=forms.DateInput(format="%Y/%m/%d"))
    tipi = [['True','Collezionista'], ['False','Venditore']]
    tipo = forms.ChoiceField(label = 'Registrarsi come', choices=tipi, initial='True' , widget=forms.RadioSelect())
    iban = forms.CharField(required=False)