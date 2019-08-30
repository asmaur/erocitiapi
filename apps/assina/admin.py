from django.contrib import admin

from .models import *
# Register your models here.

#admin.site.register(Membership)
#admin.site.register(Subscription)

@admin.register(Membership)
class MemberShipAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'get_level','get_value','get_free', 'get_status', 'valide']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'owner_fullname', 'get_citi', 'get_plano', 'end_date', 'active']
    search_fields = ["perfil__nome", "perfil__sobrenome", "user__first_name", "user__last_name"]