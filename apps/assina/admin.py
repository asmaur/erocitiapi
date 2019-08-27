from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(Membership)
#admin.site.register(Subscription)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'end_date', 'active']