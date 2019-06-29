from django.urls import path, include, re_path
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

router.register(r'subs', Subscriptions, base_name='subs')
router.register(r'p', PerfilViewset, base_name='p')
router.register(r'state', StateViewset, base_name='state')
router.register(r'sr', SearchAll, base_name='search')
router.register(r'news', NewsLetters, base_name='search')
router.register(r'denuncia', Denuncia, base_name='denun')
router.register(r'views', ViewsViewset)
router.register(r'clics', KlicsViewset)

urlpatterns = [
    re_path('', include(router.urls)),
]