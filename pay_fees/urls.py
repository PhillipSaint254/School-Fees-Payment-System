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
    path('get_faculties/', views.get_faculties, name='get_faculties'),
    path('get_courses/', views.get_courses, name='get_courses'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("pay_fees/", views.pay_fees, name="pay_fees"),
    path("pay_fees/<int:id>/", views.handle_selected_payment_method, name="handle_selected_payment_method"),
]
