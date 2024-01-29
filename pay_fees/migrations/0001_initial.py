# Generated by Django 4.2.7 on 2024-01-26 14:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import pay_fees.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("first_name", models.CharField(max_length=25)),
                ("middle_name", models.CharField(blank=True, max_length=25, null=True)),
                ("last_name", models.CharField(max_length=25)),
                ("id_number", models.IntegerField(null=True)),
                ("registration_number", models.CharField(max_length=15)),
                (
                    "email",
                    models.EmailField(
                        blank=True, default="", max_length=254, unique=True
                    ),
                ),
                ("bio", models.TextField(blank=True, max_length=500, null=True)),
                ("location", models.CharField(blank=True, max_length=30)),
                ("birth_date", models.DateField(blank=True, null=True)),
                ("phone", models.CharField(max_length=15, null=True)),
                ("is_authenticated", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_superuser", models.BooleanField(default=False)),
                (
                    "date_joined",
                    models.DateTimeField(default=pay_fees.models.default_now),
                ),
                ("last_login", models.DateTimeField(blank=True, null=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "User",
                "verbose_name_plural": "Users",
            },
            managers=[
                ("objects", pay_fees.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(default="course", max_length=50)),
                ("student_numbers", models.IntegerField(default=1000)),
                ("faculty_head", models.CharField(max_length=50, null=True)),
                ("fees", models.IntegerField(default=45670)),
                ("course_code", models.CharField(max_length=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="School",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(default="school", max_length=100)),
                (
                    "date_of_registration",
                    models.DateTimeField(default=pay_fees.models.default_now),
                ),
                ("school_head", models.CharField(max_length=50, null=True)),
                ("student_numbers", models.IntegerField(default=0)),
                ("school_code", models.CharField(max_length=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("transaction_code", models.CharField(max_length=50, unique=True)),
                ("transaction_type", models.CharField(max_length=10, null=True)),
                ("transaction_id", models.CharField(max_length=10, null=True)),
                ("transaction_time", models.DateTimeField(null=True)),
                ("transaction_amount", models.FloatField(null=True)),
                ("business_code", models.IntegerField(null=True)),
                ("bill_reference_number", models.CharField(max_length=100, null=True)),
                ("invoice_number", models.CharField(max_length=100, null=True)),
                ("original_account_balance", models.IntegerField(null=True)),
                (
                    "third_party_transaction_id",
                    models.CharField(max_length=100, null=True),
                ),
                ("msisdn", models.CharField(max_length=20, null=True)),
                ("first_name", models.CharField(max_length=50, null=True)),
                ("last_name", models.CharField(max_length=50, null=True)),
                ("complete", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("student_name", models.CharField(max_length=25, null=True)),
                ("balance", models.IntegerField(default=45670)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pay_fees.course",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Faculty",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(default="faculty", max_length=50)),
                ("student_numbers", models.IntegerField(default=1000)),
                ("faculty_code", models.CharField(max_length=15, null=True)),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pay_fees.school",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="course",
            name="faculty",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="pay_fees.faculty"
            ),
        ),
    ]
