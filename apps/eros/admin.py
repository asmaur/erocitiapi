from django.contrib import admin
from .models import *
# Register your models here.

class PerfilAdmin(admin.ModelAdmin):
    #sets up values for how admin site lists categories
    list_display = ('fullname', 'code', 'owner_name', 'owner_numero','created_at',)
    list_display_links = ('fullname', 'code', 'owner_name', 'owner_numero')
    list_per_page = 20
    ordering = ['created_at']
    search_fields = ['code',] # 'owner.user.username', ]
    exclude = ('created_at', 'updated_at', "code")



admin.site.register(Perfil, PerfilAdmin)
admin.site.register(DadosPerfil)
admin.site.register(Service)
admin.site.register(Service_especial)
admin.site.register(Local)
admin.site.register(Valor)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Album)
admin.site.register(Image)
admin.site.register(Video)
admin.site.register(Denunciar)

admin.site.register(NewsLettersAds)
admin.site.register(NewsUsers)

admin.site.register(PerfilViewCount)
admin.site.register(PerfilNumberClick)

admin.site.register(Transactions)

@admin.register(ChangePasseCode)
class ChangePasseCodeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'active']
