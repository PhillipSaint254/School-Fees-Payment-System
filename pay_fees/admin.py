from django.contrib import admin
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("first_name", "middle_name", "last_name", "email", "phone", 'registration_number')


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    search_fields = ("name", "school_head", "school_code")


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    search_fields = ("name", "faculty_code")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    search_fields = ("name", "fees", "course_code")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ("student_name", "fees")


@admin.register(PaymentMethods)
class PaymentMethodsAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    search_fields = ("transaction_code", "transaction_type", "transaction_id", "transaction_amount", "business_code",
                     "bill_reference_number", "invoice_number", "msisdn", "first_name", "last_name")
