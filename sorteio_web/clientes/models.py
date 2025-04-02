from django.db import models

# Create your models here.
class Cliente(models.Model):
    primeiro_nome = models.CharField(max_length=255)
    ultimo_nome = models.CharField(max_length=255)