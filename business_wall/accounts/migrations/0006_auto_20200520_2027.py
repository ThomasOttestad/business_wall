# Generated by Django 3.0.2 on 2020-05-20 18:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_merge_20200520_2022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signuptoken',
            name='token',
            field=models.CharField(default=uuid.UUID('5c5987ca-8cea-45b7-ac5f-70d632bdd873'), max_length=255),
        ),
    ]