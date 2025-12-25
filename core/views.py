import csv
import openpyxl
from openpyxl.styles import Font, Alignment
from datetime import datetime, timedelta, time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import connection

from .models import Patient, User, Doctor, AppointmentBooking, Appointment, PerformedService
from .forms import LoginForm, BookingForm, DoctorCompleteForm


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(login=login, password=password)
                request.session['user_id'] = user.id
                request.session['role_id'] = user.role.id
                return redirect('dashboard')
            except User.DoesNotExist:
                messages.error(request, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    request.session.flush()
    return redirect('login')


def dashboard_view(request):
    user_id = request.session.get('user_id')
    if not user_id: return redirect('login')

    user = User.objects.get(id=user_id)
    role_id = request.session.get('role_id')
    context = {'user': user}

    if role_id == 3:
        try:
            patient = Patient.objects.get(user=user)

            context['patient'] = patient
            context['appointments'] = AppointmentBooking.objects.filter(patient=patient).order_by('-date_time')
            return render(request, 'patient_dashboard.html', context)
        except Patient.DoesNotExist:
            return HttpResponse("Ошибка: Ваш профиль пациента не найден. Обратитесь в регистратуру.")

    elif role_id == 2:
        try:
            doctor = Doctor.objects.get(user=user)
            context['doctor'] = doctor
            context['appointments'] = AppointmentBooking.objects.filter(doctor=doctor).order_by('date_time')
            return render(request, 'doctor_dashboard.html', context)
        except Doctor.DoesNotExist:
            context['error'] = "Профиль врача не найден."
            return render(request, 'doctor_dashboard.html', context)

    else:
        return redirect('/admin/')


def load_doctors(request):
    spec_id = request.GET.get('spec_id')
    if spec_id:
        doctors = list(Doctor.objects.filter(specialization_id=spec_id).values('id', 'full_name'))
    else:
        doctors = list(Doctor.objects.all().values('id', 'full_name'))
    return JsonResponse(doctors, safe=False)

def load_slots(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse([], safe=False)

    try:
        search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse([], safe=False)

    bookings = AppointmentBooking.objects.filter(
        doctor_id=doctor_id,
        date_time__date=search_date
    ).exclude(status='Canceled')

    busy_slots = [b.date_time.strftime('%H:%M') for b in bookings]

    free_slots = []
    start = datetime.combine(search_date, time(9, 0))
    end = datetime.combine(search_date, time(18, 0))

    while start < end:
        slot_str = start.strftime('%H:%M')
        if slot_str not in busy_slots:
            free_slots.append(slot_str)
        start += timedelta(minutes=30)

    return JsonResponse(free_slots, safe=False)


def book_appointment_view(request):
    user_id = request.session.get('user_id')
    if not user_id: return redirect('login')

    user = User.objects.get(id=user_id)

    try:
        patient = Patient.objects.get(user=user)
    except Patient.DoesNotExist:
        return redirect('dashboard')

    if request.method == 'POST':
        form = BookingForm(request.POST)

        raw_date_time = request.POST.get('date_time')
        doc_id = request.POST.get('doctor')

        if raw_date_time and doc_id:
            doctor = Doctor.objects.get(id=doc_id)
            final_dt = datetime.strptime(raw_date_time, '%Y-%m-%d %H:%M')

            AppointmentBooking.objects.create(
                patient=patient,
                doctor=doctor,
                date_time=final_dt,
                status='Scheduled'
            )
            messages.success(request, 'Запись успешно создана!')
            return redirect('dashboard')

    else:
        form = BookingForm()

    return render(request, 'book_appointment.html', {'form': form})


def doctor_complete_view(request, booking_id):
    if request.session.get('role_id') != 2:
        return redirect('dashboard')

    booking = get_object_or_404(AppointmentBooking, id=booking_id)

    if request.method == 'POST':
        form = DoctorCompleteForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.booking = booking
            appt.save()

            services = form.cleaned_data['services']
            for svc in services:
                PerformedService.objects.create(appointment=appt, service=svc, count=1)

            booking.status = 'Completed'
            booking.save()

            messages.success(request, 'Прием завершен.')
            return redirect('dashboard')
    else:
        form = DoctorCompleteForm()

    return render(request, 'doctor_complete.html', {'form': form, 'booking': booking})


def export_patients_json(request):
    patients = list(Patient.objects.values('full_name', 'phone', 'med_card_number', 'birth_date'))
    return JsonResponse(patients, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})


def export_doctors_report_csv(request):
    response = HttpResponse(content_type='text/csv',
                            headers={'Content-Disposition': 'attachment; filename="doctors_report.csv"'})
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ФИО Врача', 'Специализация', 'Кабинет', 'Количество приемов'])

    sql_query = """
        SELECT d.full_name, s.name, o.number, COUNT(b.id) as visit_count
        FROM clinic.doctors d
        JOIN clinic.specializations s ON d.specialization_id = s.id
        LEFT JOIN clinic.offices o ON d.office_id = o.id
        LEFT JOIN clinic.appointment_bookings b ON d.id = b.doctor_id
        WHERE b.status = 'Completed' OR b.status IS NULL
        GROUP BY d.full_name, s.name, o.number
        ORDER BY visit_count DESC
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
    for row in rows:
        writer.writerow(row)

    return response


def export_my_schedule_xlsx(request):
    user_id = request.session.get('user_id')
    role_id = request.session.get('role_id')
    if not user_id or role_id != 2:
        return redirect('login')

    user = User.objects.get(id=user_id)
    try:
        doctor = Doctor.objects.get(user=user)
    except Doctor.DoesNotExist:
        return redirect('dashboard')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "План приемов"

    headers = ['Дата и Время', 'Пациент', 'Телефон', 'Статус', 'Жалобы (если есть)']
    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    bookings = AppointmentBooking.objects.filter(
        doctor=doctor,
        status='Scheduled'
    ).order_by('date_time')

    for b in bookings:
        date_str = b.date_time.strftime('%d.%m.%Y %H:%M')
        complaints = "-"
        if hasattr(b, 'appointment') and b.appointment.complaints:
            complaints = b.appointment.complaints

        ws.append([
            date_str,
            b.patient.full_name,
            b.patient.phone,
            "Ожидает приема",
            complaints
        ])

    for column_cells in ws.columns:
        length = max(len(str(cell.value) or "") for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 5

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="schedule_{doctor.license_number}.xlsx"'

    wb.save(response)
    return response