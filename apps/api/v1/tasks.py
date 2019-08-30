from celery import shared_task, task
from celery.schedules import crontab
from celery.task import periodic_task
import requests, json

from ...eros.models import *
from ...assina.models import *
from django.contrib.auth.models import User

from ...utils.mailer import *


@task(bind=True,)
def esqueci_senha_task(self, **kwargs):

    try:
        data = kwargs
        mail = Mailer(to=kwargs.get('email'), data=data, temp_html='senhas/email.html', temp_txt='senhas/email.txt')
        mail.noty_senhas()
        return "Senha Enviado"
    except Exception as ex:
        print(ex)
        # dt = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=1)
        self.retry(exc=ex, max_retries=5, countdown=15)



@task(bind=True)
def add_ads_mailchimp_task(self, email=None):
    api_url = f'https://{settings.MAILCHIMP_DATA_CENTER}.api.mailchimp.com/3.0'
    members_url = f'{api_url}/lists/{settings.MAILCHIMP_LIST_ID}/members'
    try:
        news = NewsLettersAds.objects.get(email=email)
        return None
    except Exception as ex:
        # print(ex)
        news = None

    if news is None:
        try:
            data = {
                "email_address": email,
                "status": "subscribed",
                "tags": ["ads news"]
            }
            req = requests.post(
                members_url,
                auth=("", settings.MAILCHIMP_API_KEY),
                data=json.dumps(data)
            )
            NewsLettersAds.objects.create(email=email)
            return req.status_code
        except Exception as ex:
            # print(ex)
            self.retry(exc=ex, max_retries=5, countdown=20)
    pass

@task(bind=True)
def noty_sem_perfil(self,id):
    #print(id)
    if(id):
        try:

            ag = Agente.objects.get(id=id)
            data = {"last_name":ag.user.last_name, "email": ag.user.email}
            mail = Mailer(to=ag.user.email, data=data, temp_html='mail/perfil.html', temp_txt='mail/perfil.txt')
            mail.noty_sem_perfil()

        except Exception as ex:
            #print(ex)
            self.retry(exc=ex, max_retries=5, countdown=33)



@task(bind=True)
def sem_perfil_task(self,):
    """Verifica e avisa ao usuario que não criou nenhum anuncio ainda"""
    #print("sem perfil")
    result1 = Perfil.objects.values_list('owner__id', flat=True).distinct()
    ags = Agente.objects.all()
    res2 = [ag.id for ag in ags]
    owners = list(dict.fromkeys(result1)) #agente dos perfis removendo as repetições
    sem_per = list(set(res2) - set(owners))
    if(len(sem_per) !=0):
        for id in sem_per:
            noty_sem_perfil.delay(id)
    return None

@task(bind=True)
def noty_sem_subscrition(self, id):
    try:
        user = User.objects.get(id=id)
        data = {"last_name":user.last_name, "email": user.email}
        mail = Mailer(to=user.email, data=data, temp_html='mail/assina.html', temp_txt='mail/assina.txt')
        mail.noty_sem_subs()
    except Exception as ex:
        print(ex)
        self.retry(exc=ex, max_retries=5, countdown=21)



@task(bind=True)
def sem_subscrition_task(self,):
    """Verifica e avisa ao usuario que não criou nenhum anuncio online"""
    print("sem subs")
    subs_all = Subscription.subs_active.values_list('user', flat=True).distinct()
    users = User.objects.filter(is_superuser=False).filter(is_staff=False).exclude(username='Citikey')
    subs_owners = list(dict.fromkeys(subs_all))  # agente dos perfis removendo as repetições
    users_all = [user.id for user in users]
    #print(subs_owners)
    #print(users_all)
    sem_subs_all = list(set(users_all)-set(subs_owners))
    #print("User sem subs:", sem_subs_all)
    if(len(sem_subs_all) !=0):
        for id in sem_subs_all:
            noty_sem_subscrition.delay(id)

    return None



@task(bind=True,)
def noty_vencimento(self, **kwargs):
    try:
        #print(kwargs)
        mail = Mailer(to=kwargs.get('email'), data=kwargs, temp_html='planos/planos.html', temp_txt='planos/planos.txt')
        mail.noty_planos()
        #print("perfil= {0} {1}, user= {2} {3}".format(kwargs.get("nome"), kwargs.get("sobrenome"), kwargs.get("last_name"), kwargs.get("email")))  # .strftime('%B %d %Y'))

    except Exception as ex:
        #print(ex)
        self.retry(exc=ex, max_retries=5, countdown=35)



#@periodic_task(run_every=(crontab(minute='*/1')), name="some_task", queue="notify-plano")
@task(bind=True)
def vencimento_de_plano_task(self,):
    """Informa ao usuario que o seu plano para determinado anuncio está para vencer"""
    subs = Subscription.subs_active.all().filter(end_date__lte=timezone.now()+timedelta(days=2))
    if(subs is not None):
        for sub in subs:
            noty_vencimento.delay(last_name=sub.user.last_name, email=sub.user.email, nome=sub.perfil.nome, sobrenome=sub.perfil.sobrenome, plano=sub.membership.name)
            #print("Faltam {0} para seu plano vencer: perfil= {1} {2}, user= {3} {4}".format(sub.end_date-timezone.now(), sub.perfil.nome, sub.perfil.sobrenome, sub.user.last_name, sub.user.email)) #.strftime('%B %d %Y'))


@task(bind=True)
def noty_credito_acabando(self, **kwargs):
    try:
        # print(kwargs)
        mail = Mailer(to=kwargs.get('email'), data=kwargs, temp_html="credito/credito.html", temp_txt="credito/credito.txt")
        mail.noty_credito_acabando()
        # print("perfil= {0} {1}, user= {2} {3}".format(kwargs.get("nome"), kwargs.get("sobrenome"), kwargs.get("last_name"), kwargs.get("email")))  # .strftime('%B %d %Y'))

    except Exception as ex:
        # print(ex)
        self.retry(exc=ex, max_retries=5, countdown=5)


@task(bind=True)
def credito_acabando_task(self):
    """Checar credito menor do que o minimo, e notificar que o credito está acabando"""
    try:

        balances = UserBalance.objects.filter(amount__gt=00.00).filter(amount__lte=19.00).filter(user__is_superuser=False).filter(user__is_staff=False).exclude(user__username='Citikey')
        if(balances):
            for bal in balances:
                #print(bal.user.username)
                noty_credito_acabando.delay(email=bal.user.email, last_name=bal.user.last_name, saldo=bal.amount)

    except Exception as ex:
        print(ex)


@task(bind=True)
def remove_unactive_subscription(self):
    try:
        subs = Subscription.objects.filter(end_date__lt=timezone.now())

        if(subs):
            for sub in subs:
                print(sub)
                sub.delete()

    except Exception as ex:
        print(ex)

