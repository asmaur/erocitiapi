from rest_framework import serializers

from ...eros.models import *
from ...assina.models import *


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('code', 'name',)




class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('name', 'slug',)


class CityDetailSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    class Meta:
        model = City
        fields = ('name', 'slug', 'state')



class StateDetailSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)
    class Meta:
        model = State
        fields = ('code', 'name', 'cities')



class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image_erociti',)



class DadosPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = DadosPerfil
        exclude = ('perfil',)


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        exclude = ('perfil',)


class ServiceEspecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service_especial
        exclude = ('perfil',)

class LocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Local
        exclude = ('perfil',)

class ValorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valor
        exclude = ('perfil',)


class PerfilDetailSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    dados = DadosPerfilSerializer(many=True, read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    especiais = ServiceEspecialSerializer(many=True, read_only=True)
    locais = LocalSerializer(many=True, read_only=True)
    valores = ValorSerializer(many=True, read_only=True)
    city = CityDetailSerializer()
    class Meta:
        model = Perfil
        fields = ('id', 'code', 'nome', 'category','sobrenome', 'idade', 'altura', 'peso', 'city', 'phone', 'capa', 'images', 'dados', 'services', 'especiais', 'locais', 'valores', 'description')



class PerfilSerializer(serializers.ModelSerializer):
    city = CityDetailSerializer()

    class Meta:
        model = Perfil
        fields = ('id', 'code','slug', 'nome', 'sobrenome', 'category', 'idade', 'altura', 'peso', 'city', 'phone', 'capa', 'description', 'is_vip')



class MemberShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ('id','name',)


class SubscriptionSerializer(serializers.ModelSerializer):

    perfil = PerfilSerializer(read_only=True)
    #membership = MemberShipSerializer(read_only=True)
    class Meta:
        model = Subscription
        fields = ('code', 'types', 'perfil')

class ViewsCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilViewCount
        fields = "__all__"
        read_only_fields = ["perfil"]

class KlicsCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilNumberClick
        fields = "__all__"
        read_only_fields = ["perfil"]