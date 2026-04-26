from asyncio import iscoroutinefunction
from functools import wraps
from typing import Any, Iterable, Optional

from pydantic import BaseModel

from .exceptions import FieldValidationError


class AllowedValues:
    """
    Field Allowed Values Validation Decorator
    """

    def __init__(
        self,
        field_name: str,
        choices: Iterable[Any],
        allow_none: bool = True,
        case_sensitive: bool = True,
        message: Optional[str] = None,
    ):
        """Field Allowed Values Validation Decorator

        Args:
            field_name (str): Field name that needs to be validated.
            choices (Iterable[Any]): Allowed values for the field.
            allow_none (bool, optional): If True, skip validation when field value is None. Defaults to True.
            case_sensitive (bool, optional): If False, compare string values case-insensitively. Defaults to True.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.

        Raises:
            ValueError: choices cannot be empty.
        """
        self.field_name = field_name
        self.choices = tuple(choices)
        if not self.choices:
            raise ValueError('choices cannot be empty.')
        self.allow_none = allow_none
        self.case_sensitive = case_sensitive
        self.message = message

    def _normalize_value(self, value: Any) -> Any:
        """Normalize value before comparison.

        Args:
            value (Any): Current value that needs normalization.

        Returns:
            Any: Normalized value used for comparison.
        """
        if isinstance(value, str) and not self.case_sensitive:
            return value.lower()
        return value

    def _build_default_message(self) -> str:
        """Build the default validation message.

        Returns:
            str: Default validation message.
        """
        return f'{self.field_name} must be one of {self.choices}.'

    def _validate_allowed_values(self, validate_model: BaseModel):
        """Execute allowed values validation for the current model instance.

        Args:
            validate_model (BaseModel): Pydantic model instance under validation.

        Raises:
            FieldValidationError: Raised when the field value is not in the allowed values.
        """
        field_value = getattr(validate_model, self.field_name)
        if field_value is None and self.allow_none:
            return

        normalized_value = self._normalize_value(field_value)
        normalized_choices = tuple(self._normalize_value(choice) for choice in self.choices)
        if normalized_value not in normalized_choices:
            raise FieldValidationError(
                model_name=validate_model.__class__.__name__,
                field_name=self.field_name,
                field_value=field_value,
                validator=self.__class__.__name__,
                message=self.message if self.message else self._build_default_message(),
            )

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    self._validate_allowed_values(validate_model)
                return await func(*args, **kwargs)

            return wrapper
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    self._validate_allowed_values(validate_model)
                return func(*args, **kwargs)

            return wrapper
