import csv
import os
from datetime import datetime

LOG_FILE = 'log.csv'


def log_entry(plate_number):
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([plate_number, timestamp])


def read_log_entries():
    entries = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='r', newline='') as file:
            reader = csv.reader(x.replace('\x00', '') for x in file)  # Remove NUL chars
            for row in reader:
                if len(row) == 2:
                    entries.append((row[0], row[1]))
    return entries

