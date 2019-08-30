from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token

# Create your models here.


class Agente(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="agente")
    country = models.CharField(max_length=50, blank=True, null=True, default="Brasil")
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    code_area = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    #cpf = models.CharField(max_length=50, blank=True, null=True)
    aceito = models.BooleanField(default=True)

    def __str__(self):
        return "Resp.: {0} {1}".format(self.user.first_name, self.user.last_name)

    def get_full_name(self):
        return "{0} {1}".format(self.user.first_name, self.user.last_name)

    def get_full_location(self):
        return "Adresse.: {0} {1} {2}".format(self.country, self.state, self.city)

    def owner_name(self):
        return "{0} {1}".format(self.user.last_name, self.user.first_name)

    def owner_numero(self):
        return "{0}{1}".format(self.code_area, self.phone)

    class Meta:
        verbose_name = 'agente'
        verbose_name_plural = 'agentes'
        ordering = ['-created']

class UserBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="balance")
    amount = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    created_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "Crédito de {0} na conta de {1}".format(self.amount, self.user.username)

    def get_value(self):
        return f'Crédito de {self.amount}'

    def balance_owner(self):
        return f'{self.user.first_name} {self.user.last_name}'


    class Meta:
        verbose_name = 'Crédito'
        verbose_name_plural = 'Crédito'


@receiver(post_save, sender=User)
def create_balance(sender, instance, created, **kwargs):
    if created:
        UserBalance.objects.get_or_create(user=instance)
        """try:
            balance = UserBalance.objects.get(user=instance)
        except UserBalance.DoesNotExist:
            balance = None

        if not balance:
            UserBalance.objects.create(user=instance) """


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        try:
            token = Token.objects.get(user=instance)
        except Token.DoesNotExist:
            token = None

        if not token:
            Token.objects.create(user=instance)

