from django.db import models

# Create your models here.
class CodaDoc(models.Model):
    docID = models.CharField(max_length=30)


class CodaTable(models.Model):
    docID = models.CharField(max_length=30)
    tableID = models.CharField(max_length=64)
    tableName = models.CharField(max_length=64)
