from typing import Any

from pydantic import BaseModel

from ._decorators import FieldValidator
from .exceptions import FieldValidationError


class RequiredIf(FieldValidator):
    """Field Conditional Required Validation Decorator."""

    def __init__(
        self,
        field_name: str,
        when_field: str,
        when_value: Any,
        message: str | None = None,
    ) -> None:
        """Require a field when another field matches a trigger value.

        Args:
            field_name: Name of the field to validate.
            when_field: Condition field name used to trigger validation.
            when_value: Trigger value for the condition field. Supports single value or collection.
            message: Custom error message to use when validation fails.
        """
        self.field_name = field_name
        self.when_field = when_field
        self.when_value = when_value
        self.message = message

    def _should_validate(self, value: Any) -> bool:
        """Determine whether conditional required validation should be triggered.

        Args:
            value: Current value of the condition field.

        Returns:
            True when the condition matches and required validation should run.
        """
        if isinstance(self.when_value, (list, tuple, set, frozenset)):
            return value in self.when_value
        return bool(value == self.when_value)

    def _is_empty(self, value: Any) -> bool:
        """Determine whether the target field should be treated as empty.

        Args:
            value: Current value of the target field.

        Returns:
            True when the value is considered empty for required validation.
        """
        return value is None or value in ('', [], (), {})

    def _validate(self, validate_model: BaseModel) -> None:
        if not hasattr(validate_model, self.field_name) or not hasattr(validate_model, self.when_field):
            return
        when_field_value = getattr(validate_model, self.when_field)
        if self._should_validate(when_field_value):
            field_value = getattr(validate_model, self.field_name)
            if self._is_empty(field_value):
                raise FieldValidationError(
                    model_name=validate_model.__class__.__name__,
                    field_name=self.field_name,
                    field_value=field_value,
                    validator=self.__class__.__name__,
                    message=(
                        self.message
                        if self.message
                        else f'{self.field_name} is required when {self.when_field} is {self.when_value}.'
                    ),
                )
