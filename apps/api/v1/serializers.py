from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import exceptions

from ...eros.models import *
from ...account.models import *
from ...assina.models import *


class AgenteSerializer(serializers.ModelSerializer):
    #user = UserSerializer()
    class Meta:
        model = Agente
        fields = '__all__'
        read_only_fields = ['id', 'user' ]

    def update(self, instance, validated_data):
        """
        instance.phone = validated_data.get('phone', instance.phone)
        instance.country = validated_data.get('country', instance.country)
        instance.state = validated_data.get('state', instance.state)
        instance.city = validated_data.get('city', instance.city)
        """

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance



class UserAgenteSerializer(serializers.ModelSerializer):
    agente = AgenteSerializer(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'agente') # 'is_active', )
        read_only_fields = ['id',]



class UserSerializer(serializers.ModelSerializer):
    #password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',)

        read_only_fields = ('id', 'username')


    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance



class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username", "")
        password = data.get("password", "")
        return data





class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('code', 'name',)



class CityDetailSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    class Meta:
        model = City
        fields = ('name', 'slug', 'state')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'image_erociti', 'is_public', "perfil")



class MiniPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ('pk', 'code', 'nome', 'sobrenome')
        read_only_fields = ["pk",]

class DadosPerfilSerializer(serializers.ModelSerializer):
    perfil = MiniPerfilSerializer(required=False)
    class Meta:
        model = DadosPerfil
        fields = "__all__"
        read_only_fields = ["id", "perfil"]

    def update(self, instance, validated_data):

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance




class ServiceSerializer(serializers.ModelSerializer):
    perfil = MiniPerfilSerializer(required=False)
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ["id", "perfil"]

        def update(self, instance, validated_data):

            for (key, value) in validated_data.items():
                setattr(instance, key, value)

            instance.save()
            return instance


class ServiceEspecialSerializer(serializers.ModelSerializer):
    perfil = MiniPerfilSerializer(required=False)
    class Meta:
        model = Service_especial
        fields = '__all__'
        read_only_fields = ["id", "perfil"]


    def update(self, instance, validated_data):

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance



class LocalSerializer(serializers.ModelSerializer):
    perfil = MiniPerfilSerializer(required=False)
    class Meta:
        model = Local
        fields = '__all__'
        read_only_fields = ["id", "perfil"]


    def update(self, instance, validated_data):

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class ValorSerializer(serializers.ModelSerializer):
    perfil = MiniPerfilSerializer(required=False)
    class Meta:
        model = Valor
        fields = '__all__'
        read_only_fields = ["id", "perfil"]


    def update(self, instance, validated_data):

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


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
        fields = ('pk', 'code', 'category', 'nome', 'sobrenome', 'slug', 'idade', 'peso', 'altura', 'city', 'phone', 'capa', 'is_working', 'is_vip', 'images', 'dados', 'services', 'especiais', 'locais', 'valores', 'description')




class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ('pk', 'code', 'nome', 'sobrenome',  'category', 'idade', 'peso', 'altura', 'city', 'phone', 'slug', 'capa', 'is_working', 'is_vip', 'description')# 'owner')
        read_only_fields = ["id", "owner", "code", 'is_vip', 'city', ]


        def update(self, instance, validated_data):

            for (key, value) in validated_data.items():
                setattr(instance, key, value)

            instance.save()
            return instance


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


class MemberShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ('id','membership_type', 'price', 'valide_time', 'active' ,"description")


class SubscriptionSerializer(serializers.ModelSerializer):

    perfil = PerfilSerializer(read_only=True)
    membership = MemberShipSerializer(read_only=True)
    class Meta:
        model = Subscription
        fields = ('pk', 'code', 'membership', 'perfil', 'active')


class MiniSubscriptionSerializer(serializers.ModelSerializer):

    #perfil = PerfilSerializer(read_only=True)
    membership = MemberShipSerializer(read_only=True)
    class Meta:
        model = Subscription
        fields = ('pk', 'code', 'membership', 'end_date', 'active')

class BalanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserBalance
        fields = ('id', 'amount', 'created_date', 'user')
