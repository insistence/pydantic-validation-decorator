from decimal import Decimal, InvalidOperation
from typing import Any, NoReturn

from pydantic import BaseModel

from ._decorators import FieldValidator
from .exceptions import FieldValidationError


class NumericPrecision(FieldValidator):
    """Field Numeric Precision Validation Decorator."""

    def __init__(
        self,
        field_name: str,
        max_digits: int | None = None,
        decimal_places: int | None = None,
        allow_none: bool = True,
        allow_string_number: bool = False,
        message: str | None = None,
    ) -> None:
        """Set the digit and decimal-place limits for a numeric field.

        Args:
            field_name: Name of the field to validate.
            max_digits: Maximum allowed total digits. Defaults to None.
            decimal_places: Maximum allowed decimal places. Defaults to None.
            allow_none: If True, skip validation when field value is None. Defaults to True.
            allow_string_number: If True, allow numeric string as input. Defaults to False.
            message: Custom error message to use when validation fails.

        Raises:
            ValueError: max_digits and decimal_places cannot both be None.
            ValueError: max_digits must be greater than 0 when provided.
            ValueError: decimal_places cannot be less than 0.
            ValueError: decimal_places cannot be greater than max_digits.
        """
        if max_digits is None and decimal_places is None:
            raise ValueError('max_digits and decimal_places cannot both be None.')
        if max_digits is not None and max_digits <= 0:
            raise ValueError('max_digits must be greater than 0.')
        if decimal_places is not None and decimal_places < 0:
            raise ValueError('decimal_places cannot be less than 0.')
        if max_digits is not None and decimal_places is not None and decimal_places > max_digits:
            raise ValueError('decimal_places cannot be greater than max_digits.')
        self.field_name = field_name
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        self.allow_none = allow_none
        self.allow_string_number = allow_string_number
        self.message = message

    def _convert_to_decimal(self, value: Any) -> Decimal | None:
        """Convert value to Decimal for precision calculation.

        Args:
            value: Current field value.

        Returns:
            Converted decimal value, or None when conversion fails.
        """
        if isinstance(value, bool):
            return None
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        if isinstance(value, str) and self.allow_string_number:
            try:
                return Decimal(value.strip())
            except InvalidOperation:
                return None
        return None

    def _build_default_message(self, reason: str) -> str:
        """Build default validation message based on failure reason.

        Args:
            reason: Failure reason for precision validation.

        Returns:
            Default validation message.
        """
        return f'{self.field_name} precision validation failed: {reason}.'

    def _raise_validation_error(
        self,
        validate_model: BaseModel,
        field_value: Any,
        reason: str,
    ) -> NoReturn:
        """Raise a standardized field validation error.

        Args:
            validate_model: Pydantic model instance under validation.
            field_value: Current field value.
            reason: Failure reason for precision validation.

        Raises:
            FieldValidationError: Raised when precision validation fails.
        """
        raise FieldValidationError(
            model_name=validate_model.__class__.__name__,
            field_name=self.field_name,
            field_value=field_value,
            validator=self.__class__.__name__,
            message=self.message if self.message else self._build_default_message(reason),
        )

    def _validate(self, validate_model: BaseModel) -> None:
        """Execute numeric precision validation for the current model instance.

        Args:
            validate_model: Pydantic model instance under validation.
        """
        if not hasattr(validate_model, self.field_name):
            return
        field_value = getattr(validate_model, self.field_name)
        if field_value is None and self.allow_none:
            return
        decimal_value = self._convert_to_decimal(field_value)
        if decimal_value is None:
            self._raise_validation_error(
                validate_model,
                field_value,
                'value type is not numeric or numeric string is not allowed',
            )
        _, digits, exponent = decimal_value.as_tuple()
        if not isinstance(exponent, int):
            self._raise_validation_error(validate_model, field_value, 'value must be finite')
        total_digits = len(digits) + max(exponent, 0)
        current_decimal_places = max(-exponent, 0)
        if self.max_digits is not None and total_digits > self.max_digits:
            self._raise_validation_error(
                validate_model,
                field_value,
                f'total digits {total_digits} exceed max_digits {self.max_digits}',
            )
        if self.decimal_places is not None and current_decimal_places > self.decimal_places:
            self._raise_validation_error(
                validate_model,
                field_value,
                f'decimal places {current_decimal_places} exceed decimal_places {self.decimal_places}',
            )
