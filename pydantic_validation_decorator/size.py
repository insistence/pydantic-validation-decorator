from pydantic import BaseModel

from ._decorators import FieldValidator
from .exceptions import FieldValidationError


class Size(FieldValidator):
    """Field Size Validation Decorator."""

    def __init__(
        self,
        field_name: str,
        gt: float | int | None = None,
        ge: float | int | None = None,
        lt: float | int | None = None,
        le: float | int | None = None,
        min_length: int | None = 0,
        max_length: int | None = None,
        message: str | None = None,
    ) -> None:
        """Set numeric bounds and string length limits for a field.

        Args:
            field_name: Name of the field to validate.
            gt: The numerical field value must be greater than gt. Defaults to None.
            ge: The numerical field value must be greater than or equal to ge. Defaults to None.
            lt: The numerical field value must be less than lt. Defaults to None.
            le: The numerical field value must be less than or equal to le. Defaults to None.
            min_length: The length of a string field cannot be less than min_length. Defaults to 0.
            max_length: The length of a string field cannot be greater than max_length. Defaults to
                None.
            message: Custom error message to use when validation fails.
        """
        self.field_name = field_name
        self.gt = gt
        self.ge = ge
        self.lt = lt
        self.le = le
        self.min_length = max(0, min_length or 0)
        self.max_length = max_length
        self.message = message

    def _validate(self, validate_model: BaseModel) -> None:
        if not hasattr(validate_model, self.field_name):
            return
        field_value = getattr(validate_model, self.field_name)
        if isinstance(field_value, (int, float)):
            if self.gt is not None and field_value <= self.gt:
                raise FieldValidationError(
                    model_name=validate_model.__class__.__name__,
                    field_name=self.field_name,
                    field_value=field_value,
                    validator=self.__class__.__name__,
                    message=self.message if self.message else f'{self.field_name} must be greater than {self.gt}.',
                )
            if self.ge is not None and field_value < self.ge:
                raise FieldValidationError(
                    model_name=validate_model.__class__.__name__,
                    field_name=self.field_name,
                    field_value=field_value,
                    validator=self.__class__.__name__,
                    message=self.message
                    if self.message
                    else f'{self.field_name} must be greater than or equal to {self.ge}.',
                )
            if self.lt is not None and field_value >= self.lt:
                raise FieldValidationError(
                    model_name=validate_model.__class__.__name__,
                    field_name=self.field_name,
                    field_value=field_value,
                    validator=self.__class__.__name__,
                    message=self.message if self.message else f'{self.field_name} must be less than {self.lt}.',
                )
            if self.le is not None and field_value > self.le:
                raise FieldValidationError(
                    model_name=validate_model.__class__.__name__,
                    field_name=self.field_name,
                    field_value=field_value,
                    validator=self.__class__.__name__,
                    message=self.message
                    if self.message
                    else f'{self.field_name} must be less than or equal to {self.le}.',
                )
        elif isinstance(field_value, str):
            if len(field_value) < self.min_length:
                raise FieldValidationError(
                    model_name=validate_model.__class__.__name__,
                    field_name=self.field_name,
                    field_value=field_value,
                    validator=self.__class__.__name__,
                    message=self.message
                    if self.message
                    else f'The length of {self.field_name} cannot be less than {self.min_length}.',
                )
            if self.max_length is not None and len(field_value) > self.max_length:
                raise FieldValidationError(
                    model_name=validate_model.__class__.__name__,
                    field_name=self.field_name,
                    field_value=field_value,
                    validator=self.__class__.__name__,
                    message=self.message
                    if self.message
                    else f'The length of {self.field_name} cannot be greater than {self.max_length}.',
                )
