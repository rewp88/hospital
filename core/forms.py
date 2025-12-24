from django import forms
from django.core.exceptions import ValidationError
from .models import Specialization, Doctor, AppointmentBooking, Diagnosis, Service, Appointment

class LoginForm(forms.Form):
    login = forms.CharField(label='Логин', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class BookingForm(forms.ModelForm):
    specialization = forms.ModelChoiceField(
        queryset=Specialization.objects.all(),
        label="1. Выберите специализацию",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_specialization'})
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        label="2. Выберите врача",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_doctor'})
    )
    date = forms.DateField(
        label="3. Выберите дату",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_date'})
    )
    date_time = forms.DateTimeField(widget=forms.HiddenInput(attrs={'id': 'id_date_time'}))

    class Meta:
        model = AppointmentBooking
        fields = ['specialization', 'doctor', 'date_time']

class DoctorCompleteForm(forms.ModelForm):
    diagnosis = forms.ModelChoiceField(
        queryset=Diagnosis.objects.all(),
        label="Поставить диагноз",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    complaints = forms.CharField(
        label="Жалобы",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        label="Оказанные услуги",
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'style': 'height: 150px'})
    )

    class Meta:
        model = Appointment
        fields = ['diagnosis', 'complaints', 'services']