from django.urls import path, include, re_path
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()


router.register(r'log', LoginViewset)
router.register(r'users', UserViewset)
router.register(r'ag', AgenteViewset)
router.register(r'pf', PerfilViewset)
router.register(r'img', ImageViewset)
router.register(r'dados', DadosViewset)
router.register(r'local', LocaisViewset)
router.register(r'cash', ValoresViewset)
router.register(r'services', ServiceViewset)

router.register(r'views', ViewsViewset)
router.register(r'clics', KlicsViewset)

router.register(r'especiais', ServiceEspecialViewset)
router.register(r'mem', MemberViewset)

router.register(r'pay', PaymentViewset)


urlpatterns = [
    path('', include(router.urls)),

]
