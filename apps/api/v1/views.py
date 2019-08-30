from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, permission_classes, authentication_classes
from rest_framework import permissions
from django.contrib.auth import login, logout, authenticate
from rest_framework.authentication import TokenAuthentication
import json, uuid
import datetime as dt
from decimal import Decimal
from django.conf import settings
import requests
import xmltodict
from .tasks import *


#pagseguro
from pagseguro.api import PagSeguroItem, PagSeguroApi


from .serializers import *
from ...eros.models import *
from ...assina.models import *
from ...account.models import *




class LoginViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    def create(self, request):

        try:
            username = request.data["username"]
            first_name = request.data["first_name"]
            last_name = request.data["last_name"]
            email = request.data["email"]
            confirm_email = request.data["confirm_email"]
            password = request.data["password"]
            confirm_password = request.data["confirm_password"]

            # dados para criar agente

            phone = request.data["phone"]
            #cpf = request.data["cpf"]
            city = request.data["city"]
            code_area = request.data["code_area"]
            state = request.data["state"]

            if (email != confirm_email and password != confirm_password):
                return Response({"message": "Os emails e senhas não correspondem"}, status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(username=username)
            except:
                user = None

            if user:
                return Response({"message": "Este nome de usúario não está disponível, tente outro"},
                                status.HTTP_400_BAD_REQUEST)
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                add_ads_mailchimp_task.delay(email)
                Agente.objects.create(user=user, state=state, city=city, code_area=code_area, phone=phone)

                return Response({"message": "Usúario criado com sucesso, Faça seu login na sua conta"}, status.HTTP_201_CREATED)


        except:
            return Response({"message": "Verifique seus dados"}, status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def login(self, request):
        #print(request.data)

        user = authenticate(username=request.data["username"], password=request.data["password"])
        if user is not None:
            if user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                ag = Agente.objects.get(user=user)
                ags = UserAgenteSerializer(user)
                return Response({"token": token.key, "agente": ags.data, "message": "Login realizado com sucesso.",
                                         "log": True}, status=status.HTTP_200_OK)
            else:
                message = "O úsuario foi desativado."
                return Response({ "message": message,}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return  Response({ "message": "Não foi possível authenticar com suas credenciais.", "log": False}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def logout(self, request):
        authentication_classes = (TokenAuthentication,)
        #print(request.user)
        logout(request)
        return Response({"message": "logout realizado com sucesso."}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['POST'])
    def password_code(self, request, ):

        try:
            email = request.data['email']
            user = User.objects.get(email=email)
        except Exception as ex:
            user = None

        if( user is not None):
            try:
                code = uuid.uuid4()
                email = request.data['email']
                #print(email, user.last_name, code)
                end_at = timezone.now() + timedelta(days=1)
                esqueci_senha_task.delay(email=email, code=code, last_name=user.last_name)
                ChangePasseCode.objects.create(code=code, email=email, end_at=end_at)

                return Response({"message": "Um link para recuperação da sua senha foi enviado ao seu email.!"},
                                status.HTTP_200_OK)
            except Exception as ex:
                #print(ex)
                return Response({"message": "Algo deu errado. Não foi possivel enviar o link ao seu endereço de email. Tente mais tarde!"},
                                status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Não há usúario com este email. Realize seu cadastro agora mesmo."})


    @action(detail=False, methods=["POST"])
    def check_code(self, request):
        code = request.data['code']

        try:
            change_pass = ChangePasseCode.objects.get(code=code)
        except:
            change_pass = None

        if(change_pass is not None):
            if(change_pass.active):
                return Response({"success": True}, status.HTTP_200_OK)
            else:
                return Response({"success": False}, status.HTTP_200_OK)
        else:
            return Response({"success": False}, status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def change_password(self, request, ):
        passw = request.data['password']
        passconf = request.data['confirm_password']
        code = request.data['code']

        try:
            change_pass = ChangePasseCode.objects.get(code=code)
        except:
            change_pass = None

        if (change_pass is not None):

            if (change_pass.active):

                try:
                    #print(passconf, passw)
                    #print(change_pass.email)
                    user = User.objects.get(email=change_pass.email)


                    if (passw == passconf):

                        user.set_password(passconf)
                        user.save()
                        return Response({"message": "A sua senha foi atualizado, tente logar na sua conta."},
                                        status.HTTP_200_OK)
                    else:
                        return Response({"message": "As senhas não correspondem."}, status.HTTP_400_BAD_REQUEST)

                except Exception as ex:
                    #print(ex)
                    return Response({"message": "Não há usúario com este email cadastrado."}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Código de ativação inválido."}, status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"message": "Esse código de renovação não existe mais."}, status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def adsnewsletter(self, request):
        try:
            email = request.data["email"]
            #news = NewsLettersAds(email=email)
            #news.save()
            add_ads_mailchimp_task.delay(email)
            return Response({
                                "message": "Seu email foi salvo com sucesso. Logo Receberá novidades da plataforma. Obrigado!"},
                            status.HTTP_200_OK)
        except Exception as ex:
            return Response({"message": "Não foi possível salvar seu email. Tente novamente mais tarde."},
                            status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_transactions(notificationCode):
        #print(notificationCode)
        url = f'{settings.PAGSEGURO_TRANSACTIONS_URL}{notificationCode}'
        response = requests.get(
            url,
            params={'email': settings.PAGSEGURO_EMAIL, 'token': settings.PAGSEGURO_TOKEN},
            headers={'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'},
        )
        #print(response.content)
        datas = xmltodict.parse(response.content)
        data = json.dumps(datas)

        #print(data)

        return data

    @action(detail=False, methods=["POST"])
    def notifications(self, request):
        try:
            #print(request.data)
            code = request.data["notificationCode"]
            print(code)

            data = json.loads(self.get_transactions(code))

            email = data["transaction"]["sender"]["email"]
            valor = data["transaction"]["grossAmount"]
            statusCode = data["transaction"]["status"]
            transCode = data["transaction"]["code"]
            #Notifications.objects.create(notyCode=code, transCode=transCode, status=statusCode)

            if statusCode == "3":
                #print("Aqui....")
                user = User.objects.get(email=email)
                ubalance = UserBalance.objects.get(user=user)
                ubalance.amount += Decimal(valor)
                ubalance.created_date = timezone.now()
                ubalance.save()
                Notifications.objects.create(notyCode=code, transCode=transCode, status=statusCode, creditado=True, email=email)
                return Response({"message": "OK"}, status.HTTP_200_OK)
            else:
                Notifications.objects.create(notyCode=code, transCode=transCode, status=statusCode, email=email)
                return Response({"message": "OK"}, status.HTTP_200_OK)

        except Exception as ex:
            #print(ex)
            return Response({"message": "NO"}, status.HTTP_400_BAD_REQUEST)

        #return Response({"message": "NO"}, status.HTTP_200_OK)


class UserViewset(viewsets.ViewSet):
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication,]
    permission_classes = (permissions.IsAuthenticated,)


    def list(self, request):
        serializer = UserAgenteSerializer(self.queryset, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserAgenteSerializer(user)

        return  Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, request.data)
        if(serializer.is_valid(raise_exception=True)):
            serializer.save()
            return Response({"message": "Usuário atualizado com sucesso..!"}, status.HTTP_200_OK)

        return Response({"message": "Erro ao atualizar usuário, Tente novamente..!"}, serializer.errors,
                        status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = get_object_or_404(User, pk=int(pk))
        if user:
            user.delete()
            return Response({"message": "Usuário removido com sucesso"}, status=status.HTTP_200_OK)
        return Response({"message": "Erro ao remover usuário. Tente novamente"}, status=status.HTTP_400_BAD_REQUEST)

    


class AgenteViewset(viewsets.ViewSet):
    queryset = Agente.objects.all()

    authentication_classes= (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        print(request.user)
        serializer = AgenteSerializer(self.queryset, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        queryset = get_object_or_404(Agente, pk=pk)
        serializer = AgenteSerializer(queryset)

        return Response(serializer.data)


    def update(self, request, pk=None):

        agente = get_object_or_404(Agente, pk=pk)

        serializer = AgenteSerializer(instance=agente, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Os dados foram atualizados"}, status=status.HTTP_200_OK)

        return Response({"message": "Algo deu errado ao atualizar os dados"}, serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass

    @action(detail=True, methods=["GET"])
    def perfis(self, request, pk=None):
        queryset = Perfil.objects.all().filter(owner__pk=int(pk))

        #print(queryset)
        serializer = PerfilSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status.HTTP_200_OK)



class PerfilViewset(viewsets.ViewSet):
    queryset = Perfil.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        queryset = Perfil.objects.all()
        serializer = PerfilSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)



    def create(self, request,):
        data = json.loads(request.data['datus'])

        owner = Agente.objects.get(pk=int(data['pk']))

        try:
            city = City.objects.get(name=data['cityName'])
        except City.DoesNotExist:
            city = None

        try:
            state = State.objects.get( code=data['stateCode'].lower())
        except State.DoesNotExist:
            state = None

        try:
            #print(city)
            #print(state)

            if city and city.state.code==state.code:
                Perfil.objects.create( owner=owner, city=city, nome = data['nome'], category = data['category'], sobrenome = data['sobrenome'], idade = data['idade'], altura = data['altura'], peso = data['peso'], phone = data['phone'], description = data['description'], capa_original=request.FILES['file'], capa = request.FILES['file'])

                return Response({"message": "Perfil criado com sucesso"}, status.HTTP_201_CREATED)

            elif city and city.state.code != state.code:
                state = State.objects.create(code=data['stateCode'].lower(), name = data['stateName'])
                city = City.objects.create(state=state, name=data['cityName'])
                Perfil.objects.create( owner=owner, city=city, nome = data['nome'], category = data['category'], sobrenome = data['sobrenome'], idade = data['idade'], altura = data['altura'], peso = data['peso'], phone = data['phone'], description = data['description'], capa_original=request.FILES['file'], capa = request.FILES['file'])
                return Response({"message": "Perfil criado com sucesso"}, status.HTTP_201_CREATED)

            elif not city:
                print("city nao existe")

                if state:
                    city = City.objects.create(name=data['cityName'], state=state)
                    Perfil.objects.create(owner=owner, city=city, nome=data['nome'], category=data['category'],
                                              sobrenome=data['sobrenome'], idade=data['idade'], altura=data['altura'],
                                              peso=data['peso'], phone=data['phone'], description=data['description'], capa_original=request.FILES['file'],
                                              capa=request.FILES['file'])
                    return Response({"message": "Perfil criado com sucesso"}, status.HTTP_201_CREATED)

                else:
                    state = State.objects.create(code=data['stateCode'].lower(), name=data['stateName'])
                    city = City.objects.create(state=state, name=data['cityName'])
                    Perfil.objects.create(owner=owner, city=city, nome=data['nome'], category=data['category'],
                                              sobrenome=data['sobrenome'], idade=data['idade'], altura=data['altura'],
                                              peso=data['peso'], phone=data['phone'], description=data['description'],
                                              capa_original=request.FILES['file'], capa=request.FILES['file'])

                    return Response({"message": "Perfil criado com sucesso"}, status.HTTP_201_CREATED)


        except Exception as ex:
            #print(ex)
            return Response({"message":"Algo deu errado, tente novamente."}, status.HTTP_400_BAD_REQUEST)





    def retrieve(self, request, pk=None):
        query = get_object_or_404(Perfil, pk=int(pk))
        serializer = PerfilDetailSerializer(query, context={"request": request})
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def mini(self, request, pk=None):
        query = get_object_or_404(Perfil, pk=int(pk))
        serializer = PerfilSerializer(query, context={"request": request})
        return Response(serializer.data)


    def update(self, request, pk=None):
        """Update created profiles"""

        print(request.data)
        per = get_object_or_404(Perfil, pk=int(pk))

        if request.data:
            if 'capa' in request.data:
                capa = request.FILES['capa']
                per.capa = capa
                per.capa_original = capa
                per.save()


            if 'datus' in request.data:
                data = request.data['datus']
                serializer = PerfilSerializer(per, json.loads(data))

                if serializer.is_valid(raise_exception=True):
                    serializer.save()
            return Response({"message": "Perfil atualizado com sucesso..!"},
                                    status=status.HTTP_200_OK)

        return Response({"message": "Erro ao atualizar perfil"}, status=status.HTTP_400_BAD_REQUEST)



    def destroy(self, request, pk=None):
        per = get_object_or_404(Perfil, pk=int(pk))
        if per:
            per.delete()
            return Response({"message": "Perfil removido com sucesso"}, status=status.HTTP_200_OK)
        return Response({"message": "Erro ao remover perfil"}, status=status.HTTP_400_BAD_REQUEST)



class ImageViewset(viewsets.ViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        images = Image.objects.all()
        serializer = ImageSerializer(images, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def image(self, request, pk=None):
        per = get_object_or_404(Perfil, pk=int(pk))
        images = Image.objects.all().filter(perfil=per)
        serializer = ImageSerializer(images, many=True, context={"request": request})
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def count(self, request, pk=None):
        per = Perfil.objects.get(pk=pk)
        val = Image.objects.filter(perfil=per).count()

        if (val):
            return Response({"imagelen": val}, status=status.HTTP_200_OK)
        else:
            return Response({"imagelen": 0}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def add(self, request, pk=None):
        per = get_object_or_404(Perfil, pk=int(pk))
        if request.FILES:
            for img in request.FILES:
                Image.objects.create(image_erociti=request.FILES[img], perfil = per)
            return Response({"message": "imagen adicionada com sucesso..!"}, status.HTTP_201_CREATED)
        return Response({"message": "Erro ao adicionar imagem"}, status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        query = Image.objects.all().filter(perfil__pk=int(pk))
        serializer = ImageSerializer(query, many=True, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        img = get_object_or_404(Image, pk=int(pk))
        img.delete()

        return Response({"message": "A imagem foi removida"}, status=status.HTTP_200_OK)



class DadosViewset(viewsets.ViewSet):
    queryset = DadosPerfil.objects.all()
    serializer_class = DadosPerfilSerializer

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request,):
        serializer = DadosPerfilSerializer(self.queryset, many=True)
        return  Response(serializer.data)

    def retrieve(self, request, pk=None, ):
        dado = get_object_or_404(DadosPerfil, pk=int(pk))
        serializer = DadosPerfilSerializer(dado)

        return Response(serializer.data)

    def update(self, request, pk=None, ):
        dado = get_object_or_404(DadosPerfil, pk=int(pk))
        data = json.loads(request.data['datus'])
        #print(data)
        try:
            serializer = DadosPerfilSerializer(dado, data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"message": "Os dados foram atualizados atualizados com sucesso..!"}, status=status.HTTP_200_OK)
            return Response({"message": "Algo deu errado ao atualizar os dados. Tente novamente"}, serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            #print(ex)
            return Response({"message": "Algo deu errado ao atualizar os dados. Tente novamente"}, status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, pk):
        return Response(" partial update ..!")

    def destroy(self, request, pk=None):
        return Response("destroy ..!")



class ServiceViewset(viewsets.ViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        service = get_object_or_404(Service, pk=int(pk))
        serializer = ServiceSerializer(service)

        return Response(serializer.data)

    def update(self, request, pk=None):
        service = get_object_or_404(Service, pk=int(pk))
        data = request.data
        #print(data)
        serializer = ServiceSerializer(service, data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Os serviços foram atualizados com sucesso..!"}, status=status.HTTP_200_OK)
        return Response({"message": "Erro ao atualizar os serviços..!"}, serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        pass

    def destroy(self, request, pk=None):
        pass


class ServiceEspecialViewset(viewsets.ViewSet):
    queryset = Service_especial.objects.all()
    serializer_class = ServiceEspecialSerializer

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        service = get_object_or_404(Service_especial, pk=int(pk))
        serializer = ServiceEspecialSerializer(service)

        return Response(serializer.data)

    def update(self, request, pk=None):
        service = get_object_or_404(Service_especial, pk=int(pk))
        serializer = ServiceEspecialSerializer(service, request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Os serviços foram atualizados sucesso..!"}, status=status.HTTP_200_OK)
        return Response({"message": "Erro ao atualizar os serviços..!"}, serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, pk):
        pass

    def destroy(self, request, pk=None):
        pass



class LocaisViewset(viewsets.ViewSet):
    queryset = Local.objects.all()
    serializer_class = LocalSerializer

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        queryset = get_object_or_404(Local, pk=pk)
        serializer = LocalSerializer(queryset)

        return Response(serializer.data)

    def update(self, request, pk=None):
        local = get_object_or_404(Local, pk=int(pk))
        data = request.data
        #print(data)
        serializer = LocalSerializer(local, data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Os locais foram atualizados com sucesso..!"}, status=status.HTTP_200_OK)
        return Response({"message": "Erro ao atualizar os locais..!"}, serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        pass

    def destroy(self, request, pk=None):
        pass


class ValoresViewset(viewsets.ViewSet):
    queryset = Valor.objects.all()
    serializer_class = ValorSerializer

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):
        pass


    def retrieve(self, request, pk=None):
        queryset = get_object_or_404(Valor, pk=pk)
        serializer = ValorSerializer(queryset)

        return Response(serializer.data)

    def update(self, request, pk=None):
        valor = get_object_or_404(Valor, pk=int(pk))
        data = request.data
        #print(data)
        serializer = ValorSerializer(valor, data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Os valores foram atualizados com sucesso..!"}, status=status.HTTP_200_OK)
        return Response({"message": "Erro ao atualizar os valores..!"}, serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, pk):
        pass

    def destroy(self, request, pk=None):
        pass



class ViewsViewset(viewsets.ViewSet):

    """Contar numeros de views para fazer contato com perfil e retornar estatistica por dia e por mês."""

    queryset = PerfilViewCount.objects.all()

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        query = PerfilViewCount.objects.all()
        serializer = ViewsCountSerializer(query, many=True)
        #print("list")

        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def add_views(self, request, pk=None):
        today = dt.datetime.now()
        per = Perfil.objects.get(pk=pk)
        try:
            uviews = PerfilViewCount.objects.filter(perfil=per).filter(created=today.date())
        except PerfilViewCount.DoesNotExist:
            uviews = None

        if uviews:
            pviews = uviews[0]
            vi = pviews.views + 1
            uviews.views = vi
            uviews.save()
            serializer = ViewsCountSerializer(uviews)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            uviews = PerfilViewCount.objects.create(perfil=per, created=today.date(), views=1)
            serializer = ViewsCountSerializer(uviews)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def days(self, request, pk=None):
        today = dt.datetime.now()
        per = Perfil.objects.get(pk=pk)

        try:
            uviews = PerfilViewCount.objects.filter(perfil=per).filter(created__day = today.day)
        except PerfilViewCount.DoesNotExist:
            uviews = None

        if uviews:
            vi = uviews[0]
            serializer = ViewsCountSerializer(vi)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"views":0}, status=status.HTTP_200_OK)



    @action(detail=True, methods=["GET"])
    def months(self, request, pk=None):
        today = dt.datetime.now()
        per = Perfil.objects.get(pk=pk)
        
        try:
            uviews = PerfilViewCount.objects.all().filter(perfil=per).filter(created__month=today.month)
        except PerfilViewCount.DoesNotExist:
            uviews = None
        
        if uviews:
            serializer = ViewsCountSerializer(uviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"views":0}, status=status.HTTP_200_OK)


class KlicsViewset(viewsets.ViewSet):

    """Contar numeros de klics para fazer contato com perfil e retornar estatistica por dia e por mês."""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    queryset = PerfilNumberClick.objects.all()

    def list(self, request):
        serializer = KlicsCountSerializer(self.queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def add_klics(self, request, pk=None):
        today = dt.datetime.now()
        per = Perfil.objects.get(pk=pk)
        try:
            klics = PerfilNumberClick.objects.filter(perfil=per).filter(created=today.date())
        except PerfilNumberClick.DoesNotExist:
            klics = None

        if klics:
            pklics = klics[0]
            vi = pklics.views + 1
            pklics.clicked = vi
            pklics.save()
            serializer = KlicsCountSerializer(klics)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            klics = PerfilNumberClick.objects.create(perfil=per, created=today.date(), clicked=1)
            serializer = KlicsCountSerializer(klics)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def days(self, request, pk=None):
        today = dt.datetime.now()
        per = Perfil.objects.get(pk=pk)
        
        try:
            klics = PerfilNumberClick.objects.filter(perfil=per).filter(created__day = today.day)
            #print(today.day)
            #print(klics)
        except PerfilNumberClick.DoesNotExist:
            klics = None
        
        if klics:
            clics = klics[0]
            serializer = KlicsCountSerializer(clics)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response( {"clicked":0}, status=status.HTTP_200_OK)
		


    @action(detail=True, methods=["GET"])
    def months(self, request, pk=None):
        today = dt.datetime.now()
        per = Perfil.objects.get(pk=pk)
        try:
            klics = PerfilNumberClick.objects.filter(perfil=per).filter(created__month=today.month)
        except PerfilNumberClick.DoesNotExist:
            klics = None

        if klics:
            serializer = KlicsCountSerializer(klics, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"clicked":0}, status=status.HTTP_200_OK)


class MemberViewset(viewsets.ViewSet):
    queryset = Membership.objects.all().filter(active=True)

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        serializer = MemberShipSerializer(self.queryset, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        memb = Membership.objects.get(pk=pk)

        serializer = MemberShipSerializer(memb)

        return Response(serializer.data)

    @action(methods=["GET"], detail=True)
    def planos(self, request, pk=None):
        subs = Subscription.subs_active.all().filter(perfil__pk=pk)
        #planos = [plano.membership for plano in subs]
        serializer = MiniSubscriptionSerializer(subs, many=True)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True)
    def vip(self, request, pk=None):
        count = Subscription.objects.filter(perfil__pk=pk).filter(membership__level=4).count()

        if (count >= 12):
            perfil = Perfil.objects.get(pk=pk)
            perfil.is_vip = True
            perfil.save()
            return Response({"message": "Parabéns, Você conquistou seu selo VIP. Aproveite a nossa plataforma !"},
                            status.HTTP_200_OK)

        else:
            return Response({"message": "Infelizmente, Não foi desta vez. Solicite mais tarde !"}, status.HTTP_200_OK)



class PaymentViewset(viewsets.ViewSet):
    queryset = Membership.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def generate_id(self):
        n = 90
        random = string.ascii_uppercase + string.ascii_lowercase + string.digits
        return ''.join(choice(random) for _ in range(n))

    @action(detail=False, methods=["POST"])
    def checkout(self, request):
        # print(request.data)
        pagseguro_api = PagSeguroApi(currency=request.data["currency"], reference=request.data["reference"],
                                         senderEmail=request.data["senderEmail"],#"amama@sandbox.pagseguro.com.br",#request.data["senderEmail"],
                                         senderName=request.data["senderName"],
                                         senderAreaCode=request.data["senderAreaCode"],
                                         senderPhone=request.data["senderPhone"],
                                         shipping_cost=0, )  # request.data["senderPhone"])
        item1 = PagSeguroItem(id=request.data["itemId"], description=request.data["itemDescription"],
                                  amount=request.data["itemAmount"], quantity=request.data["itemQuantity"], )

        pagseguro_api.add_item(item1)
        data = pagseguro_api.checkout()

        return Response(data)

    @action(detail=False, methods=["POST"])
    def transactions(self, request, ):
        #print(request.data)
        perId = request.data["perId"]
        userId = request.data["userId"]
        planoId = request.data["planoId"]
        transactionCode = request.data["transactionCode"]
        tipo = ['Diamond', 'Destaque', 'Top', 'Basic']

        pagseguro_api = PagSeguroApi()

        try:
            data = pagseguro_api.get_transaction(transactionCode)
        except:
            data = None

        if data:
            if data["transaction"]["status"] == "3":
                perfil = Perfil.objects.get(pk=perId)
                plano = Membership.objects.get(pk=planoId)
                user = User.objects.get(pk=userId)
                created_date = dt.datetime.today()
                end_date = dt.datetime.today() + timedelta(days=int(plano.valide_time))
                Subscription.objects.create(types=tipo.index(plano.membership_type),
                                                code=data["transaction"]["code"], user=user, membership=plano,
                                                perfil=perfil, created_date=created_date, end_date=end_date, count=1)
                return Response({"message": "Obrigado pela sua compra."}, status.HTTP_201_CREATED)
                # 4BF9CC18-6F63-4DDF-9BB9-637D5E540F28
            elif data["transaction"]["status"] in ["1", "2", "4"]:

                Transactions.objects.create(perId=perId, userId=userId, planoId=planoId,
                                                transactionCode=transactionCode)

                return Response({"message": "Obrigado por comprar o plano, Aguardamos a aprovação do pagamento."},
                                    status.HTTP_200_OK)

        return Response({"message": "Algo deu errado"})


    @action(methods=["POST"], detail=False)
    def setplanos(self, request):

        try:
            user = User.objects.get(pk=request.data["userId"])
            balance = UserBalance.objects.get(user=user)
        except Exception as ex:
            # print(ex)
            balance = None

        if balance is not None:

            try:

                data = request.data
                perfil = Perfil.objects.get(pk=data["perId"])
                plano = Membership.objects.get(pk=data["planoId"])
                #print(plano.price)
                #print(balance.amount)
                #print(balance.amount>plano.price)

                if (balance.amount >= plano.price):

                    try:
                        subs = Subscription.subs_active.all().filter(perfil=perfil).filter(membership=plano).count()
                        #print(subs)
                    except Exception as ex:
                        #print(ex)
                        subs = 0

                    if (subs == 0):
                        created_date = timezone.now()
                        end_date = timezone.now() + timedelta(days=int(plano.valide_time))
                        Subscription.objects.create(types=plano.level, code=uuid.uuid4(),
                                                        user=user, membership=plano, perfil=perfil,
                                                        created_date=created_date,
                                                        end_date=end_date, count=1)
                        new_amount = balance.amount - plano.price
                        balance.amount = new_amount
                        balance.save()
                        return Response({"message": "O plano foi adicionado ao perfil com sucesso. Atualize a página."},
                                            status.HTTP_200_OK)
                    else:
                        return Response({"message": "Você já possui esse plano ativo para este perfil."},
                                        status.HTTP_200_OK)



                else:
                    return Response({"message": "Saldo insuficiente"}, status.HTTP_400_BAD_REQUEST)

            except Exception as ex:
                # print(ex)
                return Response({"message": "Algo deu errado, tente novamente mais tarde."},
                                    status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Desculpe, Algo deu errado. tente novamente mais tarde"},
                                status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False)
    def renovar(self, request):
        data = request.data

        try:
            data = request.data
            # perfil = Perfil.objects.get(pk=data["perId"])
            plano = Membership.objects.get(pk=data["planoId"])
            subs = Subscription.objects.get(code=data["code"])
            balance = UserBalance.objects.get(user=subs.user)

            if (balance.amount >= plano.price):

                created = timezone.now()

                new_end_date = subs.end_date + timedelta(days=int(plano.valide_time))
                new_count = subs.count + 1
                subs.created_at = created
                subs.end_date = new_end_date
                subs.count = new_count
                subs.save()

                new_amount = balance.amount - plano.price
                balance.amount = new_amount
                balance.save()

                return Response({"message": "O seu plano foi renovado com sucesso"}, status.HTTP_200_OK)
            else:
                return Response({"message": "Não foi possível renovar seu plano. Crédito insuficiente"},
                                    status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({"message": "Algo deu errado, tente novamento mais tarde."},
                                status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET"], detail=True)
    def getbalance(self, request, pk=None):
        user = User.objects.get(pk=pk)
        balance = UserBalance.objects.get(user=user)

        serializer = BalanceSerializer(balance)

        return Response(serializer.data, status.HTTP_200_OK)

