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
    cpf = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "Resp.: {0} {1}".format(self.user.first_name, self.user.last_name)

    def get_full_name(self):
        return "{0} {1}".format(self.user.first_name, self.user.last_name)

    def get_full_location(self):
        return "Adresse.: {0} {1} {2}".format(self.country, self.state, self.city)

    class Meta:
        verbose_name = 'agente'
        verbose_name_plural = 'agentes'
        ordering = ['-created']


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        try:
            token = Token.objects.get(user=instance)
        except Token.DoesNotExist:
            token = None

        if not token:
            Token.objects.create(user=instance)

