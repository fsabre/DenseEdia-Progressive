"""Define some exceptions."""


class DenseEdiaException(Exception):
    pass


class ObjectNotFound(DenseEdiaException):
    pass


class ValueTypeChange(DenseEdiaException):
    def __init__(self, old_type_name: str, new_type_name: str):
        msg = (
            "Changing type is not allowed "
            f"({old_type_name} -> {new_type_name})"
        )
        super().__init__(msg)


class UnsupportedTypeException(DenseEdiaException):
    def __init__(self, value):
        super().__init__(f"Type not supported : {type(value)}")
