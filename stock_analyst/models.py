from django.db import models

# Create your models here.

class Companies(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    symbol = models.TextField(unique=True)
    company_name = models.TextField(unique=True)

class Dates(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    date = models.DateField(unique=True)

class Datapoints(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    date = models.ForeignKey(Dates, on_delete=models.CASCADE)
    open = models.FloatField()
    close = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    volume = models.FloatField()

class Update(models.Model):
    last_update = models.DateField()