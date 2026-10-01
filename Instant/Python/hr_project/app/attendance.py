from base_record import BaseRecord
from validators import validate_date, validate_time


class AttendanceRecord(BaseRecord):
    VALID_STATUSES = ["present", "late", "absent"]

    def __init__(self, employee_id, attendance_date, check_in, check_out, status):
        super().__init__(employee_id)
        # the date is part of the key, so it is read-only after creation
        self.__attendance_date = validate_date(attendance_date, "Attendance date")
        self.set_times(check_in, check_out)
        self.set_status(status)

    def get_attendance_date(self):
        return self.__attendance_date

    def get_check_in(self):
        return self.__check_in

    def get_check_out(self):
        return self.__check_out

    def set_times(self, check_in, check_out):
        check_in = validate_time(check_in, "Check-in")
        check_out = validate_time(check_out, "Check-out")
        if check_in and check_out and check_out <= check_in:
            raise ValueError("Check-out must be after check-in")
        self.__check_in = check_in
        self.__check_out = check_out

    def set_check_in(self, value):
        self.set_times(value, self.__check_out)

    def set_check_out(self, value):
        self.set_times(self.__check_in, value)

    def get_status(self):
        return self.__status

    def set_status(self, value):
        value = value.strip().lower()
        if value not in self.VALID_STATUSES:
            raise ValueError("Status must be present, late, or absent")
        self.__status = value

    def get_key(self):
        return (self.employee_id, self.__attendance_date)

    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "attendance_date": self.__attendance_date,
            "check_in": self.__check_in,
            "check_out": self.__check_out,
            "status": self.__status,
        }

    def get_summary(self):
        return f"{self.employee_id} | {self.__attendance_date} | {self.__status}"
