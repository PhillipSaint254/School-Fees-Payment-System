from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "pay_fees"

admin_urls = [
    path('', views.admin_index, name="admin_index"),
    path('add_school/', views.add_school, name="add_school"),
    path('add_staff/', views.add_staff, name="add_staff")
]

urlpatterns = [
    path("", views.index, name="index"),
    path("daraja/stk_push/", views.stk_push_callback, name='stk_push_callback'),
    path('login/', views.user_login, name="login"),
    path('register/', views.user_registration, name="register"),
    path("user_admin/", include(admin_urls)),
    path("logout/", views.user_logout, name="logout"),
    path("get_all_schools/", views.all_school, name="all_schools"),
    path("get_all_students/", views.get_all_students, name="get_all_students"),
    path('get_faculties/', views.get_faculties, name='get_faculties'),
    path('get_courses/', views.get_courses, name='get_courses'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("pay_fees/", views.pay_fees, name="pay_fees"),
    path("pay_fees/<int:id>/", views.handle_selected_payment_method, name="handle_selected_payment_method"),
    path("payment_details/<int:id>/", views.payment_details, name="payment_details"),
    path('confirm_pay/<int:id>/', views.initiate_stk_push, name="confirm_pay"),
    path("process_pay/<int:id>/", views.PayProcessView.as_view(), name="process_pay"),
    path("test_api/", views.test_api),
    path("test_api_2/", views.TestAPIView.as_view()),
    path('my_transactions/', views.my_transactions, name="my_transactions"),
    path('recover_transaction/<int:id>/', views.recover_transaction, name="recover_transaction"),
    path("my_student/", views.my_student, name="my_student")
]
