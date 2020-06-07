# Generated by Django 3.0.6 on 2020-06-06 18:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pricingdata', '0006_auto_20200606_2334'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyReturn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(db_index=True)),
                ('return_1m', models.FloatField(null=True)),
                ('return_2m', models.FloatField(null=True)),
                ('return_3m', models.FloatField(null=True)),
                ('return_4m', models.FloatField(null=True)),
                ('return_5m', models.FloatField(null=True)),
                ('return_6m', models.FloatField(null=True)),
                ('return_7m', models.FloatField(null=True)),
                ('return_8m', models.FloatField(null=True)),
                ('return_9m', models.FloatField(null=True)),
                ('return_10m', models.FloatField(null=True)),
                ('return_11m', models.FloatField(null=True)),
                ('return_12m', models.FloatField(null=True)),
                ('return_13m', models.FloatField(null=True)),
                ('return_14m', models.FloatField(null=True)),
                ('return_15m', models.FloatField(null=True)),
                ('return_16m', models.FloatField(null=True)),
                ('return_17m', models.FloatField(null=True)),
                ('return_18m', models.FloatField(null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pricingdata.Company')),
                ('exchange', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pricingdata.Exchange')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DailyReturn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(db_index=True)),
                ('return_1d', models.FloatField(null=True)),
                ('return_2d', models.FloatField(null=True)),
                ('return_3d', models.FloatField(null=True)),
                ('return_4d', models.FloatField(null=True)),
                ('return_5d', models.FloatField(null=True)),
                ('return_6d', models.FloatField(null=True)),
                ('return_7d', models.FloatField(null=True)),
                ('return_14d', models.FloatField(null=True)),
                ('return_21d', models.FloatField(null=True)),
                ('return_25d', models.FloatField(null=True)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pricingdata.Company')),
                ('exchange', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pricingdata.Exchange')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
