import json
import os
import shutil
from datetime import datetime

from employee import create_employee
from department import Department
from attendance import AttendanceRecord
from leave_request import LeaveRequest
from payroll_record import PayrollRecord

APP_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(os.path.dirname(APP_DIR), "json")

JSON_FILES = ["employees.json", 
              "departments.json", 
              "attendance.json",
              "leave_requests.json", 
              "payroll_records.json"]

class DataStorage:
    def __init__(self):
        self.problems = []        
        self.backup_dir = None    

    def _save(self, file_name, items):
        os.makedirs(JSON_DIR, exist_ok=True)
        data = [item.to_dict() for item in items]
        with open(os.path.join(JSON_DIR, file_name), "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def _load(self, file_name):
        path = os.path.join(JSON_DIR, file_name)
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            self.problems.append(f"{file_name}: the file is damaged and was ignored")
            return []
        if not isinstance(data, list):
            self.problems.append(f"{file_name}: unexpected format, the file was ignored")
            return []
        return data

    def _load_records(self, file_name, build, add):
        for data in self._load(file_name):
            try:
                add(build(data))
            except (ValueError, KeyError, TypeError, AttributeError) as error:
                name = (data.get("employee_id") or data.get("department_id") or "?") \
                    if isinstance(data, dict) else "?"
                if isinstance(error, KeyError):
                    error = f"missing field {error}"
                elif isinstance(error, (TypeError, AttributeError)):
                    error = "some fields are missing or have the wrong type"
                self.problems.append(f"{file_name}: skipped '{name}' - {error}")

    # Employees
    def save_employees(self, manager):
        self._save("employees.json", manager.get_all_employees())

    def load_employees(self, manager):
        self._load_records("employees.json", lambda d: create_employee(**d), manager.add_employee)

    # Departments
    def save_departments(self, manager):
        self._save("departments.json", manager.get_all_departments())

    def load_departments(self, manager):
        self._load_records("departments.json", lambda d: Department(**d), manager.add_department)

    # Attendance
    def save_attendance_records(self, manager):
        self._save("attendance.json", manager.get_all_attendance_records())

    def load_attendance_records(self, manager):
        self._load_records("attendance.json", lambda d: AttendanceRecord(**d), manager.add_attendance_record)

    # Leave
    def save_leave_requests(self, manager):
        self._save("leave_requests.json", manager.get_all_leave_requests())

    def load_leave_requests(self, manager):
        self._load_records("leave_requests.json", lambda d: LeaveRequest(**d), manager.add_leave_request)

    # Payroll
    def save_payroll_records(self, manager):
        self._save("payroll_records.json", manager.get_all_payroll_records())

    def load_payroll_records(self, manager):
        self._load_records("payroll_records.json", lambda d: PayrollRecord(**d), manager.add_payroll_record)

    def save_all(self, manager):
        self.save_employees(manager)
        self.save_departments(manager)
        self.save_attendance_records(manager)
        self.save_leave_requests(manager)
        self.save_payroll_records(manager)

    def backup_files(self):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = os.path.join(JSON_DIR, f"backup_{stamp}")
        os.makedirs(folder, exist_ok=True)
        for file_name in JSON_FILES:
            source = os.path.join(JSON_DIR, file_name)
            if os.path.exists(source):
                shutil.copy2(source, folder)
        return folder

    def load_all(self, manager):
        self.problems = []
        self.backup_dir = None
        self.load_employees(manager)
        self.load_departments(manager)
        self.load_attendance_records(manager)
        self.load_leave_requests(manager)
        self.load_payroll_records(manager)
        if self.problems:
            self.backup_dir = self.backup_files()
        return self.problems
