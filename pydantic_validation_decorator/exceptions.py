from typing import Any
from warnings import warn


class FieldValidationError(Exception):
    """
    Custom Field Validation Exception FieldValidationError
    """

    def __init__(
        self,
        model_name: str = None,
        field_name: str = None,
        field_value: Any = None,
        validator: str = None,
        message: str = None,
    ):
        """Custom Field Validation Exception FieldValidationError

        Args:
            model_name (str, optional): Model name with error. Defaults to None.
            field_name (str, optional): Field name with error. Defaults to None.
            field_value (Any, optional): Field value with errors. Defaults to None.
            validator (str, optional): Validation decorator with errors. Defaults to None.
            message (str, optional): Prompt message for validation failure. Defaults to None.
        """
        self.model_name = model_name
        self.field_name = field_name
        self.field_value = field_value
        self.validator = validator
        self.message = message


class FunctionTypeError(Exception):
    """
    Custom Function Type Exception FunctionTypeError
    """

    def __init__(self, error: str = None, category: Any = None):
        """Custom Function Type Exception FunctionTypeError

        Args:
            error (str, optional): Error message. Defaults to None.
            category (Any, optional): Warning category. Defaults to None.
        """
        self.error = error
        self.category = category
        warn(self.error, category=self.category)
