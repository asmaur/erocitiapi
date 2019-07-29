from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
import uuid
from django.db.models import F

from ..eros.models import Perfil
# Create your models here.

def generate_uid():
    return str(uuid.uuid4().fields[-1])[:20]


TYPE_SUBS = (
    (0,'Diamond'),
    (1,'Destak'),
    (2,'Top'),
    (3,'Basic')
)

LEVELS = (
    (0, 'level_0'),
    (1, 'level_1'),
    (2, 'level_2'),
    (3, 'level_3'),
    (4, 'level_4'),
    (5, 'level_5'),
    (6, 'level_6'),
    (7, 'level_7'),
    (8, 'level_8'),
    (9, 'level_9'),
    (10, 'level_10'),

)

MEMBERSHIP_CHOICES = (
    ('Basic', 'basic'),
    ('Top', 'top'),
    ('Destaque', 'destak'),
    ('Diamond', 'diam')
)

MEMBERSHIP_TIME = (
    ('30', '30 dias'),
    ('15', '15 dias'),

    ('7', '7 dias'),
)


TRANSACTION_STATUS_CHOICES = (
    ('aguardando', 'Aguardando'),
    ('em_analise', 'Em análise'),
    ('pago', 'Pago'),
    ('disponivel', 'Disponível'),
    ('em_disputa', 'Em disputa'),
    ('devolvido', 'Devolvido'),
    ('cancelado', 'Cancelado')
)



class Membership(models.Model):
    #membership_type = models.CharField( choices=MEMBERSHIP_CHOICES, default='Basic', max_length=30)
    name = models.CharField(help_text="Nome do Plano", max_length=50, default='Basic', blank=True)
    price = models.DecimalField(help_text=("valor do Plano"), max_digits=5, decimal_places=2, default=59.90,)
    valide_time = models.PositiveIntegerField( help_text=("Tempo de validate do Plano"), )
    #valide_time = models.CharField(choices=MEMBERSHIP_TIME, default='15', max_length=30)
    beneficios = models.TextField(blank=True,)
    level = models.IntegerField(choices=LEVELS, default=0, help_text="Escala do Plano [0 a 10]")
    active = models.BooleanField(default=False,)
    renew = models.BooleanField(help_text="Renovável ?", default=False)
    #description = models.CharField(max_length=100, blank=True,)

    class Meta:
        ordering = ['-level']
        verbose_name = "Plano"
        verbose_name_plural = 'Planos'

    def __str__(self):
        return "Plano *{0}* nivel {1}".format(self.name, self.level)

class SubscriptionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(end_date__gte = timezone.now())

class SubscriptionDaimondManager(models.Manager):
    def get_queryset(self):
        dia = super().get_queryset().filter(end_date__gte = timezone.now())
        return super().dia.filter(membership__membership_type='Diamond')

class SubscriptionTopManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(membership__membership_type='Top')

class SubscriptionDestManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(membership__membership_type='Destaque')


class Subscription(models.Model):
    types = models.IntegerField(default=0)
    code = models.CharField(max_length=100, unique=True, help_text="codigo de validação")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True)
    perfil = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    count = models.IntegerField(default=0)


    def active(self):
        if self.end_date > timezone.now():
            return True
        else:
            return False

    class Meta:
        ordering = ['-types']

    def __str__(self):
        return "Plano *{0}* para {1} {2}".format(self.membership.name, self.perfil.nome, self.perfil.sobrenome)

    objects = models.Manager()
    subs_active = SubscriptionManager()
    #subs_top = SubscriptionTopManager()
    #subs_destak = SubscriptionDestManager()
    #subs_diamond = SubscriptionDaimondManager()



