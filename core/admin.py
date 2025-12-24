import json
from django.contrib import admin
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from .models import (
    Role, User, Specialization, Office, Doctor, Patient,
    Diagnosis, Service, AppointmentBooking, Appointment,
    Prescription, PerformedService
)

@admin.action(description=' Скачать выбранных в JSON')
def export_to_json(modeladmin, request, queryset):
    data = list(queryset.values('full_name', 'phone', 'med_card_number', 'birth_date', 'address'))

    response_data = json.dumps(data, ensure_ascii=False, indent=4, cls=DjangoJSONEncoder)

    response = HttpResponse(response_data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="patients_export.json"'
    return response

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'med_card_number')
    search_fields = ('full_name', 'med_card_number')
    actions = [export_to_json]

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Specialization)
admin.site.register(Office)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialization', 'license_number')


@admin.register(AppointmentBooking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'doctor', 'patient', 'status')
    list_filter = ('status', 'doctor')


admin.site.register(Diagnosis)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(PerformedService)