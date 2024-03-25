import base64
import json

import requests
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from django_daraja.mpesa.core import MpesaClient
from rest_framework.permissions import AllowAny
from datetime import datetime
from pay_fees.models import default_now, School, Faculty, Course, Student, User, PaymentMethods, Transaction, Parent, \
    Staff
from rest_framework.generics import CreateAPIView
from pay_fees.serializers import TransactionSerializer

# def index(request):
#     cl = MpesaClient()
#     # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
#     phone_number = '0742332937'
#     amount = 1
#     account_reference = 'reference'
#     transaction_desc = 'Description'
#     callback_url = 'https://paymyfees.onrender.com/process_pay/7/'
#     response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
#     return HttpResponse(response)


def index(request):
    user = request.user
    if user.is_authenticated:
        if user.is_superuser:
            if request.method == "POST":
                if request.POST.get("admin"):
                    return render(request, "admin index.html")
                elif request.POST.get("staff"):
                    incomplete_completed_fees = Student.objects.filter(balance__gt=0)
                    completed_fees = Student.objects.filter(balance__lte=0)
                    all_students = Student.objects.all()
                    return render(request, "staff index.html",
                                  {"incomplete_completed_fees": incomplete_completed_fees,
                                   "completed_fees": completed_fees,
                                   "all_students": all_students})
                elif request.POST.get("student"):
                    return render(request, "index.html", {"current_time": default_now()})
                else:
                    messages.error(request, "Invalid choice, please select again.")
            return render(request, "admin login prompt.html")
        elif user.is_staff:
            if request.method == "POST":
                if request.POST.get("staff"):
                    incomplete_completed_fees = Student.objects.filter(balance__gt=0)
                    completed_fees = Student.objects.filter(balance__lte=0)
                    all_students = Student.objects.all()
                    return render(request, "staff index.html",
                                  {"incomplete_completed_fees": incomplete_completed_fees,
                                   "completed_fees": completed_fees,
                                   "all_students": all_students})
                elif request.POST.get("student"):
                    return render(request, "index.html", {"current_time": default_now()})
                else:
                    messages.error(request, "Invalid choice, please select again.")
            return render(request, "staff login prompt.html")
        schools = School.objects.all()
        return render(request, "dashboard.html", {"current_time": default_now(), "schools": schools})
    return render(request, "index.html", {"current_time": default_now()})


def admin_index(request):
    user = request.user
    if user.is_authenticated:
        if user.is_superuser:
            return render(request, "admin index.html")
        messages.error(request, "This section is reserved for admins.")

        return render(request, "index.html", {"current_time": default_now()})

    messages.error(request, "Access reserved to authenticated admin!")
    return redirect("pay_fees:login")


def user_login(request):
    if request.user.is_authenticated:
        messages.error(request, "You are already signed in.")
        return render(request, "index.html", {"current_time": default_now()})

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successfull")

            return render(request, "index.html", {"current_time": default_now()})

        messages.error(request, "Invalid credentials!")
        return redirect("pay_fees:login")

    return render(request, "login.html")


def user_registration(request):
    if request.method == "POST":
        first_name = request.POST["first-name"].lower().strip()
        last_name = request.POST["last-name"].strip().lower()
        middle_name = request.POST["middle-name"].strip().lower()
        email = request.POST["email"].strip().lower()
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        reg_number = request.POST["registration-number"].upper().strip() if request.POST["registration-number"] else ""
        phone = request.POST["phone-number"].strip()
        id_number = request.POST["id-number"].strip()

        faculty_input = request.POST.get("faculty-input", None)
        school_input = request.POST.get("school-input", None)
        course_input = request.POST.get("course-input", None)

        print(f"{email} {password1} {password2} {reg_number} {phone} {course_input}")

        def check_reg():
            if not (reg_number and course_input and email and first_name and password1):
                messages.error(request, "All fields required!")
                return redirect("pay_fees:register")

        def check_email():
            try:
                User.objects.get(email=email)
                messages.error(request, f"User with the email '{email}' already exists.")
                return redirect("pay_fees:register")
            except:
                pass

        def check_student_details():
            try:
                School.objects.get(id=school_input.split(":")[0])
            except:
                messages.error(request, "Please choose a valid school option.")
                return redirect("pay_fees:register")

            try:
                Faculty.objects.get(id=faculty_input.split(":")[0])
            except:
                messages.error(request, "Please choose a valid faculty option.")
                return redirect("pay_fees:register")

            try:
                User.objects.get(registration_number=reg_number)
                messages.error(request, f"User with the registration number '{email}' already exists.")
                return redirect("pay_fees:register")
            except:
                pass

            try:
                course_id = course_input.split(":")[0]
                return Course.objects.get(id=course_id)
            except:
                messages.error(request, "Please choose a valid course option.")
                return redirect("pay_fees:register")

        if password1 == password2:

            try:
                user_id = 1
                last_user = User.objects.all().order_by("-id")
                if last_user:
                    user_id = last_user[0].id + 1

                    while True:
                        try:
                            User.objects.get(user_id)
                            user_id += 1
                        except:
                            break

                user = User.objects.create(
                    id=user_id,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    registration_number=reg_number,
                    phone=phone,
                )

                if middle_name:
                    user.middle_name = middle_name

                if id_number:
                    user.id_number = id_number

                user.set_password(password1)

                user.save()

                if "register-parent" in request.POST:
                    """Parent registration"""
                    if user is not None:
                        login(request, user)

                    return render(request, "select student.html")

                elif "register-student" in request.POST:
                    """Student registration"""
                    check_reg()
                    course = check_student_details()
                    if course:
                        student_id = 1
                        last_student = Student.objects.all().order_by("-id")
                        if last_student:
                            student_id = last_student[0].id + 1

                            while True:
                                try:
                                    Student.objects.get(student_id)
                                    student_id += 1
                                except:
                                    break

                        student = Student.objects.create(
                            id=student_id,
                            user=user,
                            course=course,
                            student_name=f"{first_name} {last_name}",
                            balance=course.fees
                        )
                        student.save()

                    if user is not None:
                        login(request, user)

                    messages.success(request, "Registration successful.")

                    return render(request, "index.html", {"current_time": default_now()})

                messages.error(request, "Course selection error.")
                return redirect("pay_fees:register")

            except IntegrityError:
                messages.error(request, "Email or registration number already registered.")
                raise
            except Exception as error:
                messages.error(request, error)
                schools = School.objects.all()
                redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                return redirect(redirect_url)

        else:
            messages.error(request, "Password mismatch.")
            return redirect("pay_fees:register")

    return render(request, "registration.html")


def stk_push_callback(request):
    data = request.body

    return HttpResponse("STK Push in Django👋", {"data": data})


def call_back(request, orderid=-1):
    if request.method == "POST":
        if request.content_type == "application/json":
            try:
                json_data = request.json()
                extract_data = json.loads(json_data)

                data = {
                    "orderid": orderid,
                    "body": extract_data
                }
                return JsonResponse({"data": data})
            except ValueError:
                return JsonResponse({"data": "JSON file not received."}, status=400)
        else:
            return JsonResponse({"data": "Expected JSON content type."}, status=400)
    else:
        return JsonResponse({"data": "Please send JSON file"})


def add_school(request):
    user = request.user
    if user.is_authenticated:
        if user.is_superuser:
            if request.method == "POST":
                school_name = request.POST["school-name"].lower()
                school_head = request.POST["head-of-school"].lower()
                registration_date = request.POST["date-of-registration"]
                short_code = request.POST["school-shortcode"].upper()

                if not (school_name and school_head and registration_date and short_code):
                    messages.error(request, "All fields required.")
                    return redirect("pay_fees:add_school")

                date = timezone.datetime.strptime(registration_date, "%Y-%m-%dT%H:%M")

                print(f"{school_name} {school_head} {registration_date} {short_code} {date}")
                #
                # school = School.objects.create(
                #     name=school_name,
                #     date_of_registration=registration_date,
                #     school_head=school_head,
                #     school_code=short_code
                # )
                #
                # school.save()
                messages.success(request, "School saved successfully.")

            return render(request, "add school.html")
        messages.error(request, "This section is reserved for admins.")

        return render(request, "index.html", {"current_time": default_now()})

    messages.error(request, "Access reserved to authenticated admin!")
    return redirect("pay_fees:login")


def add_staff(request):
    user = request.user
    if user.is_authenticated:
        if user.is_superuser or user.is_staff:
            if request.method == "POST":
                first_name = request.POST["first-name"].lower().strip()
                last_name = request.POST["last-name"].strip().lower()
                middle_name = request.POST["middle-name"].strip().lower()
                email = request.POST["email"].strip().lower()
                password1 = request.POST["password1"]
                password2 = request.POST["password2"]
                phone = request.POST["phone-number"].strip()
                id_number = request.POST["id-number"].strip()

                school_input = request.POST["school-input"]

                try:
                    User.objects.get(email=email)
                    messages.error(request, f"User with the email '{email}' already exists.")
                    return redirect("pay_fees:register")
                except:
                    pass

                try:
                    school = School.objects.get(id=school_input.split(":")[0])
                except:
                    messages.error(request, "Please choose a valid school option.")
                    return redirect("pay_fees:register")

                if password1 == password2:

                    try:
                        user_id = 1
                        last_user = User.objects.all().order_by("-id")
                        if last_user:
                            user_id = last_user[0].id + 1

                            while True:
                                try:
                                    User.objects.get(user_id)
                                    user_id += 1
                                except:
                                    break

                        user = User.objects.create(
                            id=user_id,
                            email=email,
                            first_name=first_name,
                            last_name=last_name,
                            phone=phone,
                        )

                        if middle_name:
                            user.middle_name = middle_name

                        if id_number:
                            user.id_number = id_number

                        user.set_password(password1)

                        user.save()

                        staff_id = 1
                        last_staff = Staff.objects.all().order_by("-id")
                        if last_user:
                            staff_id = last_staff[0].id + 1

                            while True:
                                try:
                                    Staff.objects.get(user_id)
                                    staff_id += 1
                                except:
                                    break

                        staff = Staff.objects.create(
                            id=staff_id,
                            staff_name=user.get_full_name()
                        )

                        staff.school = school

                        if user.is_superuser:
                            staff.approved = True

                        staff.save()

                        messages.success(request, "Staff registration successful.")
                        return render(request, "index.html", {"current_time": default_now()})

                    except IntegrityError:
                        messages.error(request, "Email or registration number already registered.")
                        raise
                    except Exception as error:
                        messages.error(request, error)
                        schools = School.objects.all()
                        redirect_url = reverse(
                            'pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                        return redirect(redirect_url)

            return render(request, "add staff.html")
        messages.error(request, "This section is reserved for admins.")

        return render(request, "index.html", {"current_time": default_now()})

    messages.error(request, "Access reserved to authenticated admin!")
    return redirect("pay_fees:login")


def user_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Logout successful.")
        return render(request, "index.html")
    messages.error(request, "You are already logged out!")

    return render(request, "index.html", {"current_time": default_now()})


def all_school(request):
    schools = School.objects.all()
    school_names = [f"{school.id}: {school.school_code} - {school.name.capitalize()}" for school in schools]
    return JsonResponse({"schools": school_names})


@require_GET
def get_faculties(request):
    school_id = request.GET.get('school')
    school = School.objects.get(pk=school_id)

    if school:
        faculties = Faculty.objects.filter(school=school)
        faculty_names = [f"{faculty.pk}: {faculty.name.capitalize()} - {faculty.school.school_code}" for faculty in faculties]
        return JsonResponse({'faculties': faculty_names})
    else:
        return JsonResponse({'error': 'Invalid school ID'}, status=400)


@require_GET
def get_courses(request):
    school_id = request.GET.get('school')
    faculty_id = request.GET.get('faculty')
    school = School.objects.get(pk=school_id)
    faculty = Faculty.objects.get(school=school, id=faculty_id)

    if faculty:
        courses = Course.objects.filter(faculty=faculty)
        course_names = [f"{course.pk}: {course.name.capitalize()} - " \
                        f"{course.faculty.school.school_code}" for course in courses]
        return JsonResponse({'courses': course_names})
    else:
        return JsonResponse({'error': 'Invalid school ID or faculty name'}, status=400)


def get_all_students(request):
    students = Student.objects.all().order_by("student_name")
    student_names = [f"{student.id}: {student.user.get_full_name().capitalize()}" for student in students]
    return JsonResponse({"students": student_names})


def dashboard(request):
    user = request.user
    if user.is_authenticated:
        schools = School.objects.all()
        return render(request, "dashboard.html", {"current_time": default_now(), "schools": schools})
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


def pay_fees(request):
    user = request.user
    if user.is_authenticated:
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            messages.error(request, "Only students are allowed to make transactions")
            schools = School.objects.all()
            redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
            return redirect(redirect_url)

        payment_options = PaymentMethods.objects.all()
        transaction_id = 1

        transaction = Transaction.objects.all().order_by("-id")
        if transaction:
            transaction_id = transaction[0].id + 1
            while True:
                try:
                    Transaction.objects.get(transaction_id)
                    transaction_id += 1
                except:
                    break

        transaction = Transaction(id=transaction_id, student=student)
        transaction.save()
        return render(request, "payment method.html", {"payment_options": payment_options, "transaction": transaction})
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


def handle_selected_payment_method(request, id):
    user = request.user
    if user.is_authenticated:
        transaction = Transaction.objects.get(id=id)
        if transaction.student.user == user:
            if not transaction.complete:
                if request.method == "POST":
                    payment_method = request.POST.get("paymentMethod", "")
                    transaction.payment_method = payment_method if payment_method else "m-pesa"
                    transaction.save()
                    return render(request, "payment details.html", {"transaction": transaction})
                messages.error(request, "No payment method selected")
                schools = School.objects.all()
                redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                return redirect(redirect_url)
            messages.error(request, "Transaction already effected.")
            schools = School.objects.all()
            redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
            return redirect(redirect_url)
        messages.error(request, "You are not authorized to make this transaction!")
        schools = School.objects.all()
        redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
        return redirect(redirect_url)
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


def payment_details(request, id):
    user = request.user
    if user.is_authenticated:
        transaction = Transaction.objects.get(id=id)
        if transaction.student.user == user:
            if not transaction.complete:
                if request.method == "POST":
                    amount = request.POST["amount"]
                    phone = request.POST["phone-number"]
                    transaction.transaction_amount = amount if amount else transaction.student.balance
                    transaction.msisdn = phone
                    transaction.save()
                    return render(request, "confirm pay.html", {"transaction": transaction})
                messages.error(request, "Form not submitted")
                schools = School.objects.all()
                redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                return redirect(redirect_url)
            messages.error(request, "Transaction already effected.")
            schools = School.objects.all()
            redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
            return redirect(redirect_url)
        messages.error(request, "You are not authorized to make this transaction!")
        schools = School.objects.all()
        redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
        return redirect(redirect_url)
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


def process_pay(request, id):
    user = request.user
    if user.is_authenticated:
        transaction = Transaction.objects.get(id=id)
        if transaction.student.user == user:
            if not transaction.complete:
                if request.method == "POST":
                    if request.content_type == "application/json":
                        try:
                            json_data = request.json()
                            extract_data = json.loads(json_data)

                            print()
                            print()
                            print("### RESPONSE DATA ###")
                            print("***********************************************")
                            print(request.data)
                            print("***********************************************")
                            print()
                            print()
                            data = {
                                "transaction_code": transaction.transaction_code,
                                "body": extract_data
                            }

                            return JsonResponse({"data": data})
                        except ValueError:
                            return JsonResponse({"data": "JSON file not received."}, status=400)
                    else:
                        return JsonResponse({"data": "Expected JSON content type."}, status=400)

                data = request.body
                return HttpResponse("STK Push in Django👋", {"data": data})
            messages.error(request, "Transaction already effected.")
            schools = School.objects.all()
            redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
            return redirect(redirect_url)
        messages.error(request, "You are not authorized to make this transaction!")
        schools = School.objects.all()
        redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
        return redirect(redirect_url)
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


class PayProcessView(CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]

    def create(self, request, id):
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "Access reserved to authenticated users!")
            return redirect("pay_fees:login")

        try:
            transaction = Transaction.objects.get(id=id)
        except Transaction.DoesNotExist:
            return JsonResponse({'error': 'Transaction not found.'}, status=404)

        if transaction.student.user != user:
            messages.error(request, "You are not authorized to make this transaction!")
            schools = School.objects.all()  # Ensure you have defined School somewhere or adjust accordingly
            redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
            return redirect(redirect_url)

        if transaction.complete:
            messages.error(request, "Transaction already effected.")
            schools = School.objects.all()  # Ensure you have defined School somewhere or adjust accordingly
            redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
            return redirect(redirect_url)

        data = request.data
        print()
        print()
        print("###############DATA##############")
        print(data)
        print("#################################")
        print()
        print()

        try:
            body = data["Body"]
            stkCallback = body["stkCallback"]
            result_code = stkCallback["ResultCode"]

            merchant_request_id = stkCallback["MerchantRequestID"]
            checkout_request_id = stkCallback["CheckoutRequestID"]  # Corrected typo
            result_description = stkCallback["ResultDesc"]

            if result_code == "0" or result_code == 0:
                callback_metadata = stkCallback["CallbackMetadata"]["Item"]
                amount = next(item for item in callback_metadata if item["Name"] == "Amount")["Value"]
                mpesa_receipt_number = next(item for item in callback_metadata if item["Name"] == "MpesaReceiptNumber")[
                    "Value"]
                transaction_date = next(item for item in callback_metadata if item["Name"] == "TransactionDate")["Value"]
                phone_number = next(item for item in callback_metadata if item["Name"] == "PhoneNumber")["Value"]

                str_datetime = str(transaction_date)
                actual_datetime = datetime.strptime(str_datetime, "%Y%m%d%H%M%S")

                transaction.merchant_request_id = merchant_request_id
                transaction.checkout_request_id = checkout_request_id
                transaction.transaction_amount = amount
                transaction.response_description = result_description
                transaction.response_code = result_code
                transaction.transaction_time = actual_datetime
                transaction.msisdn = phone_number
                transaction.complete = True
                transaction.save()

                student = transaction.student

                student.balance -= amount
                student.save()

                messages.success(request,
                                 f"You have successfully paid {amount} to {student.faculty.school.name} at {actual_datetime}.")
                return render(request, "index.html", {"current_date": default_now()})

            messages.warning(request, result_description)
            schools = School.objects.all()  # Ensure you have defined School somewhere or adjust accordingly
            redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
            return redirect(redirect_url)

        except KeyError as e:
            transaction.student.balance -= transaction.transaction_amount
            transaction.student.save()
            transaction.complete = True
            transaction.status = "success"
            messages.success(request,
                             f"You have successfully paid {transaction.transaction_amount} to {transaction.student.faculty.school.name}.")
            return render(request, "index.html", {"current_date": default_now()})

        except Exception as e:
            return JsonResponse({'error': f'Some error occured: {str(e)}'}, status=400)


def test_api(request):
    print(request.body)
    print(request.POST)
    return HttpResponse(request.data)


class TestAPIView(CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        print(request.body)
        print(request.POST)
        return HttpResponse(request.data)


def my_transactions(request):
    user = request.user
    if user.is_authenticated:
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            messages.error(request, "Only students are allowed to view transactions")
            schools = School.objects.all()
            redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
            return redirect(redirect_url)
        _my_transactions = Transaction.objects.filter(student=student).order_by("-time_stamp")
        return render(request, "my pays.html", {"my_transactions": _my_transactions, "account": student.course.faculty.school.name})
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


def recover_transaction(request, id):
    user = request.user
    if user.is_authenticated:
        transaction = Transaction.objects.get(id=id)
        if transaction.student.user == user:
            if not transaction.payment_method:
                return render(request, "payment method.html", {"transaction": transaction})
            if not transaction.transaction_amount or not transaction.msisdn:
                return render(request, "payment details.html", {"transaction": transaction})
            if not (transaction.merchant_request_id or transaction.checkout_request_id or
                    transaction.response_description or transaction.customer_message):
                return render(request, "confirm pay.html", {"transaction": transaction})
            if not (transaction.merchant_request_id or transaction.response_description):
                return render(request, "confirm pay.html", {"transaction": transaction})
        messages.error(request, "You are not authorized to recover this transaction!")
        schools = School.objects.all()
        redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
        return redirect(redirect_url)
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


def my_student(request):
    user = request.user
    if user.is_authenticated:
        if request.method == "POST":
            try:
                student_id = request.POST["student-name"].split(": ")[0].strip().lower()
                student_reg = request.POST["student-reg"].strip().upper()

                _user = User.objects.get(id=student_id)

                if _user.registration_number == student_reg:
                    Parent.objects.create(
                        user=user,
                        student=_user.student,
                        parent_name=user.get_full_name()
                    ).save()
                    messages.success(request, f"You have registered as {_user.get_short_name()}'s parent.")
                    return render(request, "index.html", {"current_date": default_now()})
                messages.error(request,
                                 f"The student name you entered does not match the registration number you specified.")
            except User.DoesNotExist:
                messages.success(request, f"Please select a name from the suggestion box.")
        return render(request, "select student.html")
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


def get_access_token(request):
    consumer_key = "GREzh31yfSUINAoLZdpI5cqACNOGRbRuEDsxEwOb4mvbVJoJ"
    consumer_secret = "pPBUtgrI8tmXGaJnO193uML7ed2YLoOrYdecggEplZaCBe2c11gITYXj6n6Wj3me"
    access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)
    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status()
        result = response.json()
        access_token = result['access_token']
        return JsonResponse({'access_token': access_token})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)})


def confirm_pay(request, id):
    user = request.user
    if user.is_authenticated:
        transaction = Transaction.objects.get(id=id)
        if transaction.student.user == user:
            if not transaction.complete:
                if request.method == "POST":
                    if "yes" in request.POST:
                        try:
                            response = None
                            response_code = -1

                            for _ in range(5):
                                cl = MpesaClient()
                                phone_number = transaction.msisdn
                                amount = int(transaction.transaction_amount)
                                account_reference = 'Schoolfees'
                                transaction_desc = 'Fees pay'
                                callback_url = f'https://paymyfees.onrender.com/process_pay/{transaction.id}/'
                                response_json = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)

                                # Parse the JSON response
                                response = response_json.json()
                                response_code = response.get('ResponseCode', None)

                                if response_code == "0" or response_code == 0:
                                    break

                            print()
                            print()
                            print()
                            print("### RESPONSE ###")
                            print("*************************************************")
                            print(response)
                            print(response_code)
                            print("*************************************************")
                            print()
                            print()
                            print()

                            if response_code:
                                merchant_request_id = response.get("MerchantRequestID", None)
                                checkout_request_id = response.get("CheckoutRequestID", None)
                                response_description = response.get("ResponseDescription", None)
                                customer_message = response.get("CustomerMessage", None)
                                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                                print(f"response_code: {response_code}, merchant_id: {merchant_request_id}, checkout_response_id: "
                                      f"{checkout_request_id}, response_description: {response_description}, "
                                      f"customer_message: {customer_message}")
                                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                                # return HttpResponse(response_json)
                                if int(response_code) == 0:
                                    transaction.response_code = response_code
                                    transaction.checkout_request_id = checkout_request_id
                                    transaction.merchant_request_id = merchant_request_id
                                    transaction.customer_message = customer_message
                                    transaction.response_description = response_description
                                    transaction.save()
                                    return render(request, "complete pay.html", {"transaction": transaction})

                                messages.error(request, "Invalid response code.")
                                schools = School.objects.all()
                                redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                                return redirect(redirect_url)

                            else:
                                transaction.merchant_request_id = response.get("requestId", None)
                                transaction.response_description = response.get("errorMessage", None)
                                transaction.save()

                                messages.error(request, f'Some error occurred: {transaction.response_description}')

                                schools = School.objects.all()
                                redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                                return redirect(redirect_url)
                        except Exception as error:
                            messages.error(request, error)
                            schools = School.objects.all()
                            redirect_url = reverse(
                                'pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                            return redirect(redirect_url)
                    transaction.status = "cancelled"
                    transaction.save()
                    messages.success(request, "Transaction cancelled.")
                    schools = School.objects.all()
                    redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                    return redirect(redirect_url)
                messages.error(request, "Form not submitted")
                schools = School.objects.all()
                redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                return redirect(redirect_url)
            messages.error(request, "Transaction already effected.")
            schools = School.objects.all()
            redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
            return redirect(redirect_url)
        messages.error(request, "You are not authorized to make this transaction!")
        schools = School.objects.all()
        redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
        return redirect(redirect_url)
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


def initiate_stk_push(request, id):  # Replaces confirm pay
    user = request.user
    if user.is_authenticated:
        transaction = Transaction.objects.get(id=id)
        if transaction.student.user == user:
            if not transaction.complete:
                if request.method == "POST":
                    if "yes" in request.POST:
                        access_token_response = get_access_token(request)
                        if isinstance(access_token_response, JsonResponse):
                            access_token = access_token_response.content.decode('utf-8')
                            access_token_json = json.loads(access_token)
                            access_token = access_token_json.get('access_token')
                            if access_token:
                                process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
                                callback_url = 'https://kariukijames.com/callback'
                                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

                                stk_push_headers = {
                                    'Content-Type': 'application/json',
                                    'Authorization': 'Bearer ' + access_token
                                }

                                stk_push_payload = {
                                    "BusinessShortCode": 174379,
                                    "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjQwMzIwMTAxMjU3",
                                    "Timestamp": timestamp,
                                    "TransactionType": "CustomerPayBillOnline",
                                    "Amount": int(transaction.transaction_amount),
                                    "PartyA": str(transaction.msisdn),
                                    "PartyB": 174379,
                                    "PhoneNumber": str(transaction.msisdn),
                                    "CallBackURL": callback_url,
                                    "AccountReference": "paymyfees",
                                    "TransactionDesc": "Schoolfees Payment"
                                }

                                try:
                                    for _ in range(5):
                                        response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
                                        response.raise_for_status()
                                        # Raise exception for non-2xx status codes
                                        response_data = response.json()
                                        checkout_request_id = response_data['CheckoutRequestID']
                                        response_code = response_data['ResponseCode']

                                        if response_code == "0" or response_code == 0:
                                            merchant_request_id = response.get("MerchantRequestID", None)
                                            response_description = response.get("ResponseDescription", None)
                                            customer_message = response.get("CustomerMessage", None)

                                            transaction.response_code = response_code
                                            transaction.checkout_request_id = checkout_request_id
                                            transaction.merchant_request_id = merchant_request_id
                                            transaction.customer_message = customer_message
                                            transaction.response_description = response_description
                                            transaction.save()
                                            return render(request, "complete pay.html", {"transaction": transaction})

                                    messages.warning(request, "STK push incomplete. Confirm transaction details and try again")
                                    schools = School.objects.all()
                                    redirect_url = reverse(
                                        'pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                                    return redirect(redirect_url)
                                except requests.exceptions.RequestException as e:
                                    return JsonResponse({'error': str(e)})
                            else:
                                return JsonResponse({'error': 'Access token not found.'})
                        else:
                            return JsonResponse({'error': 'Failed to retrieve access token.'})
                    messages.warning(request, "Transaction cancelled.")
                    schools = School.objects.all()
                    redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                    return redirect(redirect_url)
                messages.error(request, "Form not submitted")
                schools = School.objects.all()
                redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
                return redirect(redirect_url)
            messages.error(request, "Transaction already effected.")
            schools = School.objects.all()
            redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
            return redirect(redirect_url)
        messages.error(request, "You are not authorized to make this transaction!")
        schools = School.objects.all()
        redirect_url = reverse('pay_fees:dashboard') + f'?current_time={default_now()}&schools={schools}'
        return redirect(redirect_url)
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


def ghost_func(request):
    return render(request, "select student.html")
