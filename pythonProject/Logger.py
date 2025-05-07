import os
import json
import csv
import shutil
import zipfile
from datetime import datetime, timedelta
from typing import Dict, Iterator, Optional

class Logger:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            config = json.load(f)

        self._validate_config(config)
        self.log_dir = config['log_dir']
        self.archive_dir = os.path.join(self.log_dir, 'archive')
        self.filename_pattern = config['filename_pattern']
        self.buffer_size = config['buffer_size']
        self.rotate_every_hours = config['rotate_every_hours']
        self.max_size_mb = config['max_size_mb']
        self.rotate_after_lines = config.get('rotate_after_lines', None)
        self.retention_days = config['retention_days']

        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)

        self.buffer = []
        self.current_file = None
        self.current_writer = None
        self.current_file_path = None
        self.current_file_open_time = None
        self.current_line_count = 0

    def start(self):
        now = datetime.now()
        self.current_file_open_time = now
        filename = now.strftime(self.filename_pattern)
        self.current_file_path = os.path.join(self.log_dir, filename)
        is_new_file = not os.path.exists(self.current_file_path)

        self.current_file = open(self.current_file_path, 'a', newline='', encoding='utf-8')
        self.current_writer = csv.writer(self.current_file)

        if is_new_file:
            self.current_writer.writerow(['timestamp', 'sensor_id', 'value', 'unit'])

    def stop(self):
        self._flush()
        if self.current_file:
            self.current_file.close()
            self.current_file = None
            self.current_writer = None
            self.current_file_path = None

    def log_reading(self, sensor_id: str, timestamp: datetime, value: float, unit: str):
        self.buffer.append([timestamp.isoformat(), sensor_id, value, unit])
        self.current_line_count += 1

        if len(self.buffer) >= self.buffer_size:
            self._flush()
            if self._should_rotate():
                self._rotate()

    def _flush(self):
        if not self.current_writer:
            return
        self.current_writer.writerows(self.buffer)
        self.current_file.flush()
        self.buffer = []

    def _should_rotate(self) -> bool:
        # Sprawdzenie rotacji czasowej
        if self.current_file_open_time:
            delta = datetime.now() - self.current_file_open_time
            if delta >= timedelta(hours=self.rotate_every_hours):
                return True

        # Sprawdzenie rotacji po rozmiarze pliku
        if os.path.getsize(self.current_file_path) >= self.max_size_mb * 1024 * 1024:
            return True

        # Sprawdzenie rotacji po liczbie linii
        if self.rotate_after_lines and self.current_line_count >= self.rotate_after_lines:
            return True

        return False

    def _rotate(self):
        self.stop()

        # Archiwizacja
        base_name = os.path.basename(self.current_file_path)
        archive_path = os.path.join(self.archive_dir, base_name.replace('.csv', '.zip'))

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(self.current_file_path, arcname=os.path.basename(self.current_file_path))

        os.remove(self.current_file_path)

        self._clean_old_archives()
        self.start()
        self.current_line_count = 0

    def _clean_old_archives(self):
        cutoff = datetime.now() - timedelta(days=self.retention_days)

        for file in os.listdir(self.archive_dir):
            if file.endswith('.zip'):
                full_path = os.path.join(self.archive_dir, file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(full_path))
                if mod_time < cutoff:
                    os.remove(full_path)

    def read_logs(self, start: datetime, end: datetime, sensor_id: Optional[str] = None) -> Iterator[Dict]:
        # Przeszukiwanie plików CSV w log_dir
        for file in os.listdir(self.log_dir):
            if file.endswith('.csv'):
                yield from self._read_csv(os.path.join(self.log_dir, file), start, end, sensor_id)

        # Przeszukiwanie archiwów ZIP
        for file in os.listdir(self.archive_dir):
            if file.endswith('.zip'):
                with zipfile.ZipFile(os.path.join(self.archive_dir, file)) as zipf:
                    for name in zipf.namelist():
                        with zipf.open(name) as f:
                            yield from self._read_csv(f, start, end, sensor_id, from_zip=True)

    def _read_csv(self, file_obj, start, end, sensor_id, from_zip=False):
        import io
        open_file = (
            io.TextIOWrapper(file_obj) if from_zip
            else open(file_obj, newline='', encoding='utf-8')
        )

        with open_file as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_time = datetime.fromisoformat(row['timestamp'])
                if start <= row_time <= end:
                    if sensor_id is None or row['sensor_id'] == sensor_id:
                        yield {
                            'timestamp': row_time,
                            'sensor_id': row['sensor_id'],
                            'value': float(row['value']),
                            'unit': row['unit']
                        }

    def _validate_config(self, config):
        required_fields = {
            'log_dir': str,
            'filename_pattern': str,
            'buffer_size': int,
            'rotate_every_hours': int,
            'max_size_mb': (int, float),
            'retention_days': int
        }

        for key, expected_type in required_fields.items():
            if key not in config:
                raise ValueError(f"Brak wymaganego pola w konfiguracji: {key}")
            if not isinstance(config[key], expected_type):
                raise TypeError(f"Pole '{key}' powinno być typu {expected_type}, a jest {type(config[key])}")

        if 'rotate_after_lines' in config and not isinstance(config['rotate_after_lines'], int):
            raise TypeError("Pole 'rotate_after_lines' (jeśli podane) musi być typu int.")
