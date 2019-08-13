import json
from typing import List

from validation.error_codes import ErrorCode


class ErrorInfo:
    def __init__(self, error_code: ErrorCode, **kwargs):
        self.error_name = error_code.name
        self.error_code = error_code.value[0]
        self.message = error_code.value[1].format(**kwargs)
        self.kwargs = {key: value for key, value in kwargs.items()}

    def to_dict(self):
        error_info = {
            'code': self.error_code,
            'name': self.error_name,
            'message': self.message
        }
        error_info.update(self.kwargs)
        return error_info


class FieldError(Exception):
    def __init__(self, field_name, errors_info):
        self.field_name = field_name
        self.errors_info = errors_info

    def to_dict(self):
        return {
            'field_name': self.field_name,
            'errors': [error_info.to_dict() for error_info in self.errors_info]
        }

    def __str__(self):
        return print(json.dumps(self.to_dict(), indent=4))


class ObjectError(Exception):
    def __init__(self, obj_name, fields_error: List[FieldError]):
        self.obj_name = obj_name
        self.fields_errors = {}
        for field_error in fields_error:
            if field_error.field_name in self.fields_errors:
                self.fields_errors[field_error.field_name].extend(field_error.errors_info)
            else:
                self.fields_errors[field_error.field_name] = field_error.errors_info

    def to_dict(self):
        return {
            'obj_name': self.obj_name,
            'errors': {
                field: [error_info.to_dict()
                        for error_info in errors_info] for field, errors_info in self.fields_errors.items()
            }
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)


