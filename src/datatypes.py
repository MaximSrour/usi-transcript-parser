from dataclasses import dataclass
from typing import List, Union


@dataclass
class Course:
    code: str
    name: str
    provider: Union[str, None]

    def __init__(self, code: str, name: str, provider: Union[str, None] = None):
        self.code = code.strip().upper()
        self.name = name.strip().upper()

        if provider is not None:
            self.provider = provider.strip().upper()
        else:
            self.provider = None


@dataclass
class Result:
    student_name: str
    result: str
    course: Course

    def to_list(self):
        output: List[str] = [
            self.student_name,
            self.result,
            self.course.code,
            self.course.name,
            self.course.provider if self.course.provider is not None else "",
        ]

        return output
