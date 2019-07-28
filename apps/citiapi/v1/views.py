from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions
from rest_framework import status
import datetime as dt


from .serializers import *
from ...eros.models import *
from ...assina.models import *




class Subscriptions(viewsets.ViewSet):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        queryset = Subscription.subs_active.all()  # .order_by('-created_date')
        serializer = SubscriptionSerializer(queryset, many=True,)
        return Response(serializer.data)



    @action(detail=False)
    def general(self, request):
        """"Conjunto de 12 modelo na pagina principal global excluindo as subs basicas"""

        queryset = Subscription.subs_active.filter(perfil__category="mulheres").filter(perfil__is_working=True).filter(perfil__suspended=False).order_by("-types")[:12]
        serializer = SubscriptionSerializer(queryset, many=True, )
        #print(queryset)
        return Response(serializer.data)


    @action(detail=False, url_name ='diamonds', url_path='(?P<code>[-\w]+)/(?P<slug>[-\w]+)/(?P<categ>[-\w]+)/diamonds')
    def diamonds(self, request, code=None, slug=None, categ=None):
        #print('subs diamond')
        diam = Subscription.subs_active.filter(types=3).filter(perfil__is_working=True).filter(perfil__suspended=False).filter(perfil__category=categ).filter(perfil__city__slug=slug).filter(perfil__city__state__code=code).order_by("-end_date")
        serializer = SubscriptionSerializer(diam, many=True, )
        return Response(serializer.data)



    @action(detail=False, url_name='destaks', url_path='(?P<code>[-\w]+)/(?P<slug>[-\w]+)/(?P<categ>[-\w]+)/destaks')
    def destaks(self, request, code=None, slug=None, categ=None):
        #print('subs destaque')
        diam = Subscription.subs_active.filter(types=2).filter(perfil__is_working=True).filter(perfil__suspended=False).filter(
            perfil__category=categ).filter(perfil__city__slug=slug).filter(perfil__city__state__code=code).order_by("-end_date")
        serializer = SubscriptionSerializer(diam, many=True, )
        return Response(serializer.data)



    @action(detail=False, url_name='tops', url_path='(?P<code>[-\w]+)/(?P<slug>[-\w]+)/(?P<categ>[-\w]+)/tops')
    def tops(self, request, code=None, slug=None, categ=None):
        #print('subs tops')
        diam = Subscription.subs_active.filter(types=1).filter(perfil__is_working=True).filter(perfil__suspended=False).filter(
            perfil__category=categ).filter(perfil__city__slug=slug).filter(perfil__city__state__code=code).order_by("-end_date")
        serializer = SubscriptionSerializer(diam, many=True, )
        return Response(serializer.data)


    @action(detail=False, url_name='tops', url_path='(?P<code>[-\w]+)/(?P<slug>[-\w]+)/(?P<categ>[-\w]+)/basic')
    def basic(self, request, code=None, slug=None, categ=None):
        #print('subs basic')
        diam = Subscription.subs_active.filter(types=0).filter(perfil__is_working=True).filter(perfil__suspended=False).filter(
            perfil__category=categ).filter(perfil__city__slug=slug).filter(perfil__city__state__code=code).order_by("-end_date")
        serializer = SubscriptionSerializer(diam, many=True, )
        return Response(serializer.data)



class PerfilViewset(viewsets.ViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        #queryset = Subscription.subs_active.all().order_by('-created_date')
        serializer = PerfilSerializer(self.queryset, many=True,)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        perfil = get_object_or_404(self.queryset, code=pk)
        serializer = PerfilDetailSerializer(perfil, )
        return Response(serializer.data)


class StateViewset(viewsets.ViewSet):
    queryset = State.objects.all()
    #serializer_class = StateDetailSerializer

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        #queryset = Subscription.subs_active.all().order_by('-created_date')
        serializer = StateDetailSerializer(self.queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, url_name='all', url_path='all')
    def all(self, request):
        #queryset = Subscription.subs_active.all().order_by('-created_date')
        serializer = StateDetailSerializer(self.queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, url_name='city', url_path='(?P<code>[-\w]+)/(?P<slug>[-\w]+)')
    def city(self, request, code=None, slug=None):
        """Get specific city."""
        city = City.objects.all().filter(state__code=code).filter(slug=slug)
        print(city)
        serializer = CitySerializer(city, many=True,  )
        return Response(serializer.data)

class SearchAll(viewsets.ViewSet):
    queryset = Subscription.subs_active.all()#filter(perfil__contain)

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=False, methods=['get'], url_name='search')
    def search(self, request):
        q = request.GET.get('q')
        cq = request.GET.get('cq')
        #print(request.GET.get['q', ''])
        result1 = Subscription.subs_active.all().filter(perfil__nome__icontains=q).filter(perfil__is_working=True).filter(perfil__suspended=False).filter(perfil__category=cq)
        result2 = Subscription.subs_active.all().filter(perfil__sobrenome__icontains=q).filter(perfil__is_working=True).filter(perfil__suspended=False).filter(perfil__category=cq)

        result = result1|result2
        results = result.order_by('types')

        serializer = SubscriptionSerializer(results, many=True)
        return Response(serializer.data)


class NewsLetters(viewsets.ViewSet):
    queryset = NewsUsers.objects.all()

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=False, methods=["POST"], url_name='newsusers')
    def newsusers(self, request):
        mail = request.data["email"]

        NewsUsers.objects.create(email=mail)

        return Response({"message": "O seu email foi adicionado com successo ..!"})

class Denuncia(viewsets.ViewSet):
    queryset = NewsUsers.objects.all()

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=False, methods=["POST"], url_name='denun')
    def denun(self, request):
        perid = request.data["perid"]
        link = request.data["link"]
        Denunciar.objects.create(perfil_id=perid, link=link)

        return Response({"message": "A sua denuncia foi recebida, iremos analiza-lo cuidasomente."})


class ViewsViewset(viewsets.ViewSet):

    """Contar numeros de views para fazer contato com perfil e retornar estatistica por dia e por mês."""

    queryset = PerfilViewCount.objects.all()

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=True, methods=["POST"])
    def more(self, request, pk=None):
        today = dt.datetime.now()
        per = Perfil.objects.get(pk=pk)
        try:
            uviews = PerfilViewCount.objects.filter(perfil=per).filter(created=today.date())
        except PerfilViewCount.DoesNotExist:
            uviews = None

        if uviews:
            pviews = uviews[0]
            vi = pviews.views + 1
            pviews.views = vi
            pviews.save()
            #serializer = ViewsCountSerializer(uviews)
            return Response({"message": "more view added"}, status=status.HTTP_200_OK)

        else:
            uviews = PerfilViewCount.objects.create(perfil=per, created=today.date(), views=1)
            #serializer = ViewsCountSerializer(uviews)
            return Response({"message": "View created"}, status=status.HTTP_200_OK)


class KlicsViewset(viewsets.ViewSet):

    """Contar numeros de klics para fazer contato com perfil e retornar estatistica por dia e por mês."""

    queryset = PerfilNumberClick.objects.all()

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        serializer = KlicsCountSerializer(self.queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def more(self, request, pk=None):
        today = dt.datetime.now()
        per = Perfil.objects.get(pk=pk)
        try:
            klics = PerfilNumberClick.objects.filter(perfil=per).filter(created=today.date())
        except PerfilNumberClick.DoesNotExist:
            klics = None

        if klics:
            pklics = klics[0]
            vi = pklics.clicked + 1
            pklics.clicked = vi
            pklics.save()
            #serializer = KlicsCountSerializer(klics)
            return Response({"message": "more clics added"}, status=status.HTTP_200_OK)

        else:
            klics = PerfilNumberClick.objects.create(perfil=per, created=today.date(), clicked=1)
            #serializer = KlicsCountSerializer(klics)
            return Response({"message": "Clicks created"}, status=status.HTTP_200_OK)