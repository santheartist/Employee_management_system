class Employee:
    def __init__(self, emp_id, name, lname, age, salary, position, email):
        self.emp_id = emp_id
        self.name = name
        self.lname = lname
        self.age = self.validate_age(age)
        self.salary = salary
        self.position = position
        self.email = email

    def validate_age(self, age):
        if not (18 <= age <= 70):
            raise ValueError("Age must be between 18 and 70.")
        return age

    def to_dict(self):
        return {
            "emp_id": self.emp_id,
            "name": self.name,
            "lname": self.lname,
            "age": self.age,
            "salary": self.salary,
            "position": self.position,
            "email": self.email
        }
