from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives
from celery.schedules import crontab
from celery.task import periodic_task, task

from ...eros.models import *
from ...assina.models import *
from django.contrib.auth.models import User
import requests, json
from ...utils.mailer import *


@task(bind=True)
def add_citi_mailchimp_task(self, email=None):
    api_url = f'https://{settings.MAILCHIMP_DATA_CENTER}.api.mailchimp.com/3.0'
    members_url = f'{api_url}/lists/{settings.MAILCHIMP_LIST_ID}/members'
    try:
        news = NewsUsers.objects.get(email=email)
        return None
    except Exception as ex:
        # print(ex)
        news = None

    if news is None:
        try:
            data = {
                "email_address": email,
                "status": "subscribed",
                "tags": ["citi news"]
            }
            req = requests.post(
                members_url,
                auth=("", settings.MAILCHIMP_API_KEY),
                data=json.dumps(data)
            )
            NewsUsers.objects.create(email=email)
            return req.status_code
        except Exception as ex:
            # print(ex)
            self.retry(exc=ex, max_retries=5, countdown=20)

@task(bind=True)
def denuncia_task(self,**kwargs):
    """Verifica se há denuncia e avisa o administrador."""
    try:
        anuncio = Perfil.objects.get(id=kwargs.get('id'))
        data = {"link":kwargs.get('link'), "last_name":anuncio.user.last_name, "first_name":anuncio.user.first_name,'code':anuncio.code,"nome":anuncio.nome, "sobrenome": anuncio.sobrenome, "feito_no": kwargs.get('feito_no')}
        mail = Mailer(to=settings.REPORT_FROM_EMAIL, data=data, temp_html='denuncia/denuncia.html', temp_txt='denuncia/denuncia.txt')
    except Exception as ex:
        #print(ex)
        self.retry(exc=ex, max_retries=5, countdown=71)
