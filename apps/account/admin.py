from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
# Register your models here.

class AgenteAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'owner_name', 'owner_numero', 'state', 'city', 'created')
    list_display_links = ('get_full_name', 'owner_name', 'owner_numero')
    search_fields = ['phone', 'user__first_name', 'user__last_name']

class BalanceAdmin(admin.ModelAdmin):
    list_display = ('get_value', 'balance_owner', 'created_date',)


admin.site.register(Agente, AgenteAdmin)

admin.site.register(UserBalance, BalanceAdmin)
