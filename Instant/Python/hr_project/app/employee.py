from abc import ABC, abstractmethod
from validators import validate_date

class Employee(ABC):
    EMPLOYMENT_TYPE = None

    def __init__(self, employee_id, full_name, email, phone, department_id, job_title, hire_date, status):
        if not employee_id.strip():
            raise ValueError("Employee ID cannot be empty")
        self.__employee_id = employee_id.strip()

        self.set_full_name(full_name)
        self.set_email(email)
        self.set_phone(phone)
        self.set_department_id(department_id)
        self.set_job_title(job_title)
        self.set_hire_date(hire_date)
        self.set_status(status)

    def get_employee_id(self):
        return self.__employee_id

    def get_full_name(self):
        return self.__full_name

    def set_full_name(self, full_name):
        if not full_name.strip():
            raise ValueError("Full name cannot be empty")
        self.__full_name = full_name.strip()

    def get_email(self):
        return self.__email

    def set_email(self, email):
        email = email.strip()
        if not email:
            raise ValueError("Email cannot be empty")
        local, _, domain = email.partition("@")
        if not local or "." not in domain or " " in email:
            raise ValueError("Email format is invalid")
        self.__email = email

    def get_phone(self):
        return self.__phone

    def set_phone(self, phone):
        phone = phone.strip()
        if not phone:
            raise ValueError("Phone cannot be empty")
        if not phone.lstrip("+").isdigit():
            raise ValueError("Phone must contain digits only")
        self.__phone = phone

    def get_department_id(self):
        return self.__department_id

    def set_department_id(self, department_id):
        if not department_id.strip():
            raise ValueError("Department ID cannot be empty")
        self.__department_id = department_id.strip()

    def get_job_title(self):
        return self.__job_title

    def set_job_title(self, job_title):
        if not job_title.strip():
            raise ValueError("Job title cannot be empty")
        self.__job_title = job_title.strip()

    def get_hire_date(self):
        return self.__hire_date

    def set_hire_date(self, hire_date):
        self.__hire_date = validate_date(hire_date, "Hire date")

    def get_employment_type(self):
        return self.EMPLOYMENT_TYPE

    def get_status(self):
        return self.__status

    def set_status(self, status):
        status = status.strip().lower()
        if status not in ["active", "on_leave", "left"]:
            raise ValueError("Status must be active, on_leave, or left")
        self.__status = status

    @abstractmethod
    def get_leave_balance(self):
        """Annual leave days."""

    def to_dict(self):
        return {
            "employee_id": self.__employee_id,
            "full_name": self.__full_name,
            "email": self.__email,
            "phone": self.__phone,
            "department_id": self.__department_id,
            "job_title": self.__job_title,
            "hire_date": self.__hire_date,
            "employment_type": self.EMPLOYMENT_TYPE,
            "status": self.__status,
        }

class FullTimeEmployee(Employee):
    EMPLOYMENT_TYPE = "full_time"

    def get_leave_balance(self):
        return 21

class PartTimeEmployee(Employee):
    EMPLOYMENT_TYPE = "part_time"

    def get_leave_balance(self):
        return 7

def create_employee(employee_id, full_name, email, phone, department_id, job_title, hire_date, employment_type, status):
    classes = {
        FullTimeEmployee.EMPLOYMENT_TYPE: FullTimeEmployee,
        PartTimeEmployee.EMPLOYMENT_TYPE: PartTimeEmployee,
    }
    employment_type = employment_type.strip().lower()
    if employment_type not in classes:
        raise ValueError("Employment type must be full_time or part_time")
    return classes[employment_type](employee_id, full_name, email, phone, department_id, job_title, hire_date, status)
