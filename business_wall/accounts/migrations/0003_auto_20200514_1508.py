# Generated by Django 3.0.2 on 2020-05-14 13:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20200514_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signuptoken',
            name='token',
            field=models.CharField(default=uuid.UUID('72387ad6-c8f6-463e-83d6-81f8cfc6a722'), max_length=255),
        ),
    ]
