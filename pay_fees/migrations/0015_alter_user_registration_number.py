# Generated by Django 4.2.7 on 2024-03-25 06:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pay_fees", "0014_staff_approved_alter_user_registration_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="registration_number",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
