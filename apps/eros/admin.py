from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(Perfil)
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

admin.site.register(PerfilViewCount)
admin.site.register(PerfilNumberClick)

admin.site.register(Transactions)

@admin.register(ChangePasseCode)
class ChangePasseCodeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'active']
