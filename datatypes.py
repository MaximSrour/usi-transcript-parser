from dataclasses import dataclass


@dataclass
class Course:
    code: str
    name: str

    def __init__(self, code: str, name: str):
        self.code = code.strip().upper()
        self.name = name.strip().upper()


@dataclass
class Result:
    student_name: str
    result: str
    course: Course

    def to_list(self):
        return [self.student_name, self.result, self.course.code, self.course.name]
