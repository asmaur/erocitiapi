from django.db import models
import string, uuid, os
from random import choice
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit



from ..account.models import *
from .processors import Watermark


# Create your models here.
def change_name(filename):
    ext = filename.split('.')[-1]
    filename = "{0}.{1}".format(uuid.uuid4().hex, ext)
    return filename

def path_perfil(instance, filename):
# file will be uploaded to MEDIA_ROOT/company_<name>/

    return 'WANUCLOUD/{0}/{1}'.format(instance.code, change_name(filename))

def image_path_album(instance, filename):
# file will be uploaded to MEDIA_ROOT/company_<name>/shop_<name>/
    parent_path = instance.perfil._meta.get_field('capa').upload_to(instance.perfil, '')
    print(parent_path)
    return 'WANUCLOUD/{0}/images/originals/{1}'.format(instance.perfil.code, change_name(filename))

def image_path_album_erociti(instance, filename):
# file will be uploaded to MEDIA_ROOT/company_<name>/shop_<name>/
    parent_path = instance.perfil._meta.get_field('capa').upload_to(instance.perfil, '')
    print(parent_path)
    return 'WANUCLOUD/{0}/images/erociti/{1}'.format(instance.perfil.code, change_name(filename))


def video_path_album(instance, filename):
# file will be uploaded to MEDIA_ROOT/company_<name>/shop_<name>/
    parent_path = instance.perfil._meta.get_field('capa').upload_to(instance.perfil, '')
    return 'WANUCLOUD/{0}/videos/{1}'.format(instance.perfil.code, change_name(filename))


def photo_path_bike(instance, filename):
    # file will be uploaded to MEDIA_ROOT/company_<name>/shop_<name>/bikes/
    parent_path = instance.shop._meta.get_field('photo').upload_to(instance.shop, '')
    return parent_path + 'bikes/{0}'.format(filename)


def generate_id():
    n = 10
    random = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(choice(random) for _ in range(n))

def generate_uid():
    return str(uuid.uuid4().fields[-1])[:10]


class PhotoManager(models.Manager):
    def get_queryset(self):
        return super(PhotoManager, self).get_queryset().filter(is_public=True)


class PerfilWorkingManager(models.Manager):
    def get_queryset(self):
        return super(PerfilWorkingManager, self).get_queryset().filter(is_working=True)

class PerfilActiveManager(models.Manager):
    def get_queryset(self):
        return super(PerfilActiveManager, self).get_queryset().filter(is_active=True)

class PerfilPublicManager(models.Manager):
    def get_queryset(self):
        return super(PerfilPublicManager, self).get_queryset().filter(is_active=True).filter(is_working=True).filter(is_suspended=False)




class State(models.Model):
    code = models.CharField(max_length=3, )
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Brasil')

    class Meta:
        verbose_name = 'State'
        verbose_name_plural = 'States'

    def __str__(self):
        return self.code



class City(models.Model):
    name = models.CharField(max_length=100, )
    slug = models.SlugField(blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.slug




class Perfil(models.Model):
    code = models.CharField(max_length=250, blank=True, unique=True,)
    owner = models.ForeignKey(Agente, on_delete=models.CASCADE, related_name='perfis')
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=50, blank=True)
    nome = models.CharField(max_length=50, blank=True)
    sobrenome = models.CharField(max_length=50, blank=True)
    idade = models.IntegerField( blank=True)
    altura = models.DecimalField(max_digits=3, decimal_places=2, blank=True)
    peso = models.IntegerField(blank=True)
    slug = models.SlugField(max_length=250, blank=True, )
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    capa = ProcessedImageField(upload_to=path_perfil, processors=[ResizeToFit(1600, 900), Watermark(text="EroCiti")], format='JPEG', options={'quality': 75}, blank=True)
    is_vip = models.BooleanField(default=False)
    suspended = models.BooleanField(default=False)
    is_working = models.BooleanField(default=True)


    objects = models.Manager()
    objects_working = PerfilWorkingManager()

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        ordering = ['-created_at']

    def __str__(self):
        return "{0} {1}".format(self.nome, self.sobrenome)

    def fullname(self):
        return "{0} {1}".format(self.nome, self.sobrenome)

    def delete(self, *args, **kwargs):
        #self.capa.delete()
        os.remove(os.path.join(settings.MEDIA_ROOT, self.capa.name))
        super(Perfil, self).delete(*args, **kwargs)





class DadosPerfil(models.Model):
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    cabelo = models.CharField(max_length=50, blank=True)
    etnia = models.CharField(max_length=50, blank=True)
    seios = models.CharField(max_length=50, blank=True)
    men = models.BooleanField(default=True)
    women = models.BooleanField(default=False)
    couple = models.BooleanField(default=False)
    dote = models.IntegerField(blank=True, null=True)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='dados')
    tipo = models.CharField(max_length=20, blank=True,)

    class Meta:
        verbose_name = "Dados perfil"
        verbose_name_plural = "Dados perfis"

    def __str__(self):
        return "Dados de: {0} {1}".format(self.perfil.nome, self.perfil.sobrenome)



class Service(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='services')
    beijo_na_boca = models.BooleanField(default=False)
    duplas = models.BooleanField(default=False)
    ejacula_corpo = models.BooleanField(default=False)
    fan_disfarces = models.BooleanField(default=False)
    massagem_erotica = models.BooleanField(default=False)
    namoradinha = models.BooleanField(default=False)
    pse = models.BooleanField(default=False)
    sexo_anal = models.BooleanField(default=False)
    sexo_oral_com_cam = models.BooleanField(default=False)
    sexo_oral_sem_cam = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return "serviços de: {0} {1}".format(self.perfil.nome, self.perfil.sobrenome)



class Service_especial(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='especiais')
    beijo_negro =  models.BooleanField(default=False)
    chuva_dourada = models.BooleanField(default=False)
    fetichismo = models.BooleanField(default=False)
    garganta_profunda = models.BooleanField(default=False)
    sado_duro = models.BooleanField(default=False)
    sado_suave = models.BooleanField(default=False)
    squirting = models.BooleanField(default=False)
    strap_on = models.BooleanField(default=False)


    class Meta:
        verbose_name = "Service Especial"
        verbose_name_plural = "Service Especiais"


    def __str__(self):
        return "Serviços especiais de: {0} {1}".format(self.perfil.nome, self.perfil.sobrenome)


class Local(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='locais')
    hotel = models.BooleanField(default=False)
    motel = models.BooleanField(default=False)
    local_proprio = models.BooleanField(default=False)
    sobre_convite = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Local"
        verbose_name_plural = "Locais"


    def __str__(self):
        return "Locais de: {0} {1}".format(self.perfil.nome, self.perfil.sobrenome)



class Valor(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='valores')
    caches_30min = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    caches_1h = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    caches_2h = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    caches_3h = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    caches_4h = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    caches_pernoite_dia_util = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    caches_sexta_noite = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    caches_fim_semana_dia = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    caches_sabado_noite = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)


    class Meta:
        verbose_name = "Valor"
        verbose_name_plural = "Valores"


    def __str__(self):
        return "Valores de: {0} {1}".format(self.perfil.nome, self.perfil.sobrenome)


class NewsUsers(models.Model):
    email = models.EmailField()
    created_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "NewsUser"
        verbose_name_plural = "NewsUsers"

        def __str__(self):
            return self.email

class Denunciar(models.Model):
    perfil_id = models.CharField(max_length=100)
    link = models.URLField()
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Denuncia"
        verbose_name_plural = "Denuncias"

    def __str__(self):
        return self.perfil_id




class Album(models.Model):

    title = models.CharField(max_length=100, blank=True)
    perfil = models.ForeignKey('Perfil', on_delete=models.CASCADE, related_name='albuns')
    created = models.DateField(auto_now=True)

    class Meta:
        ordering = ['-created']
        verbose_name = "Album"
        verbose_name_plural = 'albuns'

    def __str__(self):
        return "Album de: {0} {1}".format(self.perfil.nome, self.perfil.sobrenome)


class Image(models.Model):

    code = models.CharField(max_length=250, blank=True, unique=True, )
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='images')
    image_erociti = ProcessedImageField(upload_to=image_path_album_erociti, processors=[ResizeToFit(1600, 900), Watermark(text="EroCiti")], format='JPEG', options={'quality': 75}, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField('date added', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self):
        return "Foto de: {0} {1}".format(self.perfil.nome, self.perfil.sobrenome)

    objects = models.Manager()
    objects_active = PhotoManager()

    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.image_erociti.name))
        super(Image, self).delete(*args, **kwargs)





class Video(models.Model):
    code = models.CharField(max_length=250, blank=True, unique=True, )
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    video = models.FileField(upload_to=video_path_album, blank=True)
    is_public = models.BooleanField(default=True)
    date_added = models.DateTimeField('date added', auto_now=True)

    class Meta:
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = "Video"
        verbose_name_plural = "Videos"

    def __str__(self):
        return "Video de: {0} {1}".format(self.perfil.nome, self.perfil.sobrenome)

    default = models.Manager()
    objects = PhotoManager()



class PerfilViewCount(models.Model):

    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name="views")
    created = models.DateField(blank=True, null=True)
    views = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created']

    def month(self):
        return self.pub_date.strftime('%m')

    def __str__(self):
        return "{0} views de: {1} {2}".format(self.views, self.perfil.nome, self.perfil.sobrenome)


class PerfilNumberClick(models.Model):

    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name="klics")
    created = models.DateField(blank=True, null=True)
    clicked = models.IntegerField(default=0)

    class Meta:
        ordering = ['created']

    def month(self):
        return self.pub_date.strftime('%m')

    def __str__(self):
        return "{0} click de: {1} {2}".format(self.clicked, self.perfil.nome, self.perfil.sobrenome)


class Transactions(models.Model):
    perId = models.IntegerField()
    userId = models.IntegerField()
    planoId = models.IntegerField()
    transactionCode = models.CharField(max_length=200)
    status = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.transactionCode


class ChangePasseCode(models.Model):
    code = models.UUIDField(blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now=True)
    end_at = models.DateTimeField(blank=True)

    def active(self):
        if self.end_date > self.created_at:
            return True
        else:
            return False

    def __str__(self):
        return self.email


class NewsLettersAds(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


@receiver(pre_save, sender=Perfil)
def perfil_pre_save(sender, **kwargs):
    perfil = kwargs.get('instance')

    if not perfil.code:
        perfil.code = generate_uid()

    if not perfil.slug:
        perfil.slug = slugify("{0}-{1}".format(perfil.nome, perfil.sobrenome))

    #capa = add_text_overlay(perfil.capa, "DEI X")
    #perfil.capa = capa

    print(perfil.slug, perfil.code)

@receiver(post_save, sender=Perfil)
def perfil_post_save(sender, **kwargs):
    perfil = kwargs.get('instance')
    dad = DadosPerfil.objects.update_or_create(perfil=perfil)
    serv = Service.objects.update_or_create(perfil=perfil)
    esp = Service_especial.objects.update_or_create(perfil=perfil)
    val = Valor.objects.update_or_create(perfil=perfil)
    loc = Local.objects.update_or_create(perfil=perfil)

    print("Post Save Done")




@receiver(pre_save, sender=City)
def city_pre_save(sender, **kwargs):
    city = kwargs.get('instance')

    if not city.slug:
        city.slug = slugify(city.name)


@receiver(pre_save, sender=Image)
def image_pre_save(sender, **kwargs):
    image = kwargs.get('instance')

    if not image.code:
        image.code = generate_uid()

    print(image.code)


@receiver(pre_save, sender=Video)
def video_pre_save(sender, **kwargs):
    video = kwargs.get('instance')

    if not video.code:
        video.code = generate_uid()


