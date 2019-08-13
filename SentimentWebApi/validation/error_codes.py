from enum import Enum


class ErrorCode(Enum):
    UnknownError = 0, 'Unknown error'
    NotDefinedError = 1, 'Field is required'
    NotUniqueError = 2, 'Value is not unique'
    NotAllowedValueError = 3, 'Value is not allowed'

    NotStringError = 100, 'Value is not string value'
    WhiteSpaceStringError = 101, 'Non empty string is required'
    MaxLengthStringError = 102, 'Max allowed length is {max_length}'
    MinlengthStringError = 103, 'Min allowed length is {min_length}'

    NotIntegerStringError = 104, 'String is not integer string'
    NotFloatStringError = 105, 'String is not float string'
    NotDatetimeStringError = 106, 'String is not datetime string'
    NotEnumStringError = 107, 'String is not valid enum string'
    NotBoolStringError = 108, 'String is not boolean string'
    NotPostUrlStringError = 109, 'String is not post url string'

    MaxValueError = 110, 'Max allowed value is {max_value}'
    MinValueError = 111, 'Min allowed value is {min_value}'

    NotIntegerError = 201, 'Value is not integer value'

    NotDatetimeError = 301, 'Value is not integer value'

    NotFloatError = 401, 'Value is not float value'

    NotEnumError = 501, 'Value is not valid enum value'

    NotBoolError = 601, 'Value is not valid enum value'
