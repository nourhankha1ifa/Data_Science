import os
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QDate, Qt

from employee import create_employee
from department import Department
from attendance import AttendanceRecord
from leave_request import LeaveRequest
from payroll_record import PayrollRecord
from hr_manager import HRManager
from storage import DataStorage

APP_DIR = os.path.dirname(os.path.abspath(__file__))
GUI_DIR = os.path.join(os.path.dirname(APP_DIR), "GUI")

def ui_path(file_name):
    return os.path.join(GUI_DIR, file_name)

# Small helpers
def set_role(widget, role):
    widget.setProperty("role", role)
    widget.style().unpolish(widget)      # so the stylesheet notices the change
    widget.style().polish(widget)

def apply_roles(widget):
    for button in widget.findChildren(QtWidgets.QPushButton):
        name = button.objectName()
        if name.startswith(("buttonAdd", "buttonSave")):
            set_role(button, "primary")
        elif name.startswith("buttonDelete"):
            set_role(button, "danger")
    for label in widget.findChildren(QtWidgets.QLabel):
        if label.objectName().startswith(("labelHeading", "labelTitle")):
            set_role(label, "heading")

def fill_employee_combo(combo, manager):
    combo.clear()
    for emp in sorted(manager.get_all_employees(), key=lambda e: e.get_employee_id()):
        combo.addItem(f"{emp.get_employee_id()} - {emp.get_full_name()}", emp.get_employee_id())

def select_combo_data(combo, value):
    index = combo.findData(value)
    if index >= 0:
        combo.setCurrentIndex(index)

def set_date(date_edit, text):
    date = QDate.fromString(text, date_edit.displayFormat())
    if date.isValid():
        date_edit.setDate(date)

def get_date(date_edit):
    return date_edit.date().toString(date_edit.displayFormat())

def matches(text, *values):
    return not text or any(text in str(value).lower() for value in values)


# Dialogs
class RecordDialog(QtWidgets.QDialog):
    UI_FILE = None

    def __init__(self, save_callback, parent, manager, record=None):
        super().__init__(parent)
        uic.loadUi(ui_path(self.UI_FILE), self)
        apply_roles(self)
        self.save_callback = save_callback
        self.manager = manager

        self.setup_fields()
        if record is not None:
            self.labelTitle.setText(self.labelTitle.text().replace("Add", "Edit"))
            self.setWindowTitle(self.labelTitle.text())
            self.load_record(record)

        self.buttonSave.clicked.connect(self.on_save)
        self.buttonCancel.clicked.connect(self.reject)

    def setup_fields(self):
        """Fill combo boxes / default values (before editing)."""

    def load_record(self, record):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError

    def on_save(self):
        try:
            self.save_callback(self.get_data())
        except ValueError as error:
            QtWidgets.QMessageBox.warning(self, "Invalid data", str(error))
            return
        self.accept()

class EmployeeDialog(RecordDialog):
    UI_FILE = "employee_dialog.ui"

    def setup_fields(self):
        for dep in sorted(self.manager.get_all_departments(), key=lambda d: d.get_department_id()):
            self.comboDepartmentId.addItem(dep.get_department_id())
        self.comboDepartmentId.setCurrentIndex(-1)
        self.dateEditHireDate.setDate(QDate.currentDate())

    def load_record(self, emp):
        self.lineEditEmployeeId.setText(emp.get_employee_id())
        self.lineEditEmployeeId.setEnabled(False)
        self.lineEditFullName.setText(emp.get_full_name())
        self.lineEditEmail.setText(emp.get_email())
        self.lineEditPhone.setText(emp.get_phone())
        self.comboDepartmentId.setCurrentText(emp.get_department_id())
        self.lineEditJobTitle.setText(emp.get_job_title())
        set_date(self.dateEditHireDate, emp.get_hire_date())
        self.comboEmploymentType.setCurrentText(emp.get_employment_type())
        self.comboStatus.setCurrentText(emp.get_status())

    def get_data(self):
        return {
            "employee_id": self.lineEditEmployeeId.text(),
            "full_name": self.lineEditFullName.text(),
            "email": self.lineEditEmail.text(),
            "phone": self.lineEditPhone.text(),
            "department_id": self.comboDepartmentId.currentText(),
            "job_title": self.lineEditJobTitle.text(),
            "hire_date": get_date(self.dateEditHireDate),
            "employment_type": self.comboEmploymentType.currentText(),
            "status": self.comboStatus.currentText(),
        }

class DepartmentDialog(RecordDialog):
    UI_FILE = "department_dialog.ui"

    def setup_fields(self):
        fill_employee_combo(self.comboManager, self.manager)

    def load_record(self, dep):
        self.lineEditDepartmentId.setText(dep.get_department_id())
        self.lineEditDepartmentId.setEnabled(False)
        self.lineEditDepartmentName.setText(dep.get_name())
        select_combo_data(self.comboManager, dep.get_manager_id())

    def get_data(self):
        return {
            "department_id": self.lineEditDepartmentId.text(),
            "name": self.lineEditDepartmentName.text(),
            "manager_id": self.comboManager.currentData() or "",
        }

class AttendanceDialog(RecordDialog):
    UI_FILE = "attendance_dialog.ui"

    def setup_fields(self):
        fill_employee_combo(self.comboEmployee, self.manager)
        self.dateEditAttendance.setDate(QDate.currentDate())

    def load_record(self, rec):
        select_combo_data(self.comboEmployee, rec.employee_id)
        set_date(self.dateEditAttendance, rec.get_attendance_date())
        self.comboEmployee.setEnabled(False)
        self.dateEditAttendance.setEnabled(False)
        self.lineEditCheckIn.setText(rec.get_check_in())
        self.lineEditCheckOut.setText(rec.get_check_out())
        self.comboStatus.setCurrentText(rec.get_status())

    def get_data(self):
        return {
            "employee_id": self.comboEmployee.currentData() or "",
            "attendance_date": get_date(self.dateEditAttendance),
            "check_in": self.lineEditCheckIn.text(),
            "check_out": self.lineEditCheckOut.text(),
            "status": self.comboStatus.currentText(),
        }

class LeaveDialog(RecordDialog):
    UI_FILE = "leave_dialog.ui"

    def setup_fields(self):
        fill_employee_combo(self.comboEmployee, self.manager)
        self.dateEditStart.setDate(QDate.currentDate())
        self.dateEditEnd.setDate(QDate.currentDate())
        self.dateEditStart.dateChanged.connect(self.dateEditEnd.setMinimumDate)

    def load_record(self, req):
        select_combo_data(self.comboEmployee, req.employee_id)
        set_date(self.dateEditStart, req.get_start_date())
        set_date(self.dateEditEnd, req.get_end_date())
        self.comboEmployee.setEnabled(False)
        self.dateEditStart.setEnabled(False)
        self.dateEditEnd.setEnabled(False)
        self.comboLeaveType.setCurrentText(req.get_leave_type())
        self.lineEditReason.setText(req.get_reason())
        self.comboStatus.setCurrentText(req.get_status())

    def get_data(self):
        return {
            "employee_id": self.comboEmployee.currentData() or "",
            "leave_type": self.comboLeaveType.currentText(),
            "start_date": get_date(self.dateEditStart),
            "end_date": get_date(self.dateEditEnd),
            "reason": self.lineEditReason.text(),
            "status": self.comboStatus.currentText(),
        }


class PayrollDialog(RecordDialog):
    UI_FILE = "payroll_dialog.ui"

    def setup_fields(self):
        fill_employee_combo(self.comboEmployee, self.manager)
        self.dateEditMonth.setDate(QDate.currentDate())
        for spin in (self.spinBase, self.spinOvertime, self.spinDeductions):
            spin.valueChanged.connect(self.update_net)
        self.update_net()

    def update_net(self):
        net = self.spinBase.value() + self.spinOvertime.value() - self.spinDeductions.value()
        self.labelNetValue.setText(f"{net:,.2f}")

    def load_record(self, rec):
        select_combo_data(self.comboEmployee, rec.employee_id)
        set_date(self.dateEditMonth, rec.get_pay_month())
        self.comboEmployee.setEnabled(False)
        self.dateEditMonth.setEnabled(False)
        self.spinBase.setValue(rec.get_base_salary())
        self.spinOvertime.setValue(rec.get_overtime_pay())
        self.spinDeductions.setValue(rec.get_deductions())

    def get_data(self):
        return {
            "employee_id": self.comboEmployee.currentData() or "",
            "pay_month": get_date(self.dateEditMonth),
            "base_salary": self.spinBase.value(),
            "overtime_pay": self.spinOvertime.value(),
            "deductions": self.spinDeductions.value(),
        }

# table + search + Add / Edit / Delete
class TabController:
    def __init__(self, window, what, table, search_edit, search_button,
                 add_button, edit_button, delete_button,
                 key_size, get_rows, find, delete, open_dialog):
        self.window = window
        self.what = what
        self.table = table
        self.search_edit = search_edit
        self.key_size = key_size
        self.get_rows = get_rows
        self.find = find
        self.delete_record = delete
        self.open_dialog = open_dialog

        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        search_button.clicked.connect(self.refresh)
        search_edit.returnPressed.connect(self.refresh)
        search_edit.textChanged.connect(lambda text: None if text else self.refresh())
        add_button.clicked.connect(self.add)
        edit_button.clicked.connect(self.edit)
        delete_button.clicked.connect(self.delete)
        table.doubleClicked.connect(self.edit)

    def refresh(self):
        rows = self.get_rows(self.search_edit.text().strip().lower())
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QtWidgets.QTableWidgetItem(str(value)))
        self.window.statusbar.showMessage(f"{len(rows)} {self.what}(s) shown")

    def selected_key(self):
        row = self.table.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.information(self.window, "Select a row", f"Please select a {self.what} from the table first.")
            return None
        return tuple(self.table.item(row, c).text() for c in range(self.key_size))

    def add(self):
        if self.open_dialog(None):
            self.window.after_change()

    def edit(self):
        key = self.selected_key()
        if key is None:
            return
        record = self.find(*key)
        if record is not None and self.open_dialog(record):
            self.window.after_change()

    def delete(self):
        key = self.selected_key()
        if key is None:
            return
        answer = QtWidgets.QMessageBox.question(
            self.window, "Confirm", f"Delete {self.what} {' / '.join(key)}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if answer != QtWidgets.QMessageBox.Yes:
            return
        try:
            self.delete_record(*key)
        except ValueError as error:
            QtWidgets.QMessageBox.warning(self.window, "Cannot delete", str(error))
            return
        self.window.after_change()

# Main window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, manager, storage):
        super().__init__()
        uic.loadUi(ui_path("main_window.ui"), self)
        apply_roles(self)
        self.manager = manager
        self.storage = storage
        m = manager

        self.controllers = [
            TabController(
                self, "employee", self.tableEmployees, self.lineEditEmployeeSearch,
                self.buttonSearchEmployee, self.buttonAddEmployee,
                self.buttonEditEmployee, self.buttonDeleteEmployee,
                1, self.employee_rows, m.search_employee, m.delete_employee,
                self.employee_dialog),
            TabController(
                self, "department", self.tableDepartments, self.lineEditDepartmentSearch,
                self.buttonSearchDepartment, self.buttonAddDepartment,
                self.buttonEditDepartment, self.buttonDeleteDepartment,
                1, self.department_rows, m.search_department, m.delete_department,
                self.department_dialog),
            TabController(
                self, "attendance record", self.tableAttendance, self.lineEditAttendanceSearch,
                self.buttonSearchAttendance, self.buttonAddAttendance,
                self.buttonEditAttendance, self.buttonDeleteAttendance,
                2, self.attendance_rows, m.search_attendance_record, m.delete_attendance_record,
                self.attendance_dialog),
            TabController(
                self, "leave request", self.tableLeave, self.lineEditLeaveSearch,
                self.buttonSearchLeave, self.buttonAddLeave,
                self.buttonEditLeave, self.buttonDeleteLeave,
                3, self.leave_rows, m.search_leave_request, m.delete_leave_request,
                self.leave_dialog),
            TabController(
                self, "payroll record", self.tablePayroll, self.lineEditPayrollSearch,
                self.buttonSearchPayroll, self.buttonAddPayroll,
                self.buttonEditPayroll, self.buttonDeletePayroll,
                2, self.payroll_rows, m.search_payroll_record, m.delete_payroll_record,
                self.payroll_dialog),
        ]
        self.tabsMain.currentChanged.connect(lambda index: self.controllers[index].refresh())
        self.refresh_all()

    # ---------- common ----------
    def refresh_all(self):
        for controller in self.controllers:
            controller.refresh()
        self.controllers[self.tabsMain.currentIndex()].refresh()   # status bar text

    def after_change(self):
        try:
            self.storage.save_all(self.manager)
        except OSError as error:
            QtWidgets.QMessageBox.critical(self, "Save failed", str(error))
        self.refresh_all()

    def need_employees(self):
        if self.manager.get_all_employees():
            return True
        QtWidgets.QMessageBox.information(
            self, "No employees", "Please add at least one employee first.")
        return False

    # ---------- table rows ----------
    def employee_rows(self, text):
        rows = []
        for e in sorted(self.manager.get_all_employees(), key=lambda e: e.get_employee_id()):
            if matches(text, e.get_employee_id(), e.get_full_name()):
                dep = self.manager.search_department(e.get_department_id())
                rows.append([e.get_employee_id(), e.get_full_name(),
                             dep.get_name() if dep else e.get_department_id(),
                             e.get_job_title(), e.get_employment_type(), e.get_status()])
        return rows

    def department_rows(self, text):
        return [[d.get_department_id(), d.get_name(), d.get_manager_id()]
                for d in sorted(self.manager.get_all_departments(), key=lambda d: d.get_department_id())
                if matches(text, d.get_department_id(), d.get_name())]

    def attendance_rows(self, text):
        return [[r.employee_id, r.get_attendance_date(), r.get_check_in(),
                 r.get_check_out(), r.get_status()]
                for r in sorted(self.manager.get_all_attendance_records(), key=lambda r: r.get_key())
                if matches(text, r.employee_id, r.get_attendance_date(), r.get_status())]

    def leave_rows(self, text):
        return [[r.employee_id, r.get_start_date(), r.get_end_date(),
                 r.get_leave_type(), r.get_reason(), r.get_status()]
                for r in sorted(self.manager.get_all_leave_requests(), key=lambda r: r.get_key())
                if matches(text, r.employee_id, r.get_leave_type(), r.get_status())]

    def payroll_rows(self, text):
        return [[r.employee_id, r.get_pay_month(), f"{r.get_base_salary():,.2f}",
                 f"{r.get_overtime_pay():,.2f}", f"{r.get_deductions():,.2f}",
                 f"{r.get_net_salary():,.2f}"]
                for r in sorted(self.manager.get_all_payroll_records(), key=lambda r: r.get_key())
                if matches(text, r.employee_id, r.get_pay_month())]

    # ---------- dialogs (record is None -> add, otherwise edit) ----------
    def employee_dialog(self, employee):
        def save(data):
            new_employee = create_employee(**data)
            if employee is None:
                self.manager.add_employee(new_employee)
            else:
                self.manager.replace_employee(new_employee)

        return EmployeeDialog(save, self, self.manager, employee).exec_()

    def department_dialog(self, department):
        if department is None and not self.need_employees():
            return False

        def save(data):
            new_department = Department(**data)
            if department is None:
                self.manager.add_department(new_department)
            else:
                self.manager.replace_department(new_department)

        return DepartmentDialog(save, self, self.manager, department).exec_()

    def attendance_dialog(self, record):
        if record is None and not self.need_employees():
            return False

        def save(d):
            if record is None:
                self.manager.add_attendance_record(AttendanceRecord(**d))
            else:
                self.manager.update_attendance_record(
                    d["employee_id"], d["attendance_date"],
                    d["check_in"], d["check_out"], d["status"])

        return AttendanceDialog(save, self, self.manager, record).exec_()

    def leave_dialog(self, record):
        if record is None and not self.need_employees():
            return False

        def save(d):
            if record is None:
                self.manager.add_leave_request(LeaveRequest(**d))
            else:
                self.manager.update_leave_request(
                    d["employee_id"], d["start_date"], d["end_date"],
                    d["leave_type"], d["reason"], d["status"])

        return LeaveDialog(save, self, self.manager, record).exec_()

    def payroll_dialog(self, record):
        if record is None and not self.need_employees():
            return False

        def save(d):
            if record is None:
                self.manager.add_payroll_record(PayrollRecord(**d))
            else:
                self.manager.update_payroll_record(
                    d["employee_id"], d["pay_month"],
                    d["base_salary"], d["overtime_pay"], d["deductions"])

        return PayrollDialog(save, self, self.manager, record).exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    try:
        with open(ui_path("style.qss"), encoding="utf-8") as file:
            style = file.read()
        arrow = ui_path("arrow_down.png").replace("\\", "/")
        app.setStyleSheet(style.replace("ARROW_DOWN", arrow))
    except OSError:
        pass                                   # the app works without the style

    manager = HRManager()
    storage = DataStorage()
    try:
        problems = storage.load_all(manager)
    except OSError as error:
        QtWidgets.QMessageBox.critical(None, "Cannot read data files", str(error))
        return 1

    window = MainWindow(manager, storage)
    window.show()

    if problems:
        shown = "\n".join(problems[:10])
        if len(problems) > 10:
            shown += f"\n... and {len(problems) - 10} more"
        QtWidgets.QMessageBox.warning(
            window, "Some saved data was skipped",
            f"{shown}\n\nA backup of your original files is in:\n{storage.backup_dir}")
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
