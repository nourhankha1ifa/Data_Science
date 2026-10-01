from employee import create_employee

class HRManager:
    def __init__(self):
        self.employees = {}
        self.departments = {}
        self.attendance_records = {}
        self.leave_requests = {}
        self.payroll_records = {}

    # Employee
    def _check_unique_contact(self, email, phone, ignore_id=None):
        email = email.strip().lower()
        phone = phone.strip()
        for other in self.employees.values():
            if other.get_employee_id() == ignore_id:
                continue
            if email and other.get_email().lower() == email:
                raise ValueError("This email is already used by another employee")
            if phone and other.get_phone() == phone:
                raise ValueError("This phone number is already used by another employee")

    def add_employee(self, employee):
        employee_id = employee.get_employee_id()
        if employee_id in self.employees:
            raise ValueError("Employee ID already exists")
        self._check_unique_contact(employee.get_email(), employee.get_phone())
        self.employees[employee_id] = employee

    def search_employee(self, employee_id):
        return self.employees.get(employee_id.strip())

    def get_all_employees(self):
        return list(self.employees.values())

    def update_employee(self, employee_id, field_name, new_value):
        employee = self.search_employee(employee_id)
        if employee is None:
            raise ValueError("Employee was not found")

        setters = {
            "full_name": employee.set_full_name,
            "email": employee.set_email,
            "phone": employee.set_phone,
            "department_id": employee.set_department_id,
            "job_title": employee.set_job_title,
            "hire_date": employee.set_hire_date,
            "status": employee.set_status,
        }

        if field_name in setters:
            if field_name == "email":
                self._check_unique_contact(new_value, "", ignore_id=employee_id.strip())
            elif field_name == "phone":
                self._check_unique_contact("", new_value, ignore_id=employee_id.strip())
            setters[field_name](new_value)
        elif field_name == "employment_type":
            data = employee.to_dict()
            data["employment_type"] = new_value
            employee = create_employee(**data)
            self.employees[employee.get_employee_id()] = employee
        else:
            raise ValueError("This employee field cannot be updated")

        return employee

    def replace_employee(self, new_employee):
        employee_id = new_employee.get_employee_id()
        if employee_id not in self.employees:
            raise ValueError("Employee was not found")
        self._check_unique_contact(new_employee.get_email(), new_employee.get_phone(), ignore_id=employee_id)
        self.employees[employee_id] = new_employee
        return new_employee

    def delete_employee(self, employee_id):
        employee_id = employee_id.strip()
        if employee_id not in self.employees:
            raise ValueError("Employee was not found")

        for department in self.departments.values():
            if department.get_manager_id() == employee_id:
                raise ValueError("This employee manages a department. Change the manager first")

        for records in (self.attendance_records, self.leave_requests, self.payroll_records):
            for record in records.values():
                if record.employee_id == employee_id:
                    raise ValueError("Delete this employee's records first")

        return self.employees.pop(employee_id)

    # Department
    def add_department(self, department):
        department_id = department.get_department_id()
        if department_id in self.departments:
            raise ValueError("Department ID already exists")
        if department.get_manager_id() not in self.employees:
            raise ValueError("Department manager must be an existing employee")
        self.departments[department_id] = department

    def search_department(self, department_id):
        return self.departments.get(department_id.strip())

    def get_all_departments(self):
        return list(self.departments.values())

    def update_department(self, department_id, field_name, new_value):
        department = self.search_department(department_id)
        if department is None:
            raise ValueError("Department was not found")

        if field_name == "name":
            department.set_name(new_value)
        elif field_name == "manager_id":
            if new_value.strip() not in self.employees:
                raise ValueError("Department manager must be an existing employee")
            department.set_manager_id(new_value)
        else:
            raise ValueError("This department field cannot be updated")
        return department

    def replace_department(self, new_department):
        department_id = new_department.get_department_id()
        if department_id not in self.departments:
            raise ValueError("Department was not found")
        if new_department.get_manager_id() not in self.employees:
            raise ValueError("Department manager must be an existing employee")
        self.departments[department_id] = new_department
        return new_department

    def delete_department(self, department_id):
        department_id = department_id.strip()
        if department_id not in self.departments:
            raise ValueError("Department was not found")

        for employee in self.employees.values():
            if employee.get_department_id() == department_id:
                raise ValueError("Move employees before deleting this department")

        return self.departments.pop(department_id)

    def _add_record(self, store, record, exists_message):
        if record.employee_id not in self.employees:
            raise ValueError("Employee was not found")
        key = record.get_key()
        if key in store:
            raise ValueError(exists_message)
        store[key] = record

    @staticmethod
    def _delete_record(store, key, not_found_message):
        if key not in store:
            raise ValueError(not_found_message)
        return store.pop(key)

    # Attendance
    def add_attendance_record(self, record):
        self._add_record(self.attendance_records, record, "Attendance record already exists for this date")

    def search_attendance_record(self, employee_id, attendance_date):
        return self.attendance_records.get((employee_id.strip(), attendance_date.strip()))

    def get_all_attendance_records(self):
        return list(self.attendance_records.values())

    def update_attendance_record(self, employee_id, attendance_date, check_in, check_out, status):
        record = self.search_attendance_record(employee_id, attendance_date)
        if record is None:
            raise ValueError("Attendance record was not found")
        old_times = (record.get_check_in(), record.get_check_out())
        record.set_times(check_in, check_out)
        try:
            record.set_status(status)
        except ValueError:
            record.set_times(*old_times)
            raise
        return record

    def delete_attendance_record(self, employee_id, attendance_date):
        return self._delete_record(self.attendance_records, (employee_id.strip(), attendance_date.strip()), "Attendance record was not found")

    # Leave
    def add_leave_request(self, request):
        self._add_record(self.leave_requests, request, "Leave request already exists for these dates")

    def search_leave_request(self, employee_id, start_date, end_date):
        return self.leave_requests.get((employee_id.strip(), start_date.strip(), end_date.strip()))

    def get_all_leave_requests(self):
        return list(self.leave_requests.values())

    def update_leave_request(self, employee_id, start_date, end_date, leave_type, reason, status):
        request = self.search_leave_request(employee_id, start_date, end_date)
        if request is None:
            raise ValueError("Leave request was not found")
        if leave_type.strip().lower() not in request.VALID_LEAVE_TYPES:
            raise ValueError("Leave type must be annual, sick, or unpaid")
        if status.strip().lower() not in request.VALID_STATUSES:
            raise ValueError("Status must be pending, approved, or rejected")
        request.set_leave_type(leave_type)
        request.set_reason(reason)
        request.set_status(status)
        return request

    def update_leave_status(self, employee_id, start_date, end_date, new_status):
        request = self.search_leave_request(employee_id, start_date, end_date)
        if request is None:
            raise ValueError("Leave request was not found")
        request.set_status(new_status)
        return request

    def delete_leave_request(self, employee_id, start_date, end_date):
        return self._delete_record(self.leave_requests, (employee_id.strip(), start_date.strip(), end_date.strip()), "Leave request was not found")

    # Payroll
    def add_payroll_record(self, record):
        self._add_record(self.payroll_records, record, "Payroll record already exists for this month")

    def search_payroll_record(self, employee_id, pay_month):
        return self.payroll_records.get((employee_id.strip(), pay_month.strip()))

    def get_all_payroll_records(self):
        return list(self.payroll_records.values())

    def update_payroll_record(self, employee_id, pay_month, base_salary, overtime_pay, deductions):
        record = self.search_payroll_record(employee_id, pay_month)
        if record is None:
            raise ValueError("Payroll record was not found")
        record.set_amounts(base_salary, overtime_pay, deductions)
        return record

    def delete_payroll_record(self, employee_id, pay_month):
        return self._delete_record(self.payroll_records, (employee_id.strip(), pay_month.strip()), "Payroll record was not found")
