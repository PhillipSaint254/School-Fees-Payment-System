from django.db.models import Q
from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager


def default_now():
    now = timezone.now() + timezone.timedelta(hours=3)
    return now


def code_generate():
    last_trans = Transaction.objects.all().order_by("-transaction_code")
    current_date = datetime.now().strftime('%Y%m%d')

    if last_trans.count() > 0:
        counter = 1
        print(last_trans[0].transaction_code)
        new_code = int(last_trans[0].transaction_code[-6:-1]) + counter
        if len(str(new_code)) > 5:
            new_code = "00001"
        transaction_code = f"MxS{current_date}{new_code}"
        while True:
            try:
                Transaction.objects.get(transaction_code=transaction_code)
                counter += 1
                new_code += counter
                if len(str(new_code)) > 5:
                    new_code = "00001"
                transaction_code = f"{current_date}{new_code}"
            except Transaction.DoesNotExist:
                break
        return transaction_code
    else:
        random_numbers = ''.join(str(random.randint(0, 9)) for _ in range(5))
        transaction_code = f"MxS{current_date}{random_numbers}"
        return transaction_code


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not provided a valid email!")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_staff(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=25)
    middle_name = models.CharField(max_length=25, null=True, blank=True)
    last_name = models.CharField(max_length=25)
    id_number = models.IntegerField(null=True)
    registration_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, unique=True, default='')

    bio = models.TextField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=default_now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_full_name(self):
        return f"{self.first_name.capitalize()} {self.middle_name.capitalize() if self.middle_name else ''} {self.last_name.capitalize()}"

    def get_short_name(self):
        return self.first_name or self.email.split("@")[0]


class School(models.Model):
    name = models.CharField(max_length=100, default="school")
    date_of_registration = models.DateTimeField(default=default_now)
    school_head = models.CharField(max_length=50, null=True)
    student_numbers = models.IntegerField(default=0)
    school_code = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.name


class Faculty(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="faculty")
    student_numbers = models.IntegerField(default=1000)
    faculty_code = models.CharField(max_length=15, null=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class Course(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="course")
    student_numbers = models.IntegerField(default=1000)
    fees = models.IntegerField(default=45670)
    course_code = models.CharField(max_length=15, null=True)

    def __str__(self):
        return f"{self.name} - {self.faculty.school.school_code}"


class Student(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    student_name = models.CharField(max_length=25, null=True)
    balance = models.IntegerField(default=45670)
    full_fees = models.IntegerField(default=45670)

    def __str__(self):
        return self.student_name


@receiver(post_save, sender=Student)
def update_student_numbers(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        faculty = instance.course.faculty
        school = instance.course.faculty.school
        print("course", course)
        print("faculty", faculty)
        print("school", school)

        course.student_numbers = Student.objects.filter(course=course).count()
        course.save()

        faculty.student_numbers = Student.objects.filter(course__faculty=faculty).count()
        faculty.save()

        school.student_numbers = Student.objects.filter(course__faculty__school=school).count()
        school.save()


class Transaction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, null=True)
    transaction_code = models.CharField(max_length=50, unique=True, default=code_generate)
    transaction_type = models.CharField(max_length=10, null=True)
    transaction_id = models.CharField(max_length=10, null=True)
    transaction_time = models.DateTimeField(null=True)
    transaction_amount = models.FloatField(null=True)
    business_code = models.IntegerField(null=True)
    bill_reference_number = models.CharField(max_length=100, null=True)
    invoice_number = models.CharField(max_length=100, null=True)
    original_account_balance = models.IntegerField(null=True)
    third_party_transaction_id = models.CharField(max_length=100, null=True)
    msisdn = models.CharField(max_length=20, null=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    complete = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(default=default_now, null=True)
    payment_method = models.CharField(max_length=20, default="m-pesa")
    status = models.CharField(max_length=10, default="incomplete")
    # Preprocessing data
    merchant_request_id = models.CharField(max_length=100, null=True)
    checkout_request_id = models.CharField(max_length=100, null=True)
    response_code = models.IntegerField(null=True)
    customer_message = models.CharField(max_length=250, null=True)
    response_description = models.CharField(max_length=250, null=True)

    def __str__(self):
        return f"<{self.id}> {self.student.user.first_name} {self.student.user.last_name}"


class PaymentMethods(models.Model):
    name = models.CharField(max_length=20)
    company = models.CharField(max_length=50, null=True)
    instructions = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Payment Option"
        verbose_name_plural = "Payment Options"

    def __str__(self):
        return self.name.capitalize()


class Parent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="Parent")
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="Student")
    parent_name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.parent_name


class Staff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="Staff")
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, related_name="WorkPlace")
    staff_name = models.CharField(max_length=50, null=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.staff_name


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=50, default="Anonymous")
    comment = models.TextField()
    time_stamp = models.DateTimeField(default=default_now)
    state = models.CharField(max_length=15, default="Accepted")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}" if self.user else self.username
