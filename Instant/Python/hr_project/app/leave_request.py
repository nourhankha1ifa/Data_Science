from base_record import BaseRecord
from validators import validate_date

class LeaveRequest(BaseRecord):
    VALID_LEAVE_TYPES = ["annual", "sick", "unpaid"]
    VALID_STATUSES = ["pending", "approved", "rejected"]

    def __init__(self, employee_id, leave_type, start_date, end_date, reason, status):
        super().__init__(employee_id)
        self.set_leave_type(leave_type)

        start = validate_date(start_date, "Start date")
        end = validate_date(end_date, "End date")
        if end < start:
            raise ValueError("End date cannot be before start date")
        self.__start_date = start
        self.__end_date = end

        self.set_reason(reason)
        self.set_status(status)

    def get_start_date(self):
        return self.__start_date

    def get_end_date(self):
        return self.__end_date

    def get_leave_type(self):
        return self.__leave_type

    def set_leave_type(self, value):
        value = value.strip().lower()
        if value not in self.VALID_LEAVE_TYPES:
            raise ValueError("Leave type must be annual, sick, or unpaid")
        self.__leave_type = value

    def get_reason(self):
        return self.__reason

    def set_reason(self, value):
        self.__reason = value.strip()

    def get_status(self):
        return self.__status

    def set_status(self, value):
        value = value.strip().lower()
        if value not in self.VALID_STATUSES:
            raise ValueError("Status must be pending, approved, or rejected")
        self.__status = value

    def get_key(self):
        return (self.employee_id, self.__start_date, self.__end_date)

    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "leave_type": self.__leave_type,
            "start_date": self.__start_date,
            "end_date": self.__end_date,
            "reason": self.__reason,
            "status": self.__status,
        }

    def get_summary(self):
        return (f"{self.employee_id} | {self.__leave_type} | "
                f"{self.__start_date} -> {self.__end_date} | {self.__status}")
