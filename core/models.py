from django.db import models

class Role(models.Model):
    name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name


class User(models.Model):
    login = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=255)
    role = models.ForeignKey(Role, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.login


class Specialization(models.Model):
    name = models.CharField(unique=True, max_length=100)
    accreditation_level = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'specializations'
        verbose_name = 'Специализация'
        verbose_name_plural = 'Специализации'

    def __str__(self):
        return self.name


class Office(models.Model):
    number = models.CharField(unique=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'offices'
        verbose_name = 'Кабинет'
        verbose_name_plural = 'Кабинеты'

    def __str__(self):
        return f"Кабинет {self.number}"


class Doctor(models.Model):
    full_name = models.CharField(max_length=150)
    license_number = models.CharField(unique=True, max_length=50)
    user = models.OneToOneField(User, models.DO_NOTHING, blank=True, null=True)
    specialization = models.ForeignKey(Specialization, models.DO_NOTHING)
    office = models.ForeignKey(Office, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doctors'
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'

    def __str__(self):
        return f"{self.full_name} ({self.specialization})"

class Patient(models.Model):
    full_name = models.CharField(max_length=150)
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField()
    med_card_number = models.CharField(unique=True, max_length=50)
    phone = models.CharField(max_length=20)

    user = models.OneToOneField(User, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'patients'
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'

    def __str__(self):
        return self.full_name

class Diagnosis(models.Model):
    name = models.CharField(max_length=255)
    code_icd = models.CharField(unique=True, max_length=20)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'diagnoses'
        verbose_name = 'Диагноз'
        verbose_name_plural = 'Диагнозы'

    def __str__(self):
        return f"{self.code_icd} - {self.name}"


class Service(models.Model):
    name = models.CharField(unique=True, max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'services'
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return f"{self.name} ({self.cost} руб.)"


class AppointmentBooking(models.Model):
    date_time = models.DateTimeField()
    status = models.CharField(max_length=50, blank=True, null=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING)
    doctor = models.ForeignKey(Doctor, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'appointment_bookings'
        verbose_name = 'Запись на прием'
        verbose_name_plural = 'Записи на прием'

    def __str__(self):
        return f"{self.date_time} - {self.patient} к {self.doctor}"


class Appointment(models.Model):
    booking = models.OneToOneField(AppointmentBooking, models.DO_NOTHING)
    complaints = models.TextField(blank=True, null=True)
    diagnosis = models.ForeignKey(Diagnosis, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'appointments'
        verbose_name = 'Прием (Результат)'
        verbose_name_plural = 'Приемы (Результаты)'

    def __str__(self):
        return f"Прием {self.booking}"


class Prescription(models.Model):
    medication_name = models.CharField(max_length=200)
    appointment = models.ForeignKey(Appointment, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'prescriptions'
        verbose_name = 'Назначение'
        verbose_name_plural = 'Назначения'

    def __str__(self):
        return self.medication_name


class PerformedService(models.Model):
    appointment = models.ForeignKey(Appointment, models.DO_NOTHING)
    service = models.ForeignKey(Service, models.DO_NOTHING)
    count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'performed_services'
        verbose_name = 'Оказанная услуга'
        verbose_name_plural = 'Оказанные услуги'

    def __str__(self):
        return f"{self.service} x{self.count}"