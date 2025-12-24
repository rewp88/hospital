from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('book/', views.book_appointment_view, name='book_appointment'),
    path('ajax/doctors/', views.load_doctors, name='ajax_doctors'),
    path('ajax/slots/', views.load_slots, name='ajax_slots'),

    path('doctor/complete/<int:booking_id>/', views.doctor_complete_view, name='doctor_complete'),

    path('export/json/', views.export_patients_json, name='export_json'),
    path('export/csv/', views.export_doctors_report_csv, name='export_csv'),
    path('doctor/export/excel/', views.export_my_schedule_xlsx, name='export_doctor_xlsx'),
]
