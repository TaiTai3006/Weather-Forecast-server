from django.db import models

class Mail(models.Model):
    gmail = models.CharField(primary_key=True, max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mail'