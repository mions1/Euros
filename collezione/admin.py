from django.contrib import admin
from .models import Moneta

# Register your models here.
class MonetaAdmin(admin.ModelAdmin):
    list_filter = ['valore', 'nazionalita']
    search_fields = ['nazionalita']


admin.site.register(Moneta, MonetaAdmin)