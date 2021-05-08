# Generated by Django 3.0.2 on 2020-05-15 08:14

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('normal_rate', models.IntegerField(default=0)),
                ('overtime_rate', models.IntegerField(default=50)),
                ('holiday_rate', models.IntegerField(default=100)),
                ('weekend_rate', models.IntegerField(default=25)),
                ('evening_rate', models.IntegerField(default=15)),
            ],
        ),
        migrations.CreateModel(
            name='Time',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_time', models.DateTimeField(default=None, null=True)),
                ('time_worked', models.DurationField(default=datetime.timedelta(0))),
                ('overtime', models.DurationField(default=datetime.timedelta(0))),
                ('evening', models.DurationField(default=datetime.timedelta(0))),
                ('weekend', models.DurationField(default=datetime.timedelta(0))),
                ('holiday', models.DurationField(default=datetime.timedelta(0))),
                ('note', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='Stamp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stampedIn', models.BooleanField(default=False)),
                ('end_of_day', models.TimeField(default=datetime.time(16, 0))),
                ('shift_duration', models.DurationField(default=datetime.timedelta(seconds=28800))),
                ('additonal_rate', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='timesheet.AdditionalRate')),
                ('time_model', models.ManyToManyField(blank=True, to='timesheet.Time')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PayCheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taxes', models.IntegerField(default=25)),
                ('vacation_money_basis', models.FloatField(default=12)),
                ('wage', models.FloatField(default=0)),
                ('worker', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]