# Generated by Django 3.2.7 on 2021-10-30 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TheStocks',
            fields=[
                ('primarykey', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10)),
                ('source', models.CharField(max_length=50)),
                ('purchase_date', models.DateTimeField(default=None)),
            ],
            options={
                'db_table': 'the_stocks',
                'managed': True,
            },
        ),
    ]
