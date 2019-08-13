import re
from datetime import datetime

from validation.errorinfo import ErrorInfo
from validation.error_codes import ErrorCode


DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'

VALID_URLS_REGEXS = [
    r"^https://www.instagram.com/p/[^\s]+/$"
]


class Validator:
    def validate(self, value):
        raise NotImplementedError()


class IntegerValidator(Validator):
    def validate(self, value):
        errors = []
        new_value = value
        if isinstance(value, int):
            return errors, new_value
        if not isinstance(value, str):
            errors.append(ErrorInfo(ErrorCode.NotIntegerError))
            return errors, None
        try:
            new_value = int(new_value)
        except Exception as ex:
            errors.append(ErrorCode.NotIntegerStringError)
            return errors, None
        return errors, new_value


class StringValidator(Validator):
    def validate(self, value):
        errors = []
        new_value = value
        if not isinstance(value, str):
            errors.append(ErrorInfo(ErrorCode.NotStringError))
        return errors, None if errors else new_value


class FloatValidator(Validator):
    def validate(self, value):
        errors = []
        new_value = value
        if isinstance(value, float):
            return errors, new_value
        if isinstance(value, int):
            new_value = float(new_value)
            return errors, new_value
        if not isinstance(value, str):
            errors.append(ErrorInfo(ErrorCode.NotFloatError))
            return errors, None
        try:
            new_value = float(new_value)
        except Exception as ex:
            errors.append(ErrorCode.NotFloatStringError)
            return errors, None
        return errors, new_value


class EnumValidator(Validator):
    def __init__(self, enum_class):
        self.enum_class = enum_class

    def validate(self, value):
        errors = []
        new_value = value
        if isinstance(value, self.enum_class):
            return errors, new_value
        if not isinstance(value, str):
            errors.append(ErrorInfo(ErrorCode.NotEnumError))
            return errors, None
        for i, enum_value in enumerate(self.enum_class):
            if value == enum_value.name:
                new_value = enum_value
                return errors, new_value
        errors.append(ErrorInfo(ErrorCode.NotDatetimeStringError))
        return errors, None


class BooleanValidator(Validator):
    def validate(self, value):
        errors = []
        new_value = value
        if isinstance(value, bool):
            return errors, new_value
        if isinstance(value, int):
            new_value = bool(value)
            return errors, new_value
        if isinstance(value, str):
            lower_value = value.lower().strip()
            if lower_value == 'true':
                new_value = True
            elif lower_value == 'false':
                new_value = False
            else:
                errors.append(ErrorInfo(ErrorCode.NotBoolStringError))
            return errors, None if errors else new_value
        errors.append(ErrorInfo(ErrorCode.NotBoolError))
        return errors, None


class DatetimeValidator(Validator):
    def validate(self, value):
        errors = []
        new_value = value
        if isinstance(value, datetime):
            return errors, new_value
        if not isinstance(value, str):
            errors.append(ErrorInfo(ErrorCode.NotDatetimeError))
            return errors, None
        try:
            new_value = datetime.strptime(new_value, DATETIME_FORMAT)
        except Exception as ex:
            errors.append(ErrorInfo(ErrorCode.NotDatetimeStringError))
            return errors, None
        return errors, new_value


class IntegerMaxValueValidator(Validator):
    def __init__(self, max_value):
        self.max_value = max_value
        self.integer_validator = IntegerValidator()

    def validate(self, value):
        errors, new_value = self.integer_validator.validate(value)
        if not errors and new_value > self.max_value:
            errors.append(ErrorInfo(ErrorCode.MaxValueError, max_value=self.max_value))
        return errors, None if errors else new_value


class IntegerMinValueValidator(Validator):
    def __init__(self, min_value):
        self.min_value = min_value
        self.integer_validator = IntegerValidator()

    def validate(self, value):
        errors, new_value = self.integer_validator.validate(value)
        if not errors and new_value < self.min_value:
            errors.append(ErrorInfo(ErrorCode.MinValueError, min_value=self.min_value))
        return errors, None if errors else new_value


class StringMaxLengthValidator(Validator):
    def __init__(self, max_length):
        self.max_length = max_length
        self.string_validator = StringValidator()

    def validate(self, value):
        errors, new_value = self.string_validator.validate(value)
        if not errors and len(value) > self.max_length:
            errors.append(ErrorInfo(ErrorCode.MaxLengthStringError, max_length=self.max_length))
        return errors, None if errors else new_value


class StringMinLengthValidator(Validator):
    def __init__(self, min_length):
        self.min_length = min_length
        self.string_validator = StringValidator()

    def validate(self, value):
        errors, new_value = self.string_validator.validate(value)
        if not errors and len(value) < self.min_length:
            errors.append(ErrorInfo(ErrorCode.MaxLengthStringError, min_length=self.min_length))
        return errors, None if errors else new_value


class StringUrlValidator(Validator):
    def __init__(self, url_regexs=None):
        self.url_regexs = url_regexs if url_regexs else VALID_URLS_REGEXS
        self.string_validator = StringValidator()

    def validate(self, value):
        errors, new_value = self.string_validator.validate(value)
        if not errors and not any(regex for regex in self.url_regexs if re.match(regex, value)):
            errors.append(ErrorInfo(ErrorCode.NotPostUrlStringError))
        return errors, None if errors else new_value


class AllowedValuesValidator(Validator):
    def __init__(self, allowed_values):
        self.allowed_values = allowed_values

    def validate(self, value):
        errors = []
        new_value = value
        if value not in self.allowed_values:
            errors.append(ErrorInfo(ErrorCode.NotAllowedValueError))
        return errors, None if errors else new_value
