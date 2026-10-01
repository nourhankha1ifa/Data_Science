from employee import FullTimeEmployee
from department import Department
from attendance import AttendanceRecord
from leave_request import LeaveRequest
from payroll_record import PayrollRecord
from hr_manager import HRManager
from storage import DataStorage

manager = HRManager()

manager.add_employee(FullTimeEmployee(
    "E001", "Mona Ahmed", "mona@example.com", "01012345678",
    "D001", "HR Specialist", "2026-01-15", "active"
))
manager.add_department(Department("D001", "Human Resources", "E001"))
manager.add_attendance_record(
    AttendanceRecord("E001", "2026-09-29", "09:00", "17:00", "present"))
manager.add_leave_request(
    LeaveRequest("E001", "annual", "2026-10-01", "2026-10-03", "Family trip", "pending"))
manager.add_payroll_record(PayrollRecord("E001", "2026-09", 18000, 1000, 500))

storage = DataStorage()
storage.save_all(manager)

loaded_manager = HRManager()
storage.load_all(loaded_manager)

print(len(loaded_manager.get_all_employees()))
print(len(loaded_manager.get_all_departments()))
print(len(loaded_manager.get_all_attendance_records()))
print(len(loaded_manager.get_all_leave_requests()))
print(len(loaded_manager.get_all_payroll_records()))
