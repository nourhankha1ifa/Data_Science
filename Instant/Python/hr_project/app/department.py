class Department:
    def __init__(self, department_id, name, manager_id):
        if not department_id.strip():
            raise ValueError("Department ID cannot be empty")
        self.__department_id = department_id.strip()
        self.set_name(name)
        self.set_manager_id(manager_id)

    def get_department_id(self):
        return self.__department_id

    def get_name(self):
        return self.__name

    def set_name(self, name):
        if not name.strip():
            raise ValueError("Department name cannot be empty")
        self.__name = name.strip()

    def get_manager_id(self):
        return self.__manager_id

    def set_manager_id(self, manager_id):
        if not manager_id.strip():
            raise ValueError("Manager ID cannot be empty")
        self.__manager_id = manager_id.strip()

    def to_dict(self):
        return {
            "department_id": self.__department_id,
            "name": self.__name,
            "manager_id": self.__manager_id,
        }
