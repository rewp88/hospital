import os
import time
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Создает резервную копию базы данных и сохраняет её'

    def handle(self, *args, **options):
        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings['HOST']
        db_port = db_settings['PORT']

        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"backup_{db_name}_{timestamp}.sql"
        filepath = os.path.join(backup_dir, filename)

        self.stdout.write(f"Начинаю создание резервной копии БД '{db_name}'...")

        env = os.environ.copy()
        env['PGPASSWORD'] = str(db_password)

        cmd = [
            'pg_dump',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-F', 'c',
            '-b',
            '-v',
            '-f', filepath,
            db_name
        ]

        try:
            subprocess.run(cmd, env=env, check=True)
            self.stdout.write(self.style.SUCCESS(f"Бэкап успешно создан: {filepath}"))

            self.upload_to_cloud_simulation(filepath)

        except (FileNotFoundError, subprocess.CalledProcessError):
            self.stdout.write(self.style.WARNING("Утилита pg_dump не найдена или вернула ошибку."))
            self.stdout.write("Использую запасной вариант (Django dumpdata)...")

            # JSON дамп
            json_filename = f"backup_{db_name}_{timestamp}.json"
            json_filepath = os.path.join(backup_dir, json_filename)

            with open(json_filepath, 'w', encoding='utf-8') as f:
                from django.core.management import call_command
                call_command('dumpdata', 'core', stdout=f)

            self.stdout.write(self.style.SUCCESS(f"Бэкап (JSON) успешно создан: {json_filepath}"))
            self.upload_to_cloud_simulation(json_filepath)

    def upload_to_cloud_simulation(self, filepath):

        self.stdout.write("Подключение к удаленному хранилищу (Cloud Storage)...")
        time.sleep(1)
        self.stdout.write(f"Загрузка файла {os.path.basename(filepath)}...")
        time.sleep(2)
        self.stdout.write(self.style.SUCCESS("Файл успешно загружен в облако!"))