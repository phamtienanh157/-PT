from importlib.metadata import files
from statistics import mode
from django.db import models

# Create your models here.
class Document(models.Model):
    doc_id = models.AutoField(primary_key=True,default=None)
    file = models.FileField(upload_to='files',null=False,default=None)
    name_document = models.CharField(max_length=100,default=None)
    dictionary = models.CharField(max_length=100,default=None)
    datecreate = models.DateTimeField(null=True,blank=True)