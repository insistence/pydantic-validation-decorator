import re

from pydantic import BaseModel

from ._decorators import FieldValidator
from .exceptions import FieldValidationError


class Pattern(FieldValidator):
    """Field Pattern Validation Decorator."""

    def __init__(
        self,
        field_name: str,
        regexp: str,
        message: str | None = None,
    ) -> None:
        """Choose a regular expression for validating a field.

        Args:
            field_name: Name of the field to validate.
            regexp: Regular expression.
            message: Custom error message to use when validation fails.
        """
        self.field_name = field_name
        self.regexp = regexp
        self.message = message

    def _validate(self, validate_model: BaseModel) -> None:
        if not hasattr(validate_model, self.field_name):
            return
        field_value = getattr(validate_model, self.field_name)
        if isinstance(field_value, str) and not re.match(self.regexp, field_value):
            raise FieldValidationError(
                model_name=validate_model.__class__.__name__,
                field_name=self.field_name,
                field_value=field_value,
                validator=self.__class__.__name__,
                message=self.message if self.message else f'The format of {self.field_name} is incorrect.',
            )
