# Generated by Django 5.0.6 on 2024-07-14 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_alter_enrollment_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='grade',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
