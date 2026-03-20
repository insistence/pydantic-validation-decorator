from asyncio import iscoroutinefunction
from datetime import datetime
from functools import wraps
from typing import Any, Optional
from pydantic import BaseModel
from .exceptions import FieldValidationError


class DateTimeRange:
    """
    Field DateTime Range Validation Decorator
    """

    def __init__(
        self,
        start_field: str,
        end_field: str,
        allow_equal: bool = True,
        allow_none: bool = True,
        coerce_from_str: bool = True,
        require_timezone_consistency: bool = False,
        message: Optional[str] = None,
    ):
        """Field DateTime Range Validation Decorator

        Args:
            start_field (str): Start datetime field name.
            end_field (str): End datetime field name.
            allow_equal (bool, optional): If True, allow start datetime equal to end datetime. Defaults to True.
            allow_none (bool, optional): If True, skip validation when either field value is None. Defaults to True.
            coerce_from_str (bool, optional): If True, allow ISO datetime string and convert to datetime. Defaults to True.
            require_timezone_consistency (bool, optional): If True, require start and end datetime to be both timezone-aware or both timezone-naive. Defaults to False.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.

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
            value (datetime): Datetime value under validation.

        Returns:
            bool: True when datetime is timezone-aware.
        """
        return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None

    def _to_datetime(self, value: Any) -> Optional[datetime]:
        """Convert input value to datetime.

        Args:
            value (Any): Current field value.

        Returns:
            Optional[datetime]: Converted datetime value, or None when conversion fails.
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
            start_value (Any): Current start field value.
            end_value (Any): Current end field value.

        Returns:
            str: Default validation message.
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
    ):
        """Raise a standardized field validation error.

        Args:
            validate_model (BaseModel): Pydantic model instance under validation.
            start_value (Any): Current start field value.
            end_value (Any): Current end field value.
            reason (str): Validation failure reason.

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

    def _validate_datetime_range(self, validate_model: BaseModel):
        """Execute datetime range validation for current model instance.

        Args:
            validate_model (BaseModel): Pydantic model instance under validation.
        """
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

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if (
                    isinstance(validate_model, BaseModel)
                    and hasattr(validate_model, self.start_field)
                    and hasattr(validate_model, self.end_field)
                ):
                    self._validate_datetime_range(validate_model)
                return await func(*args, **kwargs)

            return wrapper
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if (
                    isinstance(validate_model, BaseModel)
                    and hasattr(validate_model, self.start_field)
                    and hasattr(validate_model, self.end_field)
                ):
                    self._validate_datetime_range(validate_model)
                return func(*args, **kwargs)

            return wrapper
