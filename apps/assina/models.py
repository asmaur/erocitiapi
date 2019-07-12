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
    membership_type = models.CharField(
        choices=MEMBERSHIP_CHOICES,
        default='Basic',
        max_length=30)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=59.90,)
    valide_time = models.CharField(choices=MEMBERSHIP_TIME,
        default='15',
        max_length=30)
    beneficios = models.TextField(blank=True,)
    active = models.BooleanField(default=False,)
    description = models.CharField(max_length=100, blank=True,)

    def __str__(self):
        return self.membership_type

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
    types = models.IntegerField(TYPE_SUBS, default=3)
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

    def __str__(self):
        return "Plano *{0}* para {1} {2}".format(self.membership.membership_type, self.perfil.nome, self.perfil.sobrenome)

    objects = models.Manager()
    subs_active = SubscriptionManager()
    subs_top = SubscriptionTopManager()
    subs_destak = SubscriptionDestManager()
    subs_diamond = SubscriptionDaimondManager()



