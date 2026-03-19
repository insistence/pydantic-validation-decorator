from asyncio import iscoroutinefunction
from decimal import Decimal, InvalidOperation
from functools import wraps
from typing import Any, Optional
from pydantic import BaseModel
from .exceptions import FieldValidationError


class NumericPrecision:
    """
    Field Numeric Precision Validation Decorator
    """

    def __init__(
        self,
        field_name: str,
        max_digits: Optional[int] = None,
        decimal_places: Optional[int] = None,
        allow_none: bool = True,
        allow_string_number: bool = False,
        message: Optional[str] = None,
    ):
        """Field Numeric Precision Validation Decorator

        Args:
            field_name (str): Field name that needs to be validated.
            max_digits (Optional[int], optional): Maximum allowed total digits. Defaults to None.
            decimal_places (Optional[int], optional): Maximum allowed decimal places. Defaults to None.
            allow_none (bool, optional): If True, skip validation when field value is None. Defaults to True.
            allow_string_number (bool, optional): If True, allow numeric string as input. Defaults to False.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.

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

    def _convert_to_decimal(self, value: Any) -> Optional[Decimal]:
        """Convert value to Decimal for precision calculation.

        Args:
            value (Any): Current field value.

        Returns:
            Optional[Decimal]: Converted decimal value, or None when conversion fails.
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

    def _get_precision_info(self, decimal_value: Decimal) -> tuple[int, int]:
        """Extract total digits and decimal places from decimal value.

        Args:
            decimal_value (Decimal): Decimal value for precision calculation.

        Returns:
            tuple[int, int]: Total digits and decimal places.
        """
        sign, digits, exponent = decimal_value.as_tuple()
        _ = sign
        if exponent >= 0:
            total_digits = len(digits) + exponent
            current_decimal_places = 0
        else:
            total_digits = len(digits)
            current_decimal_places = -exponent
        return total_digits, current_decimal_places

    def _build_default_message(self, reason: str) -> str:
        """Build default validation message based on failure reason.

        Args:
            reason (str): Failure reason for precision validation.

        Returns:
            str: Default validation message.
        """
        return f'{self.field_name} precision validation failed: {reason}.'

    def _raise_validation_error(
        self,
        validate_model: BaseModel,
        field_value: Any,
        reason: str,
    ):
        """Raise a standardized field validation error.

        Args:
            validate_model (BaseModel): Pydantic model instance under validation.
            field_value (Any): Current field value.
            reason (str): Failure reason for precision validation.

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

    def _validate_precision(self, validate_model: BaseModel):
        """Execute numeric precision validation for the current model instance.

        Args:
            validate_model (BaseModel): Pydantic model instance under validation.
        """
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
        total_digits, current_decimal_places = self._get_precision_info(decimal_value)
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

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    self._validate_precision(validate_model)
                return await func(*args, **kwargs)

            return wrapper
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    self._validate_precision(validate_model)
                return func(*args, **kwargs)

            return wrapper
