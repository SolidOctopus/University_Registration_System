# Generated by Django 5.0.6 on 2024-07-18 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0007_course_capacity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='available_seats',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
