from base_record import BaseRecord
from validators import validate_month

class PayrollRecord(BaseRecord):
    def __init__(self, employee_id, pay_month, base_salary, overtime_pay, deductions):
        super().__init__(employee_id)
        self.__pay_month = validate_month(pay_month, "Pay month")
        self.__base_salary = 0.0
        self.__overtime_pay = 0.0
        self.__deductions = 0.0
        self.set_amounts(base_salary, overtime_pay, deductions)

    def get_pay_month(self):
        return self.__pay_month

    def get_base_salary(self):
        return self.__base_salary

    def get_overtime_pay(self):
        return self.__overtime_pay

    def get_deductions(self):
        return self.__deductions

    def get_net_salary(self):
        return self.__base_salary + self.__overtime_pay - self.__deductions

    def set_amounts(self, base_salary, overtime_pay, deductions):
        try:
            base = float(base_salary)
            overtime = float(overtime_pay)
            ded = float(deductions)
        except (ValueError, TypeError):
            raise ValueError("Salary amounts must be numbers")

        if base < 0:
            raise ValueError("Base salary cannot be negative")
        if overtime < 0:
            raise ValueError("Overtime pay cannot be negative")
        if ded < 0:
            raise ValueError("Deductions cannot be negative")
        if base + overtime - ded < 0:
            raise ValueError("Deductions cannot exceed total earnings")

        self.__base_salary = base
        self.__overtime_pay = overtime
        self.__deductions = ded

    def set_base_salary(self, value):
        self.set_amounts(value, self.__overtime_pay, self.__deductions)

    def set_overtime_pay(self, value):
        self.set_amounts(self.__base_salary, value, self.__deductions)

    def set_deductions(self, value):
        self.set_amounts(self.__base_salary, self.__overtime_pay, value)

    def get_key(self):
        return (self.employee_id, self.__pay_month)

    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "pay_month": self.__pay_month,
            "base_salary": self.__base_salary,
            "overtime_pay": self.__overtime_pay,
            "deductions": self.__deductions,
        }

    def get_summary(self):
        return f"{self.employee_id} | {self.__pay_month} | net: {self.get_net_salary():.2f}"
