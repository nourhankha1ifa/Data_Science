from abc import ABC, abstractmethod

class BaseRecord(ABC):
    def __init__(self, employee_id):
        if not employee_id.strip():
            raise ValueError("Employee ID cannot be empty")
        self._employee_id = employee_id.strip()

    @property
    def employee_id(self):
        return self._employee_id

    @abstractmethod
    def get_key(self):
        """Unique key used by HRManager"""

    @abstractmethod
    def to_dict(self):
        """Dict used by the storage"""

    @abstractmethod
    def get_summary(self):
        """Oneline text used in the GUI tables"""
