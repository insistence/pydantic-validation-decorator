from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel

from ._decorators import FieldValidator
from .exceptions import FieldValidationError


class AllowedValues(FieldValidator):
    """Field Allowed Values Validation Decorator."""

    def __init__(
        self,
        field_name: str,
        choices: Iterable[Any],
        allow_none: bool = True,
        case_sensitive: bool = True,
        message: str | None = None,
    ) -> None:
        """Configure the set of allowed field values.

        Args:
            field_name: Name of the field to validate.
            choices: Allowed values for the field.
            allow_none: If True, skip validation when field value is None. Defaults to True.
            case_sensitive: If False, compare string values case-insensitively. Defaults to True.
            message: Custom error message to use when validation fails.

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
            value: Current value that needs normalization.

        Returns:
            Normalized value used for comparison.
        """
        if isinstance(value, str) and not self.case_sensitive:
            return value.lower()
        return value

    def _build_default_message(self) -> str:
        """Build the default validation message.

        Returns:
            Default validation message.
        """
        return f'{self.field_name} must be one of {self.choices}.'

    def _validate(self, validate_model: BaseModel) -> None:
        """Execute allowed values validation for the current model instance.

        Args:
            validate_model: Pydantic model instance under validation.

        Raises:
            FieldValidationError: Raised when the field value is not in the allowed values.
        """
        if not hasattr(validate_model, self.field_name):
            return
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
