from datetime import datetime
from typing import Any, NoReturn

from pydantic import BaseModel

from ._decorators import FieldValidator
from .exceptions import FieldValidationError


class DateTimeRange(FieldValidator):
    """Field DateTime Range Validation Decorator."""

    def __init__(
        self,
        start_field: str,
        end_field: str,
        allow_equal: bool = True,
        allow_none: bool = True,
        coerce_from_str: bool = True,
        require_timezone_consistency: bool = False,
        message: str | None = None,
    ) -> None:
        """Configure the ordering and timezone checks for two datetime fields.

        Args:
            start_field: Start datetime field name.
            end_field: End datetime field name.
            allow_equal: If True, allow start datetime equal to end datetime. Defaults to True.
            allow_none: If True, skip validation when either field value is None. Defaults to True.
            coerce_from_str: If True, allow ISO datetime string and convert to datetime. Defaults to
                True.
            require_timezone_consistency: If True, require start and end datetime to be both
                timezone-aware or both timezone-naive. Defaults to False.
            message: Custom error message to use when validation fails.

        Raises:
            ValueError: start_field and end_field cannot be the same.
        """
        if start_field == end_field:
            raise ValueError('start_field and end_field cannot be the same.')
        self.start_field = start_field
        self.end_field = end_field
        self.allow_equal = allow_equal
        self.allow_none = allow_none
        self.coerce_from_str = coerce_from_str
        self.require_timezone_consistency = require_timezone_consistency
        self.message = message

    def _is_timezone_aware(self, value: datetime) -> bool:
        """Determine whether datetime value is timezone-aware.

        Args:
            value: Datetime value under validation.

        Returns:
            True when datetime is timezone-aware.
        """
        return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None

    def _to_datetime(self, value: Any) -> datetime | None:
        """Convert input value to datetime.

        Args:
            value: Current field value.

        Returns:
            Converted datetime value, or None when conversion fails.
        """
        if isinstance(value, datetime):
            return value
        if isinstance(value, str) and self.coerce_from_str:
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return None
        return None

    def _build_default_message(self, start_value: Any, end_value: Any) -> str:
        """Build default validation message for datetime range failure.

        Args:
            start_value: Current start field value.
            end_value: Current end field value.

        Returns:
            Default validation message.
        """
        operator = '<=' if self.allow_equal else '<'
        return (
            f'{self.start_field} must satisfy {self.start_field} {operator} {self.end_field}, '
            f'but got {start_value} and {end_value}.'
        )

    def _raise_validation_error(
        self,
        validate_model: BaseModel,
        start_value: Any,
        end_value: Any,
        reason: str,
    ) -> NoReturn:
        """Raise a standardized field validation error.

        Args:
            validate_model: Pydantic model instance under validation.
            start_value: Current start field value.
            end_value: Current end field value.
            reason: Validation failure reason.

        Raises:
            FieldValidationError: Raised when datetime range validation fails.
        """
        default_message = f'{self._build_default_message(start_value, end_value)} Reason: {reason}.'
        raise FieldValidationError(
            model_name=validate_model.__class__.__name__,
            field_name=self.start_field,
            field_value=start_value,
            validator=self.__class__.__name__,
            message=self.message if self.message else default_message,
        )

    def _validate(self, validate_model: BaseModel) -> None:
        """Execute datetime range validation for current model instance.

        Args:
            validate_model: Pydantic model instance under validation.
        """
        if not hasattr(validate_model, self.start_field) or not hasattr(validate_model, self.end_field):
            return
        start_value = getattr(validate_model, self.start_field)
        end_value = getattr(validate_model, self.end_field)
        if self.allow_none and (start_value is None or end_value is None):
            return
        if start_value is None or end_value is None:
            self._raise_validation_error(validate_model, start_value, end_value, 'datetime value is None')
        start_datetime = self._to_datetime(start_value)
        end_datetime = self._to_datetime(end_value)
        if start_datetime is None or end_datetime is None:
            self._raise_validation_error(
                validate_model,
                start_value,
                end_value,
                'datetime value type is invalid or string format is invalid',
            )
        if self.require_timezone_consistency:
            start_tz_aware = self._is_timezone_aware(start_datetime)
            end_tz_aware = self._is_timezone_aware(end_datetime)
            if start_tz_aware != end_tz_aware:
                self._raise_validation_error(
                    validate_model,
                    start_value,
                    end_value,
                    'timezone awareness is inconsistent',
                )
        try:
            compare_result = start_datetime <= end_datetime if self.allow_equal else start_datetime < end_datetime
        except TypeError:
            compare_result = False
        if not compare_result:
            self._raise_validation_error(
                validate_model,
                start_value,
                end_value,
                'datetime range comparison failed',
            )
