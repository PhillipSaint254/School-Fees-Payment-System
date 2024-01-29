import json
from django.db import IntegrityError
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from django_daraja.mpesa.core import MpesaClient
from pay_fees.models import default_now, School, Faculty, Course, Student, User, PaymentMethods


# def index(request):
#     cl = MpesaClient()
#     # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
#     phone_number = '0742332937'
#     amount = 1
#     account_reference = 'reference'
#     transaction_desc = 'Description'
#     callback_url = 'https://darajambili.herokuapp.com/express-payment';
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
                    return render(request, "staff index.html")
                elif request.POST.get("student"):
                    return render(request, "index.html", {"current_time": default_now()})
                else:
                    messages.error(request, "Invalid choice, please select again.")
            return render(request, "admin login prompt.html")
        elif user.is_staff:
            if request.method == "POST":
                if request.POST.get("staff"):
                    return render(request, "staff index.html")
                elif request.POST.get("student"):
                    return render(request, "index.html", {"current_time": default_now()})
                else:
                    messages.error(request, "Invalid choice, please select again.")
            return render(request, "staff login prompt.html")
        return render(request, "dashboard.html", {"current_time": default_now()})
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
        reg_number = request.POST["registration-number"].upper().strip()
        phone = request.POST["phone-number"].strip()
        id_number = request.POST["id-number"].strip()

        faculty_input = request.POST["faculty-input"]
        school_input = request.POST["school-input"]
        course_input = request.POST["course-input"]

        course = None

        print(f"{email} {password1} {password2} {reg_number} {phone} {course_input}")

        if not (reg_number and course_input and email and first_name and password1):
            messages.error(request, "All fields required!")
            return redirect("pay_fees:register")

        try:
            User.objects.get(email=email)
            messages.error(request, f"User with the email '{email}' already exists.")
            return redirect("pay_fees:register")
        except:
            pass

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
            course = Course.objects.get(id=course_id)
        except:
            messages.error(request, "Please choose a valid course option.")
            return redirect("pay_fees:register")

        if password1 == password2:
            try:
                if course:
                    user = User.objects.create(
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

                    student = Student.objects.create(
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
                raise

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
        if user.is_superuser:
            if request.method == "POST":
                pass
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
    schools = School.objects.all().order_by("name")
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


def dashboard(request):
    user = request.user
    if user.is_authenticated:
        return render(request, "dashboard.html")
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


def pay_fees(request):
    user = request.user
    if user.is_authenticated:
        payment_options = PaymentMethods.objects.all()
        return render(request, "payment method.html", {"payment_options": payment_options})
    messages.error(request, "Access reserved to authenticated users!")
    return redirect("pay_fees:login")


