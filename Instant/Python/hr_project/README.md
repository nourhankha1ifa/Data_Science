# HR Management System

A desktop HR application built with **Python** and **PyQt5**. It manages employees, departments, attendance, leave requests, and payroll, and saves everything to JSON files so no data is lost when the app is closed.

I built this project to practice what I learned in the **AI & Data Science course at Instant**, especially object-oriented programming.

## Features

The app has five sections. In each one you can **add, view, search, edit, and delete** records.

| Section | What it manages |
|---|---|
| **Employees** | Personal details, department, job title, hire date, employment type (full-time / part-time), and status |
| **Departments** | Department name and its manager |
| **Attendance** | Daily check-in / check-out times and status (present, late, absent) |
| **Leave Requests** | Leave type (annual, sick, unpaid), dates, reason, and approval status |
| **Payroll** | Monthly base salary, overtime, deductions, and calculated net salary |

Other highlights:

- **Persistent storage:** data is saved to and loaded from JSON files.
- **Safe loading:** if a JSON file is damaged or contains invalid records, the app skips the bad entries, reports the problems, and backs up the existing files.
- **Clear error messages:** invalid input never crashes the app; a message box explains what went wrong.
- **Custom styling:** the interface uses a Qt stylesheet (`style.qss`).

## Input Validation

The app checks the data before saving and shows a clear message when something is wrong. For example:

- Invalid email format
- Duplicate employee ID (or duplicate email / phone number)
- Check-out time before check-in time
- Leave end date before start date
- Deleting a department manager, or an employee who still has records
- Deleting a department that still has employees
- Deductions that exceed total earnings

## OOP Concepts Used

| Concept | Where it is used |
|---|---|
| **Encapsulation** | Private attributes (`self.__name`) with getters and setters that validate every change, in `Employee`, `Department`, `AttendanceRecord`, `LeaveRequest`, and `PayrollRecord` |
| **Abstraction** | Abstract classes `BaseRecord` and `Employee` (built with `ABC` and `@abstractmethod`) define what subclasses must implement |
| **Inheritance** | `AttendanceRecord`, `LeaveRequest`, and `PayrollRecord` inherit from `BaseRecord`; `FullTimeEmployee` and `PartTimeEmployee` inherit from `Employee` |
| **Polymorphism** | `get_leave_balance()` returns 21 days for full-time and 7 days for part-time employees; every record type implements `get_key()`, `to_dict()`, and `get_summary()` in its own way |

## Project Structure

```
hr_project/
├── GUI/
│   ├── main_window.ui          # Main window (Qt Designer)
│   ├── employee_dialog.ui
│   ├── department_dialog.ui
│   ├── attendance_dialog.ui
│   ├── leave_dialog.ui
│   ├── payroll_dialog.ui
│   ├── style.qss               # Application stylesheet
│   └── arrow_down.png
├── json/                       # Created automatically when data is saved
└── <code folder>/
    ├── main.py                 # PyQt5 application entry point
    ├── base_record.py          # Abstract base class for records
    ├── employee.py             # Employee, FullTimeEmployee, PartTimeEmployee
    ├── department.py
    ├── attendance.py
    ├── leave_request.py
    ├── payroll_record.py
    ├── hr_manager.py           # Business logic and rules for all records
    ├── storage.py              # JSON save / load and backups
    ├── validators.py           # Date, month, and time validation
    └── check_storage.py        # Quick script to test saving and loading
```

## Technologies

- Python 3
- PyQt5
- Qt Designer
- JSON

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/nourhankha1ifa/Data_Science.git
cd Data_Science/Instant/Python/hr_project
```

### 2. Install the dependency

```bash
pip install PyQt5
```

### 3. Run the app

From the folder that contains `main.py`:

```bash
python main.py
```

### Optional: test the storage layer

```bash
python check_storage.py
```

This creates sample records, saves them to JSON, loads them back, and prints how many records of each type were loaded.

## Demo

A video of the app in action is available in my LinkedIn post. 
It shows how the app handles mistakes such as 
- An invalid email
- A duplicate ID
- A check-out time before check-in
- An attempt to delete a department manager

In each case the app shows a clear message instead of crashing.

## Acknowledgments

Thank you to my instructor **Youssef Elbadry** and my mentor **Ismail Mustafa** for their support and guidance.

## Author

**Nourhan Khalifa Abdelal**