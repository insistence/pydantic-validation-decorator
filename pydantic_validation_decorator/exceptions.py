from typing import Any
from warnings import warn


class FieldValidationError(Exception):
    """Custom Field Validation Exception FieldValidationError."""

    def __init__(
        self,
        model_name: str | None = None,
        field_name: str | None = None,
        field_value: Any = None,
        validator: str | None = None,
        message: str | None = None,
    ) -> None:
        """Record the model, field and validator that caused the error.

        Args:
            model_name: Model name with error. Defaults to None.
            field_name: Field name with error. Defaults to None.
            field_value: Field value with errors. Defaults to None.
            validator: Validation decorator with errors. Defaults to None.
            message: Prompt message for validation failure. Defaults to None.
        """
        self.model_name = model_name
        self.field_name = field_name
        self.field_value = field_value
        self.validator = validator
        self.message = message


class FunctionTypeError(Exception):
    """Custom Function Type Exception FunctionTypeError."""

    def __init__(self, error: str | None = None, category: type[Warning] | None = None) -> None:
        """Report an incompatible validation function.

        Args:
            error: Error message. Defaults to None.
            category: Warning category. Defaults to None.
        """
        self.error = error
        self.category = category
        warn(str(self.error), category=self.category, stacklevel=2)
