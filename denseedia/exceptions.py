class DenseEdiaException(Exception):
    pass


class ObjectNotFound(DenseEdiaException):
    pass


class ValueTypeChange(DenseEdiaException):
    pass


class UnsupportedTypeException(DenseEdiaException):
    pass
