from django.db import models
from django.contrib.auth.models import User


class TheStocks(models.Model):
    primarykey = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10)
    source = models.CharField(max_length=50)
    purchase_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        default=None)

    class Meta:
        managed = True
        db_table = 'the_stocks'


class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    stock = models.ForeignKey(TheStocks, on_delete=models.DO_NOTHING)
